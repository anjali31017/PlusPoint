// // global-notifications.js

// global-notifications.js
let notifications = [];

/* --------------------------------------------------
   Start SSE for global notifications
-------------------------------------------------- */
function startGlobalSSE() {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    const eventSource = new EventSource(`http://127.0.0.1:5000/sse/notifications?token=${token}`);

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "heartbeat") return;

        // Add new notification to the top
        notifications.unshift(data);

        // Update sidebar badge
        updateSidebarBadge();

        // Show toast popup in bottom-left
        showToast(data);
    };

    eventSource.onerror = () => {
        eventSource.close();
        setTimeout(startGlobalSSE, 5000); // Retry in 5s
    };
}

/* --------------------------------------------------
   Update badge on sidebar Notifications link
-------------------------------------------------- */
function updateSidebarBadge() {
    const badge = document.getElementById("sidebar-notification-badge");
    if (!badge) return;

    badge.textContent = notifications.length > 0 ? notifications.length : "";
}

/* --------------------------------------------------
   Show toast in bottom-left corner
-------------------------------------------------- */
function showToast(notification) {
    const container = document.getElementById("notification-toast-container");
    if (!container) return;

    const div = document.createElement("div");
    div.className = "bg-white shadow-md rounded-lg p-3 border border-gray-200 cursor-pointer hover:bg-gray-50 transition duration-150";
    div.innerHTML = `<strong>${notification.type}</strong>: ${notification.message.article_title || notification.message.detail || ""}`;

    // Navigate on click
    div.addEventListener("click", () => {
        if (notification.type === "👤 Someone Followed") {
            window.location.href = `firm.html?firm_id=${notification.message.firm_id}`;
        } else if ((notification.type === "LIKE" || notification.type === "ARTICLE") && notification.message.article_id) {
            window.location.href = `article.html?article_id=${notification.message.article_id}`;
        }else {
            window.location.href = "notification.html";
        }
    }); 

    container.appendChild(div);

    // Auto-remove after 5s
    setTimeout(() => div.remove(), 5000);
}

/* --------------------------------------------------
   Sidebar bell click (optional)
-------------------------------------------------- */
const bellIcon = document.getElementById("global-notification");
if (bellIcon) {
    bellIcon.addEventListener("click", () => {
        window.location.href = "notification.html";
    });
}

/* --------------------------------------------------
   Initialize
-------------------------------------------------- */
document.addEventListener("DOMContentLoaded", startGlobalSSE);












// let notifications = [];

// function startGlobalSSE() {
//     const token = localStorage.getItem("access_token");
//     if (!token) return;

//     const eventSource = new EventSource(`http://127.0.0.1:5000/sse/notifications?token=${token}`);

//     eventSource.onmessage = (event) => {
//         const data = JSON.parse(event.data);
//         if (data.type === "heartbeat") return;

//         // Add to notifications array
//         notifications.unshift(data);

//         // Update badge
//         updateBadge();

//         // Show toast popup
//         showToast(data);
//     };

//     eventSource.onerror = () => {
//         eventSource.close();
//         setTimeout(startGlobalSSE, 5000);
//     };
// }

// function updateBadge() {
//     const badge = document.getElementById("notification-badge");
//     badge.textContent = notifications.length > 0 ? notifications.length : "";
// }



// // Clickable bell icon
// document.getElementById("global-notification").addEventListener("click", () => {
//     window.location.href = "/notification.html";
// });

// // Start SSE on page load
// document.addEventListener("DOMContentLoaded", startGlobalSSE);
