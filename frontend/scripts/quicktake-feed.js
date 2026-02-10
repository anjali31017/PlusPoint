// // // quicktake-feed.js
// // // Reels / Shorts style vertical feed with SSE + state cache


// quicktake-feed.js
// Instagram / Shorts style vertical feed with SSE + state cache

let eventSource = null;

// In-memory cache
const quicktakeState = {}; // articleId -> { liked, likes, endorsed, endorse, reported }

const $wrapper = $("#content-wrapper");

// =============================
// INIT
// =============================

$(document).ready(async function () {
  const ok = await isLoggedIn();
  if (!ok) return;

  setupScrollSnap();
  connectSSE();
});

// =============================
// BACKGROUNDS
// =============================

const pastelGradients = [
  ["#fde68a", "#fbcfe8"],
  ["#bfdbfe", "#ddd6fe"],
  ["#a7f3d0", "#fef3c7"],
  ["#fecaca", "#fde68a"],
  ["#e9d5ff", "#bae6fd"],
  ["#fbcfe8", "#bbf7d0"],
];

function randomGradient() {
  const pair =
    pastelGradients[Math.floor(Math.random() * pastelGradients.length)];
  return `linear-gradient(135deg, ${pair[0]}, ${pair[1]})`;
}

// =============================
// SCROLL SNAP
// =============================

function setupScrollSnap() {
  $wrapper.css({
    height: "calc(100vh - 90px)",
    overflowY: "scroll",
    scrollSnapType: "y mandatory",
  });
}

// =============================
// SSE
// =============================

function connectSSE() {
  const token = getAccessToken();
  if (!token) return;

  const url = `http://127.0.0.1:5000/sse/feed?token=${token}`;

  eventSource = new EventSource(url);

  eventSource.onmessage = function (event) {
    if (!event.data) return;

    const data = JSON.parse(event.data);

    if (data.type === "heartbeat") return;

    renderQuickTake(data);
  };

  eventSource.onerror = function () {
    console.error("SSE disconnected — retrying...");
    eventSource.close();
    setTimeout(connectSSE, 3000);
  };
}

// =============================
// RENDER REEL
// =============================

function renderQuickTake(article) {
  const id = article.article_id;

  if ($(`#qt-${id}`).length) return;

  if (!quicktakeState[id]) {
    quicktakeState[id] = {
      liked: article.liked || false,
      likes: article.likes || 0,
      endorsed: article.endorsed || false,
      endorse: article.endorse || 0,
      reported: article.reported || false,
    };
  }

  // <div class="absolute inset-0" style="background:${randomGradient()}"></div>

  const state = quicktakeState[id];

  const $reel = $(`
<section
  id="qt-${id}"
  class="relative h-[100vh] w-full snap-start flex items-start justify-center">

  <div class="absolute inset-0 bg-slate-50"></div>

  <div class="relative z-10 w-[92%] max-w-6xl p-10">

    <div class="grid grid-cols-1 md:grid-cols-[1fr_220px] gap-8">

      <!-- CONTENT -->
      <div>

        <div class="firm-link text-lg font-bold text-purple-700 cursor-pointer">
          @${article.firm_username}
        </div>

        <h1 class="mt-5 text-4xl md:text-5xl font-black leading-tight">
          ${article.title}
        </h1>

        <p class="mt-5 text-lg text-gray-800 max-w-3xl">
          ${article.summary || article.quick_take || ""}
        </p>

        <div class="mt-4 flex gap-2 flex-wrap text-sm text-blue-700">
          ${
            article.category
              ? article.category
                  .map(
                    (t) =>
                      `<span class="px-3 py-1 rounded-full bg-blue-100">${t}</span>`
                  )
                  .join("")
              : ""
          }
          ${
            article.is_hot
              ? `<span class="px-3 py-1 text-xs rounded-full bg-red-600 text-white">
                  HOT
                </span>`
              : ""
          }
        </div>

        <div class="mt-3 flex gap-2 flex-wrap text-sm text-purple-700">
          ${
            article.tags
              ? article.tags
                  .map(
                    (t) =>
                      `<span class="px-3 py-1 rounded-full bg-purple-100">#${t}</span>`
                  )
                  .join("")
              : ""
          }
        </div>

        <button
          class="view-btn mt-8 bg-black text-white px-10 py-3 rounded-full
                 text-sm font-semibold">
          View Full Article →
        </button>

      </div>

      <!-- ACTION PANEL -->
      <div
        class="action-panel bg-white/55 backdrop-blur-xl rounded-3xl 
               p-5 shadow-lg flex flex-col justify-center space-y-4">

        <div class="action-row like-row flex justify-between cursor-pointer">
          <span class="like-label">❤️ Like</span>
          <span class="like-count">${state.likes}</span>
        </div>

        <div class="action-row endorse-row flex justify-between cursor-pointer">
          <span class="endorse-label">⭐ Endorse</span>
          <span class="endorse-count">${state.endorse}</span>
        </div>

        <div class="action-row copy-row cursor-pointer">
          🔗 Copy Link
        </div>

        <div class="action-row report-row cursor-pointer text-red-600">
          🚩 Report
        </div>

      </div>

    </div>
  </div>

