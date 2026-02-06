$(document).ready(async function () {
    lucide.createIcons();

    // -----------------------------
    // Auth protection
    // -----------------------------
    if (!getAccessToken()) {
        redirectToLogin();
        return;
    }

    const params = new URLSearchParams(window.location.search);
    const userId = params.get("user_id"); // null = self profile

    const $loader = $("#profile-loader");
    const $content = $("#profile-content");

    let isSelf = false;
    let user = {};

    // =====================================================
    // Fetch Profile
    // =====================================================
    async function fetchProfile() {
        try {
            $loader.show();
            $content.hide();

            const res = await ajaxWithJWT({
                url: `http://127.0.0.1:5000/api/user/profile${userId ? "?user_id=" + userId : ""}`,
                method: "GET"
            });

            if (res.status !== 1) throw new Error(res.message);

            const data = res.data;
            user = data.user;
            isSelf = data.is_self;

            // -----------------------------
            // Profile HTML
            // -----------------------------
            console.log(user.profile_picture_url)
            const html = `
                <div class="bg-white rounded-2xl p-6 shadow-md flex flex-col md:flex-row items-center md:items-start gap-6 w-full">
                    <div class="relative w-28 h-28 mx-auto md:mx-0 flex-shrink-0">
                        <img id="profile-avatar" src="${user.profile_picture_url || '../media/profile.jpg'}"
                             class="w-full h-full object-cover rounded-full border-4 border-purple-200">

                    </div>

                    <div class="flex-1 min-w-0">
                        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                            <h2 id="profile-name" class="text-2xl font-bold text-center md:text-left">
                                ${user.first_name} ${user.last_name}
                            </h2>
                            <span id="kyc-badge" class="text-sm font-bold px-3 py-1 rounded-full text-center md:text-left"></span>
                        </div>
                        <p id="profile-username" class="text-gray-500 mt-1 text-center md:text-left">@${user.username}</p>
                        <p id="profile-bio" class="text-gray-600 mt-2 text-center md:text-left">${user.bio || ""}</p>

                        ${isSelf ? `
                            <div id="profile-actions" class="mt-4 flex flex-col sm:flex-row gap-3 w-full md:w-auto">
                                <button id="editProfileBtn"
                                    class="px-5 py-2 bg-cyan-600 text-white rounded-full hover:bg-cyan-700 transition">
                                    Edit Profile
                                </button>
                            </div>
                        ` : ""}
                    </div>
                </div>

                <div class="mt-10 grid md:grid-cols-1 gap-10">
                    <div>
                        <h3 class="text-xl font-semibold text-gray-800 mb-4">Owned Firms</h3>
                        <div id="owned-firms" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-6"></div>
                    </div>
                </div>
            `;

            $content.html(html);

            // -----------------------------
            // KYC badge
            // -----------------------------
            const $kyc = $("#kyc-badge").text(data.kyc_status);
            if (data.kyc_status === "VERIFIED")
                $kyc.addClass("bg-green-100 text-green-700");
            else if (data.kyc_status === "PENDING")
                $kyc.addClass("bg-yellow-100 text-yellow-700");
            else if (data.kyc_status === "UNDER_REVIEW")
                $kyc.addClass("bg-sky-100 text-sky-700");
            else if (data.kyc_status === "REJECTED")
                $kyc.addClass("bg-red-100 text-red-700");
            else
                $kyc.addClass("bg-red-100 text-red-700");

            // -----------------------------
            // KYC Action Buttons (Self only)
            // -----------------------------
            if (
                isSelf &&
                (data.kyc_status === "PENDING" || data.kyc_status === "REJECTED")
            ) {
                $("#profile-actions").append(`
        <a href="kyc.html"
           class="px-5 py-2 bg-rose-400 text-white rounded-full hover:bg-rose-700 transition text-center">
            Complete KYC
        </a>

    `);
            }


            // -----------------------------
            // Register Firm Button (KYC VERIFIED)
            // -----------------------------
            if (isSelf && data.kyc_status === "VERIFIED") {
                $("#profile-actions").append(`
        <button id="registerFirmBtn"
            class="px-5 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-700 transition">
            Register Firm
        </button>

    `);
            }




            // =====================================================
            // Register Firm modal
            // =====================================================
            $(document).on("click", "#registerFirmBtn", function () {
                openRegisterFirmModal();
            });

            function openRegisterFirmModal() {
                const $modal = $(`
        <div class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center px-4">
            <div class="bg-white rounded-3xl p-6 w-full max-w-md shadow-xl animate-fade-in">
                <h3 class="text-2xl font-bold text-gray-800 mb-1">Register Firm</h3>
                <p class="text-sm text-gray-500 mb-5">
                    Create a firm under your verified account
                </p>

                <form id="registerFirmForm" class="space-y-4">
                    <div>
                        <label class="text-sm font-medium text-gray-700">Firm Name</label>
                        <input name="firm_name" required
                            class="w-full mt-1 border rounded-xl px-4 py-2 focus:ring-2 focus:ring-emerald-400 focus:outline-none">
                        <p class="text-xs text-red-500 mt-1 hidden error-firm-name"></p>
                    </div>

                    <div>
                        <label class="text-sm font-medium text-gray-700">Bio</label>
                        <textarea name="bio" rows="3" maxlength="250"
                            class="w-full mt-1 border rounded-xl px-4 py-2 focus:ring-2 focus:ring-emerald-400 focus:outline-none"></textarea>
                        <p class="text-xs text-gray-400 mt-1">Max 250 characters</p>
                        <p class="text-xs text-red-500 hidden error-bio"></p>
                    </div>

                    <div class="flex items-start gap-2">
                        <input type="checkbox" id="agreeTerms"
                            class="mt-1 w-4 h-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500">
                        <label for="agreeTerms" class="text-sm text-gray-600">
                            I agree to the
                            <a href="terms.html#registerFirm" target="_blank"
                            class="text-emerald-600 underline hover:text-emerald-700">
                                Terms & Conditions
                            </a>
                        </label>
                    </div>
                    <p class="text-xs text-red-500 hidden error-terms">
                        You must agree to the terms and conditions
                    </p>

                    <div class="flex justify-end gap-3 pt-4">
                        <button type="button" id="closeFirmModal"
                            class="px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 transition">
                            Cancel
                        </button>
                        <button type="submit"
                            class="px-5 py-2 rounded-xl bg-emerald-600 text-white font-semibold hover:bg-emerald-700 transition">
                            Register
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `);

                $("body").append($modal);

                $("#closeFirmModal").on("click", () => $modal.remove());

                // Submit
                $("#registerFirmForm").on("submit", async function (e) {
                    e.preventDefault();


                    const agreed = $("#agreeTerms").is(":checked");
                    $(".error-terms").addClass("hidden");

                    if (!agreed) {
                        $(".error-terms")
                            .text("You must agree to the terms and conditions")
                            .removeClass("hidden");
                        $submitBtn.prop("disabled", false).text("Register");
                        return;
                    }

                    const $registerBtn = $("#registerFirmForm button[type='submit']");
                    $registerBtn.prop("disabled", true).addClass("opacity-60");

                    $("#agreeTerms").on("change", function () {
                        $registerBtn.prop("disabled", !this.checked)
                            .toggleClass("opacity-60", !this.checked);
                    });


                    const firm_name = $(this).find("[name='firm_name']").val().trim();
                    const bio = $(this).find("[name='bio']").val().trim();

                    $(".error-firm-name, .error-bio").addClass("hidden");

                    if (firm_name.length < 2) {
                        $(".error-firm-name")
                            .text("Firm name must be at least 2 characters")
                            .removeClass("hidden");
                        return;
                    }

                    const $submitBtn = $(this).find("button[type='submit']");
                    $submitBtn.prop("disabled", true).text("Registering...");

                    try {
                        const res = await ajaxWithJWT({
                            url: "http://127.0.0.1:5000/api/firm/register",
                            method: "POST",
                            contentType: "application/json",
                            data: JSON.stringify({
                                firm_name,
                                bio
                            })
                        });

                        if (res.status !== 1) throw new Error(res.message);

                        Swal.fire("Success", "Firm registered successfully", "success");
                        $modal.remove();
                        fetchProfile(); // refresh firms list

                    } catch (err) {
                        Swal.fire("Error", err.message || "Failed to register firm", "error");
                    } finally {
                        $submitBtn.prop("disabled", false).text("Register");
                    }
                });
            }



            // // -----------------------------
            // // Follow / Unfollow
            // // -----------------------------
            // if (!isSelf) updateFollowBtn(data.is_following);

            // -----------------------------
            // Firms
            // -----------------------------
            renderFirms("#owned-firms", data.owned_firms, false);

            lucide.createIcons();
            $loader.hide();
            $content.fadeIn(300);

        } catch (err) {
            console.error(err);
            Swal.fire("Error", err.message || "Failed to load profile", "error");
            $loader.hide();
        }
    }

    // =====================================================
    // Render firms
    // =====================================================


    function renderFirms(container, firms) {
        const $el = $(container);
        $el.empty();

        if (!firms.length) {
            $el.html(`<p class="text-gray-500">No firms found</p>`);
            return;
        }

        firms.forEach(f => {
            // Single card style
            const cardClass = "bg-white hover:bg-indigo-50 border border-purple-200";

            // Simplified URL
            const href = `firm.html?firm_id=${f.id}`;

            $el.append(`
            <a href="${href}"
                class="w-full p-4 rounded-xl shadow-sm hover:shadow-md transition ${cardClass}">
                <h4 class="font-semibold text-gray-800 truncate">${f.firm_name}</h4>
                <p class="text-sm text-gray-500 truncate">@${f.firm_username}</p>
                <p class="text-xs mt-1 text-purple-600">
                    Trust: ${Number(f.trust_factor).toFixed(2) ?? 'N/A'}
                </p>
            </a>
        `);
        });
    }


    // function renderFirms(container, firms, isPublisher) {
    //     const $el = $(container);
    //     $el.empty();

    //     if (!firms.length) {
    //         $el.html(`<p class="text-gray-500">No firms found</p>`);
    //         return;
    //     }

    //     firms.forEach(f => {
    //         const cardClass = isPublisher
    //             ? "bg-blue-50 hover:bg-blue-100 border border-blue-100"
    //             : "bg-purple-50 hover:bg-purple-100 border border-purple-100";

    //         // 🔹 URL logic
    //         const href = isPublisher
    //             ? `firm.html?firm_id=${f.firm_id}&publisher_id=${user.id}`
    //             : `firm.html?firm_id=${f.id}`;

    //         $el.append(`
    //             <a href="${href}" target="_blank"
    //                 class="w-full p-4 rounded-xl shadow-sm hover:shadow-md transition ${cardClass}">
    //                 <h4 class="font-semibold text-gray-800 truncate">${f.firm_name}</h4>
    //                 <p class="text-sm text-gray-500 truncate">@${f.firm_username}</p>
    //                 <p class="text-xs mt-1 ${isPublisher ? 'text-blue-600' : 'text-purple-600'}">
    //                     Trust: ${f.trust_factor ?? 'N/A'}
    //                 </p>
    //             </a>
    //             `);
    //     });
    // }

    // =====================================================
    // Follow / Subscribe
    // =====================================================
    function updateFollowBtn(isFollowing) {
        const $btn = $("#followBtn");
        if (isFollowing) {
            $btn.text("Unfollow")
                .removeClass("bg-purple-600 text-white")
                .addClass("bg-gray-200 text-gray-700");
        } else {
            $btn.text("Follow")
                .removeClass("bg-gray-200 text-gray-700")
                .addClass("bg-purple-600 text-white");
        }
    }

    $(document).on("click", "#followBtn", async function () {
        try {
            const $btn = $(this);
            $btn.prop("disabled", true).text("Please wait...");

            const res = await ajaxWithJWT({
                url: "http://127.0.0.1:5000/api/user/subscribe",
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify({ user_id: userId })
            });

            if (res.status !== 1) throw new Error(res.message);
            updateFollowBtn(res.data.is_following);

        } catch (err) {
            Swal.fire("Error", err.message, "error");
        } finally {
            $("#followBtn").prop("disabled", false);
        }
    });

    // =====================================================
    // Edit profile modal
    // =====================================================
    $(document).on("click", "#editProfileBtn", function () {
        openEditModal();
    });

    function openEditModal() {
        const first = user.first_name || "";
        const last = user.last_name || "";

        const $modal = $(`
        <div class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center px-4">
            <div class="bg-white rounded-3xl p-6 w-full max-w-md shadow-xl animate-fade-in">
                <h3 class="text-2xl font-bold text-gray-800 mb-1">Edit Profile</h3>
                <p class="text-sm text-gray-500 mb-5">Update your personal details</p>

                <form id="editProfileForm" class="space-y-4">
                    <div>
                        <label class="text-sm font-medium text-gray-700">First Name</label>
                        <input name="first_name" value="${first}" class="w-full mt-1 border rounded-xl px-4 py-2 focus:ring-2 focus:ring-purple-400 focus:outline-none">
                        <p class="text-xs text-red-500 mt-1 hidden error-first"></p>
                    </div>
                    <div>
                        <label class="text-sm font-medium text-gray-700">Last Name</label>
                        <input name="last_name" value="${last}" class="w-full mt-1 border rounded-xl px-4 py-2 focus:ring-2 focus:ring-purple-400 focus:outline-none">
                        <p class="text-xs text-red-500 mt-1 hidden error-last"></p>
                    </div>
                    <div>
                        <label class="text-sm font-medium text-gray-700">Bio</label>
                        <textarea name="bio" rows="4" maxlength="250" class="w-full mt-1 border rounded-xl px-4 py-2 focus:ring-2 focus:ring-purple-400 focus:outline-none">${user.bio || ""}</textarea>
                        <div class="flex justify-between text-xs mt-1">
                            <p class="text-red-500 hidden error-bio"></p>
                            <p class="text-gray-400"><span id="bio-count">0</span>/250</p>
                        </div>
                    </div>
                    <div>
                        <label class="text-sm font-medium text-gray-700">Profile Picture</label>
                        <input type="file" name="profile_picture" accept="image/png,image/jpeg" class="w-full mt-1 text-sm">
                        <p class="text-xs text-gray-400 mt-1">PNG or JPG • Max 2MB</p>
                        <p class="text-xs text-red-500 hidden error-image"></p>
                    </div>

                    <div class="flex justify-end gap-3 pt-4">
                        <button type="button" id="closeEdit" class="px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 transition">Cancel</button>
                        <button type="submit" class="px-5 py-2 rounded-xl bg-purple-600 text-white font-semibold hover:bg-purple-700 transition disabled:opacity-60">Save Changes</button>
                    </div>
                </form>
            </div>
        </div>
        `);

        $("body").append($modal);

        $("#closeEdit").on("click", () => $modal.remove());

        // Bio counter
        const $bio = $modal.find("textarea[name='bio']");
        const updateCounter = () => $("#bio-count").text($bio.val().length);
        updateCounter();
        $bio.on("input", updateCounter);

        // Form submission
        $("#editProfileForm").on("submit", async function (e) {
            e.preventDefault();
            $(".error-first, .error-last, .error-bio, .error-image").addClass("hidden");

            const formData = new FormData(this);
            const firstName = formData.get("first_name").trim();
            const lastName = formData.get("last_name").trim();
            const bio = formData.get("bio").trim();
            const image = formData.get("profile_picture");

            let valid = true;

            if (firstName.length < 2) {
                $(".error-first").text("First name must be at least 2 characters").removeClass("hidden");
                valid = false;
            }
            if (lastName.length < 2) {
                $(".error-last").text("Last name must be at least 2 characters").removeClass("hidden");
                valid = false;
            }
            if (bio.length > 250) {
                $(".error-bio").text("Bio cannot exceed 250 characters").removeClass("hidden");
                valid = false;
            }
            if (image && image.size > 0) {
                if (!["image/jpeg", "image/png"].includes(image.type)) {
                    $(".error-image").text("Only JPG or PNG images allowed").removeClass("hidden");
                    valid = false;
                }
                if (image.size > 2 * 1024 * 1024) {
                    $(".error-image").text("Image must be under 2MB").removeClass("hidden");
                    valid = false;
                }
            }
            if (!valid) return;

            const $submitBtn = $(this).find("button[type='submit']");
            $submitBtn.prop("disabled", true).text("Saving...");

            try {
                const res = await ajaxWithJWT({
                    url: "http://127.0.0.1:5000/api/user/profile",
                    method: "PUT",
                    processData: false,
                    contentType: false,
                    data: formData
                });

                if (res.status !== 1) throw new Error(res.message);

                Swal.fire("Success", "Profile updated successfully", "success");
                $modal.remove();
                fetchProfile();

            } catch (err) {
                Swal.fire("Error", err.message, "error");
            } finally {
                $submitBtn.prop("disabled", false).text("Save Changes");
            }
        });
    }

    // =====================================================
    // Init
    // =====================================================
    fetchProfile();
});
