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