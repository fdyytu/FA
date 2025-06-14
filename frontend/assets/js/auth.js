// Authentication JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Tab switching
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    // Password toggle functionality
    setupPasswordToggle('toggleLoginPassword', 'loginPassword');
    setupPasswordToggle('toggleRegisterPassword', 'registerPassword');
    setupPasswordToggle('toggleConfirmPassword', 'confirmPassword');

    // Tab switching
    loginTab.addEventListener('click', () => {
        switchTab('login');
    });

    registerTab.addEventListener('click', () => {
        switchTab('register');
    });

    // Form submissions
    loginForm.addEventListener('submit', handleLogin);
    registerForm.addEventListener('submit', handleRegister);

    // Check if already authenticated
    if (TokenManager.isAuthenticated()) {
        window.location.href = 'dashboard.html';
    }
});

function switchTab(tab) {
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (tab === 'login') {
        loginTab.classList.add('bg-indigo-600', 'text-white');
        loginTab.classList.remove('bg-gray-200', 'text-gray-700');
        registerTab.classList.add('bg-gray-200', 'text-gray-700');
        registerTab.classList.remove('bg-indigo-600', 'text-white');
        
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    } else {
        registerTab.classList.add('bg-indigo-600', 'text-white');
        registerTab.classList.remove('bg-gray-200', 'text-gray-700');
        loginTab.classList.add('bg-gray-200', 'text-gray-700');
        loginTab.classList.remove('bg-indigo-600', 'text-white');
        
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
    }
}

function setupPasswordToggle(toggleId, inputId) {
    const toggleBtn = document.getElementById(toggleId);
    const passwordInput = document.getElementById(inputId);

    if (toggleBtn && passwordInput) {
        toggleBtn.addEventListener('click', () => {
            const icon = toggleBtn.querySelector('i');
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }
}

async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const loginData = {
        username: formData.get('username'),
        password: formData.get('password')
    };

    // Validation
    const validationRules = {
        username: { required: true, label: 'Username atau Email' },
        password: { required: true, label: 'Password' }
    };

    const errors = Utils.validateForm(loginData, validationRules);
    if (Object.keys(errors).length > 0) {
        Utils.displayFormErrors(errors);
        return;
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    const buttonText = document.getElementById('loginButtonText');
    const spinner = document.getElementById('loginSpinner');

    try {
        // Show loading state
        submitBtn.disabled = true;
        buttonText.textContent = 'Masuk...';
        spinner.classList.remove('hidden');

        const response = await APIClient.login(loginData);
        
        // Store token
        TokenManager.setToken(response.access_token);
        
        // Show success message
        Utils.showAlert('Berhasil!', 'Login berhasil. Mengalihkan ke dashboard...', 'success');
        
        // Redirect to dashboard
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1500);

    } catch (error) {
        Utils.showAlert('Login Gagal', error.message, 'error');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        buttonText.textContent = 'Masuk';
        spinner.classList.add('hidden');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const registerData = {
        full_name: formData.get('full_name'),
        username: formData.get('username'),
        email: formData.get('email'),
        phone_number: formData.get('phone_number'),
        password: formData.get('password'),
        confirmPassword: formData.get('confirmPassword')
    };

    // Validation rules
    const validationRules = {
        full_name: { required: true, label: 'Nama Lengkap', minLength: 2 },
        username: { 
            required: true, 
            label: 'Username', 
            minLength: 3,
            pattern: /^[a-zA-Z0-9_]+$/,
            message: 'Username hanya boleh mengandung huruf, angka, dan underscore'
        },
        email: { 
            required: true, 
            label: 'Email',
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Format email tidak valid'
        },
        phone_number: { 
            required: true, 
            label: 'Nomor Telepon',
            pattern: /^08[0-9]{8,11}$/,
            message: 'Nomor telepon harus dimulai dengan 08 dan 10-13 digit'
        },
        password: { 
            required: true, 
            label: 'Password', 
            minLength: 8 
        },
        confirmPassword: { 
            required: true, 
            label: 'Konfirmasi Password',
            match: 'password'
        }
    };

    const errors = Utils.validateForm(registerData, validationRules);
    if (Object.keys(errors).length > 0) {
        Utils.displayFormErrors(errors);
        return;
    }

    // Check terms agreement
    const agreeTerms = formData.get('agreeTerms');
    if (!agreeTerms) {
        Utils.showAlert('Persetujuan Diperlukan', 'Anda harus menyetujui syarat dan ketentuan untuk mendaftar.', 'warning');
        return;
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    const buttonText = document.getElementById('registerButtonText');
    const spinner = document.getElementById('registerSpinner');

    try {
        // Show loading state
        submitBtn.disabled = true;
        buttonText.textContent = 'Mendaftar...';
        spinner.classList.remove('hidden');

        // Remove confirmPassword from data sent to API
        const { confirmPassword, ...apiData } = registerData;

        const response = await APIClient.register(apiData);
        
        // Show success message
        Utils.showAlert(
            'Pendaftaran Berhasil!', 
            'Akun Anda telah berhasil dibuat. Silakan login dengan akun baru Anda.', 
            'success'
        );
        
        // Switch to login tab after successful registration
        setTimeout(() => {
            switchTab('login');
            form.reset();
        }, 2000);

    } catch (error) {
        Utils.showAlert('Pendaftaran Gagal', error.message, 'error');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        buttonText.textContent = 'Daftar Sekarang';
        spinner.classList.add('hidden');
    }
}

// Phone number formatting
document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('registerPhone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            // Ensure it starts with 08
            if (value.length > 0 && !value.startsWith('08')) {
                if (value.startsWith('8')) {
                    value = '0' + value;
                } else if (value.startsWith('62')) {
                    value = '0' + value.substring(2);
                } else {
                    value = '08' + value;
                }
            }
            
            // Limit length
            if (value.length > 13) {
                value = value.substring(0, 13);
            }
            
            e.target.value = value;
        });
    }
});

