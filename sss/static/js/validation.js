/**
 * كائن يحتوي على الأنماط (Regex) المختلفة بناءً على فئة CSS
 */
const validationPatterns = {
    'validate-letters-only': /^[a-zA-Z ]*$/, // الحروف والمسافات فقط
    'validate-numbers-only': /^[0-9]*$/, // الأرقام فقط
    'validate-letters-numbers': /^[a-zA-Z0-9 ]*$/, // الحروف والأرقام والمسافات
    'validate-symbols-only': /^[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~ ]*$/, // الرموز فقط
    'validate-letters-numbers-symbols': /^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~ ]*$/ // الكل
};

/**
 * وظيفة للتحقق من الإدخال بناءً على النمط المحدد
 * @param {HTMLElement} inputField - عنصر الإدخال (Input/Textarea)
 * @param {string} className - اسم الفئة لتحديد النمط
 */
function validateInput(inputField, className) {
    const pattern = validationPatterns[className]; // اختيار النمط بناءً على الفئة
    if (!pattern) return; // إذا لم يكن هناك نمط محدد، لا تفعل شيئًا

    inputField.addEventListener('input', function () {
        const currentValue = inputField.value;
        if (!pattern.test(currentValue)) {
            inputField.value = currentValue.replace(new RegExp(`[^${pattern.source}]`, 'g'), ''); // إزالة الأحرف غير المسموح بها
            // alert(`Invalid input! Please follow the ${className.replace('validate-', '').replace('-', ' ')} pattern.`);
        }
    });
}

/**
 * تطبيق التحقق على جميع الحقول ذات الفئات المخصصة
 */
function applyValidation() {
    Object.keys(validationPatterns).forEach(className => {
        const fields = document.querySelectorAll(`.${className}`);
        fields.forEach(field => validateInput(field, className));
    });
}

/**
 * استدعاء الدالة عند تحميل الصفحة
 */
document.addEventListener('DOMContentLoaded', function () {
    applyValidation();
});
