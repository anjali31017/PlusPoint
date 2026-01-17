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
            const html = `
                <div class="bg-white rounded-2xl p-6 shadow-md flex flex-col md:flex-row items-center md:items-start gap-6 w-full">
                    <div class="relative w-28 h-28 mx-auto md:mx-0 flex-shrink-0">
                        <img id="profile-avatar" src="${user.profile_picture_url || '../images/profile.jpg'}"
                             class="w-full h-full object-cover rounded-full border-4 border-purple-200">
                        ${isSelf ? `
                        <label for="profile-pic-input"
                            class="absolute bottom-0 right-0 bg-purple-600 text-white p-2 rounded-full cursor-pointer hover:bg-purple-700">
                            <i data-lucide="camera" class="w-4 h-4"></i>
                        </label>
                        <input type="file" id="profile-pic-input" class="hidden" accept="image/*">
                        ` : ""}
                    </div>

                    <div class="flex-1 min-w-0">
                        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                            <h2 id="profile-name" class="text-2xl font-bold text-center md:text-left">
                                ${user.first_name} ${user.last_name}
                            </h2>
                            <span id="kyc-badge" class="text-sm font-bold px-3 py-1 rounded-full text-center md:text-left"></span>
                        </div>
                        <p id="profile-username" class="text-gray-500 mt-1 text-center md:text-left">@${user.username}</p>
                        <p id="profile-email" class="text-gray-500 mt-1 text-center md:text-left">${user.email || ""}</p>
                        <p id="profile-bio" class="text-gray-600 mt-2 text-center md:text-left">${user.bio || ""}</p>

                        ${isSelf ? `<button id="editProfileBtn"
                            class="mt-4 px-5 py-2 bg-purple-600 text-white rounded-full hover:bg-purple-700 transition w-full md:w-auto">
                            Edit Profile
                        </button>` : ""}
                    </div>
                </div>

                <div class="mt-10 grid md:grid-cols-2 gap-10">
                    <div>
                        <h3 class="text-xl font-semibold text-gray-800 mb-4">Owned Firms</h3>
                        <div id="owned-firms" class="grid grid-cols-1 sm:grid-cols-1 md:grid-cols-1 gap-6"></div>
                    </div>
                    <div>
                        <h3 class="text-xl font-semibold text-gray-800 mb-4">Publisher Access</h3>
                        <div id="publisher-firms" class="grid grid-cols-1 sm:grid-cols-1 md:grid-cols-1 gap-6"></div>
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
            else
                $kyc.addClass("bg-red-100 text-red-700");

            // -----------------------------
            // Follow / Unfollow
            // -----------------------------
            if (!isSelf) updateFollowBtn(data.is_following);

            // -----------------------------
            // Firms
            // -----------------------------
            renderFirms("#owned-firms", data.owned_firms, false);
            renderFirms("#publisher-firms", data.publisher_firms, true);

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
    function renderFirms(container, firms, isPublisher) {
        const $el = $(container);
        $el.empty();

        if (!firms.length) {
            $el.html(`<p class="text-gray-500">No firms found</p>`);
            return;
        }

        firms.forEach(f => {
            const cardClass = isPublisher
                ? "bg-blue-50 hover:bg-blue-100 border border-blue-100"
                : "bg-purple-50 hover:bg-purple-100 border border-purple-100";

            $el.append(`
                <a href="firm.html?id=${isPublisher ? f.firm_id : f.id}" target="_blank"
                   class="block p-4 rounded-xl shadow-sm hover:shadow-md transition ${cardClass}">
                    <h4 class="font-semibold text-gray-800 truncate">${f.firm_name}</h4>
                    <p class="text-sm text-gray-500 truncate">@${f.firm_username}</p>
                    ${isPublisher ? `<p class="text-xs text-blue-600 mt-1">Trust: ${f.trust_factor}</p>` : ""}
                </a>
            `);
        });
    }

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
