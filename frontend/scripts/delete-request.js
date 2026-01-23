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



// // deleteRequest.js
// // Usage: initDeleteRequest($button, 'article', articleId)
// //        initDeleteRequest($button, 'firm', firmId)

// async function requestDelete(type, id) {
//     const endpointMap = {
//         article: {
//             url: `http://127.0.0.1:5000/api/user/delete/request?article_id=${id}`,
//             label: "Article"
//         },
//         firm: {
//             url: "http://127.0.0.1:5000/api/firm/request-delete",
//             label: "Firm",
//             bodyKey: "firm_id"
//         }
//     };

//     const config = endpointMap[type];
//     if (!config) throw new Error("Invalid delete type");

//     const { value: reason } = await Swal.fire({
//         title: `Request ${config.label} Deletion`,
//         input: "textarea",
//         inputPlaceholder: "Reason for deletion",
//         showCancelButton: true,
//         confirmButtonText: "Submit"
//     });

//     if (!reason || !reason.trim()) return;

//     try {
//         const payload =
//             type === "firm"
//                 ? JSON.stringify({ firm_id: id, reason })
//                 : JSON.stringify({ reason });

//         const res = await ajaxWithJWT({
//             url: config.url,
//             method: "POST",
//             contentType: "application/json",
//             data: payload
//         });

//         Swal.fire({
//             icon: "success",
//             title: "Request Submitted",
//             text: res.message || "Deletion request submitted",
//             timer: 1500,
//             showConfirmButton: false
//         });

//     } catch (err) {
//         const msg =
//             err.responseJSON?.detail ||
//             "Deletion request already exists";

//         Swal.fire({
//             icon: "info",
//             title: "Already Requested",
//             text: msg,
//             timer: 1500,
//             showConfirmButton: false
//         });
//     }
// }

// function initDeleteRequest($button, type, id) {
//     $button.off("click").on("click", function (e) {
//         e.stopPropagation();
//         requestDelete(type, id);
//     });
// }













// // deleteRequest.js
// // Usage: initDeleteRequest($button, 'article', articleId)

// async function requestDelete(type, id) {
//     const endpointMap = {
//         article: `http://127.0.0.1:5000/api/user/delete/request?article_id=${id}`
//     };

//     if (!endpointMap[type]) throw new Error("Invalid delete type");

//     const { value: reason } = await Swal.fire({
//         title: "Request Deletion",
//         input: "textarea",
//         inputPlaceholder: "Why do you want to delete this?",
//         showCancelButton: true,
//         confirmButtonText: "Submit"
//     });

//     if (!reason || !reason.trim()) return;

//     try {
//         const res = await ajaxWithJWT({
//             url: endpointMap[type],
//             method: "POST",
//             contentType: "application/json",
//             data: JSON.stringify({ reason })
//         });

//         Swal.fire({
//             icon: "success",
//             title: "Request Submitted",
//             text: res.message || "Deletion request raised",
//             timer: 1500,
//             showConfirmButton: false
//         });

//     } catch (err) {
//         const msg =
//             err.responseJSON?.detail ||
//             "Delete request already exists";

//         Swal.fire({
//             icon: "info",
//             title: "Already Requested",
//             text: msg,
//             timer: 1500,
//             showConfirmButton: false
//         });
//     }
// }

// function initDeleteRequest($button, type, id) {
//     $button.off("click").on("click", function (e) {
//         e.stopPropagation();
//         requestDelete(type, id);
//     });
// }
