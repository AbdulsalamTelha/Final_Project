/**
 * وظيفة للتحقق من إدخال الحروف والأرقام والقوسين فقط
 * @param {HTMLElement} inputField - عنصر الإدخال (Input/Textarea)
 */
function validateInput(inputField) {
    const allowedPattern = /^[a-zA-Z0-9() ]*$/; // الحروف، الأرقام، الأقواس، والمسافات
    inputField.addEventListener('input', function () {
        const currentValue = inputField.value;
        if (!allowedPattern.test(currentValue)) {
            inputField.value = currentValue.replace(/[^a-zA-Z0-9() ]/g, ''); // إزالة الأحرف غير المسموح بها
            // alert('Only letters, numbers, parentheses, and spaces are allowed.');
        }
    });
}

/**
 * تطبيق التحقق على جميع الحقول ذات فئة CSS معينة
 * @param {string} className - اسم الفئة المطبقة على الحقول المستهدفة
 */
function applyValidationToClass(className) {
    const fields = document.querySelectorAll(`.${className}`);
    fields.forEach(validateInput);
}

document.addEventListener('DOMContentLoaded', function () {
    applyValidationToClass('validate-field'); // تطبيق التحقق على الحقول ذات الفئة المحددة
});
