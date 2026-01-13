function loadUserProfile() {
    const token = localStorage.getItem('access_token');
    
    $.ajax({
        url: 'http://127.0.0.1:5000/api/user/profile',
        type: 'GET',
        headers: { 'Authorization': 'Bearer ' + token },
        success: function(response) {
            if (response.status === 1) renderProfileUI(response.data);
            else showProfileError(response.message);
        },
        error: function() { showProfileError("Server connection failed."); }
    });
}

function renderProfileUI(data) {
    const user = data.user_data;
    const $container = $('#main-content');
    const profileImg = user.profile_picture_url || '../images/profile.jpg';

    // 4-Tier KYC Logic
    let kycHTML = '';
    const status = data.kyc_status; 
    if (status === 'VERIFIED') {
        kycHTML = `<div class="text-green-600 font-bold text-xs uppercase tracking-widest flex items-center"><i data-lucide="check-circle" class="w-4 h-4 mr-2"></i> Verified</div>`;
    } else if (status === 'UNDER_REVIEW') {
        kycHTML = `<div class="text-blue-500 font-bold text-xs uppercase tracking-widest flex items-center"><i data-lucide="shield-alert" class="w-4 h-4 mr-2"></i> Under Review</div>`;
    } else if (status === 'REJECTED') {
        kycHTML = `<a href="kyc.html" class="inline-block bg-red-600 text-white text-[10px] px-3 py-1 rounded-lg font-bold">RE-SUBMIT KYC</a>`;
    } else { // PENDING
        kycHTML = `<a href="kyc.html" class="inline-block bg-purple-600 text-white text-[10px] px-3 py-1 rounded-lg font-bold">COMPLETE KYC</a>`;
    }

    const html = `
        <div class="col-span-full max-w-6xl mx-auto w-full animate-in fade-in duration-700 px-4">
            <div class="flex justify-between items-end mb-12 border-b border-gray-50 pb-6">
                <h2 class="text-4xl font-black text-gray-900 tracking-tighter">${user.username} Profile</h2>
                <button id="edit-profile-btn" class="px-8 py-3 bg-gray-900 text-white font-bold rounded-2xl hover:bg-black transition-all shadow-lg active:scale-95">Edit Profile</button>
            </div>

            <div class="flex flex-col lg:flex-row gap-20">
                <div class="w-full lg:w-1/3 space-y-12">
                    <div class="relative group w-full aspect-square max-w-[300px]">
                        <img src="${profileImg}" class="w-full h-full rounded-[3rem] object-cover ring-1 ring-gray-100 shadow-xl">
                        <label class="absolute inset-0 flex items-center justify-center bg-black/40 rounded-[3rem] opacity-0 group-hover:opacity-100 cursor-pointer transition-opacity">
                            <i data-lucide="camera" class="text-white w-10 h-10"></i>
                            <input type="file" id="edit-photo" class="hidden" accept="image/*">
                        </label>
                    </div>
                    <div class="space-y-8 pl-2">
                        <div><label class="text-[10px] font-black text-gray-300 uppercase tracking-widest">Verification Status</label><div class="mt-2">${kycHTML}</div></div>
                        <div><label class="text-[10px] font-black text-gray-300 uppercase tracking-widest">Transparency</label>
                             <button id="view-stats-btn" class="mt-2 flex items-center space-x-2 font-bold text-gray-800 hover:text-purple-600"><i data-lucide="bar-chart-2" class="w-5 h-5"></i><span>Stats</span></button></div>
                        <div><label class="text-[10px] font-black text-gray-300 uppercase tracking-widest">Account Created</label>
                             <p class="mt-1 font-bold text-gray-500">${new Date(user.created_at).toLocaleDateString('en-US', {month:'long', year:'numeric'})}</p></div>
                    </div>
                </div>

                <div class="flex-1 space-y-10">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div><label class="text-[10px] font-black text-gray-400 uppercase tracking-widest">First Name</label>
                             <input type="text" id="edit-fname" value="${user.first_name}" class="profile-input block w-full text-2xl font-bold bg-transparent border-none mt-1 outline-none" readonly></div>
                        <div><label class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Last Name</label>
                             <input type="text" id="edit-lname" value="${user.last_name}" class="profile-input block w-full text-2xl font-bold bg-transparent border-none mt-1 outline-none" readonly></div>
                    </div>
                    <div><label class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Username</label><p class="text-xl font-bold text-purple-600 mt-1">@${user.username}</p></div>
                    <div><label class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Email Address</label><p class="text-xl font-bold text-gray-800 mt-1">${user.email}</p></div>
                    <div><label class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Personal Bio</label>
                         <textarea id="edit-bio" rows="4" class="profile-input block w-full text-lg text-gray-600 bg-transparent border-none mt-2 resize-none outline-none" readonly>${user.bio || 'Tell the world about yourself...'}</textarea></div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 border-t border-gray-50 pt-8">
                        ${user.role.includes('P') && data.publisher_data ? `<div><label class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Publisher Access</label>
                        <p class="mt-1"><a href="#" class="text-purple-600 font-bold hover:underline publisher-link" data-pub-id="${data.publisher_data._id}">@${data.firm_data?.firm_username || 'portal'}</a></p></div>` : ''}
                        ${user.role.includes('F') && data.firm_data ? `<div><label class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Firm Ownership</label>
                        <p class="mt-1"><a href="#" class="text-blue-600 font-bold hover:underline firm-link" data-firm-id="${data.firm_data._id}">${data.firm_data.firm_name} (@${data.firm_data.firm_username})</a></p></div>` : ''}
                    </div>
                </div>
            </div>
        </div>`;

    $container.html(html);
    lucide.createIcons();
    setupProfileInteractions();
}

function setupProfileInteractions() {
    let isEditing = false;
    $('#edit-profile-btn').on('click', function() {
        isEditing = !isEditing;
        const $btn = $(this);
        const $inputs = $('.profile-input');

        if (isEditing) {
            $btn.text('Save Changes').addClass('bg-purple-600');
            $inputs.removeAttr('readonly').addClass('ring-2 ring-purple-100 px-2 rounded-lg bg-purple-50/20');
        } else {
            Swal.fire({ title: 'Success!', text: 'Profile Updated', icon: 'success', confirmButtonColor: '#7C3AED' });
            $btn.text('Edit Profile').removeClass('bg-purple-600').addClass('bg-gray-900');
            $inputs.attr('readonly', true).removeClass('ring-2 ring-purple-100 px-2 rounded-lg bg-purple-50/20');
        }
    });

    $('.publisher-link').on('click', function(e) {
        e.preventDefault();
        console.log("Fetching Publisher API for ID:", $(this).data('pub-id'));
    });

    $('.firm-link').on('click', function(e) {
        e.preventDefault();
        console.log("Fetching Firm API for ID:", $(this).data('firm-id'));
    });
}

function showProfileError(msg) {
    $('#main-content').html(`<div class="col-span-full py-20 text-center text-red-500 font-bold">${msg}</div>`);
}