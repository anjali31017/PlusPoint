



// auth.js

function getAccessToken() {
    return localStorage.getItem("access_token");
}

function setTokens(access, refresh) {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
}

function redirectToLogin() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "login.html";
}

async function refreshToken() {
    const refresh_token = localStorage.getItem("refresh_token");
    if (!refresh_token) {
        redirectToLogin();
        return null; // important
    }

    // Wrap jQuery AJAX in a Promise so we can await it
    return new Promise((resolve, reject) => {
        $.ajax({
            url: "http://127.0.0.1:5000/api/token/refresh",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ refresh_token }),
            success: function (res) {
                if (res.status === 1 && res.data) {
                    setTokens(res.data.access_token, res.data.refresh_token);
                    resolve(res.data.access_token); // return new token
                } else {
                    redirectToLogin();
                    resolve(null);
                }
            },
            error: function (err) {
                redirectToLogin();
                resolve(null);
            }
        });
    });
}



// async function refreshToken() {
//     const refresh_token = localStorage.getItem("refresh_token");
//     if (!refresh_token) {
//         redirectToLogin();
//         return;
//     }

//     return $.ajax({
//         url: "http://127.0.0.1:5000/api/token/refresh",
//         method: "POST",
//         contentType: "application/json",
//         data: JSON.stringify({ refresh_token }),
//     }).then(res => {
//         if (res.status === 1 && res.data) {
//             setTokens(res.data.access_token, res.data.refresh_token);
//             return res.data.access_token;
//         } else {
//             redirectToLogin();
//             throw new Error("Failed to refresh token");
//         }
//     }).catch(() => {
//         redirectToLogin();
//     });
// }

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



async function isLoggedIn() {
    let accessToken = localStorage.getItem("access_token");
    const refresh_token = localStorage.getItem("refresh_token");

    if (!accessToken) {
        redirectToLogin();
        return false;
    }

    try {
        const payload = JSON.parse(atob(accessToken.split(".")[1]));
        const now = Math.floor(Date.now() / 1000);

        if (payload.exp && payload.exp < now + 60) {
            if (!refresh_token) {
                redirectToLogin();
                return false;
            }

            const newToken = await refreshToken();
            if (!newToken) {
                redirectToLogin();
                return false;
            }
            accessToken = newToken;
        }

        return true;
    } catch (e) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        redirectToLogin();
        return false;
    }
}

