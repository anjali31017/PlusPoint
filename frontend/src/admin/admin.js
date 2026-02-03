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








// $(document).ready(function () {

//   // -------------------------------
//   // Logout
//   // -------------------------------
//   $("#logoutBtn").click(function () {
//     $.ajax({
//       url: "http://127.0.0.1:5000/api/admin/logout",
//       method: "POST",
//       xhrFields: { withCredentials: true },
//       success: function (res) {
//         if (res.status === 1) window.location.href = "login.html";
//       },
//       error: function () {
//         Swal.fire({ icon: "error", title: "Logout failed" });
//       }
//     });
//   });

//   // -------------------------------
//   // Reports Page
//   // -------------------------------
//   if ($("#reportsContainer").length) {
//     // Add a dropdown for search type
//     const searchContainer = $("#searchInput").parent();
//     if (!$("#searchType").length) {
//       searchContainer.prepend(`
//         <select id="searchType" class="border px-4 py-2 rounded">
//           <option value="">Select</option>
//           <option value="firm">Firm</option>
//           <option value="article">Article</option>
//         </select>
//       `);
//     }

//     loadReports();

//     $("#reportLink").click(() => loadReports());

//     $("#searchBtn").click(() => {
//       const searchId = $("#searchInput").val().trim();
//       const type = $("#searchType").val();
//       if (!searchId) {
//         Swal.fire({ icon: "warning", title: "Enter an ID to search" });
//         return;
//       }
//       loadReports(searchId, type);
//     });

//     $("#clearBtn").click(() => {
//       $("#searchInput").val('');
//       $("#searchType").val('');
//       loadReports();
//     });
//   }

//   // -------------------------------
//   // KYC Page
//   // -------------------------------
//   if ($("#kycContainer").length) {
//     loadKYCData();

//     $("#kycLink").click(() => loadKYCData());
//     $("#reportLink").click(() => Swal.fire({
//       icon: "info",
//       title: "Reports section",
//       text: "This section can show KYC statistics and reports."
//     }));
//   }

// });


// // ===============================
// // Reports Functions
// // ===============================
// function loadReports(searchId = '', type = '') {
//   const container = $("#reportsContainer");
//   container.html('<p class="text-center text-gray-500">Loading...</p>');

//   $.ajax({
//     url: "http://127.0.0.1:5000/api/admin/reports",
//     method: "GET",
//     xhrFields: { withCredentials: true },
//     success: function (res) {
//       let { firms, articles } = res.data;

//       if (searchId) {
//         if (type === 'firm') firms = firms.filter(f => f.id === searchId);
//         else if (type === 'article') articles = articles.filter(a => a.id === searchId);
//         else { // All
//           firms = firms.filter(f => f.id === searchId);
//           articles = articles.filter(a => a.id === searchId);
//         }
//       }

//       renderReports(firms, articles);
//     },
//     error: function () {
//       Swal.fire({ icon: "error", title: "Failed to load reports" });
//     }
//   });
// }

// function renderReports(firms, articles) {
//   const container = $("#reportsContainer");
//   container.empty();

//   if (firms.length === 0 && articles.length === 0) {
//     container.html("<p class='text-center text-gray-600'>No reports found</p>");
//     return;
//   }

//   // -------------------
//   // Render Firms
//   // -------------------
//   firms.forEach(firm => {
//     const card = $(`
//       <div class="bg-white rounded-xl shadow-md p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
//         <div class="flex-1">
//           <p><strong>Firm Name:</strong> ${firm.name}</p>
//           <p><strong>Firm ID:</strong> ${firm.firm_id.id}</p>
//           <p><strong>Total Reports:</strong> ${firm.report_count}</p>
//         </div>
//         <div class="flex flex-col gap-2">
//           <textarea placeholder="Reason for deletion" class="border px-3 py-2 rounded reasonInput"></textarea>
//           <div class="flex gap-2 mt-2">
//             <button class="deleteBtn bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded font-semibold">Delete Firm</button>
//             <button class="viewReportsBtn bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded font-semibold">View Reports</button>
//           </div>
//           <div class="mt-2 reportDetails hidden"></div>
//         </div>
//       </div>
//     `);

