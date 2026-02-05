// settings-trends.js
$(document).ready(async function () {
    const container = $("#content-wrapper");
    container.empty();
    container.append('<h2 class="text-xl font-bold mb-4">User Engagement Trends</h2>');

    container.append('Days: <input type="number" id="trends-days" min="1" value="30" class="mb-3 p-2 border rounded w-32"/><button id="trends-refresh" class="ml-2 px-3 py-1 bg-purple-600 text-white rounded">Refresh</button>');
    container.append('<canvas id="trends-chart" class="w-full h-64"></canvas>');

    let chart;

    async function loadTrends(days) {
        try {
            const trends = await ajaxWithJWT({
                url: `http://127.0.0.1:5000/api/dashboard/trends?days=${days}`,
                method: "GET",
            });

            if (!trends) return;

            const labels = trends.map(t => t.date);
            const likes = trends.map(t => t.likes);
            const endorsements = trends.map(t => t.endorsements);
            const reports = trends.map(t => t.reports);

            if (chart) chart.destroy();

            const ctx = document.getElementById("trends-chart").getContext("2d");
            chart = new Chart(ctx, {
                type: "line",
                data: {
                    labels,
                    datasets: [
                        { label: "Likes", data: likes, borderColor: "blue", fill: false, tension: 0.3 },
                        { label: "Endorsements", data: endorsements, borderColor: "green", fill: false, tension: 0.3 },
                        { label: "Reports", data: reports, borderColor: "red", fill: false, tension: 0.3 },
                    ]
                },
                options: { responsive: true, plugins: { legend: { position: "top" } } }
            });

        } catch (err) {
            console.error(err);
            container.append('<p class="text-red-500">Failed to load trends.</p>');
        }
    }

    loadTrends(30);

    $("#trends-refresh").on("click", function () {
        const days = parseInt($("#trends-days").val()) || 30;
        loadTrends(days);
    });
});
