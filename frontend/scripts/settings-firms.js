// settings-firms.js
$(document).ready(async function () {
    const container = $("#content-wrapper");
    container.empty();
    container.append('<h2 class="text-xl font-bold mb-4">Firms</h2>');

    container.append('<input type="text" id="firm-search" placeholder="Search firms..." class="mb-3 p-2 border rounded w-full"/>');

    try {
        const firms = await ajaxWithJWT({
            url: "http://127.0.0.1:5000/api/dashboard/firms",
            method: "GET",
        });

        if (!firms) return;

        const table = $(`
            <table class="min-w-full bg-white border rounded-lg">
                <thead>
                    <tr class="bg-gray-100">
                        <th class="p-3 border">Firm Name</th>
                        <th class="p-3 border">Verification Status</th>
                        <th class="p-3 border">Followers</th>
                        <th class="p-3 border">Total Articles</th>
                        <th class="p-3 border">Endorsements</th>
                        <th class="p-3 border">Reports</th>
                        <th class="p-3 border">Trust Factor</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        `);

        const tbody = table.find("tbody");

        firms.forEach(f => {
            const row = $(`
                <tr class="cursor-pointer hover:bg-gray-50">
                    <td class="p-2 border">${f.firm_name}</td>
                    <td class="p-2 border">${f.verification_status}</td>
                    <td class="p-2 border">${f.followers}</td>
                    <td class="p-2 border">${f.total_articles}</td>
                    <td class="p-2 border">${f.total_endorsements}</td>
                    <td class="p-2 border">${f.total_reports}</td>
                    <td class="p-2 border">${f.trust_factor}%</td>
                </tr>
            `);

            row.on("click", () => {
                window.location.href = `firm.html?firm_id=${f.firm_id}`;
            });

            tbody.append(row);
        });

        container.append(table);

        // Search filter
        $("#firm-search").on("keyup", function () {
            const val = $(this).val().toLowerCase();
            tbody.find("tr").each(function () {
                const text = $(this).text().toLowerCase();
                $(this).toggle(text.includes(val));
            });
        });

    } catch (err) {
        console.error(err);
        container.append('<p class="text-red-500">Failed to load firms.</p>');
    }
});
