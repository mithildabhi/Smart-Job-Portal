// Job List JavaScript Functions - Enhanced Version

// Global variables
let currentJobId = null;
let isSubmitting = false;

// Initialize job list functionality
function initializeJobList() {
    console.log('Initializing job list...');
    
    // Initialize all components
    initializeApplyButtons();
    initializeBookmarkButtons();
    initializeApplicationForm();
    initializeSearchAndFilters();
    initializeJobCards();
    
    console.log('Job list initialized successfully');
}

// Initialize apply buttons
function initializeApplyButtons() {
    const applyButtons = document.querySelectorAll('.apply-btn');
    
    applyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Check if user is logged in
            if (!isUserAuthenticated()) {
                showLoginPrompt();
                return;
            }
            
            const jobId = this.dataset.jobId;
            const jobTitle = this.dataset.jobTitle;
            const companyName = this.dataset.company;
            
            openApplicationModal(jobId, jobTitle, companyName);
        });
    });
    
    console.log(`Initialized ${applyButtons.length} apply buttons`);
}

// Initialize bookmark buttons
function initializeBookmarkButtons() {
    const bookmarkButtons = document.querySelectorAll('.btn-bookmark');
    
    bookmarkButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Check if user is logged in
            if (!isUserAuthenticated()) {
                showLoginPrompt();
                return;
            }
            
            const jobId = this.dataset.jobId;
            toggleBookmark(jobId, this);
        });
    });
    
    console.log(`Initialized ${bookmarkButtons.length} bookmark buttons`);
}

// Initialize search and filter functionality
function initializeSearchAndFilters() {
    // Search functionality
    const searchInput = document.getElementById('jobSearch');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value);
            }, 500);
        });
    }
    
    // Filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filterType = this.dataset.filter;
            const filterValue = this.dataset.value;
            applyFilter(filterType, filterValue);
            
            // Update active state
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    console.log('Search and filters initialized');
}

// Initialize job cards with hover effects
function initializeJobCards() {
    const jobCards = document.querySelectorAll('.job-card');
    
    jobCards.forEach(card => {
        // Add hover effects
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.12)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 15px rgba(0,0,0,0.08)';
        });
        
        // Add click tracking
        card.addEventListener('click', function(e) {
            // Don't track if clicking on buttons
            if (!e.target.closest('button, a')) {
                trackJobView(this.dataset.jobId);
            }
        });
    });
    
    console.log(`Initialized ${jobCards.length} job cards`);
}

// Open application modal with enhanced UI
function openApplicationModal(jobId, jobTitle, companyName) {
    currentJobId = jobId;
    
    // Update modal content
    document.getElementById('modal-job-title').textContent = jobTitle;
    document.getElementById('modal-company-name').textContent = companyName;
    
    // Reset form and errors
    const form = document.getElementById('applicationForm');
    form.reset();
    clearFormErrors();
    
    // Show modal with animation
    const modal = new bootstrap.Modal(document.getElementById('applicationModal'), {
        backdrop: 'static',
        keyboard: false
    });
    modal.show();
    
    // Focus on first form field
    setTimeout(() => {
        const firstInput = form.querySelector('textarea, input[type="file"]');
        if (firstInput) firstInput.focus();
    }, 300);
    
    console.log(`Opened application modal for job ${jobId}`);
}

