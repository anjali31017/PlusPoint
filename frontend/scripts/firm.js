async function requestDelete(type, id) {
    const endpointMap = {
        article: {
            url: `http://127.0.0.1:5000/api/user/delete/request?article_id=${id}`,
            label: "Article"
        },
        firm: {
            url: `http://127.0.0.1:5000/api/user/delete/request?firm_id=${id}`,
            label: "Firm"
        }
    };

    const config = endpointMap[type];
    if (!config) throw new Error("Invalid delete type");

    const { value: reason } = await Swal.fire({
        title: `Request ${config.label} Deletion`,
        input: "textarea",
        inputPlaceholder: "Reason for deletion",
        showCancelButton: true,
        confirmButtonText: "Submit",
        preConfirm: (val) => {
            if (!val || !val.trim()) Swal.showValidationMessage("Please enter a reason");
            return val?.trim();
        }
    });

    if (!reason) return;

    try {
        const payload = type === "article" ? JSON.stringify({ reason }) : undefined;

        const res = await ajaxWithJWT({
            url: config.url,
            method: "POST",
            contentType: "application/json",
            data: payload
        });

        Swal.fire({
            icon: "success",
            title: "Request Submitted",
            text: res.message || "Deletion request submitted",
            timer: 1500,
            showConfirmButton: false
        });

    } catch (err) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: err.responseJSON?.detail || "Deletion request already exists"
        });
    }
}

function initDeleteRequest($button, type, id) {
    $button.off("click").on("click", function (e) {
        e.stopPropagation();
        requestDelete(type, id);
    });
}

