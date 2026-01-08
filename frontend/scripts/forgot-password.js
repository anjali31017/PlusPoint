$("#forgotForm").on("submit", function (e) {
    e.preventDefault();

    $("#emailError").addClass("hidden");

    const email = $("#email").val().trim();

    if (!email || !email.includes("@")) {
        $("#emailError").removeClass("hidden");
        setTimeout(() => {
            $("#emailError").addClass('hidden').text('');
        }, 10000);
        return;
    }

    $.ajax({
        url: "http://127.0.0.1:5000/api/user/forgot-password",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ email: email }),

        beforeSend: function () {
            Swal.fire({
                title: "Sending...",
                text: "Please wait",
                allowOutsideClick: false,
                didOpen: () => Swal.showLoading()
            });
        },

        success: function (res) {
            Swal.fire({
                icon: "success",
                title: "Email Sent",
                text: res.message || "If the email exists, a reset link has been sent",
                confirmButtonText: "OK"
            }).then(() => {
                window.location.href = "login.html";
            });
        },

        error: function (xhr) {
            Swal.close();

            let message = "Something went wrong";

            if (xhr.responseJSON && xhr.responseJSON.detail) {
                message = xhr.responseJSON.detail;
            }

            Swal.fire({
                icon: "error",
                title: "Error",
                text: message
            });
        }
    });
});