// Initialize application form with validation
function initializeApplicationForm() {
    const form = document.getElementById('applicationForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate form before submission
            if (validateApplicationForm()) {
                submitApplication();
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('textarea, input[type="file"], input[type="url"]');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    }
    
    console.log('Application form initialized with validation');
}

// Enhanced form validation
function validateApplicationForm() {
    const form = document.getElementById('applicationForm');
    let isValid = true;
    
    // Clear previous errors
    clearFormErrors();
    
    // Validate cover letter
    const coverLetter = form.querySelector('[name="cover_letter"]');
    if (!coverLetter.value.trim()) {
        showFieldError(coverLetter, 'Cover letter is required');
        isValid = false;
    } else if (coverLetter.value.trim().length < 10) {
        showFieldError(coverLetter, 'Cover letter must be at least 10 characters long');
        isValid = false;
    }
    
    // Validate resume
    const resume = form.querySelector('[name="resume"]');
    if (!resume.files[0]) {
        showFieldError(resume, 'Resume is required');
        isValid = false;
    } else {
        const file = resume.files[0];
        const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        
        if (!allowedTypes.includes(file.type)) {
            showFieldError(resume, 'Please upload a PDF or Word document');
            isValid = false;
        } else if (file.size > 5 * 1024 * 1024) { // 5MB
            showFieldError(resume, 'File size must be less than 5MB');
            isValid = false;
        }
    }
    
    // Validate portfolio URL (optional)
    const portfolioUrl = form.querySelector('[name="portfolio_url"]');
    if (portfolioUrl.value.trim()) {
        const urlPattern = /^https?:\/\/.+/;
        if (!urlPattern.test(portfolioUrl.value.trim())) {
            showFieldError(portfolioUrl, 'Please enter a valid URL (starting with http:// or https://)');
            isValid = false;
        }
    }
    
    return isValid;
}

// Validate individual field
function validateField(field) {
    const name = field.name;
    const value = field.value.trim();
    
    clearFieldError(field);
    
    switch(name) {
        case 'cover_letter':
            if (!value) {
                showFieldError(field, 'Cover letter is required');
            } else if (value.length < 10) {
                showFieldError(field, 'Cover letter must be at least 10 characters long');
            }
            break;
            
        case 'resume':
            if (!field.files[0]) {
                showFieldError(field, 'Resume is required');
            }
            break;
            
        case 'portfolio_url':
            if (value && !/^https?:\/\/.+/.test(value)) {
                showFieldError(field, 'Please enter a valid URL');
            }
            break;
    }
}

// Enhanced application submission with better error handling
function submitApplication() {
    // Prevent double submission
    if (isSubmitting) {
        showAlert('warning', 'Please wait, your application is being submitted...');
        return;
    }
    
    isSubmitting = true;
    const form = document.getElementById('applicationForm');
    const formData = new FormData(form);
    
    formData.append('job_id', currentJobId);
    
    // Show enhanced loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting Application...';
    submitButton.disabled = true;
    
    // Show loading overlay on modal
    showModalLoading(true);
    
    fetch('/jobs/apply/', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: formData
    })
    .then(response => {
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Application service not found. Please contact support.');
            } else if (response.status === 403) {
                throw new Error('You do not have permission to apply for this job.');
            } else if (response.status >= 500) {
                throw new Error('Server error occurred. Please try again later.');
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        }
        
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        
        if (data.success) {
            handleSuccessfulApplication(data);
        } else {
            handleApplicationError(data);
        }
    })
    .catch(error => {
        console.error('Application submission error:', error);
        handleNetworkError(error);
    })
    .finally(() => {
        // Reset states
        isSubmitting = false;
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
        showModalLoading(false);
    });
}

// Handle successful application
function handleSuccessfulApplication(data) {
    // Hide modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('applicationModal'));
    modal.hide();
    
    // Update apply button status
    updateApplyButtonStatus(currentJobId);
    
    // Show enhanced success message with countdown
    showSuccessMessageWithRedirect(data.message);
    
    // Track successful application
    trackApplicationSubmission(currentJobId, 'success');
    
    // Redirect after countdown
    setTimeout(() => {
        window.location.href = '/students/applications/';
    }, 3000); // 3 seconds for better UX
}

// Handle application error
function handleApplicationError(data) {
    if (data.errors) {
        // Display form validation errors
        displayFormErrors(data.errors);
        showAlert('danger', 'Please correct the highlighted errors and try again.');
    } else {
        // Display general error message
        showAlert('danger', data.message || 'Application submission failed. Please try again.');
    }
    
    // Track error
    trackApplicationSubmission(currentJobId, 'error', data.message);
}

// Handle network errors
function handleNetworkError(error) {
    let errorMessage = 'Network error occurred while submitting your application.';
    
    if (error.message.includes('Failed to fetch')) {
        errorMessage = 'Unable to connect to the server. Please check your internet connection and try again.';
    } else if (error.message.includes('not found')) {
        errorMessage = 'Application service is temporarily unavailable. Please try again later.';
    } else if (error.message.includes('permission')) {
        errorMessage = 'You do not have permission to apply for this job. Please login and try again.';
    } else if (error.message.includes('Server error')) {
        errorMessage = error.message;
    }
    
    showAlert('danger', errorMessage);
    
    // Track network error
    trackApplicationSubmission(currentJobId, 'network_error', error.message);
}

