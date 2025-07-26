// Student Base Navigation JavaScript

// ✅ ADDED: Missing Profile Click Handler
function handleProfileClick(event) {
  if (!event.target.closest('.profile-dropdown-menu')) {
    // Navigate to profile page - URL will be injected from template
    if (window.studentProfileUrl) {
      window.location.href = window.studentProfileUrl;
    } else {
      // Fallback - try to construct URL
      window.location.href = '/students/profile/';
    }
  }
}

// Show Delete Modal
function showDeleteModal(event) {
  event.stopPropagation();
  const modal = new bootstrap.Modal(document.getElementById('deleteAccountModal'));
  modal.show();
}

// Toggle delete button based on confirmation checkbox
function toggleDeleteButton() {
  const checkbox = document.getElementById('confirmDeletion');
  const deleteBtn = document.getElementById('finalDeleteBtn');
  
  if (checkbox && deleteBtn) {
    deleteBtn.disabled = !checkbox.checked;
  }
}

// Submit Delete Form
function submitDeleteForm() {
  console.log('Delete form submission started');
  
  // Check if checkbox is confirmed
  const checkbox = document.getElementById('confirmDeletion');
  if (!checkbox || !checkbox.checked) {
    alert('Please confirm that you understand this action is permanent.');
    return;
  }
  
  // Find and submit the form
  const form = document.getElementById('deleteForm');
  if (form) {
    console.log('Submitting delete form');
    
    // Show loading state
    const deleteBtn = document.getElementById('finalDeleteBtn');
    if (deleteBtn) {
      deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Deleting...';
      deleteBtn.disabled = true;
    }
    
    // Hide modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('deleteAccountModal'));
    if (modal) {
      modal.hide();
    }
    
    // Submit the form
    form.submit();
  } else {
    console.error('Delete form not found');
    alert('Error: Could not find delete form. Please refresh the page and try again.');
  }
}

// ✅ ADDED: Dropdown Hover Effects
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

// Base initialization
function initializeStudentBase() {
  console.log('DOM loaded, initializing student base...');
  
  // Initialize dropdown effects
  initializeDropdownEffects();
  
  // Reset modal when it opens
  const deleteModal = document.getElementById('deleteAccountModal');
  if (deleteModal) {
    deleteModal.addEventListener('show.bs.modal', function() {
      const checkbox = document.getElementById('confirmDeletion');
      const deleteBtn = document.getElementById('finalDeleteBtn');
      
      if (checkbox) checkbox.checked = false;
      if (deleteBtn) {
        deleteBtn.disabled = true;
        deleteBtn.innerHTML = '<i class="fas fa-trash-alt me-2"></i>Yes, Delete My Account Forever';
      }
    });
  }
  
  // Verify form exists
  const form = document.getElementById('deleteForm');
  console.log('Delete form found on page load:', !!form);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeStudentBase);
