// common-header.js

$(document).ready(async function () {
    const API_URL = "https://libretranslate.de/translate"; // LibreTranslate endpoint
    const DEFAULT_LANG = "en";
    const $dropdown = $("#language-dropdown");

    // Languages including Indian languages
    const languages = {
        "English": "en",
        "Hindi": "hi",
        "Bengali": "bn",
        "Gujarati": "gu",
        "Marathi": "mr",
        "Tamil": "ta",
        "Telugu": "te",
        "Kannada": "kn",
        "Malayalam": "ml",
        "Punjabi": "pa",
        "Urdu": "ur",
        "Spanish": "es",
        "French": "fr",
        "German": "de"
    };

    // Populate dropdown
    for (const [name, code] of Object.entries(languages)) {
        $dropdown.append(`<option value="${code}">${name}</option>`);
    }

    // Load saved language
    const savedLang = localStorage.getItem("lang") || DEFAULT_LANG;
    $dropdown.val(savedLang);

    // Function to translate text
    const translateText = async (text, target) => {
        if (!text || target === DEFAULT_LANG) return text;
        try {
            const res = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    q: text,
                    source: "en",
                    target: target,
                    format: "text"
                })
            });
            const data = await res.json();
            return data.translatedText || text;
        } catch (err) {
            console.error("Translation error:", err);
            return text;
        }
    };

    // Translate static header elements
    const translateHeader = async (lang) => {
        const items = [
            { selector: "a[href='home.html'] span", text: "HOME" },
            { selector: "a[href='search.html'] span", text: "SEARCH" },
            { selector: "a[href='quickTake.html'] span", text: "QUICK TAKE" },
            { selector: "a[href='coverage.html'] span", text: "COVERAGE" },
            { selector: "a[href='trending.html'] span", text: "TRENDING" },
            { selector: "a[href='notification.html'] span", text: "NOTIFICATION" },
            { selector: "a[href='favorites.html'] span", text: "FAVORITES" },
            { selector: "a[href='profile.html'] span", text: "PROFILE" },
            { selector: "a[href='settings.html'] span", text: "SETTINGS" }
        ];

        for (const item of items) {
            const translated = await translateText(item.text, lang);
            $(item.selector).text(translated);
        }

        // Header title
        const headerTitle = $("header h2");
        const titleText = headerTitle.text().trim();
        const translatedTitle = await translateText(titleText, lang);
        headerTitle.text(translatedTitle);
    };

    // Translate dynamic content from backend
    const translateDynamicContent = async (lang) => {
        $(".article-content, #article-title, .like-text, #article-buttons button, #categories span, #tags span").each(async function () {
            const el = $(this);
            const original = el.data("original-text") || el.text();
            el.data("original-text", original);
            const translated = await translateText(original, lang);
            el.text(translated);
        });
    };

    // Initial translation
    translateHeader(savedLang);
    translateDynamicContent(savedLang);

    // When dropdown changes
    $dropdown.change(async function () {
        const selectedLang = $(this).val();
        localStorage.setItem("lang", selectedLang);
        await translateHeader(selectedLang);
        await translateDynamicContent(selectedLang);
    });
});
