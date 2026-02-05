// settings.js

$(document).ready(async function () {
    const contentWrapper = $("#content-wrapper");

    // ---------- UTILS ----------
    function parseJwt(token) {
        try {
            return JSON.parse(atob(token.split(".")[1]));
        } catch (e) {
            return null;
        }
    }

    const accessToken = localStorage.getItem("access_token");
    const userInfo = parseJwt(accessToken);
    let roles = [];
    if (userInfo?.role) {
        if (Array.isArray(userInfo.role)) {
            roles = userInfo.role;
        } else if (typeof userInfo.role === "string") {
            roles = userInfo.role.split(",");
        }
    }

    // ---------- BUTTON DEFINITIONS ----------
    const settingsItems = [];

    // If user is P or F, show all dashboard items
    if (roles.includes("P") || roles.includes("F")) {
        settingsItems.push(
            { id: "dashboardArticlesBtn", text: "Articles Dashboard", icon: "file-text", action: () => window.location.href = "dashboard-articles.html", color: "text-blue-700 hover:bg-blue-50" },
            { id: "dashboardFirmsBtn", text: "Firms Dashboard", icon: "briefcase", action: () => window.location.href = "dashboard-firms.html", color: "text-green-700 hover:bg-green-50" },
            { id: "dashboardTrendsBtn", text: "Trends", icon: "trending-up", action: () => window.location.href = "dashboard-trends.html", color: "text-yellow-700 hover:bg-yellow-50" }
        );
    }

    // These items are for all users
    settingsItems.push(
        { id: "likedArticlesBtn", text: "Liked Articles", icon: "heart", action: () => window.location.href = "liked.html", color: "text-pink-600 hover:bg-pink-50" },
        { id: "endorsedItemsBtn", text: "Endorsed Items", icon: "thumbs-up", action: () => window.location.href = "endorsed.html", color: "text-indigo-600 hover:bg-indigo-50" },
        { id: "logoutBtn", text: "Logout", icon: "log-out", action: logout, color: "text-red-600 hover:bg-red-50" },
        { id: "deleteAccountBtn", text: "Delete Account", icon: "trash-2", action: deleteAccount, color: "text-gray-700 hover:bg-gray-100" }
    );

    // ---------- RENDER LIST ----------
    const listContainer = $('<div class="flex flex-col space-y-3"></div>');

    settingsItems.forEach(item => {
        const listItem = $(`
            <button id="${item.id}" class="flex items-center justify-start space-x-4 p-4 rounded-2xl font-semibold transition-all border border-gray-100 hover:shadow-sm ${item.color}">
                <i data-lucide="${item.icon}" class="w-6 h-6"></i>
                <span>${item.text}</span>
            </button>
        `);
        listItem.on("click", item.action);
        listContainer.append(listItem);
    });

    contentWrapper.append(listContainer);
    lucide.createIcons();

    // ---------- LOGOUT FUNCTION ----------
    async function logout() {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) return redirectToLogin();

        const result = await Swal.fire({
            title: 'Logout',
            text: "Are you sure you want to logout?",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Yes, logout'
        });

        if (!result.isConfirmed) return;

        try {
            const res = await ajaxWithJWT({
                url: "http://127.0.0.1:5000/api/user/logout",
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify({ refresh_token: refreshToken }),
            });

            if (res.status === 1) {
                localStorage.removeItem("access_token");
                localStorage.removeItem("refresh_token");
                redirectToLogin();
            } else {
                Swal.fire("Error", res.message || "Failed to logout", "error");
            }
        } catch (err) {
            Swal.fire("Error", err.responseJSON?.detail || "Logout failed", "error");
        }
    }

    // ---------- DELETE ACCOUNT FUNCTION ----------
    async function deleteAccount() {
        const code = Math.random().toString(36).substring(2, 7).toUpperCase();

        const { value: userInput } = await Swal.fire({
            title: 'Delete Account',
            html: `<p>This action is <strong>irreversible</strong>.</p>
                   <p>Type the following code to confirm deletion:</p>
                   <h3 style="letter-spacing: 2px;">${code}</h3>
                   <input id="swal-input" class="swal2-input" placeholder="Type the code here">`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Delete Account',
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            preConfirm: () => {
                return document.getElementById('swal-input').value;
            },
        });

        if (!userInput || userInput.toUpperCase() !== code) {
            Swal.fire("Cancelled", "Account deletion aborted", "info");
            return;
        }

        try {
            const res = await ajaxWithJWT({
                url: "http://127.0.0.1:5000/api/user/delete/account",
                method: "POST",
                contentType: "application/json",
            });

            if (res.status === 1) {
                Swal.fire("Deleted!", res.message, "success").then(() => {
                    localStorage.removeItem("access_token");
                    localStorage.removeItem("refresh_token");
                    redirectToLogin();
                });
            } else {
                Swal.fire("Error", res.message || "Failed to delete account", "error");
            }
        } catch (err) {
            Swal.fire(
                "Error",
                err.responseJSON?.detail || err.responseText || "Delete failed",
                "error"
            );
        }
    }
});























// $(document).ready(async function () {



//     const loggedIn = await isLoggedIn();
//     if (!loggedIn) return;

//     // Your page-specific JS goes here
//     console.log("User is logged in, continue rendering page...");






//     const contentWrapper = $("#content-wrapper");

