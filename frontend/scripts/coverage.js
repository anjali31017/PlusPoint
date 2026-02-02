// // // coverage.js


$(document).ready(async function () {
  // Ensure user is logged in
  const loggedIn = await isLoggedIn();
  if (!loggedIn) return;

  const $contentWrapper = $("#content-wrapper");
  const $scrollContainer = $("main"); // scrollable container

  let page = 1;
  const firstPageSize = 10; // load 10 initially
  const pageSize = 6;       // load 6 for subsequent pages
  let loading = false;
  let noMoreData = false;

  function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  }

  function renderArticles(articles) {
    if (!articles || articles.length === 0) {
      noMoreData = true;
      if (page === 1) {
        $contentWrapper.append(`
          <div class="text-center text-gray-500 text-lg py-20">
            No articles found.
          </div>
        `);
      }
      return;
    }

    articles.forEach((article, index) => {
      const tagsHtml = article.tags?.map(tag =>
        `<span class="text-[10px] font-bold text-purple-700 bg-purple-100 px-2 py-1 rounded-full mr-1">${tag}</span>`
      ).join(" ") || "";

      const categoriesHtml = article.category?.map(cat =>
        `<span class="text-[10px] font-bold text-white bg-purple-700 px-2 py-1 rounded-full mr-1">${cat}</span>`
      ).join(" ") || "";

      const card = $(`
        <div class="group cursor-pointer bg-white p-6 hover:border-purple-200 hover:shadow-2xl transition-all duration-500">
          <div class="flex justify-between items-start mb-3">
            <h4 class="text-lg font-bold text-gray-800 group-hover:text-purple-700 transition-colors">
              ${article.title}
            </h4>
            <div class="text-sm text-gray-400 flex items-center gap-1">
              <i data-lucide="heart" class="w-4 h-4"></i> ${article.like_count || 0}
            </div>
          </div>

          <div class="flex flex-wrap gap-2 mb-3">
            ${tagsHtml} ${categoriesHtml}
          </div>

          <div class="text-xs text-gray-400">Published: ${formatDate(article.published_at)} ${new Date(article.published_at).toLocaleTimeString()}</div>
        </div>
      `);

      card.on("click", () => {
        window.location.href = `article.html?article_id=${article.id}`;
      });

      $contentWrapper.append(card);

      if (index !== articles.length) {
        $contentWrapper.append('<div class="border-t-2 border-purple-100 my-1"></div>');
      }
    });

    lucide.createIcons();
  }

  async function loadNextPage(size = pageSize) {
    if (loading || noMoreData) return;
    loading = true;

    try {
      const res = await ajaxWithJWT({
        url: `http://127.0.0.1:5000/api/article/coverage?page=${page}&page_size=${size}`,
        method: "GET",
      });

      if (res.status === 1) {
        renderArticles(res.data);
        if (res.data.length < size) noMoreData = true;
        page += 1;
      } else {
        Swal.fire({
          icon: "error",
          title: "Failed to load coverage",
          text: res.message || "Unknown error",
        });
      }
    } catch (err) {
      console.error(err);
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Failed to fetch coverage data",
      });
    } finally {
      loading = false;
    }
  }

  // Initial load with 10 articles
  await loadNextPage(firstPageSize);

  // If content doesn't fill the container, load more automatically
  async function checkAndLoadMore() {
    while (!noMoreData && $scrollContainer[0].scrollHeight <= $scrollContainer.height()) {
      await loadNextPage();
    }
  }

  await checkAndLoadMore();

  // Infinite scroll
  $scrollContainer.on("scroll", async function () {
    const scrollTop = $(this).scrollTop();
    const scrollHeight = $(this)[0].scrollHeight;
    const containerHeight = $(this).height();

    if (scrollTop + containerHeight + 100 >= scrollHeight) {
      await loadNextPage();
    }
  });
});





// // coverage.js

// // import { ajaxWithJWT, isLoggedIn } from "./auth.js";

