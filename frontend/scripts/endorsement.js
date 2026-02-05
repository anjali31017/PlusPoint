
// endorsement.js
async function endorseItem(type, id, $button) {
    const endpointMap = {
        firm: 'firm',
        article: 'article'
    };

    if (!endpointMap[type]) throw new Error("Invalid endorse type");

    try {
        // --- Step 1: Optimistic toggle ---
        const isEndorsed = $button.text().includes("You Endorsed"); // check current text

        if (!isEndorsed) {
            $button.text("You Endorsed");
        } else {
            $button.text("Give Endorsement");
        }

        // --- Step 2: Update endorsement count immediately ---
        const $endorseCount = $("#article-stats").find("span").eq(1).find("strong");
        let count = parseInt($endorseCount.text());
        if (!isEndorsed) count++; else count--;
        $endorseCount.text(count);

        // --- Step 3: Call API in background ---
        await ajaxWithJWT({
            url: `http://127.0.0.1:5000/api/user/endorse?${type}_id=${id}`,
            method: "POST",
            contentType: "application/json"
        });

    } catch (err) {
        console.error(err);
        Swal.fire("Error", "Failed to endorse.", "error");

        // --- Step 4: Revert UI if API fails ---
        const isEndorsed = $button.text().includes("You Endorsed");
        const $endorseCount = $("#article-stats").find("span").eq(1).find("strong");
        if (isEndorsed) {
            $button.text("Give Endorsement");
            $endorseCount.text(parseInt($endorseCount.text()) - 1);
        } else {
            $button.text("You Endorsed");
            $endorseCount.text(parseInt($endorseCount.text()) + 1);
        }
    }
}

// Initialize endorsement button
function initEndorseButton($button, type, id) {
    $button.off("click").on("click", function () {
        endorseItem(type, id, $button);
    });
}


