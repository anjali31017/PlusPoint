// like.js
// Usage: initLikeButton($button, articleId)

async function toggleLike(articleId, $button) {
    try {
        const res = await ajaxWithJWT({
            url: `http://127.0.0.1:5000/api/article/like?article_id=${articleId}`,
            method: "POST"
        });

        if (res.data === "liked") {
            $button
                .addClass("text-red-600")
                .removeClass("text-gray-400")
                .find("span").text("Liked");
        } else {
            $button
                .removeClass("text-red-600")
                .addClass("text-gray-400")
                .find("span").text("Like");
        }

    } catch (err) {
        Swal.fire("Error", "Failed to like article", "error");
    }
}

function initLikeButton($button, articleId) {
    $button.off("click").on("click", function (e) {
        e.stopPropagation();
        toggleLike(articleId, $button);
    });
}
