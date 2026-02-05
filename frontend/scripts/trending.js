$(document).ready(async function () {
    await isLoggedIn(); // Ensure user is logged in
    lucide.createIcons();

    loadTrending("day"); // Default to 'day'

    // Optional: add tabs for day/week/month
    $("#spanSelector button").click(function () {
        const span = $(this).data("span");
        loadTrending(span);
        $("#spanSelector button").removeClass("bg-purple-700 text-white");
        $(this).addClass("bg-purple-700 text-white");
    });
});

async function loadTrending(span = "day") {
    const container = $("#content-wrapper");
    container.html('<p class="text-center text-gray-500 mt-10">Loading trending articles...</p>');

    try {
        const articles = await ajaxWithJWT({
            url: `http://127.0.0.1:5000/api/article/trending?span=${span}`,
            method: "GET",
        });

        if (articles.status !== 1 || !articles.data.length) {
            container.html('<p class="text-center text-gray-600 mt-10">No trending articles found</p>');
            return;
        }

        container.empty();
        articles.data.forEach(article => {
            const summary = article.summary || article.content_text || "";
            const articleCard = $(`
                <div class="bg-white rounded-xl shadow-md p-6 mb-6 cursor-pointer hover:shadow-lg transition-all flex flex-col md:flex-row gap-4">
                    <div class="flex-1">
                        <h3 class="text-xl font-bold text-gray-800 mb-2">${article.title}</h3>
                        <p class="text-gray-600 mb-2 line-clamp-4">${summary}</p>
                        <!-- Categories -->
                        <div class="flex flex-wrap gap-2 mb-2">
                            ${article.category.map(cat => `<span class="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded">${cat}</span>`).join('')}
                        </div>
                        <!-- Tags -->
                        <div class="flex flex-wrap gap-2">
                            ${article.tags.map(tag => `<span class="bg-purple-100 text-purple-700 text-xs px-2 py-1 rounded">${tag}</span>`).join('')}
                        </div>
                        <p class="mt-2 text-gray-500 text-xs">Published: ${formatDate(article.published_at)}</p>
                    </div>
                    <div class="flex flex-col gap-2 md:w-48 justify-between text-gray-700">
                        <p>❤️ ${article.like_count || 0} Like</p>
                        <p>👍 ${article.endorse_count || 0} Endorsements</p>
                        <p>🛡 ${article.trust_score || 0} Trust Score</p>
                        <p class="${article.hot_topic ? 'text-red-500 font-bold' : 'text-gray-500'}">${article.hot_topic ? 'Hot Topic' : ''}</p>
                    </div>
                </div>
            `);

            articleCard.click(() => {
                window.location.href = `article.html?article_id=${article.id}`;
            });

            container.append(articleCard);
        });

    } catch (err) {
        container.html('<p class="text-center text-red-500 mt-10">Failed to load trending articles</p>');
        console.error(err);
    }
}


function formatDate(datetimeStr) {
    if (!datetimeStr) return "";
    const d = new Date(datetimeStr);
    return d.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}
