// Script to save username and password

// استرجاع القيم إذا كانت محفوظة
window.onload = function () {
    const savedUsername = localStorage.getItem('username');
    const savedPassword = localStorage.getItem('password');
    const rememberChecked = localStorage.getItem('remember') === 'true';

    if (savedUsername && savedPassword && rememberChecked) {
        document.getElementById('username').value = savedUsername;
        document.getElementById('password').value = savedPassword;
        document.getElementById('remember').checked = true;
    }
};

// حفظ القيم إذا تم تحديد "تذكرني"
document.querySelector('form').addEventListener('submit', function () {
    const remember = document.getElementById('remember').checked;
    if (remember) {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        localStorage.setItem('username', username);
        localStorage.setItem('password', password);
        localStorage.setItem('remember', true);
    } else {
        localStorage.removeItem('username');
        localStorage.removeItem('password');
        localStorage.setItem('remember', false);
    }
});