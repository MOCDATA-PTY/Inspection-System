// Minimal fix for updateGroupKmTraveled and updateGroupHours functions
// This file contains only the essential functions needed to fix the JavaScript errors

// Get CSRF Token function
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!token) {
        console.error('CSRF token not found');
        return '';
    }
    return token;
}

// Update Group Km Traveled function
function updateGroupKmTraveled(input) {
    const groupId = input.getAttribute('data-group-id');
    const kmValue = input.value;

    console.log('[KM] Updating Group KM - Group ID:', groupId, 'Value:', kmValue);

    // Check for zero value and add red border
    if (kmValue === '0' || parseFloat(kmValue) === 0) {
        input.classList.add('invalid-zero');
    } else {
        input.classList.remove('invalid-zero');
    }

    // Validate input
    if (kmValue && (isNaN(kmValue) || parseFloat(kmValue) < 0)) {
        alert('Please enter a valid positive number for kilometers.');
        input.focus();
        return;
    }
    
    // Get CSRF token
    const csrfToken = getCSRFToken();
    
    // Create form data
    const formData = new FormData();
    formData.append('group_id', groupId);
    formData.append('km_traveled', kmValue);
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    // Send update request
    fetch('/update-group-km-traveled/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('[KM] KM saved successfully:', data);
            // Show success feedback
            input.style.backgroundColor = '#d4edda';
            setTimeout(() => {
                input.style.backgroundColor = '';
            }, 500);
        } else {
            console.error('[KM] Error saving KM:', data.error);
            alert('Error updating KM: ' + data.error);
        }
    })
    .catch(error => {
        console.error('[KM] Network error saving KM:', error);
        alert('Error updating KM: ' + error.message);
    });
}

// Update Group Hours function
function updateGroupHours(input) {
    const groupId = input.getAttribute('data-group-id');
    const hoursValue = input.value;

    console.log('[HOURS] Updating Group Hours - Group ID:', groupId, 'Value:', hoursValue);

    // Check for zero value and add red border
    if (hoursValue === '0' || parseFloat(hoursValue) === 0) {
        input.classList.add('invalid-zero');
    } else {
        input.classList.remove('invalid-zero');
    }

    // Validate input
    if (hoursValue && (isNaN(hoursValue) || parseFloat(hoursValue) < 0)) {
        alert('Please enter a valid positive number for hours.');
        input.focus();
        return;
    }
    
    // Get CSRF token
    const csrfToken = getCSRFToken();
    
    // Create form data
    const formData = new FormData();
    formData.append('group_id', groupId);
    formData.append('hours', hoursValue);
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    // Send update request
    fetch('/update-group-hours/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('[HOURS] Hours saved successfully:', data);
            // Show success feedback
            input.style.backgroundColor = '#d4edda';
            setTimeout(() => {
                input.style.backgroundColor = '';
            }, 500);
        } else {
            console.error('[HOURS] Error saving Hours:', data.error);
            alert('Error updating Hours: ' + data.error);
        }
    })
    .catch(error => {
        console.error('[HOURS] Network error saving Hours:', error);
        alert('Error updating Hours: ' + error.message);
    });
}

// Update Group Approved function
function updateGroupApproved(select) {
    const groupId = select.getAttribute('data-group-id');
    const approvedValue = select.value;
    
    console.log('[APPROVED] Updating Group Approved Status - Group ID:', groupId, 'Value:', approvedValue);
    
    // Get CSRF token
    const csrfToken = getCSRFToken();
    
    // Create form data
    const formData = new FormData();
    formData.append('group_id', groupId);
    formData.append('approved_status', approvedValue);
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    // Send update request
    fetch('/update-group-approved/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('[APPROVED] Approved status saved successfully:', data);
            // Show success feedback
            select.style.backgroundColor = '#d4edda';
            setTimeout(() => {
                select.style.backgroundColor = '';
            }, 500);
        } else {
            console.error('[APPROVED] Error saving approved status:', data.error);
            alert('Error updating approved status: ' + data.error);
        }
    })
    .catch(error => {
        console.error('[APPROVED] Network error saving approved status:', error);
        alert('Error updating approved status: ' + error.message);
    });
}

// Function to validate all KM and Hours inputs on page load
function validateKmHoursInputs() {
    console.log('[VALIDATION] Checking all KM and Hours inputs for zero values...');

    // Check all KM inputs
    const kmInputs = document.querySelectorAll('.group-km-input');
    kmInputs.forEach(input => {
        const value = input.value;
        if (value === '0' || parseFloat(value) === 0) {
            input.classList.add('invalid-zero');
            console.log('[VALIDATION] Found zero KM value:', input);
        }
    });

    // Check all Hours inputs
    const hoursInputs = document.querySelectorAll('.group-hours-input');
    hoursInputs.forEach(input => {
        const value = input.value;
        if (value === '0' || parseFloat(value) === 0) {
            input.classList.add('invalid-zero');
            console.log('[VALIDATION] Found zero Hours value:', input);
        }
    });

    console.log('[VALIDATION] Validation complete. Found',
        document.querySelectorAll('.invalid-zero').length, 'zero values');
}

// Run validation when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', validateKmHoursInputs);
} else {
    // DOM is already ready, run immediately
    validateKmHoursInputs();
}

// Also run validation after a short delay to catch dynamically loaded content
setTimeout(validateKmHoursInputs, 1000);

// Expose functions to global scope
window.updateGroupKmTraveled = updateGroupKmTraveled;
window.updateGroupHours = updateGroupHours;
window.getCSRFToken = getCSRFToken;
window.updateGroupApproved = updateGroupApproved;
window.validateKmHoursInputs = validateKmHoursInputs;

console.log('✅ KM and Hours functions loaded successfully!');
console.log('Functions available:', {
    updateGroupKmTraveled: typeof window.updateGroupKmTraveled,
    updateGroupHours: typeof window.updateGroupHours,
    getCSRFToken: typeof window.getCSRFToken,
    updateGroupApproved: typeof window.updateGroupApproved,
    validateKmHoursInputs: typeof window.validateKmHoursInputs
});
