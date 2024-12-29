document.addEventListener('DOMContentLoaded', function() {
    const roleField = document.querySelector('select[name="role"]'); // حقل الدور

    // استخدام أسماء الكلاسات الصحيحة
    const studentInline = document.querySelector('#students-group'); // حقل الطالب
    const studentCourseInline = document.querySelector('#studentcourse-group'); 
    const instructorInline = document.querySelector('#instructors-group'); // حقل المدرس
    const adminInline = document.querySelector('#admins-group'); // حقل المسؤول

    function toggleInlines() {
        const selectedRole = roleField.value;

        // إخفاء جميع inlines
        if (studentInline) studentInline.style.display = 'none';
        if (studentCourseInline) studentCourseInline.style.display = 'none';
        if (instructorInline) instructorInline.style.display = 'none';
        if (adminInline) adminInline.style.display = 'none';

        // إظهار inline المناسب
        if (selectedRole === 'STUDENT') {
            if (studentInline) studentInline.style.display = 'block';
            if (studentCourseInline) studentCourseInline.style.display = 'block';
        } else if (selectedRole === 'INSTRUCTOR') {
            if (instructorInline) instructorInline.style.display = 'block';
        } else if (selectedRole === 'ADMIN') {
            if (adminInline) adminInline.style.display = 'block';
        }
    }

    // استدعاء الدالة عند تحميل الصفحة
    toggleInlines();
    // استدعاء الدالة عند تغيير الدور
    if (roleField) {
        roleField.addEventListener('change', toggleInlines);
    }
    
//////////////////////////////////

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