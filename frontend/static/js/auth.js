// Client-side validation for auth forms
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('#login form');
    const registerForm = document.querySelector('#register form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = loginForm.querySelector('#email').value.trim();
            const password = loginForm.querySelector('#password').value.trim();
            
            if (!email || !password) {
                e.preventDefault();
                alert('Please fill in all fields');
            }
        });
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const name = registerForm.querySelector('#name').value.trim();
            const email = registerForm.querySelector('#email').value.trim();
            const rollNo = registerForm.querySelector('#roll_no').value.trim();
            const password = registerForm.querySelector('#password').value.trim();
            
            if (!name || !email || !rollNo || !password) {
                e.preventDefault();
                alert('Please fill in all fields');
                return;
            }
            
            if (password.length < 6) {
                e.preventDefault();
                alert('Password must be at least 6 characters long');
                return;
            }
            
            if (!/^\d+$/.test(rollNo)) {
                e.preventDefault();
                alert('Roll number should contain only numbers');
                return;
            }
            
            if (!/^\S+@\S+\.\S+$/.test(email)) {
                e.preventDefault();
                alert('Please enter a valid email address');
            }
        });
    }
});