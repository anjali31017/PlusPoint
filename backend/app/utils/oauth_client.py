# utils/oauth_client.py
import os
from urllib.parse import urlencode

from conf import settings

def get_google_oauth_url():
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{base_url}?{urlencode(params)}"

def get_github_oauth_url():
    base_url = "https://github.com/login/oauth/authorize"
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "user:email",
    }
    return f"{base_url}?{urlencode(params)}"
