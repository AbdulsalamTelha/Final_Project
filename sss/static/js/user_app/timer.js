document.addEventListener("DOMContentLoaded", function () {
    // الحصول على time_left من عنصر HTML مخفي في الصفحة
    const timeLeftElement = document.getElementById("time-left");
    if (!timeLeftElement) {
        console.error("Element with id 'time-left' not found in DOM.");
        return;
    }

    // قراءة قيمة الوقت المتبقي
    let timeLeft = parseInt(timeLeftElement.value, 10); // القيمة تأتي من عنصر مخفي
    if (isNaN(timeLeft)) {
        console.error("Invalid time_left value.");
        return;
    }

    const timerElement = document.getElementById("timer");
    if (!timerElement) {
        console.error("Element with id 'timer' not found in DOM.");
        return;
    }

    function updateTimer() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        if (timeLeft > 0) {
            timeLeft--;
            setTimeout(updateTimer, 1000);
        } else {
            timerElement.textContent = "OTP Expired";
            const resendButton = document.getElementById("resend-button");
            if (resendButton) {
                resendButton.style.display = "block"; // Show the resend button
            }
        }
    }

    updateTimer();
});
