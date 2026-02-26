from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta, timezone
from app.config import settings
from app.controller.token_controller import create_access_token, create_refresh_token, decode_token
from app.models.token import RefreshTokenModel
from app.schema.base_schema import BaseResponse
from app.schema.user_schema import RefreshSchema
from fastapi import status


router = APIRouter(prefix="/token", tags=["User"])

@router.post("/refresh", response_model=BaseResponse)
async def refresh_token_route(data: RefreshSchema):
    try:
        token_doc = await RefreshTokenModel.find_one(RefreshTokenModel.token == data.refresh_token)
        if not token_doc or token_doc.is_revoked:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or revoked refresh token")

        if token_doc.expires_at < datetime.now():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

        payload = await decode_token(data.refresh_token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        # Issue new access token
        new_access_token = await create_access_token({
            "user_id": payload["user_id"],
            "role": payload["role"]
        })

        # Optionally: rotate refresh token
        new_refresh_token = await create_refresh_token({
            "user_id": payload["user_id"],
            "role": payload["role"]
        })
        token_doc.token = new_refresh_token
        token_doc.expires_at = datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await token_doc.save()

        return {
            "status": 1,
            "message": "Token refreshed successfully",
            "data": {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


