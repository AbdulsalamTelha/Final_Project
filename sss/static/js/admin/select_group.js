document.addEventListener("DOMContentLoaded", function () {
    const departmentField = document.getElementById("id_department");
    const levelField = document.getElementById("id_level");
    const groupField = document.getElementById("id_group");

    // التحقق من وجود الحقول قبل المتابعة
    if (!departmentField || !levelField || !groupField) {
        console.warn("One or more fields (department, level, group) are missing.");
        return;
    }

    let currentGroup = groupField.value; // الاحتفاظ بالقيمة الحالية

    function updateGroups() {
        const department = departmentField.value;
        const level = levelField.value;
        
        if (department && level) {
            fetch(`/get-groups/?department=${department}&level=${level}`)
                .then(response => response.json())
                .then(data => {
                    const currentValue = groupField.value; // الاحتفاظ بالقيمة المختارة حاليًا
                    groupField.innerHTML = '<option value="">---------</option>'; // إعادة تعيين الحقل
                    data.groups.forEach(group => {
                        const option = document.createElement("option");
                        option.value = group.id;
                        option.textContent = group.display; // عرض النص بالتنسيق الجديد
                        if (group.id === currentValue) {
                            option.selected = true; // الاحتفاظ بالقيمة السابقة إذا كانت موجودة
                        }
                        groupField.appendChild(option);
                    });
                })
                .catch(error => console.error("Error fetching groups:", error));
        } else {
            groupField.innerHTML = '<option value="">---------</option>'; // إعادة تعيين الحقل إذا لم يتم تحديد القيم
        }
    }

    // تحميل المجموعات عند تحميل الصفحة
    // if (departmentField.value && levelField.value) {
    //     updateGroups();
    // }

    // الاستماع لتغيير قيم الحقول
    departmentField.addEventListener("change", updateGroups);
    levelField.addEventListener("change", updateGroups);
});
