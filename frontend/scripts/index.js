function togglePassword(id, btn) {
    const input = document.getElementById(id);
    if (input.type === "password") {
        input.type = "text";
        btn.textContent = "🙈"; // eye closed
    } else {
        input.type = "password";
        btn.textContent = "👁️"; // eye open
    }
}




function truncateWords(str, numWords) {
    if (!str) return "";
    const words = str.split(/\s+/); // split by spaces
    if (words.length <= numWords) return str;
    return words.slice(0, numWords).join(" ") + "...";
}


function googleTranslateElementInit() {
new google.translate.TranslateElement({
pageLanguage: 'en'
}, 'google_translate_element');
}



// index.js
// $(document).ready(function () {
//   const $sidebar = $('aside');

//   // Add desktop toggle button
//   const desktopToggle = $('<button id="desktopSidebarToggle" class="hidden md:flex absolute top-5 right-0 z-40 p-2 bg-purple-600 text-white rounded-l-lg shadow-lg">⮜</button>');
//   $sidebar.append(desktopToggle);

//   // Add mobile toggle button
//   const mobileToggle = $('<button id="mobileSidebarToggle" class="fixed top-4 left-4 z-50 p-3 bg-purple-600 text-white rounded-lg shadow-lg md:hidden">☰</button>');
//   $('body').append(mobileToggle);

//   // Initialize classes
//   function initSidebar() {
//     if ($(window).width() >= 768) {
//       // Desktop: expanded by default
//       $sidebar.removeClass('w-20');
//       $sidebar.addClass('w-72');
//       $sidebar.removeClass('-translate-x-full translate-x-0');
//       $('#desktopSidebarToggle').show();
//     } else {
//       // Mobile: hidden by default
//       $sidebar.addClass('-translate-x-full');
//       $sidebar.removeClass('w-72 w-20');
//       $('#desktopSidebarToggle').hide();
//     }
//   }

//   initSidebar();

//   // Desktop toggle click
//   $('#desktopSidebarToggle').click(function () {
//     if ($sidebar.hasClass('w-72')) {
//       // Collapse
//       $sidebar.removeClass('w-72').addClass('w-20');
//       $(this).text('⮞');
//       $sidebar.find('nav a span').hide(); // hide text
//     } else {
//       // Expand
//       $sidebar.removeClass('w-20').addClass('w-72');
//       $(this).text('⮜');
//       $sidebar.find('nav a span').show(); // show text
//     }
//   });

//   // Mobile toggle click
//   $('#mobileSidebarToggle').click(function () {
//     $sidebar.toggleClass('translate-x-0 -translate-x-full');
//   });

//   // Close mobile sidebar when clicking outside
//   $(document).click(function (e) {
//     if ($(window).width() < 768) {
//       if (!$sidebar.is(e.target) && $sidebar.has(e.target).length === 0 && !$('#mobileSidebarToggle').is(e.target)) {
//         $sidebar.addClass('-translate-x-full').removeClass('translate-x-0');
//       }
//     }
//   });

//   // Handle resize
//   $(window).resize(initSidebar);

//   // Initialize icons
//   lucide.createIcons();

//   // Fade in body
//   $('body').fadeIn(400);
// });



// // index.js
// $(document).ready(function () {
//   // Inject Merriweather font globally
//   $('head').append('<link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700;900&display=swap" rel="stylesheet">');
//   $('body, body *').css('font-family', '"Merriweather", serif');

//   // Sidebar toggle button for mobile
//   const toggleBtn = $('<button id="sidebarToggle" class="fixed top-4 left-4 z-50 p-3 bg-purple-600 text-white rounded-lg shadow-lg md:hidden">☰</button>');
//   $('body').append(toggleBtn);

//   const $sidebar = $('aside');

//   // Initialize sidebar position
//   function resetSidebar() {
//     if ($(window).width() < 768) {
//       $sidebar.addClass('-translate-x-full').removeClass('translate-x-0');
//     } else {
//       $sidebar.removeClass('-translate-x-full translate-x-0');
//     }
//   }
//   resetSidebar();

//   // Toggle sidebar on button click
//   $('#sidebarToggle').click(function () {
//     $sidebar.toggleClass('translate-x-0 -translate-x-full');
//   });

//   // Close sidebar when clicking outside on mobile
//   $(document).click(function (e) {
//     if ($(window).width() < 768) {
//       if (!$sidebar.is(e.target) && $sidebar.has(e.target).length === 0 && !$('#sidebarToggle').is(e.target)) {
//         $sidebar.addClass('-translate-x-full').removeClass('translate-x-0');
//       }
//     }
//   });

//   // Handle window resize
//   $(window).resize(resetSidebar);

//   // Initialize Lucide icons
//   lucide.createIcons();

//   // Fade in body
//   $('body').fadeIn(400);
// });

