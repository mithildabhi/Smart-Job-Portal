// Student Profile JavaScript Functions - Complete Merged Version

// Global URL variables
let deleteProfilePictureUrl = '';
let uploadProfilePictureUrl = '';

// MERGED: Profile click handler from student_base.html
function handleProfileClick(event) {
  if (!event.target.closest('.profile-dropdown-menu')) {
    window.location.href = studentProfileUrl || '/students/profile/';
  }
}

// Initialize URLs
function initializeUrls() {
  deleteProfilePictureUrl = window.profileUrls?.deleteProfilePicture || '';
  uploadProfilePictureUrl = window.profileUrls?.uploadProfilePicture || '';
  
  if (!deleteProfilePictureUrl || !uploadProfilePictureUrl) {
    console.error('Profile URLs not properly configured');
    return false;
  }
  return true;
}

// Profile Picture Management
function openImageModal() {
  const modal = new bootstrap.Modal(document.getElementById('imageUploadModal'));
  modal.show();
}

function deleteProfilePicture() {
  if (!deleteProfilePictureUrl) {
    alert('Delete URL not configured. Please refresh the page.');
    return;
  }
  
  if (confirm('Are you sure you want to delete your profile picture?')) {
    fetch(deleteProfilePictureUrl, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
      },
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Update UI to show default avatar
        const container = document.getElementById('profile-avatar-container');
        container.innerHTML = `
          <i class="fas fa-user-graduate" id="default-avatar"></i>
          <div class="avatar-overlay">
            <button class="btn-avatar-action" onclick="openImageModal()" title="Add Picture">
              <i class="fas fa-camera"></i>
            </button>
          </div>
        `;
        showAlert('success', data.message);
      } else {
        showAlert('danger', data.message);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showAlert('danger', 'An error occurred while deleting the picture.');
    });
  }
}

// Image Upload Functions
function initializeImageUpload() {
  // Check if URLs are configured
  if (!initializeUrls()) {
    console.error('Cannot initialize image upload: URLs not configured');
    return;
  }
  
  // Handle image preview
  const pictureInput = document.getElementById('profile-picture-input');
  if (pictureInput) {
    pictureInput.addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
          document.getElementById('image-preview').src = e.target.result;
          document.getElementById('image-preview-container').style.display = 'block';
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Handle form submission
  const profileForm = document.getElementById('profile-picture-form');
  if (profileForm) {
    profileForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      if (!uploadProfilePictureUrl) {
        alert('Upload URL not configured. Please refresh the page.');
        return;
      }
      
      const formData = new FormData(this);
      const uploadBtn = document.getElementById('upload-btn');
      const uploadBtnText = document.getElementById('upload-btn-text');
      const uploadSpinner = document.getElementById('upload-spinner');
      
      // Show loading state
      uploadBtn.disabled = true;
      uploadBtnText.textContent = 'Uploading...';
      uploadSpinner.style.display = 'inline-block';
      
      fetch(uploadProfilePictureUrl, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Update UI with new image
          const container = document.getElementById('profile-avatar-container');
          container.innerHTML = `
            <img src="${data.image_url}" alt="Profile Picture" id="profile-image">
            <div class="avatar-overlay">
              <div class="avatar-actions">
                <button class="btn-avatar-action" onclick="openImageModal()" title="Change Picture">
                  <i class="fas fa-camera"></i>
                </button>
                <button class="btn-avatar-action" onclick="deleteProfilePicture()" title="Delete Picture">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          `;
          
          // Close modal
          const modal = bootstrap.Modal.getInstance(document.getElementById('imageUploadModal'));
          modal.hide();
          
          showAlert('success', data.message);
        } else {
          // Show errors
          const errorDiv = document.getElementById('upload-errors');
          errorDiv.innerHTML = Object.values(data.errors).flat().join('<br>');
          errorDiv.style.display = 'block';
        }
      })
      .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'An error occurred while uploading the picture.');
      })
      .finally(() => {
        // Reset loading state
        uploadBtn.disabled = false;
        uploadBtnText.textContent = 'Upload Picture';
        uploadSpinner.style.display = 'none';
      });
    });
  }

  // Reset modal when closed
  const imageModal = document.getElementById('imageUploadModal');
  if (imageModal) {
    imageModal.addEventListener('hidden.bs.modal', function () {
      const form = document.getElementById('profile-picture-form');
      const previewContainer = document.getElementById('image-preview-container');
      const errors = document.getElementById('upload-errors');
      
      if (form) form.reset();
      if (previewContainer) previewContainer.style.display = 'none';
      if (errors) errors.style.display = 'none';
    });
  }
}

// MERGED: Enhanced hover effects from student_base.html
function initializeDropdownEffects() {
  const dropdownItems = document.querySelectorAll('.dropdown-item-custom');
  dropdownItems.forEach(item => {
    item.addEventListener('mouseenter', function() {
      this.style.transform = 'translateX(5px)';
    });
    
    item.addEventListener('mouseleave', function() {
      this.style.transform = 'translateX(0)';
    });
  });
}

// Alert System
function showAlert(type, message) {
  const alertHtml = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
  `;
  
  // Add alert to the top of the page
  const alertContainer = document.createElement('div');
  alertContainer.innerHTML = alertHtml;
  document.body.insertBefore(alertContainer.firstElementChild, document.body.firstChild);
  
  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    const alert = document.querySelector('.alert');
    if (alert) {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }
  }, 5000);
}

// Animation Functions
function initializeProgressBarAnimations() {
  const progressBars = document.querySelectorAll('.progress-fill');
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const width = entry.target.style.width;
        entry.target.style.width = '0%';
        setTimeout(() => {
          entry.target.style.width = width;
        }, 100);
        observer.unobserve(entry.target);
      }
    });
  });

  progressBars.forEach(bar => observer.observe(bar));
}

function initializeStatsAnimations() {
  const statNumbers = document.querySelectorAll('.stat-number');
  
  const animateValue = (element, start, end, duration) => {
    let startTimestamp = null;
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const currentValue = Math.floor(progress * (end - start) + start);
      element.textContent = currentValue + (element.textContent.includes('%') ? '%' : '');
      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };
    window.requestAnimationFrame(step);
  };

  const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const text = entry.target.textContent;
        const number = parseInt(text.replace(/\D/g, ''));
        animateValue(entry.target, 0, number, 1500);
        statsObserver.unobserve(entry.target);
      }
    });
  });

  statNumbers.forEach(stat => statsObserver.observe(stat));
}

// Main initialization function
function initializeStudentProfile() {
  console.log('Initializing student profile...');
  
  // Initialize image upload functionality
  initializeImageUpload();
  
  // Initialize dropdown effects (merged from base)
  initializeDropdownEffects();
  
  // Initialize animations
  initializeProgressBarAnimations();
  initializeStatsAnimations();
  
  console.log('Student profile initialized successfully');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeStudentProfile);