// Real-time validation feedback
document.addEventListener('DOMContentLoaded', function() {
    // Username validation
    const usernameInput = document.getElementById('registerUsername');
    if (usernameInput) {
        usernameInput.addEventListener('blur', function() {
            const value = this.value;
            const pattern = /^[a-zA-Z0-9_]+$/;
            
            if (value && !pattern.test(value)) {
                this.classList.add('border-red-500');
                this.classList.remove('border-gray-300');
                
                // Remove existing error message
                const existingError = this.parentNode.querySelector('.error-message');
                if (existingError) existingError.remove();
                
                // Add error message
                const errorEl = document.createElement('p');
                errorEl.className = 'error-message text-red-500 text-sm mt-1';
                errorEl.textContent = 'Username hanya boleh mengandung huruf, angka, dan underscore';
                this.parentNode.appendChild(errorEl);
            } else {
                this.classList.remove('border-red-500');
                this.classList.add('border-gray-300');
                
                const existingError = this.parentNode.querySelector('.error-message');
                if (existingError) existingError.remove();
            }
        });
    }

    // Email validation
    const emailInput = document.getElementById('registerEmail');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const value = this.value;
            const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (value && !pattern.test(value)) {
                this.classList.add('border-red-500');
                this.classList.remove('border-gray-300');
                
                const existingError = this.parentNode.querySelector('.error-message');
                if (existingError) existingError.remove();
                
                const errorEl = document.createElement('p');
                errorEl.className = 'error-message text-red-500 text-sm mt-1';
                errorEl.textContent = 'Format email tidak valid';
                this.parentNode.appendChild(errorEl);
            } else {
                this.classList.remove('border-red-500');
                this.classList.add('border-gray-300');
                
                const existingError = this.parentNode.querySelector('.error-message');
                if (existingError) existingError.remove();
            }
        });
    }

    // Password confirmation validation
    const passwordInput = document.getElementById('registerPassword');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    
    if (passwordInput && confirmPasswordInput) {
        confirmPasswordInput.addEventListener('blur', function() {
            const password = passwordInput.value;
            const confirmPassword = this.value;
            
            if (confirmPassword && password !== confirmPassword) {
                this.classList.add('border-red-500');
                this.classList.remove('border-gray-300');
                
                const existingError = this.parentNode.querySelector('.error-message');
                if (existingError) existingError.remove();
                
                const errorEl = document.createElement('p');
                errorEl.className = 'error-message text-red-500 text-sm mt-1';
                errorEl.textContent = 'Password tidak cocok';
                this.parentNode.appendChild(errorEl);
            } else {
                this.classList.remove('border-red-500');
                this.classList.add('border-gray-300');
                
                const existingError = this.parentNode.querySelector('.error-message');
                if (existingError) existingError.remove();
            }
        });
    }
});
