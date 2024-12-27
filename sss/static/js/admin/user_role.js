document.addEventListener('DOMContentLoaded', function () {
    const roleField = document.querySelector('#id_role');  // تحديد حقل الدور
    
    // تحديد الحقول الخاصة بكل دور
    const studentFields = document.querySelectorAll('.student-field');
    const instructorFields = document.querySelectorAll('.instructor-field');
    const adminFields = document.querySelectorAll('.admin-field');
    
    // الحقول الإضافية الخاصة بالدور ADMIN
    const fieldsToToggle = ['is_staff', 'is_superuser'];

    // دالة لتبديل الحقول بناءً على الدور
    function toggleFields() {
        const role = roleField.value;  // الحصول على الدور المحدد

        // إخفاء جميع الحقول أولاً
        studentFields.forEach(field => field.style.display = 'none');
        instructorFields.forEach(field => field.style.display = 'none');
        adminFields.forEach(field => field.style.display = 'none');

        // إظهار الحقول بناءً على الدور المحدد
        if (role === 'STUDENT') {
            studentFields.forEach(field => field.style.display = 'block');
        } else if (role === 'INSTRUCTOR') {
            instructorFields.forEach(field => field.style.display = 'block');
        } else if (role === 'ADMIN') {
            adminFields.forEach(field => field.style.display = 'block');
        }

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
