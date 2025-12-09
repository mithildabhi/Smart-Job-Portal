// ===================
// Student Profile JavaScript - Fully Integrated
// ===================

// ------- Global Variables -------
let deleteProfilePictureUrl = '';
let uploadProfilePictureUrl = '';
let studentProfileUrl = '';

// ------- Profile Click Handler -------
function handleProfileClick(event) {
  if (!event.target.closest('.profile-dropdown-menu')) {
    window.location.href = studentProfileUrl || '/students/profile/';
  }
}

// ------- Initialize URLs -------
function initializeUrls() {
  deleteProfilePictureUrl = window.profileUrls?.deleteProfilePicture || '';
  uploadProfilePictureUrl = window.profileUrls?.uploadProfilePicture || '';
  studentProfileUrl = window.profileUrls?.studentProfile || '';
  if (!deleteProfilePictureUrl || !uploadProfilePictureUrl) {
    console.error('Profile URLs not properly configured');
    return false;
  }
  return true;
}

// ------- Image Modal -------
function openImageModal() {
  const modal = new bootstrap.Modal(document.getElementById('imageUploadModal'));
  modal.show();
}

// ------- Header Live Avatar Update -------
function updateHeaderAvatar(imageUrl) {
  // This ID must match your base template: id="student-header-avatar"
  const headerIcon = document.getElementById('student-header-avatar');
  if (!headerIcon) return;
  if (imageUrl) {
    headerIcon.innerHTML = `<img src="${imageUrl}" alt="Avatar" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
  } else {
    // You can use a global window.studentInitial set from backend for true initial.
    headerIcon.innerHTML = `<span class="student-initial">U</span>`;
  }
}

// ------- Delete Profile Picture -------
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
        // Profile page avatar
        const container = document.getElementById('profile-avatar-container');
        container.innerHTML = `
          <i class="fas fa-user-graduate" id="default-avatar"></i>
          <div class="avatar-overlay">
            <button class="btn-avatar-action" onclick="openImageModal()" title="Add Picture">
              <i class="fas fa-camera"></i>
            </button>
          </div>
        `;
        updateHeaderAvatar(null); // -------- live update header icon

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

// ------- Upload Image, Preview, and Submit -------
function initializeImageUpload() {
  if (!initializeUrls()) {
    console.error('Cannot initialize image upload: URLs not configured');
    return;
  }
  // Preview selected image before upload
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

  // AJAX upload on form submit
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

      uploadBtn.disabled = true;
      uploadBtnText.textContent = 'Uploading...';
      uploadSpinner.style.display = 'inline-block';

      fetch(uploadProfilePictureUrl, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Profile page avatar
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
          updateHeaderAvatar(data.image_url); // ------ live update header icon

          const modal = bootstrap.Modal.getInstance(document.getElementById('imageUploadModal'));
          if (modal) modal.hide();

          showAlert('success', data.message);
        } else {
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
        uploadBtn.disabled = false;
        uploadBtnText.textContent = 'Upload Picture';
        uploadSpinner.style.display = 'none';
      });
    });
  }

  // Clear preview/errors on modal close
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

// ------- Dropdown Hover Effect -------
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

// ------- Alert System -------
function showAlert(type, message) {
  const alertHtml = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
  `;
  const alertContainer = document.createElement('div');
  alertContainer.innerHTML = alertHtml;
  document.body.insertBefore(alertContainer.firstElementChild, document.body.firstChild);
  setTimeout(() => {
    const alert = document.querySelector('.alert');
    if (alert) {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }
  }, 5000);
}

// ------- Initialization -------
function initializeStudentProfile() {
  initializeImageUpload();
  initializeDropdownEffects();
}

document.addEventListener('DOMContentLoaded', initializeStudentProfile);

// ------- Expose functions for HTML ------
window.openImageModal = openImageModal;
window.deleteProfilePicture = deleteProfilePicture;
window.updateHeaderAvatar = updateHeaderAvatar;
window.handleProfileClick = handleProfileClick;


document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('profile-picture-form');
  const fileInput = document.getElementById('profile-picture-input');

  form.addEventListener('submit', function(e) {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file) {
      alert('Please choose a file first.');
      return;
    }

    const fd = new FormData();
    fd.append('profile_picture', file); // <-- MUST match Django view

    fetch('/students/profile/upload-picture/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
      },
      body: fd
    })
    .then(resp => resp.json())
    .then(data => {
      if (data.success) {
        // update image preview
        const img = document.getElementById('profile-image');
        if (img) img.src = data.image_url;
        alert('Upload success');
      } else {
        alert('Upload failed: ' + (data.message || 'unknown'));
      }
    })
    .catch(err => {
      console.error('Upload error', err);
      alert('Upload error - see console');
    });
  });
});