// Enhanced success message with better countdown
function showSuccessMessageWithRedirect(message) {
    const alertHtml = `
        <div class="alert alert-success alert-dismissible fade show position-fixed application-success-alert" 
             style="top: 20px; right: 20px; z-index: 10000; min-width: 400px; max-width: 500px;" role="alert">
            <div class="d-flex align-items-start">
                <div class="me-3">
                    <i class="fas fa-check-circle fa-2x text-success"></i>
                </div>
                <div class="flex-grow-1">
                    <h6 class="alert-heading mb-2">
                        <i class="fas fa-rocket me-2"></i>Application Submitted Successfully!
                    </h6>
                    <p class="mb-2">${message}</p>
                    <div class="progress mb-2" style="height: 4px;">
                        <div class="progress-bar bg-success" id="redirectProgress" style="width: 100%"></div>
                    </div>
                    <div class="redirect-countdown d-flex align-items-center">
                        <i class="fas fa-hourglass-half me-2 text-muted"></i>
                        <small class="text-muted">
                            Redirecting to My Applications in <span id="countdown" class="fw-bold text-success">3</span> seconds...
                        </small>
                    </div>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-success me-2" onclick="window.location.href='/students/student_application/'">
                            View My Applications Now
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="this.closest('.alert').remove()">
                            Stay Here
                        </button>
                    </div>
                </div>
            </div>
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHtml);
    
    // Enhanced countdown with progress bar
    let seconds = 3;
    const countdownElement = document.getElementById('countdown');
    const progressBar = document.getElementById('redirectProgress');
    
    const countdownInterval = setInterval(() => {
        seconds--;
        if (countdownElement) {
            countdownElement.textContent = seconds;
        }
        if (progressBar) {
            progressBar.style.width = `${(seconds / 3) * 100}%`;
        }
        if (seconds <= 0) {
            clearInterval(countdownInterval);
        }
    }, 1000);
}

// Update apply button status with animation
function updateApplyButtonStatus(jobId) {
    const applyButton = document.querySelector(`.apply-btn[data-job-id="${jobId}"]`);
    
    if (applyButton) {
        // Add animation class
        applyButton.style.transition = 'all 0.3s ease';
        applyButton.style.transform = 'scale(0.95)';
        
        setTimeout(() => {
            applyButton.classList.remove('btn-primary', 'apply-btn');
            applyButton.classList.add('btn-success');
            applyButton.innerHTML = '<i class="fas fa-check me-2"></i>Applied Successfully';
            applyButton.disabled = true;
            applyButton.onclick = null;
            
            // Reset transform
            applyButton.style.transform = 'scale(1)';
            
            // Add pulse effect
            applyButton.style.animation = 'pulse 0.6s ease-in-out';
        }, 150);
    }
}

// Enhanced bookmark functionality
function toggleBookmark(jobId, button) {
    // Prevent rapid clicking
    if (button.disabled) return;
    button.disabled = true;
    
    // Show loading state
    const icon = button.querySelector('i');
    const originalClass = icon.className;
    icon.className = 'fas fa-spinner fa-spin';
    
    fetch('/jobs/bookmark/', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            job_id: jobId
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Animate the change
            button.style.transition = 'all 0.3s ease';
            
            if (data.bookmarked) {
                icon.className = 'fas fa-heart';
                button.classList.add('active', 'text-danger');
                button.title = 'Remove from bookmarks';
                showAlert('success', 'Job bookmarked successfully!');
            } else {
                icon.className = 'far fa-heart';
                button.classList.remove('active', 'text-danger');
                button.title = 'Add to bookmarks';
                showAlert('info', 'Bookmark removed');
            }
            
            // Track bookmark action
            trackBookmarkAction(jobId, data.bookmarked);
        } else {
            icon.className = originalClass;
            showAlert('danger', data.message || 'Error updating bookmark');
        }
    })
    .catch(error => {
        console.error('Bookmark error:', error);
        icon.className = originalClass;
        showAlert('danger', 'Unable to update bookmark. Please try again.');
    })
    .finally(() => {
        button.disabled = false;
    });
}

// Show modal loading overlay
function showModalLoading(show) {
    const modal = document.getElementById('applicationModal');
    let overlay = modal.querySelector('.modal-loading-overlay');
    
    if (show) {
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'modal-loading-overlay';
            overlay.innerHTML = `
                <div class="d-flex flex-column align-items-center justify-content-center h-100">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="text-muted">Submitting your application...</p>
                </div>
            `;
            overlay.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255, 255, 255, 0.9);
                z-index: 1060;
                display: flex;
                align-items: center;
                justify-content: center;
            `;
            modal.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    } else if (overlay) {
        overlay.style.display = 'none';
    }
}

