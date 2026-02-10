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


