// // article-detail.js
// $(document).ready(async function () {
//     const urlParams = new URLSearchParams(window.location.search);
//     const articleId = urlParams.get("article_id");
//     if (!articleId) {
//         Swal.fire("Error", "No article ID provided", "error");
//         return;
//     }

//     try {
//         await isLoggedIn();

//         const res = await ajaxWithJWT({
//             url: `http://127.0.0.1:5000/api/article/detail?article_id=${articleId}`,
//             method: "GET",
//         });

//         const article = res.data;

//         // Title
//         $("#article-title").text(article.title);

//         // Publisher with profile link
//         const publisherName = article.publisher.first_name + " " + article.publisher.last_name;
//         $("#publisher-name")
//             .text(publisherName)
//             .attr("onclick", `window.location.href='profile.html?user_id=${article.publisher.id}'`)
//             .addClass("cursor-pointer");

//         // Date
//         $("#published-date").text(new Date(article.published_at).toLocaleString());

//         // Category & Tags
//         $("#category").text(article.category.join(", ") || "Uncategorized");
//         $("#tags").text(article.tags.join(", ") || "No Tags");

//         // Summary + Article
//         let contentHtml = "";
//         if (article.summary) {
//             contentHtml += `<h3 class="text-purple-700 font-semibold mt-6">SUMMARY</h3>`;
//             contentHtml += `<p>${article.summary}</p>`;
//         }
//         if (article.content) {
//             contentHtml += `<h3 class="text-purple-700 font-semibold mt-6">ARTICLE</h3>`;
//             contentHtml += `<div>${article.content}</div>`;
//         }
//         $("#article-content").html(contentHtml);

//         // Buttons
//         const $likeBtn = $("#like-btn");
//         const $endorseBtn = $("#endorse-btn");
//         const $reportBtn = $("#report-btn");
//         const $copyLinkBtn = $("#copy-link-btn");

//         const isSelf = article.is_self;
//         const showEndorse = res.data.status === 1;

//         if (isSelf) {
//             // Self: show copy link & delete request
//             $likeBtn.hide();
//             $endorseBtn.hide();
//             $reportBtn.hide();
//             $copyLinkBtn.show();
//             $copyLinkBtn.off("click").on("click", function () {
//                 navigator.clipboard.writeText(window.location.href);
//                 Swal.fire("Copied!", "Article link copied to clipboard", "success");
//             });

//             if ($("#delete-btn").length === 0) {
//                 $("#article-content").after(`
//                     <button id="delete-btn" class="btn-action bg-red-600 text-white flex items-center gap-1 mt-4">
//                         <i data-lucide="trash-2"></i><span>Delete Request</span>
//                     </button>
//                 `);
//             }
//             initDeleteRequest($("#delete-btn"), "article", article.id);
//         } else {
//             // Other users: show like, endorse (if allowed), report, copy link
//             $likeBtn.show();
//             $endorseBtn.toggle(showEndorse);
//             $reportBtn.show();
//             $copyLinkBtn.show();

//             // Initialize like & endorse buttons
//             initLikeButton($likeBtn, article.id);
//             if (showEndorse) initEndorseButton($endorseBtn, "article", article.id);

//             // Set initial button state
//             if (article.liked) {
//                 $likeBtn.addClass("text-red-600").find("span").text("❤️ You Liked");
//             }
//             if (article.endorsed) {
//                 $endorseBtn.addClass("bg-green-700").find("span").text("You Endorsed");
//             }

//             // Copy link
//             $copyLinkBtn.off("click").on("click", function () {
//                 navigator.clipboard.writeText(window.location.href);
//                 Swal.fire("Copied!", "Article link copied to clipboard", "success");
//             });

//             // Report button
//             $reportBtn.off("click").on("click", function () {
//                 Swal.fire("Reported", "You have reported this article", "success");
//             });
//         }

//         // Show Like / Endorse / Trust counts
//         $likeBtn.append(` <span class="ml-1 text-gray-700">${article.like_count}</span>`);
//         $endorseBtn.append(` <span class="ml-1 text-white">${article.endorse_count} | ${article.trust_score_snapshot}</span>`);

//         lucide.createIcons();
//     } catch (err) {
//         console.error(err);
//         Swal.fire("Error", "Failed to load article", "error");
//     }
// });



