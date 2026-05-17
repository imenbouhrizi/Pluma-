const passwordInput = document.getElementById("signupPassword");
const ruleLength = document.getElementById("ruleLength");
const ruleUppercase = document.getElementById("ruleUppercase");

if (passwordInput) {
    passwordInput.addEventListener("input", function () {
        const password = passwordInput.value;

        if (password.length >= 8) {
            ruleLength.classList.add("valid");
        } else {
            ruleLength.classList.remove("valid");
        }

        if (/[A-Z]/.test(password)) {
            ruleUppercase.classList.add("valid");
        } else {
            ruleUppercase.classList.remove("valid");
        }

          
        if(/\d/.test(password)){
            ruleNumber.classList.add("valid");
        } else {
            ruleNumber.classList.remove("valid");
        }
    });
}