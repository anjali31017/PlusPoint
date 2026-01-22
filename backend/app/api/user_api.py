from datetime import datetime, timedelta
import os
import shutil
from bson import ObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, BackgroundTasks, Query, UploadFile
from app.config import settings

from app.controller.user_controller import UserController
from app.models.users import UserModel
from app.schema.user_schema import ForgotPasswordSchema, LogoutSchema, ResetPasswordSchema, UserCreateSchema, LoginSchema, UserProfileEditSchema, UserProfileSchema
from app.controller.token_controller import create_token_pair, get_current_user
from app.models.token import RefreshTokenModel
from app.schema.base_schema import BaseResponse
from app.controller.email_controller import generate_reset_token, is_user_blocked, reset_password_email, send_otp_email
from app.schema.email_schema import OTPVerifySchema, ResendOTPSchema
from fastapi import status

from app.controller.util_controller import UtilController
from app.models.kyc import KYCModel
from app.models.firm import FirmModel, VerificationStatus
from app.kafka.producer import send_kafka_event





router = APIRouter(prefix="/user", tags=["User"])

user_controller = UserController()
util_controller = UtilController()

@router.get("/check-username")
async def check_username(username: str):
    try:
        user = await util_controller.check_username_exists(username)
        return {"available": user is None}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.post("/register", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateSchema, background_tasks: BackgroundTasks):
    try:
        
        user = await user_controller.create(user_data.dict())
        if user is None:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

        if is_user_blocked(user):
            raise HTTPException( 
                        status_code=status.HTTP_403_FORBIDDEN ,
                        detail= f"User blocked for 6 hours due to OTP failures, try again after {user.otp_blocked_until}" 
                    )
        
        background_tasks.add_task(send_otp_email, user)
        
        response_data = {
            "status": 1,
            "message": "User created, OTP sent to email",
            "data": {
                "username": user.username
            }
        }
        return response_data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.post("/verify-otp", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def verify_user_otp(otp_data: OTPVerifySchema):
    try:
        user = await UserModel.find_one(
            UserModel.username == otp_data.username, 
            UserModel.is_deleted == False
        )
        if not user:
            raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, detail="User not found" )
        
        if is_user_blocked(user):
            raise HTTPException( 
                    status_code=status.HTTP_403_FORBIDDEN ,
                    detail= f"User blocked for 6 hours due to OTP failures, try again after {user.otp_blocked_until}" 
                )
        
        if datetime.now() > user.otp_expires_at:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired")
        
        if not user.verify_otp(otp_data.otp):
            attempts = user.otp_attempts + 1
            await user.set({UserModel.otp_attempts: attempts})
            if attempts >= 5:
                await user.set({ 
                                UserModel.otp_attempts: attempts, 
                                UserModel.otp_blocked_until: datetime.now() + timedelta(hours=6) 
                            })
                raise HTTPException( status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail="Too many invalid OTP attempts. User blocked for 6 hours." )
        
            # await user.set({UserModel.is_verified: True, UserModel.is_active: True})
            raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid OTP. {5 - attempts} attempts remaining" )
        
        await user.set({
            UserModel.is_verified: True,
            UserModel.is_active: True,
            UserModel.otp_attempts: 0,
            UserModel.otp_resend_count: 0,
            UserModel.otp_blocked_until: None
         })
        
        access_token, refresh_token = await create_token_pair(user)
        
        if not access_token or not refresh_token:
            raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token generation failed"
        )
    
        return {
            "status": 1,
            "message": "OTP verified successfully",
            "data": {
            "access_token": access_token,
            "refresh_token": refresh_token
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/resend-otp", status_code=status.HTTP_200_OK)
async def resend_otp(data: ResendOTPSchema, background_tasks: BackgroundTasks):
    """
    Resend OTP email to the user.
    """
    try:
        # Find the user
        user = await UserModel.find_one(UserModel.username == data.username, UserModel.is_deleted == False)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if is_user_blocked(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                 detail= f"User blocked for 6 hours due to OTP failures, try again after {user.otp_blocked_until}" 
            )
        if user.otp_resend_count >= 3:
            await user.set({
                UserModel.otp_blocked_until: datetime.now() + timedelta(hours=6)
            })
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
             detail= f"User blocked for 6 hours due to OTP failures, try again after {user.otp_blocked_until}" 
            )
        # Resend OTP
        # success = await resend_otp_email({"username": data.username})
        background_tasks.add_task(send_otp_email, user)
        
        MAX_RESENDS = 3
        new_count = user.otp_resend_count + 1
        await user.set({ UserModel.otp_resend_count: new_count })
        # if not success:
        #     raise HTTPException(status_code=500, detail="Failed to resend OTP email")

        return {
        "status": 1,
        "message": "OTP resent successfully",
        "data": {
            "resend_count": new_count,
            "remaining_resends": max(0, MAX_RESENDS - new_count)
        }
    }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/login", response_model=BaseResponse)
async def login(data: LoginSchema):
    user = await UserModel.find_one(UserModel.email == data.email, UserModel.is_deleted == False, UserModel.is_verified == True)
    if not user or not user.verify_password(data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token, refresh_token = await create_token_pair(user)
    if not access_token or not refresh_token:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token generation failed")
    
    return {
        "status": 1,
        "message": "Login successful",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    }




@router.post("/forgot-password", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def forgot_password(data: ForgotPasswordSchema, background_tasks: BackgroundTasks):
    try:
        
        user = await UserModel.find_one(
        UserModel.email == data.email,
        UserModel.is_deleted == False
        )

        if not user:
            raise HTTPException( 
                        status_code=status.HTTP_404_NOT_FOUND ,
                        detail= f"User Not Found" 
                    )
        if not user.is_verified:
            raise HTTPException( 
                        status_code=status.HTTP_400_BAD_REQUEST ,
                        detail= f"User is not verified. Register Again." 
                    )
        
        reset_token = generate_reset_token()
        
        await user.set({
        UserModel.reset_token: reset_token,
        UserModel.reset_token_expiry: datetime.now() + timedelta(minutes=15)
        })
        
        reset_link = f"http://127.0.0.1:3000/src/reset-password.html?token={reset_token}"
        
        
        background_tasks.add_task(reset_password_email, data.email, reset_link)
        
        response_data = {
            "status": 1,
            "message": "Password reset link sent to your email",
            "data": {
                "username": user.username
            }
        }
        return response_data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    
@router.post("/reset-password", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def reset_password(data: ResetPasswordSchema, background_tasks: BackgroundTasks):
    try:
        
        user = await UserModel.find_one( UserModel.reset_token == data.token, UserModel.reset_token_expiry > datetime.now())

        if not user:
            raise HTTPException( status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token" )
        
        await user.set({
        UserModel.password_hash: UserModel.hash_detail(data.password),
        UserModel.reset_token: None,
        UserModel.reset_token_expiry: None
        })
        
        
        response_data = {
            "status": 1,
            "message": "Password reset successful",
            "data": {
                "username": user.username
            }
        }
        return response_data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.get("/profile", response_model=BaseResponse)
async def get_profile(
    user_id: str | None = Query(None),
    current_user: dict = Depends(get_current_user)
):
    try:
        # 1. Resolve target user
        target_user_id = ObjectId(user_id) if user_id else ObjectId(current_user["user_id"])

        user = await UserModel.find_one(
            UserModel.id == target_user_id,
            UserModel.is_deleted == False
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = UserProfileSchema(**user.dict())

        # 2. KYC status
        kyc = await KYCModel.find_one(
            KYCModel.user_id.id == user.id,
            KYCModel.is_deleted == False
        )
        kyc_status = kyc.kyc_status if kyc else "PENDING"

        # 3. Firms OWNED by user
        owned_firms = await FirmModel.find(
            FirmModel.owner_user_id.id == user.id,
            FirmModel.is_deleted == False,
            FirmModel.is_active == True,
            FirmModel.verification_status == VerificationStatus.APPROVED,
        ).to_list()

        owned_firms_data = []
        for firm in owned_firms:

            owned_firms_data.append({
                "id": str(firm.id),
                "firm_name": firm.firm_name,
                "firm_username": firm.firm_username,
                "bio": firm.bio,
                "trust_factor": firm.trust_factor,
                
            })

        # 5. Self check
        is_self = str(target_user_id) == str(current_user["user_id"])

        return {
            "status": 1,
            "message": "Profile fetched successfully",
            "data": {
                "is_self": is_self,
                "user": user_data,
                "kyc_status": kyc_status,
                "owned_firms": owned_firms_data,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    


@router.put("/profile", response_model=BaseResponse)
async def update_profile(
    first_name: str | None = Form(None),
    last_name: str | None = Form(None),
    bio: str | None = Form(None),
    profile_picture: UploadFile | None = File(None),
    current_user: dict = Depends(get_current_user)  # optional, can hardcode for testing
):
    try:
        # --------- Temporary current_user for testing ----------
        # current_user = {"user_id": "6966229eeed6916c53c1cb26", "username":"bryar_carver_169013022"}

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token, Login to continue"
            )

        # --------- Prepare update payload ----------
        update_data = {k: v for k, v in {
            "first_name": first_name,
            "last_name": last_name,
            "bio": bio
        }.items() if v is not None}

        print(profile_picture)
        # --------- Handle profile picture ----------
        if profile_picture and profile_picture.filename:
            # Ensure folder exists
            # os.makedirs(settings.PROFILE_UPLOAD_FOLDER, exist_ok=True)

            ext = os.path.splitext(profile_picture.filename)[1].lower()
            if ext not in [".jpg", ".jpeg", ".png"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only JPG, JPEG, PNG files are allowed"
                )

            username = current_user["username"]
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{username}_{timestamp}{ext}"
            file_path = os.path.join(settings.PROFILE_UPLOAD_FOLDER, filename)
            print("@@@@@@@@@@@@@",file_path)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(profile_picture.file, buffer)

            update_data["profile_picture_url"] = f"images/profile/{filename}"

        # --------- Update user in DB ----------
        updated_user = await user_controller.update_user(
            current_user["user_id"],
            update_data
        )
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # --------- Return response ----------
        return {
            "status": 1,
            "message": "Profile updated successfully",
            "data": UserProfileEditSchema(**updated_user.dict())
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))




@router.post("/logout", response_model=BaseResponse)
async def logout(data: LogoutSchema):
    try:
        token_doc = await RefreshTokenModel.find_one(
            RefreshTokenModel.token == data.refresh_token,
            RefreshTokenModel.is_revoked == False
            )
        if not token_doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refresh token not found")
        
        token_doc.is_revoked = True
        await token_doc.save()

        return {
            "status": 1,
            "message": "Logout successful",
            "data": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    



        

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token, Login to continue")
        
    return {"msg": f"Hello user {current_user['user_id']} with roles {current_user['role']}"}



@router.post("/delete/account", response_model=BaseResponse)
async def delete_account(current_user:dict = Depends(get_current_user)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token, Login to continue")
        
        result = await user_controller.delete_user(current_user)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
        
        return {
            "status": 1,
            "message": "Account deleted successfully",
            "data": "User Deleted"
        }
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        