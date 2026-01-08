// $(document).ready(function () {

$("#loginForm").on("submit", function (e) {
    e.preventDefault();

    // Reset errors
    $("#emailError").addClass("hidden");
    $("#passwordError").addClass("hidden");

    const email = $("#email").val().trim();
    const password = $("#password").val().trim();

    let hasError = false;

    if (!email || !email.includes("@")) {
        $("#emailError").removeClass("hidden");
        hasError = true;
        setTimeout(() => {
            $("#emailError").addClass('hidden').text('');
        }, 10000);
    }

    if (!password) {
        $("#passwordError").removeClass("hidden");
        hasError = true;
        setTimeout(() => {
            $('#passwordError').addClass('hidden').text('');
        }, 10000);
    }

    if (hasError) return;

    $.ajax({
        url: "http://127.0.0.1:5000/api/user/login",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            email: email,
            password: password
        }),
        beforeSend: function () {
            Swal.fire({
                title: "Logging in...",
                text: "Please wait",
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
        },
        success: function (response) {
            Swal.close();

            if (response.status === 1) {
                // Store tokens
                localStorage.setItem("access_token", response.data.access_token);
                localStorage.setItem("refresh_token", response.data.refresh_token);

                // Swal.fire({
                //     icon: "success",
                //     title: "Success",
                //     text: response.message,
                //     timer: 1500,
                //     showConfirmButton: false
                // }).then(() => {
                    window.location.href = "../src/home.html";
                // });
            } else {
                Swal.fire({
                    icon: "error",
                    title: "Login Failed",
                    text: response.message || "Invalid credentials"
                });
            }
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
// });