//     // Delete Firm
//     card.find(".deleteBtn").click(function () {
//       const reason = card.find(".reasonInput").val().trim();
//       if (!reason) return Swal.fire({ icon: "warning", title: "Please provide a reason" });

//       Swal.fire({
//         title: "Confirm Delete Firm?",
//         input: 'text',
//         inputLabel: 'Reason',
//         inputValue: reason,
//         showCancelButton: true,
//         confirmButtonText: "Delete",
//       }).then(result => {
//         if (!result.isConfirmed) return;
//         $.ajax({
//           url: `http://127.0.0.1:5000/api/admin/report/action?firm_id=${firm.id}`,
//           method: "POST",
//           contentType: "application/json",
//           data: JSON.stringify({ reason: result.value }),
//           xhrFields: { withCredentials: true },
//           success: () => { Swal.fire({ icon: "success", title: "Firm deleted" }); loadReports(); },
//           error: () => Swal.fire({ icon: "error", title: "Failed to delete" })
//         });
//       });
//     });

//     // View Firm Reports
//     card.find(".viewReportsBtn").click(function () {
//       $.ajax({
//         url: `http://127.0.0.1:5000/api/admin/user-reports?firm_id=${firm.id}`,
//         method: "GET",
//         xhrFields: { withCredentials: true },
//         success: function (res) {
//           const reportsDiv = card.find(".reportDetails").empty().removeClass("hidden");
//           if (!res.data.reports.length) reportsDiv.html("<p>No reports found for this firm</p>");
//           else {
//             res.data.reports.forEach(r => {
//               reportsDiv.append(`
//                 <div class="border p-2 rounded mb-2">
//                   <p><strong>Reported By:</strong> ${r.user_id.email || 'N/A'}</p>
//                   <p><strong>Reason:</strong> ${r.reason}</p>
//                   <p><strong>Created At:</strong> ${new Date(r.created_at).toLocaleString()}</p>
//                 </div>
//               `);
//             });
//           }
//         }
//       });
//     });

//     container.append(card);
//   });

//   // -------------------
//   // Render Articles
//   // -------------------
//   articles.forEach(article => {
//     const card = $(`
//       <div class="bg-white rounded-xl shadow-md p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
//         <div class="flex-1">
//           <p><strong>Article Title:</strong> ${article.title}</p>
//           <p><strong>Article ID:</strong> ${article.id}</p>
//           <p><strong>Total Reports:</strong> ${article.report_count}</p>
//         </div>
//         <div class="flex flex-col gap-2">
//           <textarea placeholder="Reason for deletion" class="border px-3 py-2 rounded reasonInput"></textarea>
//           <div class="flex gap-2 mt-2">
//             <button class="deleteBtn bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded font-semibold">Delete Article</button>
//             <button class="viewReportsBtn bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded font-semibold">View Reports</button>
//           </div>
//           <div class="mt-2 reportDetails hidden"></div>
//         </div>
//       </div>
//     `);

//     // Delete Article
//     card.find(".deleteBtn").click(function () {
//       const reason = card.find(".reasonInput").val().trim();
//       if (!reason) return Swal.fire({ icon: "warning", title: "Please provide a reason" });

//       Swal.fire({
//         title: "Confirm Delete Article?",
//         input: 'text',
//         inputLabel: 'Reason',
//         inputValue: reason,
//         showCancelButton: true,
//         confirmButtonText: "Delete",
//       }).then(result => {
//         if (!result.isConfirmed) return;
//         $.ajax({
//           url: `http://127.0.0.1:5000/api/admin/report/action?article_id=${article.id}`,
//           method: "POST",
//           contentType: "application/json",
//           data: JSON.stringify({ reason: result.value }),
//           xhrFields: { withCredentials: true },
//           success: () => { Swal.fire({ icon: "success", title: "Article deleted" }); loadReports(); },
//           error: () => Swal.fire({ icon: "error", title: "Failed to delete" })
//         });
//       });
//     });

