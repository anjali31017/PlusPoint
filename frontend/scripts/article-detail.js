


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
        <h1 class="text-3xl md:text-4xl font-extrabold text-gray-900 mb-2" >${article.title}</h1>

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
            <span>🛡 Trust Score <strong>${Number(article.trust_score_snapshot).toFixed(2)}</strong></span>
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
