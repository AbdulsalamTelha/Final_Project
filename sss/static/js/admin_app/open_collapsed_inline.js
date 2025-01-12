document.addEventListener('DOMContentLoaded', function () {
    const fieldsets = document.querySelectorAll('fieldset.module.collapse');
    fieldsets.forEach(fieldset => {
        const details = fieldset.querySelector('details');
        const errors = fieldset.querySelectorAll('.errorlist');
        if (errors.length > 0) {
            // أضف خاصية open لفتح التفاصيل
            details.setAttribute('open', '');
        } else {
            // إزالة خاصية open إذا كانت غير موجودة
            details.removeAttribute('open');
        }
    });
});
