async function requestDelete(type, id) {
    const endpointMap = {
        article: {
            url: `http://127.0.0.1:5000/api/user/delete/request?article_id=${id}`,
            label: "Article"
        },
        firm: {
            url: `http://127.0.0.1:5000/api/user/delete/request?firm_id=${id}`,
            label: "Firm"
        }
    };

    const config = endpointMap[type];
    if (!config) throw new Error("Invalid delete type");

    const { value: reason } = await Swal.fire({
        title: `Request ${config.label} Deletion`,
        input: "textarea",
        inputPlaceholder: "Reason for deletion",
        showCancelButton: true,
        confirmButtonText: "Submit",
        preConfirm: (val) => {
            if (!val || !val.trim()) Swal.showValidationMessage("Please enter a reason");
            return val?.trim();
        }
    });

    if (!reason) return;

    try {
        // Send reason in body for both article and firm
        const payload = JSON.stringify({ reason });

        const res = await ajaxWithJWT({
            url: config.url,
            method: "POST",
            contentType: "application/json",
            data: payload
        });

        Swal.fire({
            icon: "success",
            title: "Request Submitted",
            text: res.message || "Deletion request submitted",
            timer: 1500,
            showConfirmButton: false
        });

    } catch (err) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: err.responseJSON?.detail || "Deletion request already exists"
        });
    }
}



function initDeleteRequest($button, type, id) {
    $button.off("click").on("click", function (e) {
        e.stopPropagation();
        requestDelete(type, id);
    });
}


