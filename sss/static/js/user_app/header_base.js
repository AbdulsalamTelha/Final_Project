// تظهر القائمة عند تمرير الماوس على الحاوية (الصورة أو الاسم أو التبويبات)
document.addEventListener('DOMContentLoaded', function () {
    // الوظيفة العامة لإدارة القائمة المنسدلة
    const toggleDropdown = (containerSelector, menuSelector) => {
        const containers = document.querySelectorAll(containerSelector);
        containers.forEach(container => {
            const menu = container.querySelector(menuSelector);

            if (menu) {
                // إظهار القائمة عند تمرير الماوس على الحاوية
                container.addEventListener('mouseover', function () {
                    menu.classList.remove('hidden');
                });

                // إخفاء القائمة عند إبعاد الماوس عن الحاوية
                container.addEventListener('mouseout', function () {
                    menu.classList.add('hidden');
                });

                // منع إخفاء القائمة عند النقر داخلها
                menu.addEventListener('click', function (event) {
                    event.stopPropagation();
                });
            }
        });
    };

    // إدارة القائمة الخاصة بالصورة الشخصية
    toggleDropdown('#profileContainer', '#profileMenu');

    // إدارة القوائم المنسدلة للتبويبات
    toggleDropdown('.tab-container', '.tab-dropdown-menu');

    // زر وضع الليل/الصباح
    const themeToggleButton = document.getElementById('themeToggleButton');
    const themeIcon = document.getElementById('themeIcon');

    // Check localStorage for theme // استرجاع الوضع الليلي من LocalStorage
    if (localStorage.getItem('theme') === 'dark') {
        document.documentElement.classList.add('dark');
        themeIcon.classList.replace('fa-moon', 'fa-sun');
    }

    themeToggleButton.addEventListener('click', () => {
        document.documentElement.classList.toggle('dark');
        if (document.documentElement.classList.contains('dark')) {
        localStorage.setItem('theme', 'dark');
        themeIcon.classList.replace('fa-moon', 'fa-sun');
        } else {
        localStorage.setItem('theme', 'light');
        themeIcon.classList.replace('fa-sun', 'fa-moon');
        }
    });
});