// $(document).ready(async function () {
//   // Ensure user is logged in before doing anything
//   const loggedIn = await isLoggedIn();
//   if (!loggedIn) return;

//   const $contentWrapper = $("#content-wrapper");
//   let page = 1;
//   const pageSize = 6;
//   let loading = false;
//   let noMoreData = false;

//   // Format date nicely
//   function formatDate(isoString) {
//     const date = new Date(isoString);
//     return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
//   }

//   function renderArticles(articles) {
//   if (!articles || articles.length === 0) {
//     noMoreData = true;

//     // Show a friendly message if this is the first page
//     if (page === 1) {
//       $contentWrapper.append(`
//         <div class="text-center text-gray-500 text-lg py-20">
//           No articles found.
//         </div>
//       `);
//     }

//     return;
//   }

//   articles.forEach((article, index) => {
//     const tagsHtml = article.tags?.map(tag =>
//       `<span class="text-[10px] font-bold text-purple-700 bg-purple-100 px-2 py-1 rounded-full mr-1">${tag}</span>`
//     ).join(" ") || "";

//     const categoriesHtml = article.category?.map(cat =>
//       `<span class="text-[10px] font-bold text-white bg-purple-700 px-2 py-1 rounded-full mr-1">${cat}</span>`
//     ).join(" ") || "";

//     const card = $(`
//       <div class="group cursor-pointer bg-white p-6 hover:border-purple-200 hover:shadow-2xl transition-all duration-500">
//         <div class="flex justify-between items-start mb-3">
//           <h4 class="text-lg font-bold text-gray-800 group-hover:text-purple-700 transition-colors">
//             ${article.title}
//           </h4>
//           <div class="text-sm text-gray-400 flex items-center gap-1">
//             <i data-lucide="heart" class="w-4 h-4"></i> ${article.like_count || 0}
//           </div>
//         </div>

//         <div class="flex flex-wrap gap-2 mb-3">
//           ${tagsHtml} ${categoriesHtml}
//         </div>

//         <div class="text-xs text-gray-400">Published: ${formatDate(article.published_at)} ${new Date(article.published_at).toLocaleTimeString()}</div>
//       </div></div>
//       </div>
//     `);
            
//     // Make card clickable
//     card.on("click", () => {
//       window.location.href = `article.html?article_id=${article.id}`;
//     });

//     $contentWrapper.append(card);

//     // Add purple line after card except the last one
//     if (index !== articles.length - 1) {
//       const divider = $('<div class="border-t-2 border-purple-100 my-1"></div>');
//       $contentWrapper.append(divider);
//     }
//   });

//   lucide.createIcons(); // refresh icons
// }


//   // Load next page
//   async function loadNextPage() {
//     if (loading || noMoreData) return;
//     loading = true;

//     try {
//       const res = await ajaxWithJWT({
//         url: `http://127.0.0.1:5000/api/article/coverage?page=${page}&page_size=${pageSize}`,
//         method: "GET",
//       });

//       if (res.status === 1) {
//         renderArticles(res.data);
//         if (res.data.length < pageSize) noMoreData = true;
//         page += 1;
//       } else {
//         Swal.fire({
//           icon: "error",
//           title: "Failed to load coverage",
//           text: res.message || "Unknown error",
//         });
//       }
//     } catch (err) {
//       console.error(err);
//       Swal.fire({
//         icon: "error",
//         title: "Error",
//         text: "Failed to fetch coverage data",
//       });
//     } finally {
//       loading = false;
//     }
//   }

//   // Initial load
//   await loadNextPage();

//   // Infinite scroll
//   $contentWrapper.on("scroll", async function () {
//     const scrollTop = $(this).scrollTop();
//     const scrollHeight = $(this)[0].scrollHeight;
//     const containerHeight = $(this).height();

//     if (scrollTop + containerHeight + 100 >= scrollHeight) {
//       await loadNextPage();
//     }
//   });
// });