//     // View Article Reports
//     card.find(".viewReportsBtn").click(function () {
//       $.ajax({
//         url: `http://127.0.0.1:5000/api/admin/user-reports?article_id=${article.id}`,
//         method: "GET",
//         xhrFields: { withCredentials: true },
//         success: function (res) {
//           const reportsDiv = card.find(".reportDetails").empty().removeClass("hidden");
//           if (!res.data.reports.length) reportsDiv.html("<p>No reports found for this article</p>");
//           else {
//             res.data.reports.forEach(r => {
//               reportsDiv.append(`
//                 <div class="border p-2 rounded mb-2">
//                   <p><strong>Reported By:</strong> ${r.user_id.email || 'N/A'}</p>
//                   <p><strong>Reason:</strong> ${r.reason}</p>
//                   <p><strong>Created At:</strong> ${new Date(r.created_at).toLocaleString()}</p>
//                 </div>
//               `);
//             });
//           }
//         }
//       });
//     });

//     container.append(card);
//   });
// }


// // ===============================
// // KYC Functions
// // ===============================
// const commonReasons = ["Name does not match","Document expired","Photo unclear","Document altered","Other"];

// function loadKYCData() {
//   const container = $("#kycContainer");
//   container.html('<p class="text-center text-gray-500">Loading...</p>');

//   $.ajax({
//     url: "http://127.0.0.1:5000/api/admin/kyc",
//     method: "GET",
//     xhrFields: { withCredentials: true },
//     success: function (res) {
//       const data = res.data.data;
//       container.empty();
//       if (!data.length) return container.html("<p class='text-center text-gray-600'>No KYC requests available</p>");

//       data.forEach(kyc => {
//         const card = $(`
//           <div class="bg-white rounded-xl shadow-md p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
//             <div class="flex-1">
//               <p><strong>Name on ID:</strong> ${kyc.name_on_id}</p>
//               <p><strong>DOB:</strong> ${kyc.dob}</p>
//               <p><strong>ID Type:</strong> ${kyc.id_type}</p>
//               <p><strong>Last 4 of ID:</strong> ${kyc.id_last4}</p>
//               <p><strong>Status:</strong> <span class="font-semibold text-blue-600">${kyc.kyc_status}</span></p>
//             </div>
//             <div class="flex-1">
//               <a href="${kyc.id_document_path}" target="_blank">
//                 <img src="${kyc.id_document_path}" class="mt-2 w-48 border rounded" alt="ID Document">
//               </a>
//             </div>
//             <div class="flex flex-col gap-2">
//               <select class="border px-3 py-2 rounded rejectionReason">
//                 <option value="">Select reason</option>
//                 ${commonReasons.map(r => `<option value="${r}">${r}</option>`).join('')}
//               </select>
//               <input type="text" placeholder="Custom reason" class="border px-3 py-2 rounded customReason">
//               <div class="flex gap-2 mt-2">
//                 <button class="approveBtn bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded font-semibold">Approve</button>
//                 <button class="rejectBtn bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded font-semibold">Reject</button>
//               </div>
//             </div>
//           </div>
//         `);

//         // Approve
//         card.find(".approveBtn").click(() => {
//           $.ajax({
//             url: `http://127.0.0.1:5000/api/admin/kyc/${kyc.user_id.id}/approve`,
//             method: "POST",
//             xhrFields: { withCredentials: true },
//             success: () => { Swal.fire({ icon: "success", title: "KYC approved", timer: 1000, showConfirmButton: false }); loadKYCData(); },
//             error: () => Swal.fire({ icon: "error", title: "Error approving KYC" })
//           });
//         });

//         // Reject
//         card.find(".rejectBtn").click(() => {
//           let reason = card.find(".customReason").val().trim() || card.find(".rejectionReason").val();
//           if (!reason) return Swal.fire({ icon: "warning", title: "Please provide a reason" });

//           $.ajax({
//             url: `http://127.0.0.1:5000/api/admin/kyc/${kyc.user_id.id}/reject`,
//             method: "POST",
//             contentType: "application/json",
//             data: JSON.stringify({ reason }),
//             xhrFields: { withCredentials: true },
//             success: () => { Swal.fire({ icon: "success", title: "KYC rejected", timer: 1000, showConfirmButton: false }); loadKYCData(); },
//             error: () => Swal.fire({ icon: "error", title: "Error rejecting KYC" })
//           });
//         });

//         container.append(card);
//       });
//     },
//     error: () => Swal.fire({ icon: "error", title: "Could not fetch KYC data" })
//   });
// }
