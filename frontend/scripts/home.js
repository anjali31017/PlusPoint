$(document).ready(function () {
    const activeClasses = "bg-purple-50 text-purple-700 font-bold shadow-sm";
    const inactiveClasses = "text-gray-600 hover:bg-white hover:text-purple-700";

    // --- JWT & REFRESH LOGIC ---
    async function validateAndRefreshSession() {
        const accessToken = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');

        // if (!accessToken) {
        //     window.location.href = 'login.html';
        //     return;
        // }

        try {
            const payload = JSON.parse(atob(accessToken.split('.')[1]));
            const isExpired = Date.now() >= (payload.exp * 1000);
            
            // Refresh if expired OR expiring in less than 1 minute
            const isExpiringSoon = Date.now() >= (payload.exp * 1000) - 60000;

            if (isExpired || isExpiringSoon) {
                const response = await $.ajax({
                    url: 'http://127.0.0.1:5000/api/token/refresh',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ "refresh_token": refreshToken })
                });

                if (response.status === 1) {
                    localStorage.setItem('access_token', response.data.access_token);
                    localStorage.setItem('refresh_token', response.data.refresh_token);
                    $('body').show();
                } else {
                    throw new Error("Refresh failed");
                }
            } else {
                $('body').show();
            }
        } catch (e) {
            localStorage.clear();
            // window.location.href = 'login.html';
        }
    }

    validateAndRefreshSession();
    lucide.createIcons();

    // --- HEADER BUTTONS ---
    $('#header-profile-btn').on('click', () => $('.nav-link[data-page="profile"]').trigger('click'));
    $('#header-noti-btn').on('click', () => $('.nav-link[data-page="notifications"]').trigger('click'));

    // --- NAVIGATION ---
    $('.nav-link, .mobile-nav-link').on('click', function (e) {
        e.preventDefault();
        const page = $(this).data('page');
        const titleText = $(this).find('span').first().text();

        $('.nav-link').removeClass(activeClasses).addClass(inactiveClasses);
        $(`.nav-link[data-page="${page}"]`).removeClass(inactiveClasses).addClass(activeClasses);
        
        $('#current-title').text(titleText + (page === 'home' ? ' Feed' : ''));
        loadContent(page);
    });

    function loadContent(section) {
        const $container = $('#main-content');
        $container.animate({ opacity: 0 }, 200, function () {
            $container.html(`
                <div class="col-span-full flex flex-col items-center justify-center py-20">
                    <div class="w-10 h-10 border-4 border-purple-100 border-t-purple-600 rounded-full animate-spin"></div>
                </div>
            `).animate({ opacity: 1 }, 200);

            setTimeout(() => {
                if (section === 'profile') loadUserProfile();
                else if (section === 'notifications') renderNotifications($container);
                else renderGrid($container, section);
            }, 500);
        });
    }

    // Default Grid (Home)
    function renderGrid($container, section) {
        let html = '';
        for (let i = 1; i <= 3; i++) {
            html += `
                <div class="group bg-white rounded-[2.5rem] p-4 border border-gray-100 hover:border-purple-200 hover:shadow-2xl transition-all duration-500">
                    <div class="h-52 bg-gray-50 rounded-[2rem] mb-4 overflow-hidden relative">
                        <img src="https://picsum.photos/400/400?random=${section + i}" class="w-full h-full object-cover group-hover:scale-105 transition-transform">
                    </div>
                    <div class="px-2"><h4 class="text-lg font-bold text-gray-800 capitalize">${section} Item ${i}</h4></div>
                </div>`;
        }
        $container.html(html);
    }
});