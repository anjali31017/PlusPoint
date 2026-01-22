// endorsement.js
// Usage: endorseItem('firm', firmId, $button) or endorseItem('article', articleId, $button)
async function endorseItem(type, id, $button) {
    const endpointMap = {
        firm: 'firm',
        article: 'article'
    };

    if (!endpointMap[type]) throw new Error("Invalid endorse type");

    try {
        const res = await ajaxWithJWT({
            url: `http://127.0.0.1:5000/api/user/endorse?${type}_id=${id}`,
            method: "POST",
            contentType: "application/json"
        });

        // Update button text or state
        if ($button) {
            if (res.data === "endorsed") {
                $button.text("You Endorsed ").addClass("bg-green-700").removeClass("bg-green-600");
            } else {
                $button.text("Give Endorsement").addClass("bg-green-600").removeClass("bg-green-700");
            }
        }

        // Swal.fire("Success", res.message, "success");
        // Swal.fire({
        //     title: "Endorsement",
        //     text: `You have endorsed ${article.author.display_name || article.author.username}!`,
        //     icon: "success",
        //     showConfirmButton: false,
        //     timer: 2000
        // });

    } catch (err) {
        console.error(err);
        Swal.fire("Error", "Failed to endorse.", "error");
    }
}

// Initialize endorsement button
function initEndorseButton($button, type, id) {
    $button.off("click").on("click", function () {
        endorseItem(type, id, $button);
    });
}
