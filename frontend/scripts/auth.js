



// auth.js

function getAccessToken() {
    return localStorage.getItem("access_token");
}

function setTokens(access, refresh) {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
}

function redirectToLogin() {
    window.location.href = "login.html";
}

async function refreshToken() {
    const refresh_token = localStorage.getItem("refresh_token");
    if (!refresh_token) {
        redirectToLogin();
        return;
    }

    return $.ajax({
        url: "http://127.0.0.1:5000/api/token/refresh",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ refresh_token }),
    }).then(res => {
        if (res.status === 1 && res.data) {
            setTokens(res.data.access_token, res.data.refresh_token);
            return res.data.access_token;
        } else {
            redirectToLogin();
            throw new Error("Failed to refresh token");
        }
    }).catch(() => {
        redirectToLogin();
    });
}

// Wrapper for AJAX requests with automatic JWT refresh
async function ajaxWithJWT(options) {
    let token = getAccessToken();
    if (!token) {
        redirectToLogin();
        return;
    }

    options = options || {};
    options.headers = options.headers || {};
    options.headers["Authorization"] = `Bearer ${token}`;

    return $.ajax(options).fail(async function (jqXHR) {
        if (jqXHR.status === 401) { // Unauthorized
            try {
                const newToken = await refreshToken();
                options.headers["Authorization"] = `Bearer ${newToken}`;
                return $.ajax(options); // Retry original request
            } catch (err) {
                redirectToLogin();
                throw err;
            }
        }
    });
}
