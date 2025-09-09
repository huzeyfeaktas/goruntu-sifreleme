// Global variables
let currentTab = 'encrypt';
let encryptInputFile = null;
let decryptInputFile = null;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize Application
function initializeApp() {
    setupTabNavigation();
    setupFileInputs();
    setupButtons();
    setupPasswordToggles();
}

// Tab Navigation
function setupTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    // Remove active class from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    // Add active class to selected tab
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    document.getElementById(`${tabId}-tab`).classList.add('active');

    currentTab = tabId;
}

// File Input Setup
function setupFileInputs() {
    // Encrypt input file
    const encryptInputFile = document.getElementById('encrypt-input-file');
    encryptInputFile.addEventListener('change', (e) => {
        handleFileSelect(e, 'encrypt', 'input');
    });

    // Decrypt input file
    const decryptInputFile = document.getElementById('decrypt-input-file');
    decryptInputFile.addEventListener('change', (e) => {
        handleFileSelect(e, 'decrypt', 'input');
    });

    // Output path buttons
    document.getElementById('encrypt-output-btn').addEventListener('click', () => {
        handleOutputPathSelect('encrypt');
    });

    document.getElementById('decrypt-output-btn').addEventListener('click', () => {
        handleOutputPathSelect('decrypt');
    });
}

// Handle File Selection
function handleFileSelect(event, type, inputType) {
    const file = event.target.files[0];
    
    if (!file) {
        resetFileDisplay(type, inputType);
        return;
    }

    // Validate file type
    if (!isValidImageFile(file)) {
        showNotification('Lütfen geçerli bir resim dosyası seçin! (JPG, PNG, BMP)', 'error');
        resetFileDisplay(type, inputType);
        return;
    }

    // Store file reference
    if (type === 'encrypt' && inputType === 'input') {
        encryptInputFile = file;
    } else if (type === 'decrypt' && inputType === 'input') {
        decryptInputFile = file;
    }

    // Update file info
    const fileInfo = document.getElementById(`${type}-${inputType}-info`);
    fileInfo.textContent = `${file.name} (${formatFileSize(file.size)})`;

    // Show image preview
    displayImagePreview(file, type, inputType);

    // Clear output image if input changes
    if (inputType === 'input') {
        resetImageDisplay(type, 'output');
    }
}

// Display Image Preview
function displayImagePreview(file, type, inputType) {
    const reader = new FileReader();
    
    reader.onload = function(e) {
        const preview = document.getElementById(`${type}-${inputType}-preview`);
        const placeholder = document.getElementById(`${type}-${inputType}-placeholder`);
        
        preview.src = e.target.result;
        preview.classList.add('show');
        placeholder.classList.add('hide');
    };
    
    reader.readAsDataURL(file);
}

// Reset File Display
function resetFileDisplay(type, inputType) {
    const fileInfo = document.getElementById(`${type}-${inputType}-info`);
    fileInfo.textContent = 'Henüz dosya seçilmedi';
    
    resetImageDisplay(type, inputType);
    
    // Clear file reference
    if (type === 'encrypt' && inputType === 'input') {
        encryptInputFile = null;
    } else if (type === 'decrypt' && inputType === 'input') {
        decryptInputFile = null;
    }
}

// Reset Image Display
function resetImageDisplay(type, inputType) {
    const preview = document.getElementById(`${type}-${inputType}-preview`);
    const placeholder = document.getElementById(`${type}-${inputType}-placeholder`);
    
    preview.src = '';
    preview.classList.remove('show');
    placeholder.classList.remove('hide');
}

// Handle Output Path Selection
function handleOutputPathSelect(type) {
    // For web version, we'll use download functionality
    // This is a placeholder for the file save dialog
    const pathInput = document.getElementById(`${type}-output-path`);
    const defaultName = type === 'encrypt' ? 'sifreli_resim.png' : 'cozulmus_resim.png';
    pathInput.value = defaultName;
    
    showNotification('Dosya işlem tamamlandığında otomatik olarak indirilecektir.', 'info');
}

// Button Setup
function setupButtons() {
    // Encrypt button
    document.getElementById('encrypt-btn').addEventListener('click', () => {
        handleEncrypt();
    });

    // Decrypt button
    document.getElementById('decrypt-btn').addEventListener('click', () => {
        handleDecrypt();
    });

    // Reset buttons
    document.getElementById('encrypt-reset-btn').addEventListener('click', () => {
        resetTab('encrypt');
    });

    document.getElementById('decrypt-reset-btn').addEventListener('click', () => {
        resetTab('decrypt');
    });
}

// Handle Encrypt
async function handleEncrypt() {
    if (!validateEncryptForm()) {
        return;
    }

    const password = document.getElementById('encrypt-password').value;
    
    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('image', encryptInputFile);
        formData.append('password', password);

        const response = await fetch('/api/encrypt', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Şifreleme işlemi başarısız oldu!');
        }

        const blob = await response.blob();
        
        // Display encrypted image
        displayEncryptedImage(blob);
        
        // Download encrypted image
        downloadFile(blob, 'sifreli_resim.png');
        
        showNotification('Resim başarıyla şifrelendi!', 'success');
        
    } catch (error) {
        console.error('Encryption error:', error);
        showNotification(error.message || 'Şifreleme işlemi sırasında hata oluştu!', 'error');
    } finally {
        showLoading(false);
    }
}

