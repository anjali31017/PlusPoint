// requests.js

$(document).ready(function () {
  // Check session, then load delete requests
  checkAdminSession(() => loadDeleteRequests());
  attachLogoutHandler();

  $("#requestLink").click(loadDeleteRequests);
});

// Load delete requests from API
function loadDeleteRequests() {
  const container = $("#requestsContainer");
  container.html('<p class="text-center text-gray-500">Loading...</p>');

  $.ajax({
    url: "http://127.0.0.1:5000/api/admin/delete/requests",
    method: "GET",
    xhrFields: { withCredentials: true },
    success: function (res) {
      const { firms = [], articles = [] } = res.data;
      container.empty();

      if (firms.length === 0 && articles.length === 0) {
        container.html("<p class='text-center text-gray-600'>No delete requests found</p>");
        return;
      }

      renderFirmRequests(container, firms);
      renderArticleRequests(container, articles);
    },
    error: () => errorToast("Failed to load delete requests")
  });
}

// Render firm delete requests
function renderFirmRequests(container, firms) {
  firms.forEach(firm => {
    const card = $(`
      <div class="bg-white rounded-xl shadow-md p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div class="flex-1">
          <p><strong>Firm Name:</strong> ${firm.firm_name}</p>
          <p><strong>Firm Username:</strong> ${firm.firm_username}</p>
          <p><strong>Requested Reason:</strong> ${firm.delete_reason}</p>
          <p><strong>Total Reports:</strong> ${firm.report_count}</p>
        </div>
        <div class="flex flex-col gap-2">
          <button class="approveBtn bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded font-semibold">Approve Deletion</button>
        </div>
      </div>
    `);

    card.find(".approveBtn").click(() => {
      confirmAction("Approve Deletion?", `Firm: ${firm.firm_name}`).then(result => {
        if (result.isConfirmed) {
          $.ajax({
            url: `http://127.0.0.1:5000/api/admin/delete/action?firm_id=${firm._id}&action=delete`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ reason: firm.delete_reason }),
            xhrFields: { withCredentials: true },
            success: () => successToast("Firm deleted successfully"),
            error: (xhr) => errorToast(xhr.responseJSON?.detail || "Failed to delete firm")
          }).always(loadDeleteRequests);
        }
      });
    });

    container.append(card);
  });
}

// Render article delete requests
function renderArticleRequests(container, articles) {
  articles.forEach(article => {
    const card = $(`
      <div class="bg-white rounded-xl shadow-md p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div class="flex-1">
          <p><strong>Article Title:</strong> ${article.title}</p>
          <p><strong>Requested Reason:</strong> ${article.delete_reason}</p>
          <p><strong>Firm ID:</strong> ${article.firm_id.id}</p>
          <p><strong>Total Reports:</strong> ${article.report_count}</p>
        </div>
        <div class="flex flex-col gap-2">
          <button class="approveBtn bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded font-semibold">Approve Deletion</button>
        </div>
      </div>
    `);

    card.find(".approveBtn").click(() => {
      confirmAction("Approve Deletion?", `Article: ${article.title}`).then(result => {
        if (result.isConfirmed) {
          $.ajax({
            url: `http://127.0.0.1:5000/api/admin/delete/action?article_id=${article._id}&action=delete`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ reason: article.delete_reason }),
            xhrFields: { withCredentials: true },
            success: () => successToast("Article deleted successfully"),
            error: (xhr) => errorToast(xhr.responseJSON?.detail || "Failed to delete article")
          }).always(loadDeleteRequests);
        }
      });
    });

    container.append(card);
  });
}