//     // ---------- UTILS ----------
//     function parseJwt(token) {
//         try {
//             return JSON.parse(atob(token.split(".")[1]));
//         } catch (e) {
//             return null;
//         }
//     }
//     const accessToken = localStorage.getItem("access_token");
//     const userInfo = parseJwt(accessToken);
//     let roles = [];
//     if (userInfo?.role) {
//         if (Array.isArray(userInfo.role)) {
//             roles = userInfo.role;
//         } else if (typeof userInfo.role === "string") {
//             // If roles are comma-separated like "P,F"
//             roles = userInfo.role.split(",");
//         }
//     }

//     // ---------- BUTTON DEFINITIONS ----------
//     const settingsItems = [];

//     if (roles.includes("P")) {
//         settingsItems.push({ id: "managePublisherBtn", text: "Manage Publishers", icon: "users", action: managePublishers, color: "text-purple-700 hover:bg-purple-50" });
//     }
//     if (roles.includes("F")) {
//         settingsItems.push({ id: "manageFirmsBtn", text: "Manage Firms", icon: "briefcase", action: manageFirms, color: "text-blue-700 hover:bg-blue-50" });
//     }


//     settingsItems.push(
//         { id: "logoutBtn", text: "Logout", icon: "log-out", action: logout, color: "text-red-600 hover:bg-red-50" },
//         { id: "deleteAccountBtn", text: "Delete Account", icon: "trash-2", action: deleteAccount, color: "text-gray-700 hover:bg-gray-100" },

//     );

//     // ---------- RENDER LIST ----------
//     const listContainer = $('<div class="flex flex-col space-y-3"></div>');

//     settingsItems.forEach(item => {
//         const listItem = $(`
//             <button id="${item.id}" class="flex items-center justify-start space-x-4 p-4 rounded-2xl font-semibold transition-all border border-gray-100 hover:shadow-sm ${item.color}">
//                 <i data-lucide="${item.icon}" class="w-6 h-6"></i>
//                 <span>${item.text}</span>
//             </button>
//         `);
//         listItem.on("click", item.action);
//         listContainer.append(listItem);
//     });

//     contentWrapper.append(listContainer);
//     lucide.createIcons();

  

//     async function logout() {
//         const refreshToken = localStorage.getItem("refresh_token");
//         if (!refreshToken) return redirectToLogin();

//         const result = await Swal.fire({
//             title: 'Logout',
//             text: "Are you sure you want to logout?",
//             icon: 'warning',
//             showCancelButton: true,
//             confirmButtonColor: '#d33',
//             cancelButtonColor: '#3085d6',
//             confirmButtonText: 'Yes, logout'
//         });

//         if (!result.isConfirmed) return;

//         try {
//             const res = await ajaxWithJWT({
//                 url: "http://127.0.0.1:5000/api/user/logout",
//                 method: "POST",
//                 contentType: "application/json",
//                 data: JSON.stringify({ refresh_token: refreshToken }),
//             });

//             if (res.status === 1) {
//                 localStorage.removeItem("access_token");
//                 localStorage.removeItem("refresh_token");
//                 redirectToLogin();
//             } else {
//                 Swal.fire("Error", res.message || "Failed to logout", "error");
//             }
//         } catch (err) {
//             Swal.fire("Error", err.responseJSON?.detail || "Logout failed", "error");
//         }
//     }


   

//     async function deleteAccount() {
//         // Step 0: generate a random 5-character code
//         const code = Math.random().toString(36).substring(2, 7).toUpperCase(); // e.g., "A4X9T"

//         // Step 1: ask user to type the code
//         const { value: userInput } = await Swal.fire({
//             title: 'Delete Account',
//             html: `<p>This action is <strong>irreversible</strong>.</p>
//                <p>Type the following code to confirm deletion:</p>
//                <h3 style="letter-spacing: 2px;">${code}</h3>
//                <input id="swal-input" class="swal2-input" placeholder="Type the code here">`,
//             icon: 'warning',
//             showCancelButton: true,
//             confirmButtonText: 'Delete Account',
//             confirmButtonColor: '#d33',
//             cancelButtonColor: '#3085d6',
//             preConfirm: () => {
//                 return document.getElementById('swal-input').value;
//             },
//         });

//         // Step 2: If user cancels or input is incorrect
//         if (!userInput || userInput.toUpperCase() !== code) {
//             Swal.fire("Cancelled", "Account deletion aborted", "info");
//             return;
//         }

//         // Step 3: Call Delete Account API using ajaxWithJWT
//         try {
//             const res = await ajaxWithJWT({
//                 url: "http://127.0.0.1:5000/api/user/delete/account",
//                 method: "POST",
//                 contentType: "application/json",
//             });

//             if (res.status === 1) {
//                 Swal.fire("Deleted!", res.message, "success").then(() => {
//                     // Clear tokens and redirect
//                     localStorage.removeItem("access_token");
//                     localStorage.removeItem("refresh_token");
//                     redirectToLogin();
//                 });
//             } else {
//                 Swal.fire("Error", res.message || "Failed to delete account", "error");
//             }
//         } catch (err) {
//             Swal.fire(
//                 "Error",
//                 err.responseJSON?.detail || err.responseText || "Delete failed",
//                 "error"
//             );
//         }
//     }



//     function managePublishers() {
//         window.location.href = "managePublishers.html";
//     }

//     function manageFirms() {
//         window.location.href = "manageFirms.html";
//     }
// });
