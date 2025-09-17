// Simple sent status functionality
console.log('Sent status JavaScript loaded');

function updateSentStatus(dropdown) {
    console.log('🔄 updateSentStatus called');
    console.log('🔍 Dropdown element:', dropdown);
    
    const groupId = dropdown.getAttribute('data-group-id');
    const sentStatus = dropdown.value;
    
    console.log('📋 Group ID:', groupId);
    console.log('📋 Sent Status:', sentStatus);
    
    if (!groupId) {
        console.error('❌ No group ID found');
        return;
    }
    
    // Update visual appearance immediately
    if (sentStatus === 'YES') {
        dropdown.style.backgroundColor = '#10b981';
        dropdown.style.color = 'white';
        dropdown.classList.add('sent-yes');
        dropdown.classList.remove('sent-no');
    } else if (sentStatus === 'NO') {
        dropdown.style.backgroundColor = '#ef4444';
        dropdown.style.color = 'white';
        dropdown.classList.add('sent-no');
        dropdown.classList.remove('sent-yes');
    } else {
        dropdown.style.backgroundColor = '';
        dropdown.style.color = '';
        dropdown.classList.remove('sent-yes', 'sent-no');
    }
    
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    console.log('🔐 CSRF Token:', csrfToken ? 'Found' : 'NOT FOUND');
    
    // Send to backend
    const formData = new FormData();
    formData.append('group_id', groupId);
    formData.append('sent_status', sentStatus);
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    console.log('📤 Sending request to /inspections/update-sent-status/');
    console.log('📤 FormData - Group ID:', groupId, 'Status:', sentStatus);
    
    fetch('/inspections/update-sent-status/', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('📥 Response status:', response.status);
        console.log('📥 Response ok:', response.ok);
        return response.json();
    })
    .then(data => {
        console.log('📥 Response data:', data);
        if (data.success) {
            console.log('✅ Sent status updated successfully');
            
            // Update row appearance
            const groupRow = document.querySelector('tr[data-group-id="' + groupId + '"]');
            if (groupRow) {
                if (sentStatus === 'YES') {
                    groupRow.classList.add('inspection-complete');
                    console.log('✅ Row marked as complete');
                } else {
                    groupRow.classList.remove('inspection-complete');
                    console.log('✅ Row completion removed');
                }
            } else {
                console.log('❌ Could not find row with group-id:', groupId);
            }
            
            // Update countdown display based on sent status
            const containerDiv = dropdown.closest('div');
            let countdownContainer = containerDiv.querySelector('.onedrive-countdown');
            let statusText = containerDiv.querySelector('small.text-muted');
            
            if (sentStatus === 'YES') {
                // Create or show user info
                if (!statusText) {
                    statusText = document.createElement('small');
                    statusText.className = 'text-muted';
                    statusText.style.cssText = 'font-size: 0.6rem; margin-top: 2px; text-align: center;';
                    dropdown.parentNode.insertBefore(statusText, dropdown.nextSibling);
                }
                
                // Show user and timestamp info
                const actualUser = data.sent_by_username || data.user || 'User';
                let timestamp;
                
                if (data.sent_date) {
                    // Use the actual sent date from server
                    const sentDate = new Date(data.sent_date);
                    timestamp = sentDate.toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric' 
                    }) + ' ' + sentDate.toLocaleTimeString('en-US', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                    });
                } else {
                    // Fallback to current time
                    const now = new Date();
                    timestamp = now.toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric' 
                    }) + ' ' + now.toLocaleTimeString('en-US', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                    });
                }
                
                statusText.textContent = actualUser + ' - ' + timestamp;
                statusText.style.display = 'block';
                
                // Create or show countdown container
                const delayDays = dropdown.getAttribute('data-delay-days') || '3';
                const sentDateForCountdown = data.sent_date || new Date().toISOString();
                
                if (!countdownContainer) {
                    countdownContainer = document.createElement('div');
                    countdownContainer.className = 'onedrive-countdown';
                    countdownContainer.style.cssText = 'font-size: 0.5rem; margin-top: 1px; text-align: center;';
                    countdownContainer.setAttribute('data-sent-date', sentDateForCountdown);
                    countdownContainer.setAttribute('data-onedrive-uploaded', 'false');
                    countdownContainer.setAttribute('data-delay-days', delayDays);
                    
                    const countdownText = document.createElement('span');
                    countdownText.className = 'countdown-text';
                    countdownText.textContent = delayDays + ' days until upload';
                    countdownContainer.appendChild(countdownText);
                    
                    statusText.parentNode.insertBefore(countdownContainer, statusText.nextSibling);
                } else {
                    countdownContainer.style.display = 'block';
                    // Update the sent date to actual server date
                    countdownContainer.setAttribute('data-sent-date', sentDateForCountdown);
                    countdownContainer.setAttribute('data-delay-days', delayDays);
                }
                
                // Update countdown immediately
                if (window.updateOneDriveCountdown) {
                    setTimeout(() => {
                        window.updateOneDriveCountdown();
                    }, 100); // Small delay to ensure DOM is updated
                }
            } else {
                // Hide countdown and show simple status
                if (countdownContainer) {
                    countdownContainer.style.display = 'none';
                }
                if (statusText) {
                    statusText.textContent = 'Status';
                    statusText.style.display = 'block';
                }
            }
        } else {
            console.error('❌ Server error:', data.error);
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('❌ Network error:', error);
        alert('Network error occurred: ' + error.message);
    });
}

// Make function globally available
window.updateSentStatus = updateSentStatus;
console.log('updateSentStatus function defined and available globally');

