// // تظهر القائمة عند تمرير الماوس على الصورة أو الاسم
// document.addEventListener('DOMContentLoaded', function () {
//     // مرجع للحاوية والقائمة
//     const profileContainer = document.getElementById('profileContainer');
//     const profileMenu = document.getElementById('profileMenu');

//     // إظهار القائمة عند تمرير الماوس على الحاوية (الصورة + الاسم)
//     profileContainer.addEventListener('mouseover', function () {
//         profileMenu.classList.remove('hidden');
//     });

//     // إخفاء القائمة عند إبعاد الماوس عن الحاوية
//     profileContainer.addEventListener('mouseout', function () {
//         profileMenu.classList.add('hidden');
//     });

//     // منع إخفاء القائمة عند النقر داخلها
//     profileMenu.addEventListener('click', function (event) {
//         event.stopPropagation();
//     });
// });


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

////////////////////////////

    // // زر الإشعارات
    // const notificationsButton = document.getElementById('notificationsButton');
    // const notificationCount = document.getElementById('notificationCount');

    // notificationsButton.addEventListener('click', function () {
    //     // فتح قائمة الإشعارات (اختياري: أضف نافذة منبثقة)
    //     alert('No new notifications.');
    //     notificationCount.classList.add('hidden'); // إخفاء العدد بعد القراءة
    // });

    // زر الإشعارات وعناصر القائمة
    const notificationsButton = document.getElementById('notificationsButton');
    const notificationsMenu = document.getElementById('notificationsMenu');
    const notificationCount = document.getElementById('notificationCount');

    // إظهار وإخفاء القائمة عند الضغط على زر الإشعارات
    notificationsButton.addEventListener('click', function (event) {
        event.stopPropagation(); // منع إغلاق القائمة إذا تم النقر على الزر
        notificationsMenu.classList.toggle('hidden');
    });

    // إخفاء القائمة عند النقر خارجها
    document.addEventListener('click', function () {
        notificationsMenu.classList.add('hidden');
    });

    // مثال لإزالة العدد عند فتح القائمة
    notificationsButton.addEventListener('click', function () {
        notificationCount.textContent = '';
        notificationCount.classList.add('hidden');
    });

    // زر وضع الليل/الصباح
    // const themeToggleButton = document.getElementById('themeToggleButton');
    // const themeIcon = document.getElementById('themeIcon');

    // themeToggleButton.addEventListener('click', function () {
    //     document.documentElement.classList.toggle('dark');
    //     if (document.documentElement.classList.contains('dark')) {
    //         themeIcon.classList.replace('fa-moon', 'fa-sun');
    //     } else {
    //         themeIcon.classList.replace('fa-sun', 'fa-moon');
    //     }
    // });


    // themeToggleButton.addEventListener('click', () => {
    //     document.documentElement.classList.toggle('dark');
    //     themeIcon.classList.toggle('fa-sun');
    //     themeIcon.classList.toggle('fa-moon');
    // });



    // const themeToggleButton = document.getElementById('themeToggleButton');
    // const themeIcon = document.getElementById('themeIcon');

    // // استرجاع الوضع الليلي من LocalStorage
    // if (localStorage.getItem('theme') === 'dark') {
    //     document.documentElement.classList.add('dark');
    //     themeIcon.classList.add('fa-sun');
    //     themeIcon.classList.remove('fa-moon');
    // }

    // themeToggleButton.addEventListener('click', () => {
    //     document.documentElement.classList.toggle('dark');
    //     const isDarkMode = document.documentElement.classList.contains('dark');

    //     // تحديث الأيقونة
    //     themeIcon.classList.toggle('fa-sun', isDarkMode);
    //     themeIcon.classList.toggle('fa-moon', !isDarkMode);

    //     // حفظ الحالة في LocalStorage
    //     localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    // });


    const themeToggleButton = document.getElementById('themeToggleButton');
    const themeIcon = document.getElementById('themeIcon');

    // Check localStorage for theme
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