// Handle Decrypt
async function handleDecrypt() {
    if (!validateDecryptForm()) {
        return;
    }

    const password = document.getElementById('decrypt-password').value;
    
    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('image', decryptInputFile);
        formData.append('password', password);

        const response = await fetch('/api/decrypt', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Şifre çözme işlemi başarısız oldu!');
        }

        const blob = await response.blob();
        
        // Display decrypted image
        displayDecryptedImage(blob);
        
        // Download decrypted image
        downloadFile(blob, 'cozulmus_resim.png');
        
        showNotification('Şifre başarıyla çözüldü!', 'success');
        
    } catch (error) {
        console.error('Decryption error:', error);
        showNotification(error.message || 'Şifre çözme işlemi sırasında hata oluştu!', 'error');
    } finally {
        showLoading(false);
    }
}

// Display Encrypted Image
function displayEncryptedImage(blob) {
    const url = URL.createObjectURL(blob);
    const preview = document.getElementById('encrypt-output-preview');
    const placeholder = document.getElementById('encrypt-output-placeholder');
    
    preview.src = url;
    preview.classList.add('show');
    placeholder.classList.add('hide');
}

// Display Decrypted Image
function displayDecryptedImage(blob) {
    const url = URL.createObjectURL(blob);
    const preview = document.getElementById('decrypt-output-preview');
    const placeholder = document.getElementById('decrypt-output-placeholder');
    
    preview.src = url;
    preview.classList.add('show');
    placeholder.classList.remove('hide');
}

// Download File
function downloadFile(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Form Validation
function validateEncryptForm() {
    if (!encryptInputFile) {
        showNotification('Lütfen şifrelenecek bir resim seçin!', 'error');
        return false;
    }

    const password = document.getElementById('encrypt-password').value.trim();
    if (!password) {
        showNotification('Lütfen bir şifre girin!', 'error');
        return false;
    }

    return true;
}

function validateDecryptForm() {
    if (!decryptInputFile) {
        showNotification('Lütfen çözülecek bir resim seçin!', 'error');
        return false;
    }

    const password = document.getElementById('decrypt-password').value.trim();
    if (!password) {
        showNotification('Lütfen şifreyi girin!', 'error');
        return false;
    }

    return true;
}

// Reset Tab
function resetTab(type) {
    // Clear file inputs
    document.getElementById(`${type}-input-file`).value = '';
    document.getElementById(`${type}-output-path`).value = '';
    document.getElementById(`${type}-password`).value = '';
    
    // Reset file info
    document.getElementById(`${type}-input-info`).textContent = 'Henüz dosya seçilmedi';
    
    // Reset image displays
    resetImageDisplay(type, 'input');
    resetImageDisplay(type, 'output');
    
    // Clear file references
    if (type === 'encrypt') {
        encryptInputFile = null;
    } else {
        decryptInputFile = null;
    }
    
    showNotification(`${type === 'encrypt' ? 'Şifreleme' : 'Şifre çözme'} sekmesi sıfırlandı.`, 'info');
}

// Password Toggle
function setupPasswordToggles() {
    // This function is called from HTML onclick
}

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Utility Functions
function isValidImageFile(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp'];
    return validTypes.includes(file.type);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Loading Overlay
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (show) {
        overlay.classList.add('show');
    } else {
        overlay.classList.remove('show');
    }
}

// Notification System
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    const icon = notification.querySelector('.notification-icon');
    const messageEl = notification.querySelector('.notification-message');
    
    // Set message
    messageEl.textContent = message;
    
    // Set type and icon
    notification.className = `notification ${type}`;
    
    switch (type) {
        case 'success':
            icon.className = 'notification-icon fas fa-check-circle';
            break;
        case 'error':
            icon.className = 'notification-icon fas fa-exclamation-circle';
            break;
        case 'info':
        default:
            icon.className = 'notification-icon fas fa-info-circle';
            break;
    }
    
    // Show notification
    notification.classList.add('show');
    
    // Auto hide after 4 seconds
    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

// Keyboard Shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + 1 for encrypt tab
    if ((e.ctrlKey || e.metaKey) && e.key === '1') {
        e.preventDefault();
        switchTab('encrypt');
    }
    
    // Ctrl/Cmd + 2 for decrypt tab
    if ((e.ctrlKey || e.metaKey) && e.key === '2') {
        e.preventDefault();
        switchTab('decrypt');
    }
    
    // Escape to close loading
    if (e.key === 'Escape') {
        showLoading(false);
    }
});

// Drag and Drop Support
function setupDragAndDrop() {
    const dropZones = document.querySelectorAll('.image-wrapper');
    
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('drag-over');
        });
        
        zone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            zone.classList.remove('drag-over');
        });
        
        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (isValidImageFile(file)) {
                    // Determine which input this belongs to
                    const zoneId = zone.closest('.image-container').querySelector('img').id;
                    if (zoneId.includes('encrypt-input')) {
                        handleDroppedFile(file, 'encrypt', 'input');
                    } else if (zoneId.includes('decrypt-input')) {
                        handleDroppedFile(file, 'decrypt', 'input');
                    }
                } else {
                    showNotification('Lütfen geçerli bir resim dosyası sürükleyin!', 'error');
                }
            }
        });
    });
}

function handleDroppedFile(file, type, inputType) {
    // Update file input
    const fileInput = document.getElementById(`${type}-${inputType}-file`);
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;
    
    // Trigger change event
    const event = new Event('change', { bubbles: true });
    fileInput.dispatchEvent(event);
}

// Initialize drag and drop when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupDragAndDrop();
});

// Error Handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showNotification('Beklenmeyen bir hata oluştu!', 'error');
});

// Unhandled Promise Rejection
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showNotification('İşlem sırasında hata oluştu!', 'error');
});