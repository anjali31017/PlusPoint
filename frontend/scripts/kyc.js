// ===== KYC Page JS with jQuery AJAX =====
$(document).ready(function () {

    // ===== Helper function to show error messages =====
    function showError(message) {
        $("#kycError").text(message).removeClass("hidden");

        // Hide after 10 seconds
        setTimeout(function () {
            $("#kycError").addClass("hidden").text("");
        }, 10000);
    }

    function showDobError(message) {
        $("#dobError").text(message).removeClass("hidden");

        // Hide after 10 seconds
        setTimeout(function () {
            $("#dobError").addClass("hidden").text("");
        }, 10000);
    }

    // ===== File upload preview =====
    $("#id_document").on("change", function () {
        const file = this.files[0];
        if (!file) return;

        // Clear previous file errors
        $("#kycError").addClass("hidden").text("");

        // Show file name
        $("#uploadText").text(file.name);

        // Preview image if image file
        if (file.type.startsWith("image/")) {
            const reader = new FileReader();
            reader.onload = function (e) {
                $("#docPreview").attr("src", e.target.result).removeClass("hidden");
            };
            reader.readAsDataURL(file);
        } else {
            $("#docPreview").addClass("hidden");
        }
    });

    // ===== Only allow numbers for ID Last 4 Digits =====
    // $("#id_last4").on("input", function () {
    //     this.value = this.value.replace(/\D/g, ""); // Remove any non-digit characters
    // });

    // ===== Form submit =====
    $("#kycForm").on("submit", function (e) {
        e.preventDefault();

        // Hide previous errors
        $("#kycError, #dobError").addClass("hidden").text("");

        // ===== Validation =====
        if (!$("#id_document").val()) {
            showError("Please upload your ID document.");
            return;
        }

        if (!$("#kyc_consent").is(":checked")) {
            showError("You must agree to the consent checkbox.");
            return;
        }

        const dobVal = $("#dob").val();
        if (!dobVal) {
            showDobError("Date of birth is required.");
            return;
        }

        const dob = new Date(dobVal);
        const today = new Date();
        let age = today.getFullYear() - dob.getFullYear();
        const m = today.getMonth() - dob.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) age--;
        if (age < 18) {
            showDobError("You must be at least 18 years old to submit KYC.");
            return;
        }

        // ===== Disable submit button =====
        const btn = $(this).find("button[type=submit]");
        btn.prop("disabled", true).text("Submitting...");

        // ===== Prepare FormData =====
        const formData = new FormData(this);

        // ===== AJAX request =====
        $.ajax({
            url: "http://127.0.0.1:5000/api/kyc/create",
            type: "POST",
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("access_token")
            },
            data: formData,
            processData: false,
            contentType: false,
            success: function (data) {
                console.log("KYC submission response:", data);
                Swal.fire({
                    icon: "success",
                    title: "KYC Submitted!",
                    text: data.data || "Sent for verification. Check your email.",
                    confirmButtonText: "OK"
                }).then(() => {
                    window.location.href = "home.html";
                });
            },
            error: function (xhr) {
                console.error("KYC submission error:", xhr);
                let errorMessage = "Something went wrong";

                // Get backend message if available
                if (xhr.responseJSON) {
                    errorMessage =
                        xhr.responseJSON.message ||
                        xhr.responseJSON.detail ||
                        errorMessage;
                }

                // Show error message in red below the form
                showError(errorMessage);

                // Re-enable submit button
                btn.prop("disabled", false).text("Submit KYC");
            }
        });
    });
});




// // ===== KYC Page JS with jQuery AJAX =====

// $(document).ready(function () {

//     // File upload preview
//     $("#id_document").on("change", function () {
//         const file = this.files[0];
//         if (!file) return;

//         // Show file name
//         $("#uploadText").text(file.name);

//         // Preview image if image file
//         if (file.type.startsWith("image/")) {
//             const reader = new FileReader();
//             reader.onload = function (e) {
//                 $("#docPreview").attr("src", e.target.result).removeClass("hidden");
//             };
//             reader.readAsDataURL(file);
//         } else {
//             $("#docPreview").addClass("hidden");
//         }
//     });

//     // Only allow numbers for ID Last 4 Digits
//     $("#id_last4").on("input", function () {
//         this.value = this.value.replace(/\D/g, ""); // Remove any non-digit characters
//     });

//     // Form submit
//     $("#kycForm").on("submit", function (e) {
//         e.preventDefault();

//         // Hide previous errors
//         $("#kycError").addClass("hidden");
//         $("#dobError").addClass("hidden");

//         if (!$("#id_document").val()) {
//             $("#kycError").text("Please upload your ID document.").removeClass("hidden");
//             return;
//         }

//         // Consent check
//         if (!$("#kyc_consent").is(":checked")) {
//             $("#kycError").text("You must agree to the consent checkbox.").removeClass("hidden");
//             return;
//         }

        

//         // DOB check >= 18
//         const dobVal = $("#dob").val();
//         if (!dobVal) {
//             $("#dobError").text("Date of birth is required.").removeClass("hidden");
//             return;
//         }


//         const dob = new Date(dobVal);
//         const today = new Date();
//         let age = today.getFullYear() - dob.getFullYear();
//         const m = today.getMonth() - dob.getMonth();
//         if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) age--;
//         if (age < 18) {
//             $("#dobError").text("You must be at least 18 years old to submit KYC.").removeClass("hidden");
//             return;
//         }

//         // Disable submit button
//         const btn = $(this).find("button[type=submit]");
//         btn.prop("disabled", true).text("Submitting...");

//         // Prepare form data
//         const formData = new FormData(this);

//         $.ajax({
//             url: "http://127.0.0.1:5000/api/kyc/create",
//             type: "POST",
//             headers: {
//                 "Authorization": "Bearer " + localStorage.getItem("access_token")
//             },
//             data: formData,
//             processData: false,
//             contentType: false,
//             success: function (data) {
//                 console.log("KYC submission response:", data);
//                 Swal.fire({
//                     icon: "success",
//                     title: "KYC Submitted!",
//                     text: data.data || "Sent for verification. Check your email.",
//                     confirmButtonText: "OK"
//                 }).then(() => {
//                     window.location.href = "home.html";
//                 });
//             },

//             error: function (xhr) {
//                 console.error("KYC submission error:", xhr);
//                 // Default error
//                 let errorMessage = "Something went wrong";

//                 // Get backend message if available
//                 if (xhr.responseJSON) {
//                     errorMessage =
//                         xhr.responseJSON.message ||
//                         xhr.responseJSON.detail ||
//                         errorMessage;
//                 }

//                 // Show error message in red below the form
//                 $("#kycError").text(errorMessage).removeClass("hidden");

//                 // Re-enable submit button
//                 const btn = $("#kycForm").find("button[type=submit]");
//                 btn.prop("disabled", false).text("Submit KYC");
//             }

//         });
//     });

// });