// Form error handling
function displayFormErrors(errors) {
    clearFormErrors();
    
    Object.keys(errors).forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            showFieldError(field, errors[fieldName].join('<br>'));
        }
    });
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.innerHTML = message;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) errorDiv.remove();
}

function clearFormErrors() {
    document.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });
    document.querySelectorAll('.invalid-feedback').forEach(error => {
        error.remove();
    });
}

// Enhanced alert system
function showAlert(type, message, duration = 5000) {
    // Remove existing alerts of the same type
    document.querySelectorAll(`.alert-${type}`).forEach(alert => {
        if (alert.classList.contains('position-fixed')) {
            alert.remove();
        }
    });
    
    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 350px; max-width: 500px;" role="alert">
            <div class="d-flex align-items-center">
                <i class="fas ${getAlertIcon(type)} me-2"></i>
                <div class="flex-grow-1">${message}</div>
            </div>
            <button type="button" class="btn-close" onclick="document.getElementById('${alertId}').remove()"></button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-dismiss (except for success messages with redirects)
    if (type !== 'success' || !message.includes('Application Submitted')) {
        setTimeout(() => {
            const alertElement = document.getElementById(alertId);
            if (alertElement) {
                alertElement.style.animation = 'slideOut 0.3s ease-in-out';
                setTimeout(() => alertElement.remove(), 300);
            }
        }, duration);
    }
}

// Utility functions
function getAlertIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        danger: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    return icons[type] || 'fa-info-circle';
}

function isUserAuthenticated() {
    // Check if user is authenticated (you can customize this)
    return document.querySelector('[name=csrfmiddlewaretoken]') !== null;
}

function showLoginPrompt() {
    showAlert('warning', 'Please login to apply for jobs or bookmark them.');
    setTimeout(() => {
        window.location.href = '/students/login/';
    }, 2000);
}

// Search and filter functions
function performSearch(query) {
    const searchParams = new URLSearchParams(window.location.search);
    if (query.trim()) {
        searchParams.set('search', query);
    } else {
        searchParams.delete('search');
    }
    window.location.search = searchParams.toString();
}

function applyFilter(filterType, filterValue) {
    const searchParams = new URLSearchParams(window.location.search);
    searchParams.set(filterType, filterValue);
    window.location.search = searchParams.toString();
}

// Analytics and tracking
function trackJobView(jobId) {
    // Track job view for analytics
    if (typeof gtag !== 'undefined') {
        gtag('event', 'job_view', {
            'job_id': jobId
        });
    }
}

function trackApplicationSubmission(jobId, status, errorMessage = null) {
    // Track application submission
    if (typeof gtag !== 'undefined') {
        gtag('event', 'application_submit', {
            'job_id': jobId,
            'status': status,
            'error_message': errorMessage
        });
    }
}

function trackBookmarkAction(jobId, bookmarked) {
    if (typeof gtag !== 'undefined') {
        gtag('event', bookmarked ? 'job_bookmark' : 'job_unbookmark', {
            'job_id': jobId
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeJobList();
    
    // Add fade-in animation to job cards
    const jobCards = document.querySelectorAll('.job-card');
    jobCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .job-card {
        transition: all 0.3s ease;
    }
    
    .application-success-alert {
        animation: slideInRight 0.5s ease-out;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .modal-loading-overlay {
        backdrop-filter: blur(2px);
    }
`;
document.head.appendChild(style);

// Export functions for external use
window.jobListFunctions = {
    submitApplication,
    toggleBookmark,
    showAlert,
    trackJobView
};

console.log('Enhanced Job List JavaScript loaded successfully');
