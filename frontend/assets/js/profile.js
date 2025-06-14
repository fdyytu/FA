// Profile JavaScript
let currentUser = null;
let isEditing = false;

document.addEventListener('DOMContentLoaded', async function() {
    // Initialize profile page
    await initializeProfile();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load profile data
    await loadProfileData();
});

async function initializeProfile() {
    try {
        // Get current user info
        currentUser = await APIClient.getCurrentUser();
        
    } catch (error) {
        console.error('Failed to initialize profile:', error);
        Utils.showAlert('Error', 'Gagal memuat data profil', 'error');
    }
}

function setupEventListeners() {
    // Edit profile button
    document.getElementById('editProfileBtn').addEventListener('click', toggleEditMode);
    document.getElementById('cancelEditBtn').addEventListener('click', cancelEdit);
    
    // Forms
    document.getElementById('profileForm').addEventListener('submit', handleProfileUpdate);
    document.getElementById('passwordForm').addEventListener('submit', handlePasswordChange);
    
    // Password toggles
    setupPasswordToggle('toggleCurrentPassword', 'currentPassword');
    setupPasswordToggle('toggleNewPassword', 'newPassword');
    setupPasswordToggle('toggleConfirmNewPassword', 'confirmNewPassword');
    
    // Notification settings
    document.getElementById('emailNotification').addEventListener('change', handleNotificationChange);
    document.getElementById('smsNotification').addEventListener('change', handleNotificationChange);
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

async function loadProfileData() {
    try {
        // Load user profile
        await loadUserProfile();
        
        // Load user statistics
        await loadUserStatistics();
        
    } catch (error) {
        console.error('Failed to load profile data:', error);
    }
}

async function loadUserProfile() {
    try {
        const user = await APIClient.getCurrentUser();
        
        // Update profile card
        document.getElementById('profileName').textContent = user.full_name;
        document.getElementById('profileUsername').textContent = `@${user.username}`;
        document.getElementById('joinDate').textContent = Utils.formatDateOnly(user.created_at);
        
        // Update form fields
        document.getElementById('fullName').value = user.full_name || '';
        document.getElementById('username').value = user.username || '';
        document.getElementById('email').value = user.email || '';
        document.getElementById('phoneNumber').value = user.phone_number || '';
        
    } catch (error) {
        console.error('Failed to load user profile:', error);
        Utils.showAlert('Error', 'Gagal memuat data profil', 'error');
    }
}

async function loadUserStatistics() {
    try {
        // Load wallet balance
        const balanceData = await APIClient.getWalletBalance();
        document.getElementById('walletBalance').textContent = Utils.formatCurrency(balanceData.balance);
        
        // Load transaction statistics
        const [ppobStats, walletTransactions] = await Promise.all([
            APIClient.getPPOBStatistics(),
            APIClient.getWalletTransactions(1, 1000) // Get all transactions for counting
        ]);
        
        const totalTransactions = (ppobStats.total_count || 0) + (walletTransactions.total || 0);
        const successTransactions = ppobStats.success_count || 0;
        
        document.getElementById('totalTransactions').textContent = totalTransactions;
        document.getElementById('successTransactions').textContent = successTransactions;
        
    } catch (error) {
        console.error('Failed to load user statistics:', error);
        document.getElementById('totalTransactions').textContent = '0';
        document.getElementById('successTransactions').textContent = '0';
        document.getElementById('walletBalance').textContent = 'Rp 0';
    }
}

function toggleEditMode() {
    isEditing = !isEditing;
    
    const editBtn = document.getElementById('editProfileBtn');
    const formActions = document.getElementById('formActions');
    const formInputs = document.querySelectorAll('#profileForm input');
    
    if (isEditing) {
        // Enable editing
        editBtn.textContent = 'Batal Edit';
        editBtn.classList.remove('bg-indigo-600', 'hover:bg-indigo-700');
        editBtn.classList.add('bg-gray-600', 'hover:bg-gray-700');
        
        formActions.classList.remove('hidden');
        
        formInputs.forEach(input => {
            if (input.name !== 'username') { // Username should not be editable
                input.disabled = false;
                input.classList.remove('bg-gray-100', 'disabled:bg-gray-100');
                input.classList.add('bg-white');
            }
        });
        
    } else {
        cancelEdit();
    }
}

function cancelEdit() {
    isEditing = false;
    
    const editBtn = document.getElementById('editProfileBtn');
    const formActions = document.getElementById('formActions');
    const formInputs = document.querySelectorAll('#profileForm input');
    
    // Disable editing
    editBtn.innerHTML = '<i class="fas fa-edit mr-2"></i>Edit Profil';
    editBtn.classList.remove('bg-gray-600', 'hover:bg-gray-700');
    editBtn.classList.add('bg-indigo-600', 'hover:bg-indigo-700');
    
    formActions.classList.add('hidden');
    
    formInputs.forEach(input => {
        input.disabled = true;
        input.classList.remove('bg-white');
        input.classList.add('bg-gray-100', 'disabled:bg-gray-100');
    });
    
    // Reset form to original values
    loadUserProfile();
}

async function handleProfileUpdate(event) {
    event.preventDefault();
    
    if (!isEditing) return;
    
    const form = event.target;
    const formData = new FormData(form);
    const profileData = {
        full_name: formData.get('full_name'),
        email: formData.get('email'),
        phone_number: formData.get('phone_number')
    };
    
    // Validation
    const validationRules = {
        full_name: { required: true, label: 'Nama Lengkap', minLength: 2 },
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
        }
    };

    const errors = Utils.validateForm(profileData, validationRules);
    if (Object.keys(errors).length > 0) {
        Utils.displayFormErrors(errors);
        return;
    }
    
    const submitBtn = form.querySelector('button[type="submit"]');
    const buttonText = document.getElementById('saveButtonText');
    const spinner = document.getElementById('saveSpinner');
    
    try {
        // Show loading state
        submitBtn.disabled = true;
        buttonText.textContent = 'Menyimpan...';
        spinner.classList.remove('hidden');
        
        await APIClient.updateProfile(profileData);
        
        Utils.showAlert('Berhasil!', 'Profil berhasil diperbarui', 'success');
        
        // Exit edit mode
        toggleEditMode();
        
        // Reload profile data
        await loadUserProfile();
        
    } catch (error) {
        Utils.showAlert('Update Gagal', error.message, 'error');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        buttonText.textContent = 'Simpan Perubahan';
        spinner.classList.add('hidden');
    }
}

