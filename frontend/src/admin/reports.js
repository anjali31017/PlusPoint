// reports.js

$(document).ready(function () {
  checkAdminSession(() => loadReports());
  attachLogoutHandler();

  // Remove top search for firm/article, search is inline per card now
});

// Load reports
function loadReports() {
  const container = $("#reportsContainer");
  container.html('<p class="text-center text-gray-500">Loading...</p>');

  $.ajax({
    url: "http://127.0.0.1:5000/api/admin/reports",
    method: "GET",
    xhrFields: { withCredentials: true },
    success: function (res) {
      const { firms = [], articles = [] } = res.data;
      container.empty();

      if (firms.length === 0 && articles.length === 0) {
        container.html("<p class='text-center text-gray-600'>No reports found</p>");
        return;
      }

      renderFirmReports(container, firms);
      renderArticleReports(container, articles);
    },
    error: () => errorToast("Failed to load reports")
  });
}

// Render firms
function renderFirmReports(container, firms) {
  firms.forEach(firm => {
    const card = $(`
      <div class="bg-white rounded-xl shadow-md p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div class="flex-1">
          <p><strong>Firm Name:</strong> ${firm.firm_name}</p>
          <p><strong>Firm UserName:</strong> ${firm.firm_username}</p>
          <p><strong>Total Reports:</strong> ${firm.report_count}</p>
          <div class="mt-2 reportDetails hidden"></div>
        </div>
        <div class="flex flex-col gap-2">
          <textarea placeholder="Reason for deletion" class="border px-3 py-2 rounded reasonInput"></textarea>
          <div class="flex gap-2 mt-2">
            <button class="deleteBtn bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded font-semibold">Delete Firm</button>
            <button class="viewReportsBtn bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded font-semibold" data-type="firm" data-id="${firm._id}">View Reports</button>
          </div>
          
        </div>
      </div>
    `);

    // Delete firm
    card.find(".deleteBtn").click(() => {
      const reason = card.find(".reasonInput").val().trim();
      if (!reason) return Swal.fire({ icon: "warning", title: "Provide a reason" });

      confirmAction("Confirm Delete Firm?", `Reason: ${reason}`, "Delete").then(result => {
        if (result.isConfirmed) {
          $.ajax({
            url: `http://127.0.0.1:5000/api/admin/delete/action?firm_id=${firm._id}&action=report`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ reason }),
            xhrFields: { withCredentials: true },
            success: () => successToast("Firm deleted"),
            error: () => errorToast("Failed to delete firm")
          }).always(loadReports);
        }
      });
    });

    // View reports
    card.find(".viewReportsBtn").click(function () {
      const type = $(this).data("type");
      const id = $(this).data("id");
      const detailsDiv = card.find(".reportDetails").removeClass("hidden").empty();

      $.ajax({
        url: `http://127.0.0.1:5000/api/admin/user-reports?firm_id=${firm._id}`,
        method: "GET",
        xhrFields: { withCredentials: true },
        success: function (res) {
          const reports = res.data.reports || [];
          if (reports.length === 0) {
            detailsDiv.html("<p>No reports found for this firm</p>");
          } else {
            reports.forEach(r => {
              detailsDiv.append(`
                <div class="border p-2 rounded mb-2">
                  <p><strong>Reason:</strong> ${r.reason}</p>
                  <p><strong>Reported At:</strong> ${formatDate(r.created_at)}</p>
                </div>
              `);
            });
          }
        },
        error: () => detailsDiv.html("<p>Failed to load reports</p>")
      });
    });

    container.append(card);
  });
}

// Render articles
function renderArticleReports(container, articles) {
  articles.forEach(article => {
    const card = $(`
      <div class="bg-white rounded-xl shadow-md p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div class="flex-1">
          <p><strong>Article Title:</strong> ${article.title}</p>
          <p><strong>Total Reports:</strong> ${article.report_count}</p>
          <div class="mt-2 reportDetails hidden"></div>
        </div>
        
        <div class="flex flex-col gap-2">
          <textarea placeholder="Reason for deletion" class="border px-3 py-2 rounded reasonInput"></textarea>
          <div class="flex gap-2 mt-2">
            <button class="deleteBtn bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded font-semibold">Delete Article</button>
            <button class="viewReportsBtn bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded font-semibold" data-type="article" data-id="${article._id}">View Reports</button>
          </div>
          
        </div>
        
      </div>
      
    `);


    // <div class="mt-2 reportDetails hidden"></div>


    // Delete article
    card.find(".deleteBtn").click(() => {
      const reason = card.find(".reasonInput").val().trim();
      if (!reason) return Swal.fire({ icon: "warning", title: "Provide a reason" });

      confirmAction("Confirm Delete Article?", `Reason: ${reason}`, "Delete").then(result => {
        if (result.isConfirmed) {
          $.ajax({
            url: `http://127.0.0.1:5000/api/admin/delete/action?article_id=${article._id}&action=report`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ reason }),
            xhrFields: { withCredentials: true },
            success: () => successToast("Article deleted"),
            error: () => errorToast("Failed to delete article")
          }).always(loadReports);
        }
      });
    });

    // View reports
    card.find(".viewReportsBtn").click(function () {
      const id = $(this).data("id");
      const detailsDiv = card.find(".reportDetails").removeClass("hidden").empty();

      $.ajax({
        url: `http://127.0.0.1:5000/api/admin/user-reports?article_id=${id}`,
        method: "GET",
        xhrFields: { withCredentials: true },
        success: function (res) {
          const reports = res.data.reports || [];
          if (reports.length === 0) {
            detailsDiv.html("<p>No reports found for this article</p>");
          } else {
            reports.forEach(r => {
              detailsDiv.append(`
                <div class="border p-2 rounded mb-2">
                  <p><strong>Reason:</strong> ${r.reason}</p>
                  <p><strong>Reported At:</strong> ${formatDate(r.created_at)}</p>
                </div>
              `);
            });
          }
        },
        error: () => detailsDiv.html("<p>Failed to load reports</p>")
      });
    });

    container.append(card);
  });
}
