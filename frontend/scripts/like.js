// like.js
// Usage: initLikeButton($button, articleId)

// async function toggleLike(articleId, $button) {
//     try {
//         const res = await ajaxWithJWT({
//             url: `http://127.0.0.1:5000/api/article/like?article_id=${articleId}`,
//             method: "POST"
//         });

//         if (res.data === "liked") {
//             $button
//                 .addClass("bg-red-600 text-white")
//                 .removeClass("bg-gray-200 text-gray-600")
//                 $button.find(".like-text").text("You Liked");
//         } else {
//             $button
//                 .removeClass("bg-red-600 text-white")
//                 .addClass("bg-gray-200 text-gray-600")
//                 $button.find(".like-text").text("Like");
//         }

//     } catch (err) {
//         Swal.fire("Error", "Failed to like article", "error");
//     }
// }

// async function toggleLike(articleId, $button) {
//     try {
//         // Optimistic toggle
//         const isLiked = $button.hasClass("bg-red-600");
//         if (!isLiked) {
//             $button.addClass("bg-red-600 text-white").removeClass("bg-gray-200 text-gray-600");
//             $button.find(".like-text").text("You Liked");
//         } else {
//             $button.removeClass("bg-red-600 text-white").addClass("bg-gray-200 text-gray-600");
//             $button.find(".like-text").text("Like");
//         }

//         const $likeCount = $("#article-stats").find("span").first().find("strong");
//         let count = parseInt($likeCount.text());
//         if (!isLiked) count++; // increment if we just liked
//         else count--;           // decrement if we just unliked
//         $likeCount.text(count);

//         // Call API in background
//         const res = await ajaxWithJWT({
//             url: `http://127.0.0.1:5000/api/article/like?article_id=${articleId}`,
//             method: "POST"
//         });

//         // Optional: adjust if backend disagrees
//         if (res.data === "liked" && !isLiked) return;  // all good
//         if (res.data !== "liked" && isLiked) return;    // all good
//         // If API disagrees, you could revert the toggle
//     } catch (err) {
//         Swal.fire("Error", "Failed to like article", "error");
//         // revert UI toggle on error
//         const isLiked = $button.hasClass("bg-red-600");
//         if (isLiked) {
//             $button.removeClass("bg-red-600 text-white").addClass("bg-gray-200 text-gray-600");
//             $button.find(".like-text").text("Like");
//         } else {
//             $button.addClass("bg-red-600 text-white").removeClass("bg-gray-200 text-gray-600");
//             $button.find(".like-text").text("You Liked");
//         }
//     }
// }


async function toggleLike(articleId, $button) {
    try {
        // --- Step 1: Optimistic toggle ---
        const isLiked = $button.hasClass("bg-red-600"); // true if currently liked

        if (!isLiked) {
            $button.addClass("bg-red-600 text-white").removeClass("bg-gray-200 text-gray-600");
            $button.find(".like-text").text("You Liked");
        } else {
            $button.removeClass("bg-red-600 text-white").addClass("bg-gray-200 text-gray-600");
            $button.find(".like-text").text("Like");
        }

        // --- Step 2: Update like count immediately ---
        const $likeCount = $("#article-stats").find("span").first().find("strong");
        let count = parseInt($likeCount.text());
        if (!isLiked) count++; // increment if we just liked
        else count--;           // decrement if we just unliked
        $likeCount.text(count);

        // --- Step 3: Call API in background ---
        await ajaxWithJWT({
            url: `http://127.0.0.1:5000/api/article/like?article_id=${articleId}`,
            method: "POST"
        });

    } catch (err) {
        Swal.fire("Error", "Failed to like article", "error");

        // --- Step 4: Revert UI if API fails ---
        const isLiked = $button.hasClass("bg-red-600");
        if (isLiked) {
            $button.removeClass("bg-red-600 text-white").addClass("bg-gray-200 text-gray-600");
            $button.find(".like-text").text("Like");
            // revert like count
            const $likeCount = $("#article-stats").find("span").first().find("strong");
            $likeCount.text(parseInt($likeCount.text()) - 1);
        } else {
            $button.addClass("bg-red-600 text-white").removeClass("bg-gray-200 text-gray-600");
            $button.find(".like-text").text("You Liked");
            const $likeCount = $("#article-stats").find("span").first().find("strong");
            $likeCount.text(parseInt($likeCount.text()) + 1);
        }
    }
}



function initLikeButton($button, articleId) {
    $button.off("click").on("click", function (e) {
        e.stopPropagation();
        toggleLike(articleId, $button);
    });
}
