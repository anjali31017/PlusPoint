from datetime import datetime, timedelta, timezone
from http.client import HTTPException
from fastapi import Header
from jose import jwt, JWTError

from app.config import settings
from app.models.token import RefreshTokenModel
from fastapi import status

async def create_access_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    except Exception as e:
        print(f"Error creating access token: {e}")
        return None

async def create_refresh_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    except Exception as e:
        print(f"Error creating refresh token: {e}")
        return None

async def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
    except Exception as e:  
        print(f"Error decoding token: {e}")
        return None
    
async def create_token_pair(user: dict):
    try:
        token_data = {
            "user_id": str(user.id), 
            "username": user.username , 
            "role": [r.value for r in user.role], 
            "status": user.status,
            }

        access_token = await create_access_token(token_data)
        refresh_token = await create_refresh_token(token_data)

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await RefreshTokenModel(
            user_id=str(user.id),
            token=refresh_token,
            expires_at=expires_at,
        ).insert()
        return access_token, refresh_token
    except Exception as e:
        print(f"Error creating token pair: {e}")
        return None, None
    


async def get_current_user(authorization: str = Header(...)):
    try:
        if not authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
        token = authorization.split(" ")[1]
        payload = await decode_token(token)
        if not payload:
            return None
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# # Function to handle the protected route
# async def protected_route(current_user: dict = Depends(get_current_user)):
#     return {"msg": f"Hello user {current_user['user_id']} with roles {current_user['role']}"}


# @router.post("/profile/update")
# async def update_profile(
#     profile_data: ProfileUpdateSchema, 
#     current_user: dict = Depends(get_current_user)
# ):
#     ...
# user = await UserModel.get(current_user["user_id"])
# if not user or user.is_deleted:
#     raise HTTPException(status_code=404, detail="User not found")

# # Update fields
# user.first_name = profile_data.first_name
# user.last_name = profile_data.last_name
# user.bio = profile_data.bio
# await user.save()
