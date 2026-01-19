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
    $header.after(`
        <section id="searchSection" class="p-4 bg-white border-b border-purple-100 sticky top-[72px] z-10">
            <div class="flex flex-col md:flex-row gap-2">
                <!-- Keyword -->
                <input id="searchInput" type="text"
                    placeholder="Search publishers, firms, articles..."
                    class="flex-1 px-4 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500">

                <!-- Tags -->
                <input id="tagsInput" type="text"
                    placeholder="Tags (comma separated)"
                    class="flex-1 px-4 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500">

                <!-- Categories -->
                <input id="categoriesInput" type="text"
                    placeholder="Categories (comma separated)"
                    class="flex-1 px-4 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500">

                <!-- Hot Topic -->
                <label class="flex items-center space-x-2">
                    <input id="hotTopicInput" type="checkbox" class="rounded border-gray-300">
                    <span class="text-gray-700 text-sm">Hot Topic</span>
                </label>

                <!-- Search Button -->
                <button id="searchBtn"
                    class="px-5 py-3 rounded-full bg-purple-600 text-white font-semibold hover:bg-purple-700 transition">
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
                    <a href="profile.html?firm_id=${f.id}" target="_blank"
                       class="p-4 bg-blue-50 rounded-xl shadow-sm block">
                        <p class="font-semibold">${f.firm_name}</p>
                        <p class="text-xs text-gray-500 mt-1">${f.articles_count} articles</p>
                    </a>
                `).join('')}
            </div>`;
        } else { // quick_take or coverage
            html = `<div class="space-y-3">
                ${data.map(a => `
                    <a href="article.html?id=${a.id}&type=${section}" target="_blank"
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
            search_text: searchText || undefined,
            tags: tags.length ? tags : undefined,
            categories: categories.length ? categories : undefined,
            hot_topic: hotTopic,
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



// $(document).ready(function () {
//     // Protect page
//     if (!getAccessToken()) {
//         redirectToLogin();
//         return;
//     }

//     const $main = $("main");
//     const $header = $main.find("header");

//     // Inject search UI BELOW header
//     $header.after(`
//         <section id="searchSection" class="p-4 bg-white border-b border-purple-100 sticky top-[72px] z-10">
//             <div class="flex gap-2">
//                 <input id="searchInput" type="text"
//                     placeholder="Search publishers, firms, articles..."
//                     class="flex-1 px-4 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500">
//                 <button id="searchBtn"
//                     class="px-5 py-3 rounded-full bg-purple-600 text-white font-semibold hover:bg-purple-700 transition">
//                     Search
//                 </button>
//             </div>
//         </section>

//         <section id="resultsWrapper" class="p-4 space-y-8"></section>

//         <div id="loader" class="hidden flex justify-center py-6">
//             <div class="loader"></div>
//         </div>
//     `);

//     const $resultsWrapper = $("#resultsWrapper");
//     const $loader = $("#loader");

//     let currentPage = 1;
//     const pageSize = 10;
//     let currentQuery = "";
//     let isLoading = false;

//     // ----------------------------
//     // Render Helpers
//     // ----------------------------
//     function section(title, content) {
//         if (!content || content.length === 0) return "";
//         return `
//             <div>
//                 <h3 class="text-lg font-bold mb-3">${title}</h3>
//                 ${content}
//             </div>
//         `;
//     }

//     function publisherCard(p) {
//         return `
//             <div class="p-4 bg-purple-50 rounded-xl shadow-sm">
//                 <p class="font-semibold">${p.first_name ?? ""} ${p.last_name ?? ""}</p>
//                 <p class="text-sm text-gray-500">@${p.username}</p>
//                 <p class="text-xs text-gray-400 mt-1">${p.articles_count} articles</p>
//             </div>
//         `;
//     }

//     function firmCard(f) {
//         return `
//             <div class="p-4 bg-blue-50 rounded-xl shadow-sm">
//                 <p class="font-semibold">${f.firm_name}</p>
//                 <p class="text-xs text-gray-500 mt-1">${f.articles_count} articles</p>
//             </div>
//         `;
//     }

//     function articleCard(a) {
//         return `
//             <div class="p-4 bg-white rounded-xl shadow hover:shadow-md transition">
//                 <h4 class="font-semibold text-gray-800 truncate">${a.title}</h4>
//                 <p class="text-xs text-gray-500 mt-1">
//                     ${a.publisher.first_name ?? ""} ${a.publisher.last_name ?? ""} · ${a.firm.firm_name}
//                 </p>
//             </div>
//         `;
//     }

//     // ----------------------------
//     // API Call
//     // ----------------------------
//     async function performSearch(reset = true) {
//         if (isLoading || !currentQuery) return;
//         isLoading = true;
//         $loader.removeClass("hidden");

//         if (reset) {
//             currentPage = 1;
//             $resultsWrapper.empty();
//         }

//         try {
//             const response = await ajaxWithJWT({
//                 url: "http://127.0.0.1:5000/api/article/search",
//                 method: "POST",
//                 contentType: "application/json",
//                 data: JSON.stringify({
//                     search_text: currentQuery,
//                     page: currentPage,
//                     page_size: pageSize
//                 })
//             });

//             // Build sections
//             const publishersHTML = response.publishers
//                 .map(publisherCard)
//                 .join("");

//             const firmsHTML = response.firms
//                 .map(firmCard)
//                 .join("");

//             const quickTakeHTML = response.quick_take
//                 .map(articleCard)
//                 .join("");

//             const coverageHTML = response.coverage
//                 .map(articleCard)
//                 .join("");

//             $resultsWrapper.append(`
//                 ${section("Publishers", `<div class="grid grid-cols-2 md:grid-cols-3 gap-4">${publishersHTML}</div>`)}
//                 ${section("Firms", `<div class="grid grid-cols-2 md:grid-cols-3 gap-4">${firmsHTML}</div>`)}
//                 ${section("QuickTake", `<div class="space-y-3">${quickTakeHTML}</div>`)}
//                 ${section("Coverage", `<div class="space-y-3">${coverageHTML}</div>`)}
//             `);

//             currentPage++;

//         } catch (err) {
//             console.error(err);
//             Swal.fire("Error", "Failed to fetch search results", "error");
//         } finally {
//             isLoading = false;
//             $loader.addClass("hidden");
//         }
//     }

//     // ----------------------------
//     // Events
//     // ----------------------------
//     $("#searchBtn").on("click", function () {
//         currentQuery = $("#searchInput").val().trim();
//         if (currentQuery) performSearch(true);
//     });

//     // Enter key support
//     $("#searchInput").on("keypress", function (e) {
//         if (e.which === 13) {
//             $("#searchBtn").click();
//         }
//     });

// });









// // search.js
// $(document).ready(function () {
//     // Redirect if not logged in
//     if (!getAccessToken()) redirectToLogin();

//     const $main = $("main");
//     const $header = $main.find("header");

//     // Add search input and button just below header
//     $header.after(`
//         <div class="p-4 bg-white sticky top-[70px] z-10 flex gap-2">
//             <input type="text" id="searchInput" placeholder="Search articles..." 
//                 class="flex-1 p-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-500">
//             <button id="searchBtn" class="px-4 py-3 bg-purple-600 text-white rounded-full hover:bg-purple-700 transition">Search</button>
//         </div>
//         <div class="results-container grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 p-4"></div>
//         <div id="loader" class="flex justify-center py-4 hidden">
//             <div class="loader"></div>
//         </div>
//     `);

//     const $resultsContainer = $(".results-container");
//     const $loader = $("#loader");

//     let page = 1;
//     const limit = 10;
//     let keyword = "";
//     let loading = false;
//     let totalPages = 1;

//     // Fetch articles from API
//     async function fetchResults(reset = false) {
//         if (loading || page > totalPages) return;
//         loading = true;
//         $loader.show();

//         try {
//             const data = { page, limit, keyword, tags: [], publisher: "", firm: "" };

//             const res = await ajaxWithJWT({
//                 url: "http://127.0.0.1:5000/api/article/search",
//                 method: "POST",
//                 contentType: "application/json",
//                 data: JSON.stringify(data)
//             });

//             if (res && res.results) {
//                 totalPages = Math.ceil(res.total / limit);

//                 if (reset) $resultsContainer.empty();

//                 res.results.forEach(article => {
//                     const $card = $(`
//                         <div class="bg-white rounded-lg shadow hover:shadow-md transition cursor-pointer p-4 flex flex-col justify-between">
//                             <h3 class="font-semibold text-gray-800 text-lg truncate">${article.title}</h3>
//                             <p class="text-gray-500 text-sm mt-1">Publisher: ${article.publisher?.first_name || 'Unknown'}</p>
//                         </div>
//                     `);
//                     $resultsContainer.append($card);
//                 });

//                 page++;
//             }

//         } catch (err) {
//             console.error("Error fetching articles:", err);
//             Swal.fire({
//                 icon: 'error',
//                 title: 'Oops...',
//                 text: 'Failed to load articles!'
//             });
//         } finally {
//             loading = false;
//             $loader.hide();
//         }
//     }

//     // Trigger search on button click
//     $("#searchBtn").on("click", function () {
//         keyword = $("#searchInput").val().trim();
//         page = 1;
//         if (keyword) {
//             fetchResults(true);
//         } else {
//             $resultsContainer.empty();
//         }
//     });

//     // Infinite scroll
//     $(window).on("scroll", function () {
//         if ($(window).scrollTop() + $(window).height() >= $(document).height() - 200) {
//             fetchResults();
//         }
//     });
// });





// // search.js

// $(document).ready(function () {
//     // JWT-protected page
//     if (!getAccessToken()) {
//         redirectToLogin();
//         return;
//     }

//     // Add search input and results container dynamically
//     const $main = $("main");
//     $main.prepend(`
//         <div class="p-6 bg-white sticky top-0 z-10">
//             <input type="text" id="searchInput" placeholder="Search articles..." 
//                 class="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500">
//         </div>
//         <div class="results-container p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
//         <div id="loader" class="flex justify-center py-4 hidden">
//             <div class="loader"></div>
//         </div>
//     `);

//     const $resultsContainer = $(".results-container");
//     const $loader = $("#loader");
//     let page = 1;
//     const limit = 10;
//     let keyword = "";
//     let loading = false;
//     let totalPages = 1;

//     // Function to fetch results from API
//     async function fetchResults(reset = false) {
//         if (loading || page > totalPages) return;
//         loading = true;
//         $loader.show();

//         try {
//             const requestData = {
//                 page,
//                 limit,
//                 keyword,
//                 tags: [],
//                 publisher: "",
//                 firm: ""
//             };

//             // Trigger API with JWT
//             const res = await ajaxWithJWT({
//                 url: "http://127.0.0.1:5000/api/article/search",
//                 method: "POST",
//                 contentType: "application/json",
//                 data: JSON.stringify(requestData)
//             });

//             if (res && res.results) {
//                 totalPages = Math.ceil(res.total / limit);

//                 if (reset) $resultsContainer.empty();

//                 res.results.forEach(article => {
//                     // Render only title
//                     const $card = $(`
//                         <div class="p-4 bg-purple-50 rounded-lg shadow hover:shadow-md transition cursor-pointer">
//                             <h3 class="font-bold text-purple-700 text-lg truncate">${article.title}</h3>
//                             <p class="text-gray-500 text-sm mt-1">Publisher: ${article.publisher?.first_name || 'Unknown'}</p>
//                         </div>
//                     `);
//                     $resultsContainer.append($card);
//                 });

//                 page++;
//             }

//         } catch (err) {
//             console.error("Error fetching articles:", err);
//             Swal.fire({
//                 icon: 'error',
//                 title: 'Oops...',
//                 text: 'Failed to load articles!'
//             });
//         } finally {
//             loading = false;
//             $loader.hide();
//         }
//     }

//     // **Trigger API immediately on page load**
//     fetchResults(true);

//     // Search input handler with debounce
//     let debounceTimer;
//     $("#searchInput").on("input", function () {
//         clearTimeout(debounceTimer);
//         keyword = $(this).val().trim();
//         page = 1;
//         debounceTimer = setTimeout(() => {
//             fetchResults(true); // reset results when searching
//         }, 500);
//     });

//     // Infinite scroll
//     $(window).on("scroll", function () {
//         if ($(window).scrollTop() + $(window).height() >= $(document).height() - 200) {
//             fetchResults();
//         }
//     });
// });








// // scripts/search.js
// $(document).ready(function () {
//     lucide.createIcons();

//     const API_BASE = "http://127.0.0.1:5000/api";
//     let page = 1;
//     const limit = 10;
//     let keyword = "";
//     let isLoading = false;

//     // Check JWT
//     function getAccessToken() {
//         return localStorage.getItem("access_token");
//     }

//     function getRefreshToken() {
//         return localStorage.getItem("refresh_token");
//     }

//     function redirectToLogin() {
//         window.location.href = "login.html";
//     }

//     function refreshToken(callback) {
//         const refreshToken = getRefreshToken();
//         if (!refreshToken) redirectToLogin();

//         $.ajax({
//             url: `${API_BASE}/token/refresh`,
//             method: "POST",
//             contentType: "application/json",
//             data: JSON.stringify({ refresh_token: refreshToken }),
//             success: function (res) {
//                 localStorage.setItem("access_token", res.data.access_token);
//                 localStorage.setItem("refresh_token", res.data.refresh_token);
//                 callback();
//             },
//             error: function () {
//                 redirectToLogin();
//             }
//         });
//     }

//     function ajaxWithAuth(settings) {
//         const token = getAccessToken();
//         settings.headers = { Authorization: `Bearer ${token}` };
//         settings.error = function (xhr) {
//             if (xhr.status === 401) {
//                 // Try refreshing token
//                 refreshToken(() => $.ajax(settings));
//             } else {
//                 console.error(xhr);
//                 alert("Error fetching data.");
//             }
//         };
//         $.ajax(settings);
//     }

//     function renderArticleCard(article) {
//         return `
//         <div class="bg-white rounded-2xl shadow-md p-4 border border-gray-100 hover:shadow-lg transition-all">
//             <h4 class="font-bold text-lg text-purple-700 mb-2">${article.title}</h4>
//             <p class="text-gray-700 text-sm mb-2">${article.summary || article.content.slice(0, 150)}...</p>
//             <p class="text-gray-500 text-xs">Publisher: ${article.publisher?.first_name || ""} ${article.publisher?.last_name || ""}</p>
//             <p class="text-gray-500 text-xs">Firm: ${article.firm?.firm_name || ""}</p>
//             <p class="text-gray-500 text-xs">Published: ${new Date(article.published_at).toLocaleDateString()}</p>
//         </div>`;
//     }

//     function displayResults(dataArray) {
//         if (!dataArray || dataArray.length === 0) return;

//         // Clear sections on new search
//         if (page === 1) {
//             $(".search-section").addClass("hidden");
//             $("#publishers-results").empty();
//             $("#firms-results").empty();
//             $("#coverage-results").empty();
//             $("#quicktake-results").empty();
//         }

//         const publishers = dataArray.filter(a => a.publisher);
//         const firms = dataArray.filter(a => a.firm);
//         const coverage = dataArray.filter(a => a.categories && a.categories.length);
//         const quicktake = dataArray.filter(a => a.hot_topic);

//         if (publishers.length) {
//             $("#publishers-section").removeClass("hidden");
//             publishers.forEach(a => $("#publishers-results").append(renderArticleCard(a)));
//         }

//         if (firms.length) {
//             $("#firms-section").removeClass("hidden");
//             firms.forEach(a => $("#firms-results").append(renderArticleCard(a)));
//         }

//         if (coverage.length) {
//             $("#coverage-section").removeClass("hidden");
//             coverage.forEach(a => $("#coverage-results").append(renderArticleCard(a)));
//         }

//         if (quicktake.length) {
//             $("#quicktake-section").removeClass("hidden");
//             quicktake.forEach(a => $("#quicktake-results").append(renderArticleCard(a)));
//         }
//     }



//     // function displayResults(data) {
//     //     // Clear sections on new search
//     //     if (page === 1) {
//     //         $(".search-section").addClass("hidden");
//     //         $("#publishers-results").empty();
//     //         $("#firms-results").empty();
//     //         $("#coverage-results").empty();
//     //         $("#quicktake-results").empty();
//     //     }

//     //     if (data.publishers && data.publishers.length > 0) {
//     //         $("#publishers-section").removeClass("hidden");
//     //         data.publishers.forEach(a => $("#publishers-results").append(renderArticleCard(a)));
//     //     }

//     //     if (data.firms && data.firms.length > 0) {
//     //         $("#firms-section").removeClass("hidden");
//     //         data.firms.forEach(a => $("#firms-results").append(renderArticleCard(a)));
//     //     }

//     //     if (data.coverage && data.coverage.length > 0) {
//     //         $("#coverage-section").removeClass("hidden");
//     //         data.coverage.forEach(a => $("#coverage-results").append(renderArticleCard(a)));
//     //     }

//     //     if (data.quicktake && data.quicktake.length > 0) {
//     //         $("#quicktake-section").removeClass("hidden");
//     //         data.quicktake.forEach(a => $("#quicktake-results").append(renderArticleCard(a)));
//     //     }
//     // }

//     function fetchSearchResults(reset = false) {
//         if (isLoading) return;
//         isLoading = true;
//         $("#loading-spinner").show();

//         if (reset) page = 1;

//         const payload = {
//             page,
//             limit,
//             keyword: $("#search-input").val().trim(),
//             tags: [],
//             publisher: "",
//             firm: ""
//         };

//         ajaxWithAuth({
//             url: `${API_BASE}/article/search`,
//             method: "POST",
//             contentType: "application/json",
//             data: JSON.stringify(payload),
//             success: function (res) {
//                 displayResults(res.data);
//                 page++;
//                 isLoading = false;
//                 $("#loading-spinner").hide();
//             }
//         });
//     }

//     // Search button click
//     $("#search-btn").click(function () {
//         page = 1;
//         fetchSearchResults(true);
//     });

//     // Enter key triggers search
//     $("#search-input").keypress(function (e) {
//         if (e.which === 13) {
//             page = 1;
//             fetchSearchResults(true);
//         }
//     });

//     // Infinite scroll
//     $(".content-scroll").scroll(function () {
//         const scrollContainer = $(this);
//         if (scrollContainer.scrollTop() + scrollContainer.innerHeight() >= scrollContainer[0].scrollHeight - 50) {
//             fetchSearchResults();
//         }
//     });
// });
