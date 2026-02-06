// search.js
$(document).ready(function () {
    // Protect page
    if (!getAccessToken()) {
        redirectToLogin();
        return;
    }

    const $main = $("main");
    const $header = $main.find("header");

    // Inject search UI BELOW header
    // Inject search UI BELOW header
    $header.after(`
    <section id="searchSection"
        class="p-4 bg-white border-b border-purple-100 sticky top-[72px] z-10">

        <!-- ROW 1 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
            <input id="searchInput" type="text"
                placeholder="Search publishers, firms, articles..."
                class="w-full px-4 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500">

            <input id="tagsInput" type="text"
                placeholder="Tags (comma separated)"
                class="w-full px-4 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500">

            <input id="categoriesInput" type="text"
                placeholder="Categories (comma separated)"
                class="w-full px-4 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500">
        </div>

        <!-- ROW 2 -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-3 items-center">

            <!-- Start Date -->
            <div class="flex items-center gap-2">
                <label for="startDateInput" class="text-sm text-gray-700 whitespace-nowrap">
                    Start date:
                </label>
                <input id="startDateInput" type="date"
                    class="flex-1 px-4 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500">
            </div>

            <!-- End Date -->
            <div class="flex items-center gap-2">
                <label for="endDateInput" class="text-sm text-gray-700 whitespace-nowrap">
                    End date:
                </label>
                <input id="endDateInput" type="date"
                    class="flex-1 px-4 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500">
            </div>

            <!-- Hot Topic -->
            <div class="flex items-center gap-2 md:justify-center">
                <input id="hotTopicInput" type="checkbox" class="rounded border-gray-300">
                <label for="hotTopicInput" class="text-gray-700 text-sm">
                    Hot Topic
                </label>
            </div>

            <!-- Search Button -->
            <button id="searchBtn"
                class="w-full px-5 py-3 rounded-full bg-purple-600 text-white font-semibold hover:bg-purple-700 transition">
                Search
            </button>

        </div>
    </section>

    <div id="loader" class="hidden flex justify-center py-6">
        <div class="loader"></div>
    </div>

    <section id="resultsWrapper" class="p-4 space-y-8"></section>
    `);



    const $resultsWrapper = $("#resultsWrapper");
    const $loader = $("#loader");

    let currentPage = 1;
    const pageSize = 10;
    let isLoading = false;

    // ----------------------------
    // Helper: render section
    // ----------------------------
    function renderSection(section, data) {
        if (!data || data.length === 0) return "";

        let html = "";
        if (section === "publishers") {
            html = `<div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                ${data.map(p => `
                    <a href="profile.html?user_id=${p.id}" target="_blank"
                       class="p-4 bg-purple-50 rounded-xl shadow-sm block">
                        <p class="font-semibold">${p.first_name ?? ""} ${p.last_name ?? ""}</p>
                        <p class="text-sm text-gray-500">@${p.username}</p>

                    </a>
                `).join('')}
            </div>`;
        } else if (section === "firms") {
            html = `<div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                ${data.map(f => `
                    <a href="firm.html?firm_id=${f.id}" target="_blank"
                       class="p-4 bg-blue-50 rounded-xl shadow-sm block">
                        <p class="font-semibold">${f.firm_name}</p>
                        <p class="text-sm text-gray-500">@${f.firm_username}</p>
                    </a>
                `).join('')}
            </div>`;
        } else { // quick_take or coverage
            html = `<div class="space-y-3">
                ${data.map(a => `
                    <a href="article.html?article_id=${a.id}&type=${section}" target="_blank"
                       class="p-4 bg-white rounded-xl shadow hover:shadow-md transition block">
                        <h4 class="font-semibold text-gray-800 truncate">${a.title}</h4>
                        <p class="text-xs text-gray-500 mt-1">
                            ${a.publisher.first_name ?? ""} ${a.publisher.last_name ?? ""} · ${a.firm.firm_name}
                        </p>
                    </a>
                `).join('')}
            </div>`;
        }

        $("#resultsContent").html(html);
    }

    // ----------------------------
    // Perform API Search
    // ----------------------------
    async function performSearch(reset = true) {
        if (isLoading) return;
        isLoading = true;
        $loader.removeClass("hidden");

        if (reset) {
            currentPage = 1;
            $resultsWrapper.empty();
            $("#resultsTabs").remove();
            $("#resultsContent").remove();
        }

        const searchText = $("#searchInput").val().trim();
        // const tags = $("#tagsInput").val().split(",").map(t => t.trim()).filter(t => t);
        const tags = $("#tagsInput").val().split(",").map(t => t.trim()).filter(t => t);
        const categories = $("#categoriesInput").val().split(",").map(c => c.trim()).filter(c => c);
        const hotTopic = $("#hotTopicInput").is(":checked") ? true : undefined;

        // Do not send empty keyword for publishers/firms
        const requestPayload = {
            search_text: $("#searchInput").val().trim() || undefined,
            tags: tags.length ? tags : undefined,
            categories: categories.length ? categories : undefined,
            hot_topic: hotTopic,
            start_date: $("#startDateInput").val() || undefined,
            end_date: $("#endDateInput").val() || undefined,
            page: currentPage,
            page_size: pageSize
        };


        try {
            const response = await ajaxWithJWT({
                url: "http://127.0.0.1:5000/api/article/search",
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify(requestPayload)
            });

            const sectionsData = {
                publishers: searchText ? response.publishers : [], // only show if keyword entered
                firms: searchText ? response.firms : [],
                quick_take: response.quick_take,
                coverage: response.coverage
            };

            // Remove previous tabs/content
            $("#resultsTabs, #resultsContent").remove();

            // Build tabs dynamically
            const tabsHTML = Object.entries(sectionsData)
                .filter(([key, data]) => data && data.length > 0)
                .map(([key, data], i) => `
                <button class="tab-btn px-4 py-2 ${i === 0 ? 'border-b-2 border-purple-600 font-semibold' : 'text-gray-500'}"
                        data-section="${key}">
                    ${key.replace('_', ' ').toUpperCase()} (${data.length})
                </button>
            `).join("");

            if (tabsHTML) {
                $resultsWrapper.before(`
                <div id="resultsTabs" class="flex gap-4 border-b border-gray-200 mb-4">
                    ${tabsHTML}
                </div>
                <div id="resultsContent" class="space-y-4"></div>
            `);

                const firstSection = Object.keys(sectionsData).find(k => sectionsData[k].length > 0);
                renderSection(firstSection, sectionsData[firstSection]);

                // Tab click handler
                $(".tab-btn").on("click", function () {
                    $(".tab-btn").removeClass("border-b-2 border-purple-600 font-semibold").addClass("text-gray-500");
                    $(this).removeClass("text-gray-500").addClass("border-b-2 border-purple-600 font-semibold");
                    const section = $(this).data("section");
                    renderSection(section, sectionsData[section]);
                });
            } else {
                $resultsWrapper.html(`<p class="text-gray-500 text-center py-6">No results found</p>`);
            }

        } catch (err) {
            console.error(err);
            Swal.fire("Error", "Failed to fetch search results", "error");
        } finally {
            isLoading = false;
            $loader.addClass("hidden");
        }
    }

    // ----------------------------
    // Events
    // ----------------------------
    $("#searchBtn").on("click", function () {
        performSearch(true);
    });

    // Enter key support for keyword input
    $("#searchInput").on("keypress", function (e) {
        if (e.which === 13) $("#searchBtn").click();
    });
});


// // search.js

