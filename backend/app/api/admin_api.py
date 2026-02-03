from bson import ObjectId
from app.controller.admin_controller import AdminController
from app.schema.base_schema import BaseResponse
from app.schema.admin_schema import AdminRejctReasonSchema, AdminSchema
from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, HTTPException, status
from app.models.admin import AdminModel
from app.controller.admin_controller import admin_required
from app.controller.user_controller import UserController
from app.models.firm import FirmModel
from app.models.article import ArticleModel, ArticleStatus
from app.models.report import ReportModel
from app.controller.email_controller import (
    KYC_status_email,
    report_action_email,
)


router = APIRouter(prefix="/admin", tags=["Admin"])

admin_controller = AdminController()
user_controller = UserController()


@router.post(
    "/register", response_model=BaseResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(admin_data: AdminSchema):
    try:

        admin = await admin_controller.create_admin(admin_data.dict())
        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Admin already exists"
            )

        response_data = {
            "status": 1,
            "message": "Admin created",
            "data": {"username": admin.email},
        }
        return response_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/login", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def admin_login(request: Request, data: AdminSchema):
    try:
        admin = await AdminModel.find_one(
            AdminModel.email == data.email, AdminModel.is_deleted == False
        )
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not admin.verify_password(data.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Set session
        request.session["admin_id"] = str(admin.id)
        return {
            "status": 1,
            "message": "Login successful",
            "data": {"email": admin.email},
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get(
    "/check-session", response_model=BaseResponse, status_code=status.HTTP_200_OK
)
async def check_session(request: Request):
    try:
        admin_id = request.session.get("admin_id")
        if admin_id:
            return {
                "status": 1,
                "message": "Admin is logged in",
                "data": {"admin_id": admin_id},
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/logout", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def logout(request: Request):
    request.session.clear()
    return {"status": 1, "message": "Logged out successfully", "data": {None}}


@router.get("/dashboard", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def dashboard(admin_id: str = Depends(admin_required)):
    return {"KYC": "/admin/kyc", "Firms": "/admin/firms", "Reports": "/admin/reports"}


@router.get("/kyc", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def list_kyc(admin_id: str = Depends(admin_required)):
    try:
        kyc_data = await admin_controller.get_kyc()

        if not kyc_data or len(kyc_data) == 0:
            return {
                "status": 1,
                "message": "No KYC data to validate",
                "data": {"data": []},
            }

        return {
            "status": 1,
            "message": "KYC data retrieved",
            "data": {
                "data": kyc_data,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/kyc/{user_id}/approve",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_kyc(
    user_id: str,
    background_tasks: BackgroundTasks,
    admin_id: str = Depends(admin_required),
):
    try:
        kyc = await admin_controller.approve_kyc(user_id)

        if kyc is None:
            return {
                "status": 1,
                "message": "No KYC data to validate",
                "data": {"data": []},
            }
        user = await user_controller.get_user(user_id)
        background_tasks.add_task(
            KYC_status_email, to_email=user.email, status=kyc.kyc_status, reason=None
        )

        return {
            "status": 1,
            "message": "KYC approved",
            "data": {
                "kyc_id": str(kyc.id),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/kyc/{user_id}/reject", response_model=BaseResponse, status_code=status.HTTP_200_OK
)
async def reject_kyc(
    user_id: str,
    data: AdminRejctReasonSchema,
    background_tasks: BackgroundTasks,
    admin_id: str = Depends(admin_required),
):
    try:
        kyc_record = await admin_controller.reject_kyc(user_id, data.reason)
        if kyc_record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="KYC record not found"
            )

        user = await user_controller.get_user(user_id)

        background_tasks.add_task(
            KYC_status_email,
            to_email=user.email,
            status=kyc_record.kyc_status,
            reason=kyc_record.rejection_reason,
        )

        return {
            "status": 1,
            "message": "KYC Rejected",
            "data": {
                "kyc_id": str(kyc_record.id),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# Reports
@router.get("/reports", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def list_reports(admin_id: str = Depends(admin_required)):
    try:
        firms = await FirmModel.find(
            FirmModel.is_deleted == False, FirmModel.report_count >= 30
        ).to_list()

        articles = await ArticleModel.find(
            ArticleModel.is_deleted == False,
            ArticleModel.status == ArticleStatus.PUBLISHED,
            ArticleModel.report_count >= 15,
        ).to_list()

        return {
            "status": 1,
            "message": "Reported Firms",
            "data": {
                "firms": firms,
                "articles": articles,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get(
    "/user-reports", response_model=BaseResponse, status_code=status.HTTP_200_OK
)
async def list_reports(admin_id: str = Depends(admin_required)):
    try:
        reports = await ReportModel.find_all().sort("-created_at").to_list()

        return {
            "status": 1,
            "message": "Reported Firms",
            "data": {
                "reports": reports,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/report/action",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
)
async def handle_report(
    firm_id: str = Query(None),
    article_id: str = Query(None),
    admin_id: str = Depends(admin_required),
    data: AdminRejctReasonSchema = None,
    background_tasks: BackgroundTasks = None,
):
    try:
        to_email = None
        firm = None
        article = None
        if firm_id:
            firm = await FirmModel.find_one(
                FirmModel.id == ObjectId(firm_id), FirmModel.is_deleted == False
            )

            if not firm:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Firm Not Found"
                )
            
            firm.is_deleted = True
            firm.is_active = False
            await firm.save()
            print("deltetedddd")
            owner = await firm.owner_user_id.fetch()
            to_email = owner.email

            

        if article_id:
            article = await ArticleModel.find_one(
                ArticleModel.id == ObjectId(article_id),
                ArticleModel.is_deleted == False,
            )

            if not article:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Article Not Found"
                )

            article.is_deleted = True
            await article.save()
            
            owner = await article.publisher_id.fetch()
            to_email = owner.email

            

        delete_reports = await ReportModel.find_many(
            ReportModel.article_id.id == firm,
            ReportModel.article_id.id == article,
            ReportModel.is_deleted == False,
        ).to_list()
        for report in delete_reports:
            report.is_deleted = True
            await report.save()

        # send mail
        background_tasks.add_task(
            report_action_email,
            to_email=to_email,
            firm=firm,
            article=article,
            reason=data.reason,
        )

        return {
            "status": 1,
            "message": "Deleted Successfully",
            "data": None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
