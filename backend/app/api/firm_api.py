from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query

# from app.controller.user_controller import UserController
from app.controller.token_controller import get_current_user
from app.schema.base_schema import BaseResponse
from app.controller.firm_controller import FirmController
from app.schema.firm_schema import AddPublisherSchema, FirmCreateSchema, FirmDetailsOutSchema
from fastapi import status

from app.models.users import UserModel
from app.models.kyc import KYCModel
from app.models.firm import FirmModel
from app.models.article import ArticleModel
from app.controller.article_controller import ArticleController
from app.schema.article_schema import ArticleOutSchema


router = APIRouter(prefix="/firm", tags=["Firm"])

firm_controller = FirmController()
article_controller = ArticleController()

@router.post(
    "/register", response_model=BaseResponse, status_code=status.HTTP_201_CREATED
)
async def create_firm_api(
    firm_data: FirmCreateSchema, current_user: dict = Depends(get_current_user)
):
    """
    Create a new firm. Only KYC-verified users can create a firm.
    """
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token, Login to continue",
            )

        user = await UserModel.get(ObjectId(current_user["user_id"]))
        if not user or not user.is_verified or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User Not found"
            )

        kyc = await KYCModel.find_one(
            KYCModel.user_id.id == ObjectId(current_user["user_id"])
        )
        if not kyc or kyc.kyc_status != "VERIFIED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="KYC required to create firm",
            )

        success = await firm_controller.create_firm(
            firm_data, user, ObjectId(current_user["user_id"])
        )

        if not success:
            # Could be failure due to duplicate username, etc
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create firm."
            )

        return BaseResponse(
            status=1,
            message="Firm created successfully",
            data={"firm_username": success.firm_username},
        )

    except HTTPException as e:
        # propagate HTTPException so FastAPI can return it
        raise e

    except Exception as e:
        # catch all unexpected errors
        return BaseResponse(
            status=0, message=f"Internal server error: {str(e)}", data=None
        )


@router.post("/add-publisher", response_model=BaseResponse)
async def add_publisher(
    data: AddPublisherSchema, current_user: dict = Depends(get_current_user)
):
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token, Login to continue",
            )

        new_publisher = await firm_controller.add_publisher(data)
        response_data = {
            "status": 1,
            "message": "Publisher added successfully",
            "data": {
                "publisher_user_id": str(new_publisher.publisher_user_id.id),
                "invited_at": new_publisher.invited_at,
            },
        }
        return response_data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# @router.get("/details", response_model=BaseResponse)
# async def get_firm_details(
#     firm_id: str | None = Query(None), 
#     current_user: dict = Depends(get_current_user)
    
#     ):
#     try:
#         if current_user is None:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid access token, Login to continue",
#             )
        
#         if not firm_id:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="firm_id is required"
#             )
        
#         try:
#             firm_oid = ObjectId(firm_id)
#         except Exception:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Invalid firm_id"
#             )
            
#         firm =await FirmModel.find_one(
#             FirmModel.id == firm_oid,
#             FirmModel.is_deleted == False,
#         )
#         if not firm:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="Firm not found"
#             )
        
        
#         query = [
#             ArticleModel.firm_id.id == firm_oid,
#             ArticleModel.is_deleted == False,
#             ArticleModel.status == ArticleStatus.PUBLISHED,
#         ]
   

#         articles = await ArticleModel.find(*query).sort(-ArticleModel.published_at).to_list()
#         article_data = articles if articles else None

#         data = {"firm_data": firm, "articles": article_data}

            
#         response_data = {
#             "status": 1,
#             "message": "Firm details fetched successfully",
#             "data": data,
#         }
#         return response_data
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#         )



# from beanie import PydanticObjectId

# @router.get("/details", response_model=BaseResponse)
# async def get_firm_details(
#     firm_id: str | None = Query(None), 
#     current_user: dict = Depends(get_current_user)
# ):
#     if current_user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid access token, Login to continue",
#         )

#     if not firm_id:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="firm_id is required"
#         )

#     try:
#         firm_oid = PydanticObjectId(firm_id)
#     except Exception:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid firm_id"
#         )

#     # Fetch firm
#     firm = await FirmModel.find_one(FirmModel.id == firm_oid, FirmModel.is_deleted == False)
#     if not firm:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Firm not found"
#         )

#     # Fetch linked owner user
#     await firm.fetch_link(FirmModel.owner_user_id)

#     # Fetch articles
#     query = [
#         ArticleModel.firm_id.id == firm_oid,
#         ArticleModel.is_deleted == False,
#         ArticleModel.status == ArticleStatus.PUBLISHED,
#     ]

