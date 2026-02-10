// // settings-articles.js



$(document).ready(async function () {
    const container = $("#content-wrapper");
    container.empty();

    container.append('<h2 class="text-xl font-bold mb-4">Top 5 Article Engagement (Likes)</h2>');

    // --- Add search input ---
    container.append('<input type="text" id="article-search" placeholder="Search articles..." class="mb-3 p-2 border rounded w-full"/>');

    try {
        const articles = await ajaxWithJWT({
            url: "http://127.0.0.1:5000/api/dashboard/articles",
            method: "GET",
        });

        if (!articles) return;

        // --- Chart code ---
        const topArticles = articles
            .filter(a => a.status.toLowerCase() === "published")
            .sort((a, b) => b.likes - a.likes)
            .slice(0, 5);

        const colors = ['#7C3AED', '#3B82F6', '#F59E0B', '#EF4444', '#10B981'];

        container.append('<canvas id="likesChart" class="mb-6" width="600" height="150"></canvas>');
        const ctx = document.getElementById('likesChart').getContext('2d');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: topArticles.map((_, i) => i + 1), // simple numeric labels or empty
                datasets: [{
                    label: 'Likes',
                    data: topArticles.map(a => a.likes),
                    backgroundColor: colors
                }]
            },
            options: {
                indexAxis: 'y', // horizontal bars
                responsive: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return `${context.parsed.x} Likes`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        title: { display: true, text: 'Likes Count' }
                    },
                    y: {
                        title: { display: true, text: 'Top 5 Articles' }, // only label
                        ticks: {
                            display: false // hide individual tick labels
                        },
                        grid: { display: false }
                    }
                }
            }
        });



        // --- Table code remains ---
        const table = $(`
            <table class="min-w-full bg-white border rounded-lg">
                <thead>
                    <tr class="bg-gray-100">
                        <th class="p-3 border">Title</th>
                        <th class="p-3 border">Status</th>
                        <th class="p-3 border">Likes</th>
                        <th class="p-3 border">Endorsements</th>
                        <th class="p-3 border">Reports</th>
                        <th class="p-3 border">Published At</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        `);

        const tbody = table.find("tbody");
        articles.forEach(a => {
            const row = $(`
                <tr class="cursor-pointer hover:bg-gray-50">
                    <td class="p-2 border">${a.title}</td>
                    <td class="p-2 border">${a.status}</td>
                    <td class="p-2 border">${a.likes}</td>
                    <td class="p-2 border">${a.endorsements}</td>
                    <td class="p-2 border">${a.reports}</td>
                    <td class="p-2 border">${new Date(a.published_at).toLocaleString()}</td>
                </tr>
            `);
            row.on("click", () => {
                window.location.href = `article.html?article_id=${a.article_id}`;
            });
            tbody.append(row);
        });

        container.append(table);

        // --- Search filter ---
        $("#article-search").on("keyup", function () {
            const val = $(this).val().toLowerCase();
            tbody.find("tr").each(function () {
                const text = $(this).text().toLowerCase();
                $(this).toggle(text.includes(val));
            });
        });

    } catch (err) {
        console.error(err);
        container.append('<p class="text-red-500">Failed to load articles.</p>');
    }
});
