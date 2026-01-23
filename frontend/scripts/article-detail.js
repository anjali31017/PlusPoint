$(document).ready(async function () {
    lucide.createIcons();

    const urlParams = new URLSearchParams(window.location.search);
    const article_id = urlParams.get('article_id');

    if (!article_id) {
        Swal.fire('Error', 'Article ID missing', 'error');
        return;
    }

    try {
        const token = getAccessToken(); // from auth.js

        const article = await $.ajax({
            url: `http://127.0.0.1:5000/api/article/detail?article_id=${article_id}`,
            headers: token ? { 'Authorization': `Bearer ${token}` } : {},
            method: 'GET',
            contentType: 'application/json'
        });

        if (article.status !== 1) {
            Swal.fire('Error', 'Article not found', 'error');
            return;
        }

        const data = article.data;

        // Populate HTML
        $('#article-title').text(data.title);
        $('#article-content').html(data.content);
        $('#published-date').text(new Date(data.published_at).toLocaleString());
        $('#publisher-name').text(`${data.publisher.first_name} ${data.publisher.last_name}`);
        $('#publisher-name').click(() => {
            window.location.href = `profile.html?user_id=${data.publisher.id}`;
        });

        $('#category').text(data.category.join(', '));
        $('#tags').text(data.tags.join(', '));

        // Initialize buttons
        initLikeButton($('#like-btn'), data.id);
        initEndorseButton($('#endorse-btn'), 'article', data.id);
        initReportButton($('#report-btn'), 'article', data.id);

        // Copy link
        $('#copy-link-btn').click(() => {
            const url = window.location.href;
            navigator.clipboard.writeText(url).then(() => {
                Swal.fire({
                    title: 'Copied!',
                    text: 'Article link copied to clipboard.',
                    icon: 'success',
                    timer: 1000,
                    showConfirmButton: false
                });
            });
        });

    } catch (err) {
        console.error(err);
        Swal.fire('Error', 'Failed to load article', 'error');
    }
});
