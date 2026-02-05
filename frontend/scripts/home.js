// feed.js

$(document).ready(async function () {
    const loggedIn = await isLoggedIn();
    if (!loggedIn) return;

    await fetchAndRenderMixedFeed();
});

// Render article HTML
function renderArticle(article) {
    const articleId = article.article_id || article.id;
    const title = article.title || "Untitled";
    const summary = article.summary || "";
    const tags = article.tags || [];
    const categories = article.category || [];
    const likes = article.likes ?? article.like_count ?? 0;
    const endorse = article.endorse ?? article.endorse_count ?? 0;
    const published = new Date(article.published_at).toLocaleString();

    // Category pills
    const categoryHtml = categories
        .map(c => `<span class="bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full text-xs mr-1">${c}</span>`)
        .join("");

    // Tag pills
    const tagHtml = tags
        .map(t => `<span class="bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full text-xs mr-1">${t}</span>`)
        .join("");

    return `
        <div class="border rounded-xl p-4 mb-4 cursor-pointer hover:shadow-lg transition"
             onclick="window.location.href='article.html?article_id=${articleId}'">
            <h3 class="font-bold text-lg text-purple-700">${title}</h3>
            <p class="text-gray-600 mt-1 text-sm">${summary}</p>
            <div class="flex flex-wrap gap-1 mt-2">
                ${categoryHtml}
                ${tagHtml}
            </div>
            <div class="flex justify-between mt-2 text-xs text-gray-500">
                <span>Likes: ${likes}</span>
                <span>Endorsed: ${endorse}</span>
                <span>${published}</span>
            </div>
        </div>
    `;
}

// Render section label and wrapper
function renderSection(label, articlesHtml, isRecommended = false) {
    const bgClass = isRecommended ? "bg-slate-100 p-4 rounded-xl mb-6" : "";
    return `
        <div class="${bgClass}">
            <h3 class="text-xl font-bold text-gray-800 mb-2">${label}</h3>
            ${articlesHtml}
        </div>
    `;
}

// Fetch feeds
async function fetchFeed(url) {
    try {
        const response = await ajaxWithJWT({ url, method: "GET" });
        if (response.status === 1) {
            if (Array.isArray(response.data)) return response.data;
            if (response.data.articles) return response.data.articles;
        }
        return [];
    } catch (err) {
        console.error(err);
        return [];
    }
}

// Fetch and render mixed feed
// fetchAndRenderMixedFeed corrected
async function fetchAndRenderMixedFeed() {
    
    const followingFeed = await fetchFeed("http://127.0.0.1:5000/api/user/feed/following");
    const recommendedFeed = await fetchFeed("http://127.0.0.1:5000/api/user/feed/recommended?page=1&page_size=50");

    // If no recommended, show all following once
    if (recommendedFeed.length === 0) {
        if (followingFeed.length > 0) {
            const html = followingFeed.map(renderArticle).join("");
            $("#content-wrapper").append(renderSection("Following:", html, false));
        }
        return;
    }

    // If recommended exists, alternate chunks
    const followingChunk = 3;
    const recommendedChunk = 2;
    let fIndex = 0, rIndex = 0;

    let firstFollowingRendered = false; // To ensure Following label doesn't repeat

    while (fIndex < followingFeed.length || rIndex < recommendedFeed.length) {
        // Following section
        if (fIndex < followingFeed.length && !firstFollowingRendered) {
            let html = "";
            for (let i = 0; i < followingChunk && fIndex < followingFeed.length; i++, fIndex++) {
                html += renderArticle(followingFeed[fIndex]);
            }
            $("#content-wrapper").append(renderSection("Following:", html, false));
            firstFollowingRendered = true;
        } else if (fIndex < followingFeed.length) {
            // append next 2 following articles without repeating the label
            let html = "";
            for (let i = 0; i < followingChunk && fIndex < followingFeed.length; i++, fIndex++) {
                html += renderArticle(followingFeed[fIndex]);
            }
            $("#content-wrapper").append(html);
        }

        // Recommended section
        if (rIndex < recommendedFeed.length) {
            let html = "";
            for (let i = 0; i < recommendedChunk && rIndex < recommendedFeed.length; i++, rIndex++) {
                html += renderArticle(recommendedFeed[rIndex]);
            }
            $("#content-wrapper").append(renderSection("Recommended for You:", html, true));
        }
    }
}