</section>
`);

  // =============================
  // EVENTS
  // =============================

  $reel.find(".firm-link").on("click", () => {
    location.href = `/src/firm.html?firm_id=${article.firm_id}`;
  });

  $reel.find(".view-btn").on("click", () => {
    location.href = `/src/article.html?article_id=${id}`;
  });

  const $likeRow = $reel.find(".like-row");
  initLikeButton($likeRow, id);

  $likeRow.on("click", () => {
    const s = quicktakeState[id];
    s.liked = !s.liked;
    s.likes += s.liked ? 1 : -1;
    updateCounts($reel, s);
  });

  const $endorseRow = $reel.find(".endorse-row");
  initEndorseButton($endorseRow, "article", id);

  $endorseRow.on("click", () => {
    const s = quicktakeState[id];
    s.endorsed = !s.endorsed;
    s.endorse += s.endorsed ? 1 : -1;
    updateCounts($reel, s);
  });

  const $reportRow = $reel.find(".report-row");
  initReportButton($reportRow, "article", id);

  // COPY
  $reel.find(".copy-row").on("click", () => {
    const url = `${location.origin}/src/article.html?article_id=${id}`;
    navigator.clipboard.writeText(url);

    Swal.fire({
      toast: true,
      position: "bottom",
      icon: "success",
      title: "Link copied",
      showConfirmButton: false,
      timer: 1200,
    });
  });

  // 🔥 APPLY INITIAL STATE FROM BACKEND
  applyInitialState($reel, id);

  $wrapper.append($reel);
}

// =============================
// APPLY INITIAL STATE
// =============================

function applyInitialState($reel, id) {
  const state = quicktakeState[id];

  if (state.liked) {
    $reel.find(".like-row").addClass("font-bold text-red-600");
    $reel.find(".like-label").text("❤️ Liked");
  }

  if (state.endorsed) {
    $reel.find(".endorse-row").addClass("font-bold text-purple-700");
    $reel.find(".endorse-label").text("⭐ Endorsed");
  }

  if (state.reported) {
    $reel
      .find(".report-row")
      .addClass("opacity-50 pointer-events-none")
      .text("🚩 Already Reported");
  }

  updateCounts($reel, state);
}

// =============================
// UPDATE UI
// =============================

function updateCounts($reel, state) {
  $reel.find(".like-count").text(state.likes);
  $reel.find(".endorse-count").text(state.endorse);

  $reel
    .find(".like-row")
    .toggleClass("font-bold text-red-600", state.liked);

  $reel
    .find(".endorse-row")
    .toggleClass("font-bold text-purple-700", state.endorsed);

  $reel
    .find(".like-label")
    .text(state.liked ? "❤️ Liked" : "❤️ Like");

  $reel
    .find(".endorse-label")
    .text(state.endorsed ? "⭐ Endorsed" : "⭐ Endorse");
}

