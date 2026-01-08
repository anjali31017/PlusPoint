$(document).ready(function () {
    const token = new URLSearchParams(window.location.search).get("token");

    if (!token) {
        $("#formError").text("Reset token is missing or expired").removeClass("hidden");
        return;
    }

    $("#resetForm").on("submit", function (e) {
        e.preventDefault();

        // Clear previous errors
        $(".error-msg").text("").addClass("hidden");

        const password = $("#password").val().trim();
        const confirmPassword = $("#confirmPassword").val().trim();
        let valid = true;

        // Password validations
        if (!password) {
            $("#passwordError").text("Password is required").removeClass("hidden");
            valid = false;
        } else if (password.length < 6) {
            $("#passwordError").text("Password must be at least 6 characters").removeClass("hidden");
            valid = false;
        } else if (!/^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$/.test(password)) {
            $("#passwordError").text("Password must include letters, numbers, and a special character").removeClass("hidden");
            valid = false;
        }

        // Confirm password validation
        if (confirmPassword !== password) {
            $("#confirmPasswordError").text("Passwords do not match").removeClass("hidden");
            valid = false;
        }

        if (!valid) {
            return;
        }

        // AJAX request
        $.ajax({
            url: "http://127.0.0.1:5000/api/user/reset-password",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ token, password }),
            beforeSend: function () {
                $("#formError").text("Resetting...").removeClass("hidden");
            },
            success: function (res) {
                Swal.fire({
                    icon: "success",
                    title: "Success",
                    text: res.message || "Password reset successful"
                }).then(() => window.location.href = "login.html");
            },
            error: function (xhr) {
                let msg = "Invalid or expired link";
                if (xhr.responseJSON && xhr.responseJSON.detail) msg = xhr.responseJSON.detail;
                $("#formError").text(msg).removeClass("hidden");
            }
        });
    });
});