$(document).ready(async function () {
    const params = new URLSearchParams(window.location.search);
    const articleId = params.get("article_id");

    if (!articleId) {
        Swal.fire("Error", "Invalid article", "error");
        return;
    }

    try {
        // Get user status
        const userStatus = await isLoggedIn(); // should return {status: true/false, ...}

        const res = await ajaxWithJWT({
            url: `http://127.0.0.1:5000/api/article/detail?article_id=${articleId}`,
            method: "GET"
        });

        if (res.status !== 1) {
            Swal.fire("Error", "Article not found", "error");
            return;
        }

        renderArticle(res.data, userStatus);

    } catch (err) {
        console.error(err);
        Swal.fire("Error", "Failed to load article", "error");
    }
});


function renderArticle(article, userStatus) {

    const accessToken = localStorage.getItem("access_token");
    let currentUserStatus = false;
    if (accessToken) {
        try {
            const payload = JSON.parse(atob(accessToken.split(".")[1]));
            currentUserStatus = payload.status === true;
        } catch (e) { currentUserStatus = false; }
    }

    const isSelf = article.is_self;


    // Clear container
    const $container = $(".max-w-6xl");
    $container.empty();

    // Build main article HTML
    const html = `
    <article class="bg-white rounded-2xl shadow-sm border border-purple-100 p-6 md:p-8">

        <!-- Title -->
        <h1 class="text-3xl md:text-4xl font-extrabold text-gray-900 mb-2">${article.title}</h1>

        <!-- Meta -->
        <div class="flex flex-wrap items-center gap-2 text-sm text-gray-500 mb-4">
            <span>By 
                <a href="profile.html?user_id=${article.publisher.id}" 
                   class="text-purple-600 font-semibold hover:underline">
                    ${article.publisher.first_name} ${article.publisher.last_name}
                </a>
            </span>
            <span>•</span>
            <span>${new Date(article.published_at).toLocaleDateString()}</span>
            <span>•</span>
            <span>${new Date(article.published_at).toLocaleTimeString()}</span>
        </div>

        <!-- Buttons -->
        <div class="flex flex-wrap gap-3 mb-4" id="article-buttons"></div>

        <!-- Stats -->
        <div class="flex flex-wrap gap-6 text-sm text-gray-600 mb-6" id="article-stats">
            <span>❤️ <strong>${article.like_count}</strong> Likes</span>
            <span>👍 <strong>${article.endorse_count}</strong> Endorsements</span>
            <span>🛡 Trust Score <strong>${article.trust_score_snapshot}</strong></span>
        </div>

        <!-- Categories & Tags -->
        <div class="flex flex-wrap gap-2 mb-6">
            ${article.category.map(c => `<span class="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-xs font-medium">${c}</span>`).join("")}
            ${article.tags.map(t => `<span class="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-medium">#${t}</span>`).join("")}
        </div>

        <!-- Summary -->
        <h2 class="text-purple-600 font-extrabold tracking-wide uppercase text-sm mb-2">SUMMARY</h2>
        <p class="text-lg text-gray-700 font-medium mb-8 leading-relaxed">${article.summary || "No summary available."}</p>

        <!-- Article -->
        <h2 class="text-purple-600 font-extrabold tracking-wide uppercase text-sm mb-2">ARTICLE</h2>
        <div class="article-content prose max-w-none text-gray-800">${article.content}</div>
    </article>
    `;

    $container.html(html);

    const $btnContainer = $("#article-buttons");

    // --- Buttons ---
    if (isSelf) {
        // Self user: show delete request + copy link
        const $deleteBtn = $('<button class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all">Request Delete</button>');
        initDeleteRequest($deleteBtn, 'article', article.id);
        $btnContainer.append($deleteBtn);
    } 
    else 
        {
        // Other user: like, endorse (if allowed), report, copy link
        const $likeBtn = $(`
            <button class="px-4 py-2 ${article.liked ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-600'} rounded-lg flex items-center gap-2">
                <span class="like-text" >${article.liked ? 'You Liked' : 'Like'}</span>
            </button>
        `);
        initLikeButton($likeBtn, article.id);
        $btnContainer.append($likeBtn);

        if (currentUserStatus) {
            const $endorseBtn = $(`
                <button class="px-4 py-2 ${article.endorsed ? 'bg-green-600 text-white' : 'bg-green-600 text-white'} rounded-lg">
                    ${article.endorsed ? 'You Endorsed' : 'Give Endorsement'}
                </button>
            `);
            initEndorseButton($endorseBtn, 'article', article.id);
            $btnContainer.append($endorseBtn);
        }

        const $reportBtn = $('<button class="px-4 py-2 bg-red-100 text-red-600 rounded-lg">Report</button>');
        initReportButton($reportBtn, 'article', article.id);
        $btnContainer.append($reportBtn);
    }

    // Copy link button (always visible)
    const $copyBtn = $('<button class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg">🔗 Copy Link</button>');
    $copyBtn.click(() => {
        navigator.clipboard.writeText(window.location.href);
        Swal.fire({ icon: 'success', title: 'Link copied', timer: 1000, showConfirmButton: false });
    });
    $btnContainer.append($copyBtn);
}

// function renderArticle(article, userStatus) {
//     const isSelf = article.is_self;

//     // Show endorsement button only if userStatus.status is true
//     const showEndorseBtn = !isSelf && userStatus.status;

//     const html = `
//     <article class="bg-white rounded-2xl shadow-sm border border-purple-100 p-6 md:p-8">

//         <!-- Title -->
//         <h1 class="text-3xl md:text-4xl font-extrabold text-gray-900 mb-2">
//             ${article.title}
//         </h1>

//         <!-- Meta -->
//         <div class="flex flex-wrap items-center gap-2 text-sm text-gray-500 mb-4">
//             <span>
//                 By
//                 <a href="profile.html?user_id=${article.publisher.id}"
//                    class="text-purple-600 font-semibold hover:underline">
//                     ${article.publisher.first_name} ${article.publisher.last_name}
//                 </a>
//             </span>
//             <span>•</span>
//             <span>${new Date(article.published_at).toLocaleDateString()}</span>
//             <span>•</span>
//             <span>${new Date(article.published_at).toLocaleTimeString()}</span>
//         </div>

//         <!-- Action Buttons -->
//         <div class="flex flex-wrap gap-3 mb-6">

//             ${!isSelf ? `
//                    <button id="likeBtn"
//                     class="btn-action flex items-center gap-2 px-4 py-2 text-sm font-medium
//                     ${article.liked ? 'bg-red-50 text-red-600' : 'bg-gray-100 text-gray-600'}">
//                     <span>${article.liked ? '❤️ You Liked' : '❤️ Like'}</span>
//                     <span id="likeCount">${article.like_count || 0}</span>
//                 </button>

//                 ${showEndorseBtn ? `
//                 <button id="endorseBtn"
//                     class="btn-action px-4 py-2 ${article.endorsed ? 'bg-green-700' : 'bg-green-600'} text-white text-sm font-medium">
//                     ${article.endorsed ? 'You Endorsed' : 'Give Endorsement'}
//                     <span id="endorseCount">${article.endorse_count || 0}</span>
//                 </button>
//                 ` : ''}

//                 <button id="reportBtn"
//                     class="btn-action px-4 py-2 bg-red-100 text-red-600 text-sm font-medium">
//                     Report
//                 </button>
//             ` : `
//                 <button id="deleteReqBtn"
//                     class="btn-action px-4 py-2 bg-red-600 text-white text-sm font-medium">
//                     Request Delete
//                 </button>
//             `}

//             <button id="copyBtn"
//                 class="btn-action px-4 py-2 bg-gray-100 text-gray-700 text-sm font-medium">
//                 🔗 Copy Link
//             </button>

//         </div>

//         <!-- Stats -->
//         <div class="flex flex-wrap gap-6 text-sm text-gray-600 mb-6">
//             <span>❤️ <strong>${article.like_count}</strong> Likes</span>
//             <span>👍 <strong>${article.endorse_count}</strong> Endorsements</span>
//             <span>🛡 Trust Score <strong>${article.trust_score_snapshot}</strong></span>
//         </div>

//         <!-- Categories & Tags -->
//         <div class="flex flex-wrap gap-2 mb-6">
//             ${article.category.map(c =>
//         `<span class="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-xs font-medium">${c}</span>`
//     ).join("")}

//             ${article.tags.map(t =>
//         `<span class="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-medium">#${t}</span>`
//     ).join("")}
//         </div>

//         <!-- Summary -->
//         <h2 class="text-purple-600 font-extrabold tracking-wide uppercase text-sm mb-2">
//             SUMMARY
//         </h2>
//         <p class="text-lg text-gray-700 font-medium mb-8 leading-relaxed">
//             ${article.summary || "FETCHING SUMMARY"}
//         </p>

//         <!-- Article -->
//         <h2 class="text-purple-600 font-extrabold tracking-wide uppercase text-sm mb-2">
//             ARTICLE
//         </h2>
//         <div class="article-content prose max-w-none text-gray-800">
//             ${article.content}
//         </div>

//     </article>
//     `;

//     $(".max-w-6xl").html(html);

//     /* ---- Bind Actions ---- */
//     if (!isSelf) {
//         initLikeButton($("#likeBtn"), article.id);
//         if (showEndorseBtn) initEndorseButton($("#endorseBtn"), "article", article.id);
//         initReportButton($("#reportBtn"), "article", article.id);
//     } else {
//         initDeleteRequest($("#deleteReqBtn"), "article", article.id);
//     }

//     $("#copyBtn").on("click", copyArticleLink);
// }

/* ---------- Helpers ---------- */
function copyArticleLink() {
    navigator.clipboard.writeText(window.location.href);
    Swal.fire({
        icon: "success",
        title: "Link copied",
        timer: 1000,
        showConfirmButton: false
    });
}









// $(document).ready(async function () {
//     const params = new URLSearchParams(window.location.search);
//     const articleId = params.get("article_id");

//     if (!articleId) {
//         Swal.fire("Error", "Invalid article", "error");
//         return;
//     }

//     try {
//         await isLoggedIn();

//         const res = await ajaxWithJWT({
//             url: `http://127.0.0.1:5000/api/article/detail?article_id=${articleId}`,
//             method: "GET"
//         });

//         if (res.status !== 1) {
//             Swal.fire("Error", "Article not found", "error");
//             return;
//         }

//         renderArticle(res.data);

//     } catch (err) {
//         console.error(err);
//         Swal.fire("Error", "Failed to load article", "error");
//     }
// });

// function renderArticle(article) {
//     const isSelf = article.is_self;

//     const html = `
//     <article class="bg-white rounded-2xl shadow-sm border border-purple-100 p-6 md:p-8">

//         <!-- Title -->
//         <h1 class="text-3xl md:text-4xl font-extrabold text-gray-900 mb-2">
//             ${article.title}
//         </h1>

//         <!-- Meta -->
//         <div class="flex flex-wrap items-center gap-2 text-sm text-gray-500 mb-4">
//             <span>
//                 By
//                 <a href="profile.html?user_id=${article.publisher.id}"
//                    class="text-purple-600 font-semibold hover:underline">
//                     ${article.publisher.first_name} ${article.publisher.last_name}
//                 </a>
//             </span>
//             <span>•</span>
//             <span>${new Date(article.published_at).toLocaleDateString()}</span>
//             <span>•</span>
//             <span>${new Date(article.published_at).toLocaleTimeString()}</span>
//         </div>

//         <!-- Action Buttons -->
//         <div class="flex flex-wrap gap-3 mb-6">

//             ${!isSelf ? `
                
//                 <button id="likeBtn"
//                     class="btn-action flex items-center gap-2 px-4 py-2 text-sm font-medium
//                     ${article.liked ? 'bg-red-50 text-red-600' : 'bg-gray-100 text-gray-600'}">
//                      <span>${article.liked ? 'You Liked' : 'Like'}</span>
//                 </button>


//                 <button id="endorseBtn"
//                     class="btn-action px-4 py-2 bg-green-600 text-white text-sm font-medium">
//                     ${article.endorsed ? 'You Endorsed' : 'Give Endorsement'}
//                 </button>

//                 <button id="reportBtn"
//                     class="btn-action px-4 py-2 bg-red-100 text-red-600 text-sm font-medium">
//                     Report
//                 </button>
//             ` : `
//                 <button id="deleteReqBtn"
//                     class="btn-action px-4 py-2 bg-red-600 text-white text-sm font-medium">
//                     Request Delete
//                 </button>
//             `}

//             <button id="copyBtn"
//                 class="btn-action px-4 py-2 bg-gray-100 text-gray-700 text-sm font-medium">
//                 🔗 Copy Link
//             </button>

//         </div>

//         <!-- Stats -->
//         <div class="flex flex-wrap gap-6 text-sm text-gray-600 mb-6">
//             <span>❤️ <strong>${article.like_count}</strong> Likes</span>
//             <span>👍 <strong>${article.endorse_count}</strong> Endorsements</span>
//             <span>🛡 Trust Score <strong>${article.trust_score_snapshot}</strong></span>
//         </div>

//         <!-- Categories & Tags -->
//         <div class="flex flex-wrap gap-2 mb-6">
//             ${article.category.map(c =>
//         `<span class="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-xs font-medium">${c}</span>`
//     ).join("")}

//             ${article.tags.map(t =>
//         `<span class="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-medium">#${t}</span>`
//     ).join("")}
//         </div>

//         <!-- Summary -->
//         <h2 class="text-purple-600 font-extrabold tracking-wide uppercase text-sm mb-2">
//             SUMMARY
//         </h2>
//         <p class="text-lg text-gray-700 font-medium mb-8 leading-relaxed">
//             ${article.summary || "FETCHING SUMMARY"}
//         </p>

//         <!-- Article -->
//         <h2 class="text-purple-600 font-extrabold tracking-wide uppercase text-sm mb-2">
//             ARTICLE
//         </h2>
//         <div class="article-content prose max-w-none text-gray-800">
//             ${article.content}
//         </div>


//     </article>
//     `;

//     $(".max-w-6xl").html(html);

//     /* ---- Bind Actions ---- */

//     if (!isSelf) {
//         initLikeButton($("#likeBtn"), article.id);
//         initEndorseButton($("#endorseBtn"), "article", article.id);
//         initReportButton($("#reportBtn"), "article", article.id);
//     } else {
//         initDeleteRequest($("#deleteReqBtn"), "article", article.id);
//     }

//     $("#copyBtn").on("click", copyArticleLink);
// }

// /* ---------- Helpers ---------- */

// function copyArticleLink() {
//     navigator.clipboard.writeText(window.location.href);
//     Swal.fire({
//         icon: "success",
//         title: "Link copied",
//         timer: 1000,
//         showConfirmButton: false
//     });
// }














// $(document).ready(async function () {
//     const params = new URLSearchParams(window.location.search);
//     const articleId = params.get("article_id");

//     if (!articleId) {
//         Swal.fire("Error", "Invalid article", "error");
//         return;
//     }

//     try {
//         await isLoggedIn();

//         const res = await ajaxWithJWT({
//             url: `http://127.0.0.1:5000/api/article/detail?article_id=${articleId}`,
//             method: "GET"
//         });

//         if (res.status !== 1) {
//             Swal.fire("Error", "Article not found", "error");
//             return;
//         }

//         renderArticle(res.data);

//     } catch (err) {
//         console.error(err);
//         Swal.fire("Error", "Failed to load article", "error");
//     }
// });

// function renderArticle(article) {
//     const isSelf = article.is_self;

//     const buttonsHtml = `
//         ${!isSelf ? `
//             <button id="likeBtn"
//                 class="flex items-center gap-2 text-sm font-medium
//                 ${article.liked ? 'text-red-600' : 'text-gray-400'}">
//                 ❤️ <span>${article.liked ? 'Liked' : 'Like'}</span>
//             </button>

//             <button id="endorseBtn"
//                 class="btn-action bg-green-600 text-white text-sm rounded-lg">
//                 ${article.endorsed ? 'You Endorsed' : 'Give Endorsement'}
//             </button>

//             <button id="reportBtn"
//                 class="btn-action bg-red-100 text-red-600 text-sm rounded-lg">
//                 Report
//             </button>
//         ` : `
//             <button id="deleteReqBtn"
//                 class="btn-action bg-red-600 text-white text-sm rounded-lg">
//                 Request Delete
//             </button>
//         `}

//         <button id="copyBtn"
//             class="btn-action bg-gray-200 text-gray-700 text-sm rounded-lg">
//             Copy Link
//         </button>
//     `;



//     const html = `
//         <article class="bg-white rounded-xl shadow p-6">

//             <div class="flex justify-end mb-4 gap-3" id="article-actions">
//                 ${buttonsHtml}
//             </div>
//             <h1 class="text-3xl font-bold mb-2">${article.title}</h1>

//             <p class="text-gray-500 text-sm mb-4">
//                 By
//                 <a href="profile.html?user_id=${article.publisher.id}"
//                 class="text-purple-600 font-medium hover:underline">
//                     ${article.publisher.first_name} ${article.publisher.last_name}
//                 </a>
//                 • ${new Date(article.published_at).toLocaleDateString()}
//             </p>


//             <p class="text-gray-700 mb-6">${article.summary}</p>

//             <div class="article-content prose max-w-none">
//                 ${article.content}
//             </div>

//             ${buttonsHtml}
//         </article>
//     `;

//     $(".max-w-6xl").html(html);


//     if (!isSelf) {
//         initLikeButton($("#likeBtn"), article.id);
//         initEndorseButton($("#endorseBtn"), "article", article.id);
//         initReportButton($("#reportBtn"), "article", article.id);
//     } else {
//         initDeleteRequest($("#deleteReqBtn"), "article", article.id);
//     }

//     $("#copyBtn").on("click", copyArticleLink);

// }

// /* Helpers */

// function copyArticleLink() {
//     navigator.clipboard.writeText(window.location.href);
//     Swal.fire({
//         icon: "success",
//         title: "Link copied",
//         timer: 1000,
//         showConfirmButton: false
//     });
// }

// async function deleteArticle(articleId) {
//     const confirm = await Swal.fire({
//         title: "Delete Article?",
//         text: "This action cannot be undone.",
//         icon: "warning",
//         showCancelButton: true,
//         confirmButtonText: "Delete"
//     });

//     if (!confirm.isConfirmed) return;

//     try {
//         await ajaxWithJWT({
//             url: `http://127.0.0.1:5000/api/article/delete?article_id=${articleId}`,
//             method: "DELETE"
//         });

//         Swal.fire("Deleted", "Article removed", "success");
//         window.location.href = "home.html";

//     } catch (err) {
//         Swal.fire("Error", "Failed to delete article", "error");
//     }
// }










// // $(document).ready(async function () {
// //     lucide.createIcons();

// //     const urlParams = new URLSearchParams(window.location.search);
// //     const article_id = urlParams.get('article_id');

// //     if (!article_id) {
// //         Swal.fire('Error', 'Article ID missing', 'error');
// //         return;
// //     }

// //     try {
// //         const token = getAccessToken(); // from auth.js

// //         const article = await $.ajax({
// //             url: `http://127.0.0.1:5000/api/article/detail?article_id=${article_id}`,
// //             headers: token ? { 'Authorization': `Bearer ${token}` } : {},
// //             method: 'GET',
// //             contentType: 'application/json'
// //         });

// //         if (article.status !== 1) {
// //             Swal.fire('Error', 'Article not found', 'error');
// //             return;
// //         }

// //         const data = article.data;

// //         // Populate HTML
// //         $('#article-title').text(data.title);
// //         $('#article-content').html(data.content);
// //         $('#published-date').text(new Date(data.published_at).toLocaleString());
// //         $('#publisher-name').text(`${data.publisher.first_name} ${data.publisher.last_name}`);
// //         $('#publisher-name').click(() => {
// //             window.location.href = `profile.html?user_id=${data.publisher.id}`;
// //         });

// //         $('#category').text(data.category.join(', '));
// //         $('#tags').text(data.tags.join(', '));

// //         // Initialize buttons
// //         initLikeButton($('#like-btn'), data.id);
// //         initEndorseButton($('#endorse-btn'), 'article', data.id);
// //         initReportButton($('#report-btn'), 'article', data.id);

// //         // Copy link
// //         $('#copy-link-btn').click(() => {
// //             const url = window.location.href;
// //             navigator.clipboard.writeText(url).then(() => {
// //                 Swal.fire({
// //                     title: 'Copied!',
// //                     text: 'Article link copied to clipboard.',
// //                     icon: 'success',
// //                     timer: 1000,
// //                     showConfirmButton: false
// //                 });
// //             });
// //         });

// //     } catch (err) {
// //         console.error(err);
// //         Swal.fire('Error', 'Failed to load article', 'error');
// //     }
// // });
