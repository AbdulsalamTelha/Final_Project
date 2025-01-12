document.addEventListener('DOMContentLoaded', function () {
    // مرجع للزر والقائمة
    const profileMenuButton = document.getElementById('profileMenuButton');
    const profileMenu = document.getElementById('profileMenu');

    // إظهار/إخفاء القائمة عند الضغط على الصورة
    profileMenuButton.addEventListener('click', function (event) {
        profileMenu.classList.toggle('hidden');
        event.stopPropagation(); // منع التفاعل مع الأحداث الأخرى
    });

    // إخفاء القائمة عند الضغط خارجها
    document.addEventListener('click', function () {
        if (!profileMenu.classList.contains('hidden')) {
            profileMenu.classList.add('hidden');
        }
    });

    // منع إخفاء القائمة عند النقر داخلها
    profileMenu.addEventListener('click', function (event) {
        event.stopPropagation();
    });
});