async function handlePasswordChange(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const passwordData = {
        current_password: formData.get('current_password'),
        new_password: formData.get('new_password'),
        confirm_password: formData.get('confirm_password')
    };
    
    // Validation
    const validationRules = {
        current_password: { required: true, label: 'Password Saat Ini' },
        new_password: { 
            required: true, 
            label: 'Password Baru', 
            minLength: 8 
        },
        confirm_password: { 
            required: true, 
            label: 'Konfirmasi Password',
            match: 'new_password'
        }
    };

    const errors = Utils.validateForm(passwordData, validationRules);
    if (Object.keys(errors).length > 0) {
        Utils.displayFormErrors(errors);
        return;
    }
    
    const submitBtn = form.querySelector('button[type="submit"]');
    const buttonText = document.getElementById('passwordButtonText');
    const spinner = document.getElementById('passwordSpinner');
    
    try {
        // Show loading state
        submitBtn.disabled = true;
        buttonText.textContent = 'Mengubah...';
        spinner.classList.remove('hidden');
        
        // Remove confirm_password from data sent to API
        const { confirm_password, ...apiData } = passwordData;
        
        await APIClient.changePassword(apiData);
        
        Utils.showAlert('Berhasil!', 'Password berhasil diubah', 'success');
        
        // Reset form
        form.reset();
        
    } catch (error) {
        Utils.showAlert('Ubah Password Gagal', error.message, 'error');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        buttonText.textContent = 'Ubah Password';
        spinner.classList.add('hidden');
    }
}

function handleNotificationChange(event) {
    const setting = event.target.id;
    const enabled = event.target.checked;
    
    // Here you would typically save the notification preference to the server
    console.log(`${setting} changed to:`, enabled);
    
    // For now, just show a message
    const settingName = setting === 'emailNotification' ? 'Email' : 'SMS';
    const status = enabled ? 'diaktifkan' : 'dinonaktifkan';
    
    Utils.showAlert(
        'Pengaturan Disimpan',
        `Notifikasi ${settingName} telah ${status}`,
        'success'
    );
}

// Phone number formatting
document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('phoneNumber');
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
    // Email validation
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            if (!isEditing) return;
            
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
    const newPasswordInput = document.getElementById('newPassword');
    const confirmNewPasswordInput = document.getElementById('confirmNewPassword');
    
    if (newPasswordInput && confirmNewPasswordInput) {
        confirmNewPasswordInput.addEventListener('blur', function() {
            const newPassword = newPasswordInput.value;
            const confirmPassword = this.value;
            
            if (confirmPassword && newPassword !== confirmPassword) {
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

// Auto-refresh profile data every 60 seconds
setInterval(async () => {
    try {
        if (!isEditing) {
            await loadUserStatistics();
        }
    } catch (error) {
        console.error('Auto-refresh failed:', error);
    }
}, 60000);
