document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        const messages = document.querySelectorAll('.fixed > div > div');
        messages.forEach(message => {
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 500); // إزالة الرسالة بعد انتهاء الانتقال
        });
    }, 5000); // 5000ms = 5 ثوانٍ
});
