$(document).ready(function () {

    /* =========================
    OTP INPUT HANDLING
    ========================= */
    const $otpInputs = $('.otp-input');

    $otpInputs.on('input', function () {
        $(this).val($(this).val().replace(/[^0-9]/g, ''));

        const index = $otpInputs.index(this);
        if ($(this).val().length === 1 && index < $otpInputs.length - 1) {
            $otpInputs.eq(index + 1).focus();
        }
    });

    $otpInputs.on('keydown', function (e) {
        const index = $otpInputs.index(this);
        if (e.key === 'Backspace' && !$(this).val() && index > 0) {
            $otpInputs.eq(index - 1).focus();
        }
    });


    /* =========================
    OTP 5-MINUTE TIMER
    ========================= */
    let otpCountdown = 5 * 60;
    let otpTimerInterval;

    function startOtpTimer() {
        clearInterval(otpTimerInterval);
        otpCountdown = 5 * 60;

        otpTimerInterval = setInterval(function () {
            const minutes = Math.floor(otpCountdown / 60);
            const seconds = otpCountdown % 60;

            $('#otpTimer').text(
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
            );

            if (otpCountdown <= 0) {
                clearInterval(otpTimerInterval);
                $('#otpTimer').text("00:00");
            } else {
                otpCountdown--;
            }
        }, 1000);
    }

    startOtpTimer();


    /* =========================
    RESEND OTP COOLDOWN (40s)
    ========================= */
    let resendCountdown = 40;
    let resendInterval;
    const $resendBtn = $('#resendOTP');

    function startResendCooldown() {
        clearInterval(resendInterval);
        resendCountdown = 40;

        $resendBtn
            .addClass('opacity-50 pointer-events-none')
            .text(`Resend OTP (${resendCountdown}s)`);

        resendInterval = setInterval(function () {
            resendCountdown--;
            $resendBtn.text(`Resend OTP (${resendCountdown}s)`);

            if (resendCountdown <= 0) {
                clearInterval(resendInterval);
                $resendBtn
                    .removeClass('opacity-50 pointer-events-none')
                    .text('Resend OTP');
            }
        }, 1000);
    }

    startResendCooldown();


    /* =========================
    RESEND OTP CLICK
    ========================= */
    $resendBtn.on('click', function (e) {
        e.preventDefault();


        // e.stopPropagation();
        if (resendCountdown > 0) return;

        const username = sessionStorage.getItem("username");
        if (!username) {
            Swal.fire("Session Expired", "Please register again", "error");
            window.location.href = "register.html";
            return;
        }
        $.ajax({
            url: "http://127.0.0.1:5000/api/user/resend-otp",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ username }),

            beforeSend: function () {
                $resendBtn
                    .text('Sending...')
                    .addClass('pointer-events-none opacity-50');
            },

            success: function (res) {
                Swal.fire({
                    icon: 'success',
                    title: 'OTP Resent ✅',
                    text: `Remaining attempts: ${res.data.remaining_resends}` || 'A new OTP has been sent to your email',
                    confirmButtonColor: '#7C3AED'
                });

                // 🔁 Restart both timers
                otpCountdown = 5 * 60;
                resendCountdown = 40;

                startOtpTimer();
                startResendCooldown();
            },

            error: function (xhr) {
                let errorMessage = "Unable to resend OTP";

                if (xhr.responseJSON) {
                    errorMessage =
                        xhr.responseJSON.detail ||
                        xhr.responseJSON.message ||
                        errorMessage;
                }

                Swal.fire({
                    icon: 'error',
                    title: 'Failed ❌',
                    text: errorMessage,
                    confirmButtonColor: '#DC2626'
                });

                // 🚫 USER BLOCKED (6 hours)
                if (xhr.status === 403) {
                    $resendBtn
                        .text('Resend OTP')
                        .addClass('pointer-events-none opacity-50');
                    return;
                }

                // restore button if not blocked
                $resendBtn
                    .text('Resend OTP')
                    .removeClass('pointer-events-none opacity-50');
            }
        });
    });

    /* =========================
        VERIFY OTP SUBMIT
    ========================= */
    $('#otpForm').on('submit', function (e) {

        e.preventDefault();
        const $errorMsg = $('#otpError');
        $errorMsg.text('').addClass('hidden');

        const otp = $.map($otpInputs, input => $(input).val()).join('');
        if (otp.length !== 6) {
            Swal.fire("Invalid OTP", "Enter 6-digit OTP", "error");
            return;
        }

        const username = sessionStorage.getItem("username");
        if (!username) {
            Swal.fire({
                icon: "error",
                title: "Session Expired",
                text: "Please register again",
                timer: 2000,
                showConfirmButton: false
            }).then(() => {
                window.location.href = "register.html";
            });
            return;
        }

        const $submitBtn = $(this).find('button[type="submit"]');
        $submitBtn.prop('disabled', true).text('Verifying...');

        $.ajax({
            url: "http://127.0.0.1:5000/api/user/verify-otp",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ username, otp }),

            success: function (res) {
                Swal.fire({
                    icon: 'success',
                    title: 'Verified 🎉',
                    text: res.message || 'OTP verified successfully',
                    confirmButtonColor: '#7C3AED'
                }).then(() => {
                    localStorage.setItem('access_token', res.data.access_token);
                    localStorage.setItem('refresh_token', res.data.refresh_token);
                    window.location.href = "home.html";
                });
            },
            // $errorMsg.text("Enter a valid 6-digit OTP").removeClass('hidden');
            error: function (xhr) {
                let msg = "Verification failed";
                if (xhr.responseJSON) {
                    msg = xhr.responseJSON.message || xhr.responseJSON.detail || msg;
                    $errorMsg.text(msg).removeClass('hidden');
                    setTimeout(() => {
                        $errorMsg.addClass('hidden').text('');
                    }, 10000);

                }
                // if (xhr.status === 404) {
                //     console.log("404 User not found");
                //     $errorMsg.text(msg).removeClass('hidden');
                // }
                // if (xhr.status === 400) {
                //     console.log("400");
                //     $errorMsg.text(msg).removeClass('hidden');
                // }
                // if (xhr.status === 500) {
                //     console.log("500");
                //     $errorMsg.text(msg).removeClass('hidden');
                // }
                // if (xhr.status === 401) {
                //     console.log("401");
                //     $errorMsg.text(msg).removeClass('hidden');
                // }
                // if (xhr.status === 429) {
                //     console.log("429");
                //     $errorMsg.text(msg).removeClass('hidden');
                // }

                // if (xhr.status === 403) {
                //     console.log("403");
                //     //     Swal.fire({
                //     //     icon: 'error',
                //     //     title: 'User Not Found ❌',
                //     //     text: msg,
                //     //     confirmButtonColor: '#DC2626'
                //     // });
                // }

            },

            complete: function () {
                $submitBtn.prop('disabled', false).text('Verify OTP');
            }
        });
    });

});
