function passwdVisibility(button) {
    let inputPasswd = button.closest('p').querySelector('input');

    if (inputPasswd.type == 'password') {
        inputPasswd.type = 'text';
        button.classList.remove("fa-eye-slash");
        button.classList.add("fa-eye");
    }
    else {
        inputPasswd.type = 'password';        
        button.classList.remove('fa-eye');
        button.classList.add('fa-eye-slash');
    }
}