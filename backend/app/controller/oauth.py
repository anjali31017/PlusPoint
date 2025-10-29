# controllers/auth_controller.py
import httpx
from sqlalchemy.orm import Session
from models.user import User
from models.oauth_identity import OAuthIdentity
from utils.jwt_handler import create_access_token
from conf import settings

async def handle_google_callback(code: str, db: Session):
    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
    }
    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=data)
        token_data = token_response.json()

        # Fetch user info
        userinfo_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        userinfo = userinfo_response.json()

    return await _upsert_oauth_user(
        db=db,
        provider="google",
        provider_user_id=userinfo["id"],
        email=userinfo["email"],
        name=userinfo.get("name"),
        profile_pic=userinfo.get("picture"),
        access_token=token_data["access_token"],
    )

async def handle_github_callback(code: str, db: Session):
    # Exchange code for token
    token_url = "https://github.com/login/oauth/access_token"
    data = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        headers = {"Accept": "application/json"}
        token_response = await client.post(token_url, data=data, headers=headers)
        token_data = token_response.json()

        # Get user info
        userinfo_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        userinfo = userinfo_response.json()

        # Also get email if not present
        if not userinfo.get("email"):
            email_resp = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            email_data = email_resp.json()
            primary_email = next((e["email"] for e in email_data if e["primary"]), None)
            userinfo["email"] = primary_email

    return await _upsert_oauth_user(
        db=db,
        provider="github",
        provider_user_id=str(userinfo["id"]),
        email=userinfo["email"],
        name=userinfo.get("name"),
        profile_pic=userinfo.get("avatar_url"),
        access_token=token_data["access_token"],
    )

async def _upsert_oauth_user(
    db: Session,
    provider: str,
    provider_user_id: str,
    email: str,
    name: str,
    profile_pic: str,
    access_token: str,
):
    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name=name, profile_pic=profile_pic)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Link OAuth account
    oauth_account = (
        db.query(OAuthIdentity)
        .filter_by(provider_name=provider, provider_user_id=provider_user_id)
        .first()
    )

    if not oauth_account:
        oauth_account = OAuthIdentity(
            provider_name=provider,
            provider_user_id=provider_user_id,
            email=email,
            access_token=access_token,
            user_id=user.user_ref_id,
        )
        db.add(oauth_account)
        db.commit()

    # Generate your JWT
    jwt_token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": jwt_token, "token_type": "bearer"}