#     articles = await ArticleModel.find(*query).sort(-ArticleModel.published_at).to_list()
    
#     # Fetch linked publisher users for each article
#     for article in articles:
#         await article.fetch_link(ArticleModel.publisher_id)

#     article_data = articles if articles else None

#     data = {
#         "firm_data": firm,
#         "articles": article_data
#     }

#     response_data = {
#         "status": 1,
#         "message": "Firm details fetched successfully",
#         "data": data,
#     }
#     return response_data


# @router.get("/details", response_model=BaseResponse)
# async def get_firm_details(
#     firm_id: str | None = Query(None),
#     current_user: dict = Depends(get_current_user)
# ):
#     """
#     Fetch firm details along with its published articles and owner info.
#     Only limited fields of owner and publisher are returned.
#     """
#     if current_user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid access token, Login to continue",
#         )

#     if not firm_id:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="firm_id is required"
#         )

#     try:
#         firm_oid = ObjectId(firm_id)
#     except Exception:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid firm_id"
#         )

#     # Fetch firm
#     firm = await FirmModel.find_one(FirmModel.id == firm_oid, FirmModel.is_deleted == False)
#     if not firm:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Firm not found"
#         )

#     # Fetch linked owner user
#     await firm.fetch_link(FirmModel.owner_user_id)
#     owner_data = {
#         "username": firm.owner_user_id.username,
#         "first_name": firm.owner_user_id.first_name,
#         "last_name": firm.owner_user_id.last_name,
#         "profile_picture_url": firm.owner_user_id.profile_picture_url,
#     }

#     # Fetch articles using ArticleService
#     articles = await article_controller.get_articles_by_firm(firm_oid)

#     # Prepare response data
#     data = {
#         "firm_data": {
#             "id": str(firm.id),
#             "firm_name": firm.firm_name,
#             "firm_username": firm.firm_username,
#             "bio": firm.bio,
#             "trust_factor": firm.trust_factor,
#             "owner": owner_data,
#         },
#         "articles": articles if articles else None
#     }

#     return {
#         "status": 1,
#         "message": "Firm details fetched successfully",
#         "data": data,
#     }



@router.get("/details", response_model=BaseResponse)
async def get_firm_details(
    firm_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token, Login to continue",
            )
        if not firm_id:
            raise HTTPException(status_code=400, detail="firm_id is required")
        
        # Fetch firm by ID
        firm = await FirmModel.get(ObjectId(firm_id))
        if not firm or firm.is_deleted or not firm.is_active:
            raise HTTPException(status_code=404, detail="Firm not found")
        
        # Resolve the owner link
        owner = await firm.owner_user_id.fetch()
        owner_info = {
            "id": str(owner.id),
            "username": owner.username,
            "first_name":owner.first_name,
            "last_name":owner.last_name,
        } if owner else None

        # Pagination
        skip = (page - 1) * page_size

        # Fetch published articles
        articles_cursor = ArticleModel.find(
            ArticleModel.firm_id.id == firm.id,
            ArticleModel.status == "PUBLISHED",
            ArticleModel.is_deleted == False
        ).sort("-published_at").skip(skip).limit(page_size)

        articles = []
        async for article in articles_cursor:
            # Resolve the publisher link
            publisher = await article.publisher_id.fetch()
            publisher_info = {
                "id": str(publisher.id),
                "username": publisher.username,
                "first_name":publisher.first_name,
                "last_name":publisher.last_name,
            } if publisher else None

            articles.append(ArticleOutSchema(
                id=str(article.id),
                title=article.title,
                summary=article.summary,
                tags=article.tags,
                category=article.category,
                published_at=article.published_at,
                publisher=publisher_info
            ))

        # Check if current user is the owner
        
        is_self = False
        if owner and current_user:
            is_self = str(current_user["user_id"]) == str(owner.id)

        # Build final response
        response_data = FirmDetailsOutSchema(
            id=str(firm.id),
            firm_name=firm.firm_name,
            firm_username=firm.firm_username,
            bio=firm.bio,
            verification_status=firm.verification_status.value,
            trust_factor=firm.trust_factor,
            violations_count=firm.violations_count,
            is_verified=firm.is_verified,
            created_at=firm.created_at,
            owner=owner_info,
            articles=articles,
            is_self=is_self
        )
        
        return{
            "status": 1,
            "message": "Firm fetched successfully",
            "data": response_data.dict()
        } 
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )