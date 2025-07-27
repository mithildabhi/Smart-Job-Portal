// Job List JavaScript Functions

// Global variables
let currentJobId = null;

// Initialize job list functionality
function initializeJobList() {
    console.log('Initializing job list...');
    
    // Initialize apply buttons
    initializeApplyButtons();
    
    // Initialize bookmark buttons
    initializeBookmarkButtons();
    
    // Initialize application form
    initializeApplicationForm();
    
    console.log('Job list initialized successfully');
}

// Initialize apply buttons
function initializeApplyButtons() {
    const applyButtons = document.querySelectorAll('.apply-btn');
    
    applyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const jobId = this.dataset.jobId;
            const jobTitle = this.dataset.jobTitle;
            const companyName = this.dataset.company;
            
            openApplicationModal(jobId, jobTitle, companyName);
        });
    });
}

// Initialize bookmark buttons
function initializeBookmarkButtons() {
    const bookmarkButtons = document.querySelectorAll('.btn-bookmark');
    
    bookmarkButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const jobId = this.dataset.jobId;
            toggleBookmark(jobId, this);
        });
    });
}

// Open application modal
function openApplicationModal(jobId, jobTitle, companyName) {
    currentJobId = jobId;
    
    // Update modal content
    document.getElementById('modal-job-title').textContent = jobTitle;
    document.getElementById('modal-company-name').textContent = companyName;
    
    // Reset form
    document.getElementById('applicationForm').reset();
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('applicationModal'));
    modal.show();
}

// Initialize application form
function initializeApplicationForm() {
    const form = document.getElementById('applicationForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitApplication();
        });
    }
}

// Submit job application
function submitApplication() {
    const form = document.getElementById('applicationForm');
    const formData = new FormData(form);
    
    // Add job ID to form data
    formData.append('job_id', currentJobId);
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';
    submitButton.disabled = true;
    
    // Submit application
    fetch('/jobs/apply/', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Hide modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('applicationModal'));
            modal.hide();
            
            // Update apply button to show applied status
            updateApplyButtonStatus(currentJobId);
            
            // Show success message
            showAlert('success', data.message || 'Application submitted successfully!');
        } else {
            // Show error messages
            showAlert('danger', data.message || 'Error submitting application');
            
            if (data.errors) {
                displayFormErrors(data.errors);
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'An error occurred while submitting your application');
    })
    .finally(() => {
        // Reset button state
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    });
}

// Update apply button status after successful application
function updateApplyButtonStatus(jobId) {
    const applyButton = document.querySelector(`.apply-btn[data-job-id="${jobId}"]`);
    
    if (applyButton) {
        applyButton.classList.remove('btn-primary', 'apply-btn');
        applyButton.classList.add('btn-success');
        applyButton.innerHTML = '<i class="fas fa-check me-1"></i>Applied';
        applyButton.disabled = true;
        applyButton.removeEventListener('click', applyButton.clickHandler);
    }
}

// Toggle bookmark status
function toggleBookmark(jobId, button) {
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
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Toggle bookmark icon
            const icon = button.querySelector('i');
            if (data.bookmarked) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                button.classList.add('active');
                showAlert('success', 'Job bookmarked!');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                button.classList.remove('active');
                showAlert('info', 'Bookmark removed');
            }
        } else {
            showAlert('danger', data.message || 'Error updating bookmark');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'An error occurred');
    });
}

// Display form errors
function displayFormErrors(errors) {
    // Clear previous errors
    document.querySelectorAll('.error-message').forEach(el => el.remove());
    
    // Display new errors
    Object.keys(errors).forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message text-danger mt-1';
            errorDiv.innerHTML = errors[fieldName].join('<br>');
            field.parentNode.appendChild(errorDiv);
        }
    });
}

// Show alert messages
function showAlert(type, message) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;" role="alert">
            <i class="fas ${getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = document.querySelector('.alert:last-of-type');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// Get appropriate icon for alert type
function getAlertIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        danger: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    return icons[type] || 'fa-info-circle';
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeJobList);
