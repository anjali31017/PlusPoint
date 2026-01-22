// favorites.js

$(document).ready(async function () {
    // Check if user is logged in
    const loggedIn = await isLoggedIn();
    if (!loggedIn) return;

    // Show loading spinner
    showLoading();

    // Fetch followed firms
    await fetchFollowingFirms();
});

// Global variable to store firms for FE search
let allFirms = [];

async function fetchFollowingFirms() {
    try {
        const res = await ajaxWithJWT({
            url: "http://127.0.0.1:5000/api/user/following",
            method: "GET",
            contentType: "application/json",
        });

        hideLoading();

        if (res.status === 1 && res.data) {
            allFirms = res.data; // Save for FE search
            renderFirms(allFirms);
            renderSearchInput();
        } else {
            Swal.fire({
                icon: "error",
                title: "Oops!",
                text: res.message || "Failed to fetch following firms.",
            });
        }
    } catch (err) {
        hideLoading();
        console.error(err);
        Swal.fire({
            icon: "error",
            title: "Oops!",
            text: "Something went wrong while fetching following firms.",
        });
    }
}

function renderSearchInput() {
    const container = $("#content-wrapper");

    // Only add search input if not already present
    if ($("#firm-search").length) return;

    const searchInput = $(`
        <div class="mb-6">
            <input type="text" id="firm-search" placeholder="Search followed firms..."
                class="w-full p-3 rounded-xl border border-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-gray-800">
        </div>
    `);

    container.prepend(searchInput);

    $("#firm-search").on("input", function () {
        const query = $(this).val().toLowerCase();
        const filtered = allFirms.filter(firm =>
            firm.firm_name.toLowerCase().includes(query) ||
            firm.firm_username.toLowerCase().includes(query)
        );
        renderFirms(filtered);
    });
}

function renderFirms(firms) {
    const container = $("#content-wrapper");
    // Remove old grid but keep search input
    container.find(".grid").remove();

    if (firms.length === 0) {
        // Show empty state below search
        container.append(`
            <p class="text-center text-gray-400 mt-20 text-lg">No firms match your search.</p>
        `);
        return;
    }

    const grid = $('<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"></div>');

    firms.forEach(firm => {
        const card = $(`
            <div class="cursor-pointer p-5 bg-purple-50 rounded-2xl shadow hover:shadow-lg transition-all duration-200">
                <div class="flex items-center space-x-4">
                    <div class="w-12 h-12 rounded-full bg-purple-200 flex items-center justify-center text-white font-bold text-lg">
                        ${firm.firm_name[0]}
                    </div>
                    <div>
                        <h3 class="text-lg font-semibold text-purple-700">${firm.firm_name}</h3>
                        <p class="text-sm text-gray-500">@${firm.firm_username}</p>
                    </div>
                </div>
            </div>
        `);

        card.click(() => {
            window.location.href = `http://127.0.0.1:3000/src/firm.html?firm_id=${firm.firm_id}`;
        });

        grid.append(card);
    });

    container.append(grid);
}

// Loading spinner functions
function showLoading() {
    const container = $("#content-wrapper");
    container.html(`
        <div id="loading-spinner" class="flex justify-center items-center h-60">
            <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-purple-500 border-b-4 border-gray-200"></div>
        </div>
    `);
}

function hideLoading() {
    $("#loading-spinner").remove();
}
