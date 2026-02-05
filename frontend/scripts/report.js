// report.js
// Reusable report function for firm or article
// Usage: reportItem('firm', firmId) or reportItem('article', articleId)
async function reportItem(type, id) {
    const endpointMap = {
        firm: 'firm_id',
        article: 'article_id'
    };

    const key = endpointMap[type];
    if (!key) throw new Error("Invalid report type");

    const { value: reason } = await Swal.fire({
        title: `Report ${type.charAt(0).toUpperCase() + type.slice(1)}`,
        input: 'textarea',
        inputLabel: 'Reason',
        inputPlaceholder: 'Type your reason here...',
        showCancelButton: true,
        confirmButtonText: 'Report',
        inputValidator: (value) => {
            if (!value || value.trim() === '') {
                return 'You must enter a reason to report!';
            }
        }
    });

    if (!reason) return; // redundant, but safe

    try {
        const res = await ajaxWithJWT({
            url: `http://127.0.0.1:5000/api/user/report?${key}=${id}`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ reason: reason.trim() })
        });

        Swal.fire({
            title: "Reported",
            text: `${type.charAt(0).toUpperCase() + type.slice(1)} has been reported.`,
            icon: "success",
            showConfirmButton: false,
            timer: 1000
        });
    } catch (err) {
        console.error(err);
        const msg = err.responseJSON?.detail || "Failed to report.";
        Swal.fire("Error", msg, "error");
    }
}


// Initialize a report button
function initReportButton($button, type, id) {
    $button.off("click").on("click", function () {
        reportItem(type, id);
    });
}
