function confirmDeletion(event) {
    event.preventDefault(); // منع الفورم من الإرسال مباشرة
    Swal.fire({
        title: 'Are you sure?',
        text: "This action cannot be undone!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            event.target.submit(); // إذا تم تأكيد الحذف، يتم إرسال الفورم
        }
    });
}