$(document).ready(async function () {
    const loggedIn = await isLoggedIn();
    if (!loggedIn) return;

    const urlParams = new URLSearchParams(window.location.search);
    const firm_id = urlParams.get("firm_id");
    if (!firm_id) {
        Swal.fire("Error", "No firm selected.", "error");
        return;
    }

    let currentPage = 1, hasMore = true, isSelf = false;
    const $container = $(".max-w-6xl");

    $container.append(`
        <div id="firm-info" class="mb-8"></div>
        <div class="flex justify-end mb-4" id="firm-actions"></div>
        <div id="articles-list" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4"></div>
        <div id="loading-spinner" class="text-center py-4 hidden">
            <i data-lucide="loader" class="w-8 h-8 animate-spin text-purple-600"></i>
        </div>
        <div id="no-articles" class="text-center py-8 text-gray-500 hidden">No articles found</div>
    `);

    async function fetchFirm() {
        if (!hasMore) return;
        $("#loading-spinner").show();
        try {
            const res = await ajaxWithJWT({
                url: `http://127.0.0.1:5000/api/firm/details?firm_id=${firm_id}&page=${currentPage}&page_size=5`,
                method: "GET"
            });

            if (res.status !== 1) {
                Swal.fire("Error", res.message || "Failed to fetch firm.", "error");
                return;
            }

            const firm = res.data;
            isSelf = firm.is_self;

            if (currentPage === 1) {
                renderFirmInfo(firm);
                renderFirmActions(firm);
            }

            renderArticles(firm.articles);
            currentPage++;

            if (!firm.articles || firm.articles.length < 5) hasMore = false;

            if (!firm.articles || (currentPage === 2 && firm.articles.length === 0)) {
                $("#no-articles").show();
            } else {
                $("#no-articles").hide();
            }

        } catch (err) {
            console.error(err);
            Swal.fire("Error", "Something went wrong.", "error");
        } finally {
            $("#loading-spinner").hide();
        }
    }

    function renderFirmInfo(firm) {
        const $firmDiv = $("#firm-info");
        $firmDiv.empty();

        const badge = firm.is_verified
            ? `<span class="badge bg-purple-600 text-white px-2 py-1 rounded ml-2 text-xs">VERIFIED</span>`
            : '';

        const ownerLink = firm.owner
            ? `<a href="profile.html?user_id=${firm.owner.id}" class="text-purple-600 font-medium hover:underline">${firm.owner.display_name || firm.owner.username}</a>`
            : "Unknown";

        $firmDiv.append(`
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center">
                <div class="mb-4 sm:mb-0">
                    <h1 class="text-3xl font-bold">${firm.firm_name} ${badge}</h1>
                    <p class="text-gray-500">@${firm.firm_username}</p>
                    <p class="mt-2">${firm.bio || ''}</p>
                    <div class="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
                        <span>Trust Factor: <strong>${Number(firm.trust_factor).toFixed(2)}</strong></span>
                        <span>Followers: <strong>${firm.follow_count ?? 0}</strong></span>
                        <span>Owner: ${ownerLink}</span>
                    </div> 
                </div>
            </div>
        `);
    }

    function renderFirmActions(firm) {
        const $actions = $("#firm-actions");
        $actions.empty();

        const accessToken = localStorage.getItem("access_token");
        let currentUserStatus = false;
        if (accessToken) {
            try {
                const payload = JSON.parse(atob(accessToken.split(".")[1]));
                currentUserStatus = payload.status === true;
            } catch (e) { currentUserStatus = false; }
        }

        if (isSelf) {
            const $createBtn = $('<button class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">Create Article</button>')
                .click(() => window.open(`createArticle.html?firm_id=${firm.id}`));

            const $deleteBtn = $('<button class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">Delete Account</button>')
                .click(() => requestDelete('firm', firm.id));

            $actions.append($createBtn, $deleteBtn);
        } else {
            const $followBtn = $(`<button class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition-all">${firm.following ? 'Following' : 'Follow'}</button>`);
            $actions.append($followBtn);

            $followBtn.click(async () => {
                try {
                    const res = await ajaxWithJWT({
                        url: `http://127.0.0.1:5000/api/firm/follow?firm_id=${firm.id}`,
                        method: "POST"
                    });
                    $followBtn.text(res.data.status === "followed" ? "Following" : "Follow");
                } catch (err) {
                    Swal.fire("Error", "Failed to follow.", "error");
                }
            });

            if (currentUserStatus) {
                const $endorseBtn = $(`<button class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-all ml-2">${firm.endorsed ? 'You Endorsed' : 'Give Endorsement'}</button>`);
                $actions.append($endorseBtn);
                initEndorseButton($endorseBtn, 'firm', firm.id);
            }

            const $reportBtn = $('<button class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-all ml-2">Report Firm</button>');
            $actions.append($reportBtn);
            initReportButton($reportBtn, 'firm', firm.id);
        }
    }

    function renderArticles(articles) {
        const $list = $("#articles-list");
        if (!articles || articles.length === 0) return;

        const accessToken = localStorage.getItem("access_token");
        let currentUserId = null;
        if (accessToken) {
            try {
                currentUserId = JSON.parse(atob(accessToken.split(".")[1])).user_id;
            } catch (e) { }
        }

        $(document).off("click.articleDropdown").on("click.articleDropdown", () => {
            $(".dropdown-menu").hide();
        });

        articles.forEach(article => {
            const isAuthor = currentUserId === String(article.publisher?.id);

            const $card = $(`
            <div class="card bg-white rounded-lg border border-purple-200 shadow-sm overflow-hidden relative group">
                <div class="p-4 cursor-pointer" data-article-id="${article.id}">
                    <h3 class="font-bold text-lg">${article.title}</h3>
                    <p class="text-gray-500 mt-1">${truncateWords(article.summary || article.content_text, 20)}</p>
                    <div class="flex flex-wrap gap-2 mt-2 text-xs text-gray-400">
                        ${article.category.map(c => `<span class="bg-purple-100 px-2 py-1 rounded">${c}</span>`).join('')}
                        ${article.tags.map(t => `<span class="bg-blue-100 px-2 py-1 rounded">#${t}</span>`).join('')}
                    </div>
                </div>
                <div class="absolute top-2 right-2">
                    <div class="relative inline-block text-left">
                        <button class="dropdown-btn p-1 text-gray-400 hover:text-gray-600" type="button">
                            <i data-lucide="more-vertical" class="w-5 h-5"></i>
                        </button>
                        <div class="dropdown-menu hidden origin-top-right absolute right-0 mt-2 w-44 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
                            <div class="py-1 text-sm text-gray-700">
                                ${!isAuthor ? `<button class="w-full text-left px-4 py-2 hover:bg-gray-100 article-report">Report</button>` : ''}
                                ${isAuthor ? `<button class="w-full text-left px-4 py-2 hover:bg-gray-100 article-del">Request Delete</button>` : ''}
                                <button class="w-full text-left px-4 py-2 hover:bg-gray-100 article-copy">Copy Link</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            `);

            $card.find(".dropdown-btn").click(e => {
                e.stopPropagation();
                $(e.currentTarget).siblings(".dropdown-menu").toggle();
            });

            $card.find(".p-4").click(() => window.open(`article.html?article_id=${article.id}`));

            const $reportBtn = $card.find(".article-report");
            if ($reportBtn.length) {
                initReportButton($reportBtn, 'article', article.id);
                $reportBtn.click(e => { e.stopPropagation(); $card.find(".dropdown-menu").hide(); });
            }

            const $deleteBtn = $card.find(".article-del");
            if ($deleteBtn.length) {
                initDeleteRequest($deleteBtn, 'article', article.id);
                $deleteBtn.click(e => { e.stopPropagation(); $card.find(".dropdown-menu").hide(); });
            }

            $card.find(".article-copy").click(e => {
                e.stopPropagation();
                navigator.clipboard.writeText(`${window.location.origin}/src/article.html?article_id=${article.id}`);
                $card.find(".dropdown-menu").hide();
            });

            $list.append($card);
        });

        lucide.createIcons();
    }

    // --- Infinite scroll ---
    $(window).on("scroll", () => {
        if (!hasMore) return;
        const scrollBottom = $(window).scrollTop() + $(window).height();
        const docHeight = $(document).height();
        if (scrollBottom + 100 >= docHeight) { // 100px from bottom
            fetchFirm();
        }
    });

    fetchFirm();
});















// async function requestDelete(type, id) {
//     const endpointMap = {
//         article: {
//             url: `http://127.0.0.1:5000/api/user/delete/request?article_id=${id}`,
//             label: "Article"
//         },
//         firm: {
//             url: `http://127.0.0.1:5000/api/user/delete/request?firm_id=${id}`,
//             label: "Firm"
//         }
//     };

//     const config = endpointMap[type];
//     if (!config) throw new Error("Invalid delete type");

//     const { value: reason } = await Swal.fire({
//         title: `Request ${config.label} Deletion`,
//         input: "textarea",
//         inputPlaceholder: "Reason for deletion",
//         showCancelButton: true,
//         confirmButtonText: "Submit",
//         preConfirm: (val) => {
//             if (!val || !val.trim()) Swal.showValidationMessage("Please enter a reason");
//             return val?.trim();
//         }
//     });

//     if (!reason) return;

//     try {
//         const payload = type === "article" ? JSON.stringify({ reason }) : undefined;

//         const res = await ajaxWithJWT({
//             url: config.url,
//             method: "POST",
//             contentType: "application/json",
//             data: payload
//         });

//         Swal.fire({
//             icon: "success",
//             title: "Request Submitted",
//             text: res.message || "Deletion request submitted",
//             timer: 1500,
//             showConfirmButton: false
//         });

//     } catch (err) {
//         Swal.fire({
//             icon: "error",
//             title: "Error",
//             text: err.responseJSON?.detail || "Deletion request already exists"
//         });
//     }
// }

// function initDeleteRequest($button, type, id) {
//     $button.off("click").on("click", function (e) {
//         e.stopPropagation();
//         requestDelete(type, id);
//     });
// }

// $(document).ready(async function () {
//     // Ensure user is logged in
//     const loggedIn = await isLoggedIn();
//     if (!loggedIn) return;

//     const urlParams = new URLSearchParams(window.location.search);
//     const firm_id = urlParams.get("firm_id");
//     if (!firm_id) {
//         Swal.fire("Error", "No firm selected.", "error");
//         return;
//     }

//     let currentPage = 1, hasMore = true, isSelf = false;
//     const $container = $(".max-w-6xl");

//     $container.append(`
//         <div id="firm-info" class="mb-8"></div>
//         <div class="flex justify-end mb-4" id="firm-actions"></div>
//         <div id="articles-list" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4"></div>
//         <div id="loading-spinner" class="text-center py-4 hidden">
//             <i data-lucide="loader" class="w-8 h-8 animate-spin text-purple-600"></i>
//         </div>
//         <div id="no-articles" class="text-center py-8 text-gray-500 hidden">No articles found</div>
//     `);

//     async function fetchFirm() {
//         if (!hasMore) return;
//         $("#loading-spinner").show();
//         try {
//             const res = await ajaxWithJWT({
//                 url: `http://127.0.0.1:5000/api/firm/details?firm_id=${firm_id}&page=${currentPage}&page_size=5`,
//                 method: "GET"
//             });

//             if (res.status !== 1) {
//                 Swal.fire("Error", res.message || "Failed to fetch firm.", "error");
//                 return;
//             }

//             const firm = res.data;
//             isSelf = firm.is_self;

//             renderFirmInfo(firm);
//             renderFirmActions(firm);
//             renderArticles(firm.articles);
//             currentPage++;

//             if (!firm.articles || firm.articles.length === 0 && currentPage === 2) {
//                 $("#no-articles").show();
//             } else {
//                 $("#no-articles").hide();
//             }

//             if (!firm.articles || firm.articles.length < 5) hasMore = false;

//         } catch (err) {
//             console.error(err);
//             Swal.fire("Error", "Something went wrong.", "error");
//         } finally {
//             $("#loading-spinner").hide();
//         }
//     }

//     function renderFirmInfo(firm) {
//         const $firmDiv = $("#firm-info");
//         $firmDiv.empty();

//         const badge = firm.is_verified
//             ? `<span class="badge bg-purple-600 text-white px-2 py-1 rounded ml-2 text-xs">VERIFIED</span>`
//             : '';

//         const ownerLink = firm.owner
//             ? `<a href="profile.html?user_id=${firm.owner.id}" class="text-purple-600 font-medium hover:underline">${firm.owner.display_name || firm.owner.username}</a>`
//             : "Unknown";

//         $firmDiv.append(`
//             <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center">
//                 <div class="mb-4 sm:mb-0">
//                     <h1 class="text-3xl font-bold">${firm.firm_name} ${badge}</h1>
//                     <p class="text-gray-500">@${firm.firm_username}</p>
//                     <p class="mt-2">${firm.bio || ''}</p>
//                     <div class="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
//                         <span>Trust Factor: <strong>${firm.trust_factor}</strong></span>
//                         <span>Followers: <strong>${firm.follow_count ?? 0}</strong></span>
//                         <span>Owner: ${ownerLink}</span>
//                     </div> 
//                 </div>
//             </div>
//         `);
//     }

//     function renderFirmActions(firm) {
//         const $actions = $("#firm-actions");
//         $actions.empty();

//         const accessToken = localStorage.getItem("access_token");
//         let currentUserStatus = false;
//         if (accessToken) {
//             try {
//                 const payload = JSON.parse(atob(accessToken.split(".")[1]));
//                 currentUserStatus = payload.status === true;
//             } catch (e) { currentUserStatus = false; }
//         }

//         if (isSelf) {
//             // const $createBtn = $('<button class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">Create Article</button>')
//             //     .click(() => window.location.href = `createArticle.html?firm_id=${firm.id}`);
//            const $createBtn = $('<button class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">Create Article</button>')
//     .click(() => window.location.href = `createArticle.html?firm_id=${firm.id}`);

//             const $deleteBtn = $('<button class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">Delete Account</button>')
//                 .click(() => requestDelete('firm', firm.id));

//             $actions.append($createBtn, $deleteBtn);
//         } else {
//             const $followBtn = $(`<button class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition-all">${firm.following ? 'Following' : 'Follow'}</button>`);
//             $actions.append($followBtn);

//             $followBtn.click(async () => {
//                 try {
//                     const res = await ajaxWithJWT({
//                         url: `http://127.0.0.1:5000/api/firm/follow?firm_id=${firm.id}`,
//                         method: "POST"
//                     });
//                     $followBtn.text(res.data.status === "followed" ? "Following" : "Follow");
//                 } catch (err) {
//                     Swal.fire("Error", "Failed to follow.", "error");
//                 }
//             });

//             if (currentUserStatus) {
//                 const $endorseBtn = $(`<button class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-all ml-2">${firm.endorsed ? 'You Endorsed' : 'Give Endorsement'}</button>`);
//                 $actions.append($endorseBtn);
//                 initEndorseButton($endorseBtn, 'firm', firm.id);
//             }

//             const $reportBtn = $('<button class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-all ml-2">Report Firm</button>');
//             $actions.append($reportBtn);
//             initReportButton($reportBtn, 'firm', firm.id);
//         }
//     }

//     function renderArticles(articles) {
//         const $list = $("#articles-list");
//         $list.empty();
//         if (!articles || articles.length === 0) return;

//         const accessToken = localStorage.getItem("access_token");
//         let currentUserId = null;
//         if (accessToken) {
//             try {
//                 currentUserId = JSON.parse(atob(accessToken.split(".")[1])).user_id;
//             } catch (e) { }
//         }

//         $(document).off("click.articleDropdown").on("click.articleDropdown", () => {
//             $(".dropdown-menu").hide();
//         });

//         articles.forEach(article => {
//             const isAuthor = currentUserId === String(article.publisher?.id);

//             const $card = $(`
//             <div class="card bg-white rounded-lg border border-purple-200 shadow-sm overflow-hidden relative group">
//                 <div class="p-4 cursor-pointer" data-article-id="${article.id}">
//                     <h3 class="font-bold text-lg">${article.title}</h3>
//                     <p class="text-gray-500 mt-1">${truncateWords(article.summary || article.content_text, 20)}</p>
//                     <div class="flex flex-wrap gap-2 mt-2 text-xs text-gray-400">
//                         ${article.category.map(c => `<span class="bg-purple-100 px-2 py-1 rounded">${c}</span>`).join('')}
//                         ${article.tags.map(t => `<span class="bg-blue-100 px-2 py-1 rounded">#${t}</span>`).join('')}
//                     </div>
//                 </div>
//                 <div class="absolute top-2 right-2">
//                     <div class="relative inline-block text-left">
//                         <button class="dropdown-btn p-1 text-gray-400 hover:text-gray-600" type="button">
//                             <i data-lucide="more-vertical" class="w-5 h-5"></i>
//                         </button>
//                         <div class="dropdown-menu hidden origin-top-right absolute right-0 mt-2 w-44 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
//                             <div class="py-1 text-sm text-gray-700">
//                                 ${!isAuthor ? `<button class="w-full text-left px-4 py-2 hover:bg-gray-100 article-report">Report</button>` : ''}
//                                 ${isAuthor ? `<button class="w-full text-left px-4 py-2 hover:bg-gray-100 article-del">Request Delete</button>` : ''}
//                                 <button class="w-full text-left px-4 py-2 hover:bg-gray-100 article-copy">Copy Link</button>
//                             </div>
//                         </div>
//                     </div>
//                 </div>
//             </div>
//             `);

//             $card.find(".dropdown-btn").click(e => {
//                 e.stopPropagation();
//                 $(e.currentTarget).siblings(".dropdown-menu").toggle();
//             });

//             $card.find(".p-4").click(() => window.location.href = `article.html?article_id=${article.id}`);

//             const $reportBtn = $card.find(".article-report");
//             if ($reportBtn.length) {
//                 initReportButton($reportBtn, 'article', article.id);
//                 $reportBtn.click(e => { e.stopPropagation(); $card.find(".dropdown-menu").hide(); });
//             }

//             const $deleteBtn = $card.find(".article-del");
//             if ($deleteBtn.length) {
//                 initDeleteRequest($deleteBtn, 'article', article.id);
//                 $deleteBtn.click(e => { e.stopPropagation(); $card.find(".dropdown-menu").hide(); });
//             }

//             $card.find(".article-copy").click(e => {
//                 e.stopPropagation();
//                 navigator.clipboard.writeText(`${window.location.origin}/src/article.html?article_id=${article.id}`);
//                 $card.find(".dropdown-menu").hide();
//             });

//             $list.append($card);
//         });

//         lucide.createIcons();
//     }

//     fetchFirm();
// });











// $(document).ready(async function () {
//     // Ensure user is logged in
//     const loggedIn = await isLoggedIn();
//     if (!loggedIn) return;

//     const urlParams = new URLSearchParams(window.location.search);
//     const firm_id = urlParams.get("firm_id");
//     if (!firm_id) {
//         Swal.fire("Error", "No firm selected.", "error");
//         return;
//     }

//     let currentPage = 1, loading = false, hasMore = true, isSelf = false;
//     const $container = $(".max-w-6xl");
//     $container.append(`
//         <div id="firm-info" class="mb-8"></div>
//         <div class="flex justify-end mb-4" id="firm-actions"></div>
//         <div id="articles-list" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4"></div>
//         <div id="loading-spinner" class="text-center py-4 hidden">
//             <i data-lucide="loader" class="w-8 h-8 animate-spin text-purple-600"></i>
//         </div>
//         <div id="no-articles" class="text-center py-8 text-gray-500 hidden">No articles found</div>
//     `);

//     // Fetch firm details
//     async function fetchFirm() {
//         if (!hasMore) return;
//         $("#loading-spinner").show();
//         try {
//             const res = await ajaxWithJWT({
//                 url: `http://127.0.0.1:5000/api/firm/details?firm_id=${firm_id}&page=${currentPage}&page_size=5`,
//                 method: "GET"
//             });

//             if (res.status !== 1) {
//                 Swal.fire("Error", res.message || "Failed to fetch firm.", "error");
//                 return;
//             }

//             const firm = res.data;
//             isSelf = firm.is_self;

//             renderFirmInfo(firm);
//             renderFirmActions(firm);
//             renderArticles(firm.articles);
//             currentPage++;

//             if (!firm.articles || firm.articles.length === 0 && currentPage === 2) {
//                 $("#no-articles").show();
//             } else {
//                 $("#no-articles").hide();
//             }

//             if (!firm.articles || firm.articles.length < 5) hasMore = false;

//         } catch (err) {
//             console.error(err);
//             Swal.fire("Error", "Something went wrong.", "error");
//         } finally {
//             $("#loading-spinner").hide();
//         }
//     }

//     // Render firm info
//     function renderFirmInfo(firm) {
//         const $firmDiv = $("#firm-info");
//         $firmDiv.empty();

//         const badge = firm.is_verified
//             ? `<span class="badge bg-purple-600 text-white px-2 py-1 rounded ml-2 text-xs">VERIFIED</span>`
//             : '';

//         const ownerLink = firm.owner
//             ? `<a href="profile.html?user_id=${firm.owner.id}" class="text-purple-600 font-medium hover:underline">${firm.owner.display_name || firm.owner.username}</a>`
//             : "Unknown";

//         $firmDiv.append(`
//             <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center">
//                 <div class="mb-4 sm:mb-0">
//                     <h1 class="text-3xl font-bold">${firm.firm_name} ${badge}</h1>
//                     <p class="text-gray-500">@${firm.firm_username}</p>
//                     <p class="mt-2">${firm.bio || ''}</p>
//                     <div class="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
//                         <span>Trust Factor: <strong>${firm.trust_factor}</strong></span>
//                         <span>Followers: <strong>${firm.follow_count ?? 0}</strong></span>
//                         <span>Owner: @${ownerLink}</span>
//                     </div> 
//                 </div>
//             </div>
//         `);
//     }

//     // Render firm actions (Follow, Endorse, Report)
//     function renderFirmActions(firm) {
//         const $actions = $("#firm-actions");
//         $actions.empty();

//         const accessToken = localStorage.getItem("access_token");
//         let currentUserStatus = false;
//         if (accessToken) {
//             try {
//                 const payload = JSON.parse(atob(accessToken.split(".")[1]));
//                 currentUserStatus = payload.status === true; // verified or not
//             } catch (e) { currentUserStatus = false; }
//         }

//         if (isSelf) {
//             const $createBtn = $('<button class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">Create Article</button>')
//                 .click(() => window.location.href = `createArticle.html?firm_id=${firm.id}`);
           
//             const $deleteBtn = $('<button class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">Delete Account</button>')
//                 .click(async () => {
//                     await requestDelete('firm', firm.id); // Reuse your existing delete function
//                 });

//             $actions.append($createBtn, $deleteBtn);
//         }
//         else {
//             // Follow button
//             const $followBtn = $(`<button class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition-all">${firm.following ? 'Following' : 'Follow'}</button>`);
//             $actions.append($followBtn);

//             $followBtn.click(async () => {
//                 try {
//                     const res = await ajaxWithJWT({
//                         url: `http://127.0.0.1:5000/api/firm/follow?firm_id=${firm.id}`,
//                         method: "POST"
//                     });
//                     if (res.data.status === "followed") {
//                         $followBtn.text("Following");

//                     } else {
//                         $followBtn.text("Follow");
//                     }
//                     // Swal.fire("Success", res.message, "success");
//                 } catch (err) {
//                     Swal.fire("Error", "Failed to follow.", "error");
//                 }
//             });

//             // Endorsement button for verified users
//             if (currentUserStatus) {
//                 const $endorseBtn = $(`<button class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-all ml-2">${firm.endorsed ? 'You Endorsed' : 'Give Endorsement'}</button>`);
//                 $actions.append($endorseBtn);
//                 initEndorseButton($endorseBtn, 'firm', firm.id);
//             }

//             // Report button
//             const $reportBtn = $('<button class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-all ml-2">Report Firm</button>');
//             $actions.append($reportBtn);
//             initReportButton($reportBtn, 'firm', firm.id);
//         }
//     }


//     function renderArticles(articles) {
//         const $list = $("#articles-list");
//         $list.empty();
//         if (!articles || articles.length === 0) return;

//         const accessToken = localStorage.getItem("access_token");
//         let currentUserId = null;
//         if (accessToken) {
//             try {
//                 currentUserId = JSON.parse(atob(accessToken.split(".")[1])).user_id;
//             } catch (e) { }
//         }

//         // Attach document click handler once for closing all dropdowns
//         $(document).off("click.articleDropdown").on("click.articleDropdown", () => {
//             $(".dropdown-menu").hide();
//         });

//         articles.forEach(article => {
//             const isAuthor = currentUserId === String(article.publisher?.id);

//             const $card = $(`
//             <div class="card bg-white rounded-lg border border-purple-200 shadow-sm overflow-hidden relative group">
//                 <div class="p-4 cursor-pointer" data-article-id="${article.id}">
//                     <h3 class="font-bold text-lg">${article.title}</h3>
//                     <p class="text-gray-500 mt-1">${truncateWords(article.summary || article.content_text, 20)}</p>
//                     <div class="flex flex-wrap gap-2 mt-2 text-xs text-gray-400">
//                         ${article.category.map(c => `<span class="bg-purple-100 px-2 py-1 rounded">${c}</span>`).join('')}
//                         ${article.tags.map(t => `<span class="bg-blue-100 px-2 py-1 rounded">#${t}</span>`).join('')}
//                     </div>
//                 </div>
//                 <div class="absolute top-2 right-2">
//                     <div class="relative inline-block text-left">
//                         <button class="dropdown-btn p-1 text-gray-400 hover:text-gray-600" type="button">
//                             <i data-lucide="more-vertical" class="w-5 h-5"></i>
//                         </button>
//                         <div class="dropdown-menu hidden origin-top-right absolute right-0 mt-2 w-44 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
//                             <div class="py-1 text-sm text-gray-700">
//                                 ${!isAuthor ? `<button class="w-full text-left px-4 py-2 hover:bg-gray-100 article-report">Report</button>` : ''}
//                                 ${isAuthor ? `<button class="w-full text-left px-4 py-2 hover:bg-gray-100 article-del">Request Delete</button>` : ''}
//                                 <button class="w-full text-left px-4 py-2 hover:bg-gray-100 article-copy">Copy Link</button>
//                             </div>
//                         </div>
//                     </div>
//                 </div>
//             </div>
//         `);

//             // Open/close dropdown
//             $card.find(".dropdown-btn").click(e => {
//                 e.stopPropagation();
//                 $(e.currentTarget).siblings(".dropdown-menu").toggle();
//             });

//             // Navigate to article page
//             $card.find(".p-4").click(() => window.location.href = `article.html?article_id=${article.id}`);

//             // Article report
//             const $reportBtn = $card.find(".article-report");
//             if ($reportBtn.length) {
//                 initReportButton($reportBtn, 'article', article.id);
//                 $reportBtn.click(e => {
//                     e.stopPropagation();
//                     $card.find(".dropdown-menu").hide();
//                 });
//             }

//             // Article delete
//             const $deleteBtn = $card.find(".article-del");
//             if ($deleteBtn.length) {
//                 initDeleteRequest($deleteBtn, 'article', article.id);
//                 $deleteBtn.click(e => {
//                     e.stopPropagation();
//                     $card.find(".dropdown-menu").hide();
//                 });
//             }

//             // Copy link
//             $card.find(".article-copy").click(e => {
//                 e.stopPropagation();
//                 const link = `${window.location.origin}/src/article.html?article_id=${article.id}`;
//                 navigator.clipboard.writeText(link)

//                 $card.find(".dropdown-menu").hide();
//             });

//             $list.append($card);
//         });

//         lucide.createIcons();
//     }





//     // Infinite scroll
//     $(window).scroll(async function () {
//         if (!hasMore || loading) return;
//         if ($(window).scrollTop() + $(window).height() > $(document).height() - 300) {
//             loading = true;
//             await fetchFirm();
//             loading = false;
//         }
//     });

//     // Initial fetch
//     fetchFirm();
// });








// // $(document).ready(async function () {
// //     // Ensure user is logged in
// //     const loggedIn = await isLoggedIn();
// //     if (!loggedIn) return;

// //     // Get firm_id from URL
// //     const urlParams = new URLSearchParams(window.location.search);
// //     const firm_id = urlParams.get("firm_id");
// //     if (!firm_id) {
// //         Swal.fire("Error", "No firm selected.", "error");
// //         return;
// //     }

// //     // State
// //     let currentPage = 1;
// //     let loading = false;
// //     let hasMore = true;
// //     let isSelf = false;

// //     const $container = $(".max-w-6xl");
// //     $container.append(`
// //         <div id="firm-info" class="mb-8"></div>
// //         <div class="flex justify-end mb-4" id="firm-actions"></div>
// //         <div id="articles-list" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4"></div>
// //         <div id="loading-spinner" class="text-center py-4 hidden">
// //             <i data-lucide="loader" class="w-8 h-8 animate-spin text-purple-600"></i>
// //         </div>
// //         <div id="no-articles" class="text-center py-8 text-gray-500 hidden">No articles found</div>
// //     `);

// //     // Fetch firm details
// //     async function fetchFirm() {
// //         if (!hasMore) return;
// //         $("#loading-spinner").show();
// //         try {
// //             const res = await ajaxWithJWT({
// //                 url: `http://127.0.0.1:5000/api/firm/details?firm_id=${firm_id}&page=${currentPage}&page_size=5`,
// //                 method: "GET"
// //             });

// //             if (res.status !== 1) {
// //                 Swal.fire("Error", res.message || "Failed to fetch firm.", "error");
// //                 return;
// //             }

// //             const firm = res.data;
// //             isSelf = firm.is_self;

// //             renderFirmInfo(firm);    // renders name, trust, owner, verification badge
// //             renderFirmActions(firm); // renders Create Article / Delete Account buttons
// //             renderArticles(firm.articles); // renders articles grid
// //             currentPage++;

// //             if (!firm.articles || firm.articles.length === 0 && currentPage === 2) {
// //                 $("#no-articles").show();
// //             } else {
// //                 $("#no-articles").hide();
// //             }

// //             // Check if there are less than page_size articles → no more
// //             if (!firm.articles || firm.articles.length < 5) hasMore = false;

// //         } catch (err) {
// //             console.error(err);
// //             Swal.fire("Error", "Something went wrong.", "error");
// //         } finally {
// //             $("#loading-spinner").hide();
// //         }
// //     }

// //     // Render firm info
// // function renderFirmInfo(firm) {
// //     const $firmDiv = $("#firm-info");
// //     $firmDiv.empty();

// //     const badge = firm.is_verified
// //         ? `<span class="badge bg-purple-600 text-white px-2 py-1 rounded ml-2 text-xs">VERIFIED</span>`
// //         : '';

// //     const ownerLink = firm.owner
// //         ? `<a href="profile.html?user_id=${firm.owner.id}" class="text-purple-600 font-medium hover:underline">${firm.owner.display_name || firm.owner.username}</a>`
// //         : "Unknown";

// //     $firmDiv.append(`
// //         <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center">
// //             <div class="mb-4 sm:mb-0">
// //                 <h1 class="text-3xl font-bold">${firm.firm_name} ${badge}</h1>
// //                 <p class="text-gray-500">@${firm.firm_username}</p>
// //                 <p class="mt-2">${firm.bio || ''}</p>

// //                 <!-- Stats row -->
// //                 <div class="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
// //                     <span class="flex items-center gap-1">
// //                     <span>Trust Factor: </span>
// //                         <strong class="text-gray-800">${firm.trust_factor}</strong>
// //                     </span>
// //                     <span class="flex items-center gap-1">
// //                     <span>Followers: </span>
// //                         <strong class="text-gray-800">${firm.follow_count ?? 0}</strong>
// //                     </span>
// //                     <span class="flex items-center">
// //                         Owner: @${ownerLink}
// //                     </span>
// //                 </div> 
// //             </div>
// //         </div>
// //     `);



// //         // Firm-level report button for non-self users
// //         const $actions = $("#firm-actions");
// //         $actions.empty();

// //         if (!isSelf) {
// //             $actions.append(`<button id="report-firm-btn" class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-all">Report Firm</button>`);
// //             $("#report-firm-btn").off("click").on("click", function () {
// //                 Swal.fire({
// //                     title: 'Report Firm',
// //                     input: 'textarea',
// //                     inputLabel: 'Reason',
// //                     inputPlaceholder: 'Type your reason here...',
// //                     showCancelButton: true,
// //                     confirmButtonText: 'Report'
// //                 }).then(async (res) => {
// //                     if (res.isConfirmed && res.value.trim() !== "") {
// //                         try {
// //                             await ajaxWithJWT({
// //                                 url: `http://127.0.0.1:5000/api/firm/report`,
// //                                 method: "POST",
// //                                 contentType: "application/json",
// //                                 data: JSON.stringify({ firm_id, reason: res.value })
// //                             });
// //                             Swal.fire("Reported", "Firm has been reported.", "success");
// //                         } catch (err) {
// //                             Swal.fire("Error", "Failed to report firm.", "error");
// //                         }
// //                     }
// //                 });
// //             });
// //         } else {
// //             // Self user: Follow button hidden
// //         }

// //         // Follow button for non-self
// //         if (!isSelf) {
// //             $actions.append(`<button id="follow-btn" class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition-all ml-2">Follow</button>`);
// //             $("#follow-btn").off("click").on("click", async function () {
// //                 try {
// //                     await ajaxWithJWT({
// //                         url: `http://127.0.0.1:5000/api/follow`,
// //                         method: "POST",
// //                         contentType: "application/json",
// //                         data: JSON.stringify({ firm_id })
// //                     });
// //                     Swal.fire("Success", "Followed successfully!", "success");
// //                 } catch (err) {
// //                     Swal.fire("Error", "Failed to follow.", "error");
// //                 }
// //             });
// //         }
// //     }


// //     // function truncateText(text, maxLength = 150) {
// //     //     if (!text) return "";
// //     //     return text.length > maxLength ? text.slice(0, maxLength) + "..." : text;
// //     // }

// //     function truncateWords(text, maxWords = 20) {
// //         if (!text) return "";
// //         const words = text.split(/\s+/);
// //         return words.length > maxWords ? words.slice(0, maxWords).join(" ") + "..." : text;
// //     }

// //     // Render articles



// //     function renderArticles(articles) {
// //         const $list = $("#articles-list");
// //         if (!articles || articles.length === 0) return;

// //         // Decode JWT once for current user
// //         const accessToken = localStorage.getItem("access_token");
// //         let currentUserStatus = false;
// //         let currentUserId = null;
// //         if (accessToken) {
// //             try {
// //                 const payload = JSON.parse(atob(accessToken.split(".")[1]));
// //                 currentUserStatus = payload.status === true;
// //                 currentUserId = payload.user_id;
// //             } catch (e) { }
// //         }

// //         articles.forEach(article => {
// //             const author = article.author || { id: null, display_name: "Unknown", username: "unknown" };
// //             const isAuthor = currentUserId === String(author.id);

// //             const $card = $(`
// //                 <div class="card bg-white rounded-lg border border-purple-200 shadow-sm overflow-hidden relative group">
// //                     <div class="p-4 cursor-pointer" data-article-id="${article.id}">
// //                         <h3 class="font-bold text-lg">${article.title}</h3>
// //                         <p class="text-gray-500 mt-1">${truncateWords(article.summary || article.content_text, 20)}</p>
// //                         <div class="flex flex-wrap gap-2 mt-2 text-xs text-gray-400">
// //                             ${article.category.map(c => `<span class="bg-purple-100 px-2 py-1 rounded">${c}</span>`).join('')}
// //                             ${article.tags.map(t => `<span class="bg-blue-100 px-2 py-1 rounded">#${t}</span>`).join('')}
// //                         </div>
// //                     </div>

// //                     <!-- 3-dot dropdown menu -->
// //                     <div class="absolute top-2 right-2">
// //                         <div class="relative inline-block text-left">
// //                             <button class="dropdown-btn p-1 text-gray-400 hover:text-gray-600" type="button">
// //                                 <i data-lucide="more-vertical" class="w-5 h-5"></i>
// //                             </button>
// //                             <div class="dropdown-menu hidden origin-top-right absolute right-0 mt-2 w-44 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
// //                             <div class="py-1 text-sm text-gray-700">
// //                                 ${!isSelf && currentUserStatus ? `<button class="w-full text-left px-4 py-2 hover:bg-gray-100 article-report">Report</button>` : ''}
// //                                 ${isSelf ? `<button class="w-full text-left px-4 py-2 hover:bg-gray-100 article-del">Request Delete</button>` : ''}
// //                                 <button class="w-full text-left px-4 py-2 hover:bg-gray-100 article-copy">Copy Link</button>
// //                             </div>
// //                         </div>
// //                         </div>
// //                     </div>
// //                 </div>
// //             `);

// //             // Toggle dropdown visibility
// //             $card.find(".dropdown-btn").click(function (e) {
// //                 e.stopPropagation();
// //                 $(this).siblings(".dropdown-menu").toggle();
// //             });

// //             $(document).click(function () {
// //                 $card.find(".dropdown-menu").hide();
// //             });

// //             // Article click redirect
// //             $card.find(".p-4").click(function () {
// //                 const id = $(this).data("article-id");
// //                 window.location.href = `article.html?article_id=${id}`;
// //             });

// //             // Article report
// //             $card.find(".article-report").click(function (e) {
// //                 e.stopPropagation();
// //                 Swal.fire({
// //                     title: 'Report Article',
// //                     html: `
// //                     <select id="report-reason" class="w-full p-2 border rounded mb-2">
// //                         <option value="">Select a reason</option>
// //                         <option value="spam">Spam</option>
// //                         <option value="offensive">Offensive</option>
// //                         <option value="plagiarism">Plagiarism</option>
// //                         <option value="other">Other</option>
// //                     </select>
// //                     <textarea id="report-custom" class="w-full p-2 border rounded mt-2" placeholder="Custom reason" style="display:none"></textarea>
// //                 `,
// //                     showCancelButton: true,
// //                     confirmButtonText: 'Report',
// //                     preConfirm: () => {
// //                         const reason = $("#report-reason").val();
// //                         const custom = $("#report-custom").val();
// //                         if (!reason) Swal.showValidationMessage('Please select a reason');
// //                         return reason === "other" ? custom : reason;
// //                     }
// //                 }).then(async (res) => {
// //                     if (res.isConfirmed && res.value.trim() !== "") {
// //                         try {
// //                             await ajaxWithJWT({
// //                                 url: `http://127.0.0.1:5000/api/article/report`,
// //                                 method: "POST",
// //                                 contentType: "application/json",
// //                                 data: JSON.stringify({ article_id: article.id, reason: res.value })
// //                             });
// //                             Swal.fire("Reported", "Article has been reported.", "success");
// //                         } catch (err) {
// //                             Swal.fire("Error", "Failed to report article.", "error");
// //                         }
// //                     }
// //                 });

// //                 $("#report-reason").change(function () {
// //                     if ($(this).val() === "other") {
// //                         $("#report-custom").show();
// //                     } else {
// //                         $("#report-custom").hide();
// //                     }
// //                 });

// //                 $card.find(".dropdown-menu").hide();
// //             });

// //             // Article delete request (self user)
// //             $card.find(".article-del").click(function (e) {
// //                 e.stopPropagation();
// //                 Swal.fire({
// //                     title: 'Request Article Deletion',
// //                     input: 'textarea',
// //                     inputLabel: 'Reason',
// //                     inputPlaceholder: 'Type your reason here...',
// //                     showCancelButton: true,
// //                     confirmButtonText: 'Submit',
// //                 }).then(async (res) => {
// //                     if (res.isConfirmed && res.value.trim() !== "") {
// //                         try {
// //                             await ajaxWithJWT({
// //                                 url: `http://127.0.0.1:5000/api/article/request-delete`,
// //                                 method: "POST",
// //                                 contentType: "application/json",
// //                                 data: JSON.stringify({ article_id: article.id, reason: res.value })
// //                             });
// //                             Swal.fire("Success", "Delete request submitted!", "success");
// //                         } catch (err) {
// //                             Swal.fire("Error", "Failed to submit request.", "error");
// //                         }
// //                     }
// //                 });
// //                 $card.find(".dropdown-menu").hide();
// //             });

// //             // Copy link
// //             $card.find(".article-copy").click(function (e) {
// //                 e.stopPropagation();
// //                 const link = `${window.location.origin}/article.html?article_id=${article.id}`;
// //                 navigator.clipboard.writeText(link);
// //                 $card.find(".dropdown-menu").hide();
// //             });

// //             // Endorse article author
// //             $card.find(".article-endorse").click(function (e) {
// //                 e.stopPropagation();
// //                 Swal.fire("Endorsement", `You have endorsed ${article.author.display_name || article.author.username}!`, "success");
// //                 // Later: call endorsement API here
// //                 $card.find(".dropdown-menu").hide();
// //             });

// //             $list.append($card);
// //         });

// //         lucide.createIcons();
// //     }






// //     function renderFirmActions(firm) {
// //         const $actions = $("#firm-actions");
// //         $actions.empty();

// //         // Decode JWT to get current user status
// //         const accessToken = localStorage.getItem("access_token");
// //         let currentUserStatus = false;
// //         if (accessToken) {
// //             try {
// //                 const payload = JSON.parse(atob(accessToken.split(".")[1]));
// //                 currentUserStatus = payload.status === true; // verified or not
// //             } catch (e) {
// //                 currentUserStatus = false;
// //             }
// //         }

// //         if (isSelf) {
// //             // Self user: Create Article & Delete Account
// //             const $createBtn = $(`
// //             <button class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
// //                 Create Article
// //             </button>
// //         `).click(() => {
// //                 window.location.href = `createArticle.html?firm_id=${firm.id}`;
// //             });

// //             const $deleteBtn = $(`
// //             <button class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">
// //                 Delete Account
// //             </button>
// //         `).click(() => {
// //                 Swal.fire({
// //                     title: 'Request Account Deletion',
// //                     html: `
// //                     <p>Provide a reason for requesting firm deletion:</p>
// //                     <textarea id="delete-reason" class="w-full p-2 border rounded mt-2" placeholder="Type your reason"></textarea>
// //                 `,
// //                     showCancelButton: true,
// //                     confirmButtonText: 'Submit',
// //                     preConfirm: () => {
// //                         const reason = $("#delete-reason").val();
// //                         if (!reason || reason.trim() === "") {
// //                             Swal.showValidationMessage('Please enter a reason');
// //                         }
// //                         return reason;
// //                     }
// //                 }).then(async (res) => {
// //                     if (res.isConfirmed) {
// //                         try {
// //                             await ajaxWithJWT({
// //                                 url: "http://127.0.0.1:5000/api/firm/request-delete",
// //                                 method: "POST",
// //                                 contentType: "application/json",
// //                                 data: JSON.stringify({ firm_id: firm.id, reason: res.value })
// //                             });
// //                             Swal.fire("Success", "Delete request submitted!", "success");
// //                         } catch (err) {
// //                             Swal.fire("Error", "Failed to submit request.", "error");
// //                         }
// //                     }
// //                 });
// //             });

// //             $actions.append($createBtn, $deleteBtn);
// //         } else {
// //             // Non-self users: Follow, Endorse (if verified), Report
// //             const $followBtn = $(`
// //             <button id="follow-btn" class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition-all">
// //                 Follow
// //             </button>
// //         `).click(async () => {
// //                 try {
// //                     await ajaxWithJWT({
// //                         url: `http://127.0.0.1:5000/api/follow`,
// //                         method: "POST",
// //                         contentType: "application/json",
// //                         data: JSON.stringify({ firm_id })
// //                     });
// //                     Swal.fire("Success", "Followed successfully!", "success");
// //                 } catch (err) {
// //                     Swal.fire("Error", "Failed to follow.", "error");
// //                 }
// //             });

// //             $actions.append($followBtn);

// //             // Endorsement button only for verified users
// //             if (currentUserStatus) {
// //                 const $endorseBtn = $(`
// //                 <button id="endorse-btn" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-all ml-2">
// //                     Endorse
// //                 </button>
// //             `).click(() => {
// //                     Swal.fire("Endorsement", "Your endorsement has been noted!", "success");
// //                     // Later: call endorsement API here
// //                 });
// //                 $actions.append($endorseBtn);
// //             }

// //             // Report button for firm
// //             const $reportBtn = $(`
// //             <button id="report-firm-btn" class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-all ml-2">
// //                 Report Firm
// //             </button>
// //         `).click(() => {
// //                 Swal.fire({
// //                     title: 'Report Firm',
// //                     input: 'textarea',
// //                     inputLabel: 'Reason',
// //                     inputPlaceholder: 'Type your reason here...',
// //                     showCancelButton: true,
// //                     confirmButtonText: 'Report'
// //                 }).then(async (res) => {
// //                     if (res.isConfirmed && res.value.trim() !== "") {
// //                         try {
// //                             await ajaxWithJWT({
// //                                 url: `http://127.0.0.1:5000/api/firm/report`,
// //                                 method: "POST",
// //                                 contentType: "application/json",
// //                                 data: JSON.stringify({ firm_id, reason: res.value })
// //                             });
// //                             Swal.fire("Reported", "Firm has been reported.", "success");
// //                         } catch (err) {
// //                             Swal.fire("Error", "Failed to report firm.", "error");
// //                         }
// //                     }
// //                 });
// //             });

// //             $actions.append($reportBtn);
// //         }
// //     }





// //     // Infinite scroll
// //     $(window).scroll(async function () {
// //         if (!hasMore || loading) return;

// //         if ($(window).scrollTop() + $(window).height() > $(document).height() - 300) {
// //             loading = true;
// //             await fetchFirm();
// //             loading = false;
// //         }
// //     });

// //     // Initial fetch
// //     fetchFirm();
// // });
