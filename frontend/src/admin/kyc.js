// kyc.js

$(document).ready(function () {
  // Ensure session is active, else redirect to login
  checkAdminSession(() => {
    loadKYCData();
  });

  // Attach logout handler
  attachLogoutHandler();

  // Optional: KYC link reloads page
  $("#kycLink").click(loadKYCData);
  $("#reportLink").click(function () {
    Swal.fire({ icon: "info", title: "Reports Section", text: "Go to Reports tab to view reports." });
  });
});

// Common rejection reasons
const commonReasons = [
  "Name does not match",
  "Document expired",
  "Photo unclear",
  "Document altered",
  "Other"
];

function loadKYCData() {
  const container = $("#kycContainer");
  container.html('<p class="text-center text-gray-500">Loading...</p>');

  $.ajax({
    url: "http://127.0.0.1:5000/api/admin/kyc",
    method: "GET",
    xhrFields: { withCredentials: true },
    success: function (res) {
      const data = res.data.data;
      container.empty();

      if (!data || data.length === 0) {
        container.html("<p class='text-center text-gray-600'>No KYC requests available</p>");
        return;
      }

      data.forEach(kyc => {
        const card = $(`
          <div class="bg-white rounded-xl shadow-md p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div class="flex-1">
              <p><strong>Name on ID:</strong> ${kyc.name_on_id}</p>
              <p><strong>DOB:</strong> ${kyc.dob}</p>
              <p><strong>ID Type:</strong> ${kyc.id_type}</p>
              <p><strong>Last 4 of ID:</strong> ${kyc.id_last4}</p>
              <p><strong>Status:</strong> <span class="font-semibold text-blue-600">${kyc.kyc_status}</span></p>
            </div>
            <div class="flex-1">
              <a href="${kyc.id_document_path}" target="_blank" rel="noopener noreferrer">
                <img src="${kyc.id_document_path}" alt="ID Document" class="mt-2 w-48 border rounded cursor-zoom-in">
              </a>
            </div>
            <div class="flex flex-col gap-2">
              <select class="border px-3 py-2 rounded rejectionReason">
                <option value="">Select reason</option>
                ${commonReasons.map(r => `<option value="${r}">${r}</option>`).join('')}
              </select>
              <input type="text" placeholder="Custom reason" class="border px-3 py-2 rounded customReason">
              <div class="flex gap-2 mt-2">
                <button class="approveBtn bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded font-semibold">Approve</button>
                <button class="rejectBtn bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded font-semibold">Reject</button>
              </div>
            </div>
          </div>
        `);

        // Approve KYC
        card.find(".approveBtn").click(() => {
          $.ajax({
            url: `http://127.0.0.1:5000/api/admin/kyc/${kyc.user_id.id}/approve`,
            method: "POST",
            xhrFields: { withCredentials: true },
            success: () => successToast("KYC approved"),
            error: (xhr) => errorToast(xhr.responseJSON?.detail || "Something went wrong")
          }).always(loadKYCData);
        });

        // Reject KYC
        card.find(".rejectBtn").click(() => {
          let reason = card.find(".customReason").val().trim();
          if (!reason) reason = card.find(".rejectionReason").val();
          if (!reason) {
            Swal.fire({ icon: "warning", title: "Please provide a reason" });
            return;
          }

          $.ajax({
            url: `http://127.0.0.1:5000/api/admin/kyc/${kyc.user_id.id}/reject`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ reason }),
            xhrFields: { withCredentials: true },
            success: () => successToast("KYC rejected"),
            error: (xhr) => errorToast(xhr.responseJSON?.detail || "Something went wrong")
          }).always(loadKYCData);
        });

        container.append(card);
      });
    },
    error: () => errorToast("Could not fetch KYC data")
  });
}
