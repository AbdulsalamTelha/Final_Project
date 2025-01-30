// إخفاء حقل واحد فقط من حقول كلمات المرور  ... استخدمت في صفحة تسجيل الدخول
function toggleOneFieldPasswordVisibility(inputId, icon) {
    const input = document.getElementById(inputId);
    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        input.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}


// إخفاء البقية وإظهار حقل واحد فقط ... استخدمت في صفحة تغيير كلمة المرور
function togglePasswordVisibility(inputId, icon) {
    // الحصول على جميع حقول كلمات المرور
    const passwordFields = document.querySelectorAll('input[type="password"], input[type="text"]');

    // الحصول على الحقل الحالي
    const currentField = document.getElementById(inputId);

    // إذا كان الحقل الحالي مخفيًا، قم بإظهاره وإخفاء الباقي
    if (currentField.type === "password") {
        // إخفاء جميع كلمات المرور الأخرى
        passwordFields.forEach(field => {
            if (field.id !== inputId && field.type === "text") {
                field.type = "password";
                const otherIcon = field.parentElement.querySelector('.fa-eye-slash');
                if (otherIcon) {
                    otherIcon.classList.remove("fa-eye-slash");
                    otherIcon.classList.add("fa-eye");
                }
            }
        });

        // إظهار الحقل الحالي
        currentField.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        // إخفاء الحقل الحالي
        currentField.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}