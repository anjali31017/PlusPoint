// moderation.js

$(document).ready(function () {
  checkAdminSession(() => loadModerationArticles());
  attachLogoutHandler();

  $("#moderationLink").click(loadModerationArticles);
});

function loadModerationArticles() {
  const container = $("#moderationContainer");
  container.html('<p class="text-center text-gray-500">Loading...</p>');

  $.ajax({
    url: "http://127.0.0.1:5000/api/admin/moderation",
    method: "GET",
    xhrFields: { withCredentials: true },
    success: function (res) {
      const { articles = [] } = res.data;
      container.empty();

      if (articles.length === 0) {
        container.html("<p class='text-center text-gray-600'>No articles pending moderation</p>");
        return;
      }

      articles.forEach(article => {
        const card = $(`
          <div class="bg-white rounded-xl shadow-md p-6 flex flex-col gap-4">
            <p><strong>Title:</strong> ${article.title}</p>
            <div class="articleContent border p-4 rounded bg-gray-50 max-h-96 overflow-auto">${article.content}</div>
            <textarea placeholder="Reason for rejection (if rejecting)" class="border px-3 py-2 rounded customReason"></textarea>
            <div class="flex gap-2 mt-2">
              <button class="acceptBtn bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded font-semibold">Accept</button>
              <button class="rejectBtn bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded font-semibold">Reject</button>
            </div>
          </div>
        `);

        // Accept article
        card.find(".acceptBtn").click(() => {
          confirmAction("Publish Article?", `Title: ${article.title}`).then(result => {
            if (result.isConfirmed) {
              $.ajax({
                url: `http://127.0.0.1:5000/api/admin/moderation/accept?article_id=${article._id}`,
                method: "POST",
                xhrFields: { withCredentials: true },
                success: () => successToast("Article published"),
                error: (xhr) => errorToast(xhr.responseJSON?.detail || "Failed to publish article")
              }).always(loadModerationArticles);
            }
          });
        });

        // Reject article
        card.find(".rejectBtn").click(() => {
          let reason = card.find(".customReason").val().trim();
          if (!reason) {
            Swal.fire({ icon: "warning", title: "Please provide a reason for rejection" });
            return;
          }

          confirmAction("Reject Article?", `Title: ${article.title}\nReason: ${reason}`).then(result => {
            if (result.isConfirmed) {
              $.ajax({
                url: `http://127.0.0.1:5000/api/admin/moderation/reject?article_id=${article._id}`,
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify({ reason }),
                xhrFields: { withCredentials: true },
                success: () => successToast("Article rejected"),
                error: (xhr) => errorToast(xhr.responseJSON?.detail || "Failed to reject article")
              }).always(loadModerationArticles);
            }
          });
        });

        container.append(card);
      });
    },
    error: () => errorToast("Failed to fetch moderation articles")
  });
}
