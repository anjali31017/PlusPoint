function userRegistrationForm() {

    $('.text-red-500').addClass('hidden');

    let firstname = $('#firstname').val().trim();
    let lastname = $('#lastname').val().trim();
    let email = $('#email').val().trim();
    let password = $('#password').val();

    let isValid = true;

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{6,}$/;

    if (!firstname) {
        $('#firstnameError').removeClass('hidden');
        isValid = false;
        setTimeout(() => {
            $('#firstnameError').addClass('hidden').text('');
        }, 10000);
    }

    if (!email || !emailRegex.test(email)) {
        $('#emailError').removeClass('hidden');
        isValid = false;
        setTimeout(() => {
            $('#emailError').addClass('hidden').text('');
        }, 10000);
    }

    if (!password || !passwordRegex.test(password)) {
        $('#passwordError')
            .text('Password must be 6+ chars with letter & number')
            .removeClass('hidden');
        isValid = false;
        setTimeout(() => {
            $('#passwordError').addClass('hidden').text('');
        }, 10000);
    }

    if (!isValid) return;

    // Disable button + loader
    $('#user-registration-btn').prop('disabled', true);
    $('#btn-text').text('Registering...');
    $('#btn-loader').removeClass('hidden');

    $.ajax({
        url: "http://127.0.0.1:5000/api/user/register",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            first_name: firstname,
            last_name: lastname || "",
            email: email,
            password: password
        }),

        success: function (response) {
            console.log(response);
            // Swal.fire({
            //     icon: 'success',
            //     title: 'Registration Successful 🎉',
            //     text: response.message || 'Your account has been created',
            //     confirmButtonColor: '#7C3AED'
            // }).then(() => {
            // ✅ Redirect AFTER user clicks OK
            sessionStorage.setItem("username", response.data.username);
            window.location.href = "otp.html";

            // window.location.href = `otp.html?username=${response.data.username}`;
            // });

            $('#registerForm')[0].reset();
        },

        error: function (xhr) {

            let errorMessage = "Something went wrong";

            if (xhr.responseJSON) {
                errorMessage =
                    xhr.responseJSON.message ||
                    xhr.responseJSON.detail ||
                    errorMessage;
            }

            Swal.fire({
                icon: 'error',
                title: 'Registration Failed ❌',
                text: errorMessage
            });
        },

        // error: function (xhr) {

        //     Swal.fire({
        //         icon: 'error',
        //         title: 'Registration Failed ❌',
        //         text: xhr.responseJSON?.message || 'Something went wrong',
        //         confirmButtonColor: '#DC2626'
        //     });
        // },

        complete: function () {
            $('#user-registration-btn').prop('disabled', false);
            $('#btn-text').text('Register');
            $('#btn-loader').addClass('hidden');
        }
    });
}



