// notification.js

let notifications = [];
let eventSource = null;

/* --------------------------------------------------
   Helper Functions
-------------------------------------------------- */
function formatMessage(n) {
    const m = n.message || {};

    switch (n.type) {
        case "ARTICLE":
            return `📰 New article: <b>${m.article_title || "Article"}</b> by <i>${m.article_firm || "Article"}</i>`;
        case "FOLLOW":
            return `👤 Someone followed your firm`;
        case "LIKE":
            return `❤️ Someone liked your article <b>${m.article_title || ""}</b>`;
        case "ADMIN":
            return `🛡️ <b>${m.status || "Admin update"}</b>${m.detail ? `<br/><span class="text-sm text-gray-500">Reason: ${m.detail}</span>` : ""}`;
        default:
            return `🔔 New notification`;
    }
}

function handleNotificationClick(n) {
    const m = n.message || {};

    switch (n.type) {
        case "FOLLOW":
            if (m.firm_id) window.location.href = `firm.html?firm_id=${m.firm_id}`;
            break;
        case "LIKE":
        case "ARTICLE":
            if (m.article_id) window.location.href = `article.html?article_id=${m.article_id}`;
            break;
        default:
            // window.location.href = "notification.html";
            break;
    }
}

/* --------------------------------------------------
   Render Table (for notification.html only)
-------------------------------------------------- */
function renderNotifications() {
    const wrapper = $("#content-wrapper");
    if (!wrapper.length) return; // Only run on notification.html

    wrapper.empty();
    wrapper.append(`
        <div id="notificationTableContainer" class="w-full overflow-x-auto">
            <table class="w-full table-auto border border-gray-200 text-sm">
                <thead class="bg-gray-100">
                    <tr>
                        <th class="px-4 py-2 text-left">Notification</th>
                        <th class="px-4 py-2 text-center">Type</th>
                        <th class="px-4 py-2 text-center">Time</th>
                    </tr>
                </thead>
                <tbody id="notification-tbody" class="divide-y divide-gray-200"></tbody>
            </table>
        </div>
    `);

    const tbody = $("#notification-tbody");

    if (notifications.length === 0) {
        tbody.append(`
            <tr>
                <td colspan="3" class="text-center text-gray-400 py-6">
                    🎉 You have no notifications yet
                </td>
            </tr>
        `);
        return;
    }

    notifications.forEach(n => {
        tbody.append(`
            <tr class="cursor-pointer hover:bg-purple-50" data-id="${n._id}">
                <td class="px-2 py-3 break-words">${formatMessage(n)}</td>
                <td class="px-2 py-3 text-center">${n.type}</td>
                <td class="px-2 py-3 text-center">${new Date(n.created_at).toLocaleDateString()} ${new Date(n.created_at).toLocaleTimeString()}</td>
            </tr>
        `);
    });
}

/* --------------------------------------------------
   AJAX Wrapper with JWT
-------------------------------------------------- */
async function ajaxWithJWT({ url, method = "GET", data, contentType = "application/json" }) {
    const token = localStorage.getItem("access_token");
    const options = {
        method,
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": contentType
        }
    };
    if (data) options.body = data;

    const res = await fetch(url, options);
    if (!res.ok) throw new Error("Request failed");
    return await res.json();
}

/* --------------------------------------------------
   Badge & Toast Functions
-------------------------------------------------- */
// function updateBadge() {
//     const badge = document.getElementById("notification-badge");
//     if (badge) badge.textContent = notifications.length > 0 ? notifications.length : "";
// }

function showToast(notification) {
    const container = document.getElementById("notification-toast-container");
    if (!container) return;

    const div = document.createElement("div");
    div.className = "bg-white shadow-md rounded-lg p-3 border border-gray-200 cursor-pointer hover:bg-gray-50 transition duration-150";
    div.innerHTML = `<strong>${notification.type}</strong>: ${notification.message.article_title || notification.message.detail || ""}`;

    div.addEventListener("click", () => handleNotificationClick(notification));

    container.appendChild(div);

    setTimeout(() => div.remove(), 5000);
}

/* --------------------------------------------------
   Row Click Navigation
-------------------------------------------------- */
$(document).on("click", "tr[data-id]", function () {
    const id = $(this).data("id");
    const notif = notifications.find(n => n._id === id);
    if (notif) handleNotificationClick(notif);
});

/* --------------------------------------------------
   Load Previous Notifications
-------------------------------------------------- */
async function loadNotifications() {
    try {
        const res = await ajaxWithJWT({
            url: "http://127.0.0.1:5000/sse/list",
            method: "GET"
        });
        notifications = res.data || [];
        renderNotifications();
        // updateBadge();
    } catch (e) {
        console.error("Load notifications failed:", e);
    }
}

/* --------------------------------------------------
   SSE - Global
-------------------------------------------------- */

async function refreshTokenSilently() {
    try {
        const newToken = await refreshToken();
        if (!newToken) {
            redirectToLogin();
            return false;
        }
        return true;
    } catch (e) {
        redirectToLogin();
        return false;
    }
}


function startSSE() {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    eventSource = new EventSource(`http://127.0.0.1:5000/sse/notifications?token=${token}`);

    eventSource.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "heartbeat" || data.type === "connection_established") return;

        if (
            data.type === "ADMIN" &&
            data.message?.status === "KYC Approved!"
        ) {
            await refreshTokenSilently();
        }

        notifications.unshift(data);

        showToast(data);
        renderNotifications();
    };

    eventSource.onerror = () => {
        eventSource.close();
        setTimeout(startSSE, 5000);
    };
}

/* --------------------------------------------------
   Init
-------------------------------------------------- */
$(document).ready(async function () {
    await loadNotifications();
    startSSE();
});











