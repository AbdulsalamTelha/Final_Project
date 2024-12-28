document.addEventListener('DOMContentLoaded', function () {
    const roleField = document.querySelector('#id_role');  // تحديد حقل الدور

    // الحقول الإضافية الخاصة بالدور ADMIN
    const fieldsToToggle = ['is_staff', 'is_superuser'];

    // دالة لتبديل الحقول بناءً على الدور
    function toggleFields() {
        const role = roleField.value;  // الحصول على الدور المحدد

        //-----------------------------Admin--------------------
        // إظهار أو إخفاء الحقول الإضافية بناءً على الدور ADMIN
        fieldsToToggle.forEach(field => {
            const fieldContainer = document.querySelector(`.form-row.field-${field}`);
            if (fieldContainer) {
                if (role === 'ADMIN') {
                    fieldContainer.style.display = '';  // إظهار الحقل
                } else {
                    fieldContainer.style.display = 'none';  // إخفاء الحقل
                }
            }
        });

    }

    // تنفيذ عند تحميل الصفحة أو عند تغيير الدور
    roleField.addEventListener('change', toggleFields);
    toggleFields();  // تأكد من تنفيذ عند تحميل الصفحة
});
