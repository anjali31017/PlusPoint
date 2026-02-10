// // admin.js
// admin.js - shared functions for admin pages

// Check if session is active, else redirect to login
function checkAdminSession(onActive = null) {
  $.ajax({
    url: "http://127.0.0.1:5000/api/admin/check-session",
    method: "GET",
    xhrFields: { withCredentials: true },
    success: function (res) {
      if (res.status === 1 && typeof onActive === "function") {
        onActive();
      } else {
        window.location.href = "login.html";
      }
    },
    error: function () {
      window.location.href = "login.html";
    }
  });
}

// Logout function
function adminLogout() {
  $.ajax({
    url: "http://127.0.0.1:5000/api/admin/logout",
    method: "POST",
    xhrFields: { withCredentials: true },
    success: function (res) {
      if (res.status === 1) {
        Swal.fire({
          icon: "success",
          title: res.message,
          timer: 1000,
          showConfirmButton: false
        }).then(() => window.location.href = "login.html");
      } else {
        Swal.fire({ icon: "error", title: "Logout failed", text: res.message || "Try again" });
      }
    },
    error: function (xhr) {
      Swal.fire({ icon: "error", title: "Error", text: xhr.responseJSON?.detail || "Could not logout" });
    }
  });
}

// SweetAlert wrapper for confirm dialogs
function confirmAction(title, text, confirmText = "Confirm") {
  return Swal.fire({
    title,
    text,
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: confirmText
  });
}

// SweetAlert success toast
function successToast(message) {
  Swal.fire({ icon: "success", title: message, timer: 1000, showConfirmButton: false });
}

// SweetAlert error toast
function errorToast(message) {
  Swal.fire({ icon: "error", title: "Error", text: message });
}

// Format ISO date string to local readable
function formatDate(isoString) {
  return new Date(isoString).toLocaleString();
}

// Utility: get query param from URL
function getQueryParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

// Attach logout button handler (reuse in any page)
function attachLogoutHandler(btnSelector = "#logoutBtn") {
  $(btnSelector).click(adminLogout);
}




