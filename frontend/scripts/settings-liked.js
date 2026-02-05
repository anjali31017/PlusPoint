// settings-liked.js
$(document).ready(async function () {
    const container = $("#content-wrapper");
    container.empty();
    container.append('<h2 class="text-xl font-bold mb-4">Liked Articles</h2>');

    container.append('<input type="text" id="liked-search" placeholder="Search liked articles..." class="mb-3 p-2 border rounded w-full"/>');

    try {
        const res = await ajaxWithJWT({
            url: "http://127.0.0.1:5000/api/article/liked",
            method: "GET",
        });

        if (!res || !res.data) return;

        const table = $(`
            <table class="min-w-full bg-white border rounded-lg">
                <thead>
                    <tr class="bg-gray-100">
                        <th class="p-3 border">Article Title</th>
                        <th class="p-3 border">Liked At</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        `);

        const tbody = table.find("tbody");

        res.data.forEach(a => {
            const row = $(`
                <tr class="cursor-pointer hover:bg-gray-50">
                    <td class="p-2 border">${a.article_title}</td>
                    <td class="p-2 border">${new Date(a.created_at).toLocaleString()}</td>
                </tr>
            `);

            row.on("click", () => {
                window.location.href = `article.html?article_id=${a.article_id}`;
            });

            tbody.append(row);
        });

        container.append(table);

        // Search filter
        $("#liked-search").on("keyup", function () {
            const val = $(this).val().toLowerCase();
            tbody.find("tr").each(function () {
                const text = $(this).text().toLowerCase();
                $(this).toggle(text.includes(val));
            });
        });

    } catch (err) {
        console.error(err);
        container.append('<p class="text-red-500">Failed to load liked articles.</p>');
    }
});
