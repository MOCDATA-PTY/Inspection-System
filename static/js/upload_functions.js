// Clean Upload Functions - No Syntax Errors
// Use global DEBUG_MODE or set local default
window.DEBUG_MODE = window.DEBUG_MODE !== undefined ? window.DEBUG_MODE : false;

// Conditional logging functions
const debugLog = (...args) => { if (window.DEBUG_MODE) console.log(...args); };
const debugInfo = (...args) => { if (window.DEBUG_MODE) console.log(...args); };
const debugWarn = (...args) => { if (window.DEBUG_MODE) console.warn(...args); };
const debugError = (...args) => console.error(...args); // Always show errors

try {
    debugLog('Upload functions JavaScript loaded');
} catch (error) {
    debugError('Error loading upload functions:', error);
}

// Get CSRF token function
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) {
        return token.value;
    }
    // Fallback - this will be replaced by Django template
    return window.csrfToken || '';
}

// Upload RFI function - CLEAN VERSION
function uploadRFI(groupId) {
    debugLog('uploadRFI called with groupId:', groupId);
    
    if (!groupId) {
        alert('Error: Group ID is missing');
        return;
    }
    
    try {
        // Create a file input element
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf';
        fileInput.style.display = 'none';
        
        debugLog('File input element created successfully');
        
        fileInput.onchange = function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate PDF file
                if (!file.name.toLowerCase().endsWith('.pdf')) {
                    alert('Only PDF files are allowed. Please select a PDF document.');
                    return;
                }
                
                // Create form data
                const formData = new FormData();
                formData.append('file', file);
                formData.append('group_id', groupId);
                formData.append('document_type', 'rfi');
                formData.append('csrfmiddlewaretoken', getCSRFToken());
                
                debugLog('Uploading file:', file.name, 'for group:', groupId);
                uploadInProgress = true; // Set upload flag to prevent status check override
                
                // Show loading message
                const originalAlert = alert;
                alert = function(msg) { debugLog('Alert:', msg); };
                
                // Upload file
                fetch('/upload-document/', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok: ' + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    alert = originalAlert; // Restore alert
                    uploadInProgress = false; // Clear upload flag
                        if (data.success) {
                            alert(data.message || 'RFI document uploaded successfully!');
                            debugLog('Upload successful:', data);
                            
                            // Update button directly to show username
                            const buttonId = 'rfi-' + groupId;
                            debugLog('DEBUG: Updating RFI button to show username for:', buttonId);
                            
                                // Find and update the button - simplified approach
                                let button = document.getElementById(buttonId);
                                
                                if (button) {
                                    debugLog('SUCCESS Found RFI button, updating to green success state');
                                    
                                    // Clear file-deleted attributes since we now have a file
                                    button.removeAttribute('data-file-deleted');
                                    button.removeAttribute('data-last-updated');
                                    
                                    // Update button to green success state
                                    button.disabled = true;
                                    button.className = 'btn btn-sm btn-success success';
                                    button.style.backgroundColor = '#28a745';
                                    button.style.borderColor = '#28a745';
                                    button.style.cursor = 'not-allowed';
                                    button.innerHTML = 'RFI ✓';
                                    button.title = 'RFI file exists';
                                    
                                    // Remove the onclick handler since button is now disabled
                                    button.onclick = null;
                                    
                                    debugLog('SUCCESS Updated RFI button to green success state');
                                    
        // IMPORTANT: Mark that files need refresh for this client
        if (window.uploadedFiles) {
            window.uploadedFiles[groupId] = true;
        } else {
            window.uploadedFiles = {[groupId]: true};
        }
        
                        // Update View Files button colors after upload with delay to ensure server processing
                        debugLog('Updating button colors after RFI upload...');
                        debugLog('Setting 5-second timer for delayed color update...');
                        debugLog('[DEBUG] Upload in progress flag:', uploadInProgress);
                        
                        // Immediately make View Files button ORANGE since we just uploaded a file
                        makeViewFilesButtonOrange(groupId);
        debugLog('DEBUG [DEBUG] Marked groupId for file refresh:', groupId);
        
        // Clear upload flag before setting delayed update to prevent race condition
        uploadInProgress = false;
        debugLog('DEBUG [DEBUG] Cleared upload flag before delayed update');
        
        setTimeout(() => {
            debugLog('TIMER Timer fired! Starting delayed color update...');
            debugLog('DEBUG [DEBUG] Upload in progress flag at timer execution:', uploadInProgress);
            debugLog('DEBUG [DEBUG] Status check in progress flag:', statusCheckInProgress);
            if (typeof updateAllViewFilesButtonColors === 'function') {
                debugLog('INFO Delayed file status check after RFI upload...');
                updateAllViewFilesButtonColors();
            } else {
                debugWarn('updateAllViewFilesButtonColors function not available');
            }
            
            // Also update RFI button color with delayed check
            debugLog('INFO Delayed RFI button color update...');
            updateRFIButtonColorDelayed(groupId);
        }, 5000); // 5 second delay to ensure server processing is complete
                                    
                                    // Check if View Files popup is open - if so, auto-refresh it
                                    const modal = document.getElementById('filesModal');
                                    if (modal && modal.style.display === 'block') {
                                        debugLog('INFO View Files popup is open - auto-refreshing after RFI upload...');
                                        
                                        // Wait 2 seconds for file to be saved, then refresh the popup
                                        setTimeout(() => {
                                            debugLog('INFO Auto-refreshing View Files popup with new RFI file...');
                                            
                                            // Get the current popup data from the groupId
                                            const dateStr = groupId.match(/\d{8}$/);
                                            if (dateStr) {
                                                const formattedDate = dateStr[0].substring(0,4) + '-' + dateStr[0].substring(4,6) + '-' + dateStr[0].substring(6,8);
                                                const clientName = groupId.replace(/_\d{8}$/, '').replace(/_/g, ' ');
                                                
                                                debugLog('INFO Refreshing files for:', clientName, 'on', formattedDate, 'with groupId:', groupId);
                                                loadInspectionFiles(groupId, clientName, formattedDate);
                                            }
                                        }, 2000);
                                    }
                                } else {
                                    debugLog('⚠️ RFI button not found, but continuing without page refresh');
                                    // Page refresh removed to prevent button color reset
                                }
                    } else {
                        alert('Upload failed: ' + (data.error || 'Unknown error'));
                        console.error('Upload failed:', data);
                    }
                })
                .catch(error => {
                    alert = originalAlert; // Restore alert
                    uploadInProgress = false; // Clear upload flag
                    console.error('Upload error:', error);
                    alert('Upload error: ' + error.message);
                });
            }
        };
        
        // Add to DOM and trigger click
        document.body.appendChild(fileInput);
        fileInput.click();
        
        // Clean up after a short delay
        setTimeout(() => {
            if (document.body.contains(fileInput)) {
                document.body.removeChild(fileInput);
                debugLog('File input removed from body');
            }
        }, 100);
        
    } catch (error) {
        console.error('Error in uploadRFI function:', error);
        alert('Error in upload function: ' + error.message);
    }
}

// Upload Invoice function - CLEAN VERSION
function uploadInvoice(groupId) {
    debugLog('uploadInvoice called with groupId:', groupId);
    
    if (!groupId) {
        alert('Error: Group ID is missing');
        return;
    }
    
    try {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf';
        fileInput.style.display = 'none';
        
        fileInput.onchange = function(e) {
            const file = e.target.files[0];
            if (file) {
                if (!file.name.toLowerCase().endsWith('.pdf')) {
                    alert('Only PDF files are allowed. Please select a PDF document.');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                formData.append('group_id', groupId);
                formData.append('document_type', 'invoice');
                formData.append('csrfmiddlewaretoken', getCSRFToken());
                
                debugLog('Uploading invoice:', file.name, 'for group:', groupId);
                uploadInProgress = true; // Set upload flag to prevent status check override
                
                fetch('/upload-document/', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    uploadInProgress = false; // Clear upload flag
                    if (data.success) {
                        alert(data.message || 'Invoice uploaded successfully!');
                        debugLog('Invoice upload successful:', data);
                        
                        // Update button directly to green success state
                        const buttonId = 'invoice-' + groupId;
                        debugLog('DEBUG Updating Invoice button to green success state for:', buttonId);
                        
                        // Find and update the button
                        let button = document.getElementById(buttonId);
                        if (!button) {
                            // Try to find button by pattern search
                            const allButtons = document.querySelectorAll(`button[id^="invoice-"]`);
                            for (let btn of allButtons) {
                                if (btn.id === buttonId) {
                                    button = btn;
                                    break;
                                }
                            }
                        }
                        
                        if (button) {
                            debugLog('SUCCESS Found Invoice button, updating to green success state');
                            
                            // Clear file-deleted attributes since we now have a file
                            button.removeAttribute('data-file-deleted');
                            button.removeAttribute('data-last-updated');
                            
                            // Update button to green success state
                            button.disabled = true;
                            button.className = 'btn btn-sm btn-success success';
                            button.style.backgroundColor = '#28a745';
                            button.style.borderColor = '#28a745';
                            button.style.cursor = 'not-allowed';
                            button.innerHTML = 'Invoice ✓';
                            button.title = 'Invoice file exists';
                            
                            // Remove the onclick handler since button is now disabled
                            button.onclick = null;
                            
                            debugLog('SUCCESS Updated Invoice button to green success state');
                            
                            // IMPORTANT: Mark that files need refresh for this client
                            if (window.uploadedFiles) {
                                window.uploadedFiles[groupId] = true;
                            } else {
                                window.uploadedFiles = {[groupId]: true};
                            }
                            debugLog('DEBUG [DEBUG] Marked groupId for file refresh:', groupId);
                            
                            // Update View Files button colors after upload with delay to ensure server processing
                            debugLog('Updating button colors after Invoice upload...');
                            
                            // Immediately make View Files button ORANGE since we just uploaded a file
                            makeViewFilesButtonOrange(groupId);
                            debugLog('TIMER Setting 5-second timer for delayed color update...');
                            
                            // Clear upload flag before setting delayed update to prevent race condition
                            uploadInProgress = false;
                            debugLog('DEBUG [DEBUG] Cleared upload flag before delayed update');
                            
                            setTimeout(() => {
                                debugLog('TIMER Timer fired! Starting delayed color update...');
                                debugLog('DEBUG [DEBUG] Upload in progress flag at timer execution:', uploadInProgress);
                                debugLog('DEBUG [DEBUG] Status check in progress flag:', statusCheckInProgress);
                                if (typeof updateAllViewFilesButtonColors === 'function') {
                                    debugLog('INFO Delayed file status check after Invoice upload...');
                                    updateAllViewFilesButtonColors();
                                } else {
                                    debugWarn('updateAllViewFilesButtonColors function not available');
                                }
                                
                                // Also update Invoice button color with delayed check
                                debugLog('INFO Delayed Invoice button color update...');
                                updateInvoiceButtonColorDelayed(groupId);
                            }, 5000); // 5 second delay to ensure server processing is complete
                            
                            // Check if View Files popup is open - if so, auto-refresh it
                            const modal = document.getElementById('filesModal');
                            if (modal && modal.style.display === 'block') {
                                debugLog('INFO View Files popup is open - auto-refreshing after Invoice upload...');
                                
                                // Wait 2 seconds for file to be saved, then refresh the popup
                                setTimeout(() => {
                                    debugLog('INFO Auto-refreshing View Files popup with new Invoice file...');
                                    
                                    // Get the current popup data from the groupId
                                    const dateStr = groupId.match(/\d{8}$/);
                                    if (dateStr) {
                                        const formattedDate = dateStr[0].substring(0,4) + '-' + dateStr[0].substring(4,6) + '-' + dateStr[0].substring(6,8);
                                        const clientName = groupId.replace(/_\d{8}$/, '').replace(/_/g, ' ');
                                        
                                        debugLog('INFO Refreshing files for:', clientName, 'on', formattedDate, 'with groupId:', groupId);
                                        loadInspectionFiles(groupId, clientName, formattedDate);
                                    }
                                }, 2000);
                            }
                        } else {
                            debugLog('⚠️ Invoice button not found, but continuing without page refresh');
                            // Page refresh removed to prevent button color reset
                        }
                    } else {
                        alert('Invoice upload failed: ' + (data.error || 'Unknown error'));
                        console.error('Invoice upload failed:', data);
                    }
                })
                .catch(error => {
                    uploadInProgress = false; // Clear upload flag
                    console.error('Invoice upload error:', error);
                    alert('Invoice upload error: ' + error.message);
                });
            }
        };
        
        document.body.appendChild(fileInput);
        fileInput.click();
        
        setTimeout(() => {
            if (document.body.contains(fileInput)) {
                document.body.removeChild(fileInput);
            }
        }, 100);
        
    } catch (error) {
        console.error('Error in uploadInvoice function:', error);
        alert('Error in upload function: ' + error.message);
    }
}

// Upload Lab function
function uploadLab(inspectionId) {
    debugLog('uploadLab called with inspectionId:', inspectionId);
    
    if (!inspectionId) {
        alert('Error: Inspection ID is missing');
        return;
    }
    
    try {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf';
        fileInput.style.display = 'none';
        
        fileInput.onchange = function(e) {
            const file = e.target.files[0];
            if (file) {
                if (!file.name.toLowerCase().endsWith('.pdf')) {
                    alert('Only PDF files are allowed. Please select a PDF document.');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                formData.append('inspection_id', inspectionId);
                formData.append('document_type', 'lab');
                formData.append('csrfmiddlewaretoken', getCSRFToken());
                
                debugLog('Uploading lab result:', file.name, 'for inspection:', inspectionId);
                uploadInProgress = true;
                
                fetch('/upload-document/', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    uploadInProgress = false;
                    if (data.success) {
                        alert(data.message || 'Lab result uploaded successfully!');
                        debugLog('Lab upload successful:', data);
                        
                        // Update button to green success state
                        const buttonId = 'lab-' + inspectionId;
                        let button = document.getElementById(buttonId);
                        if (button) {
                            button.classList.add('uploaded');
                            button.innerHTML = '<i class="fas fa-flask"></i> Lab ✓';
                            button.disabled = true;
                            button.title = 'Lab result uploaded';
                        }
                        
                        // Trigger delayed color update
                        setTimeout(() => {
                            updateAllViewFilesButtonColors();
                        }, 1000);
                    } else {
                        alert(data.message || 'Failed to upload lab result');
                        console.error('Lab upload failed:', data);
                    }
                })
                .catch(error => {
                    uploadInProgress = false;
                    console.error('Error uploading lab result:', error);
                    alert('Error uploading lab result. Please try again.');
                });
            }
        };
        
        document.body.appendChild(fileInput);
        fileInput.click();
        document.body.removeChild(fileInput);
        
    } catch (error) {
        console.error('Error creating file input for lab upload:', error);
        alert('Error creating file input. Please try again.');
    }
}

// Upload Lab Form function
function uploadLabForm(inspectionId) {
    debugLog('uploadLabForm called with inspectionId:', inspectionId);
    
    if (!inspectionId) {
        alert('Error: Inspection ID is missing');
        return;
    }
    
    try {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf';
        fileInput.style.display = 'none';
        
        fileInput.onchange = function(e) {
            const file = e.target.files[0];
            if (file) {
                if (!file.name.toLowerCase().endsWith('.pdf')) {
                    alert('Only PDF files are allowed. Please select a PDF document.');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                formData.append('inspection_id', inspectionId);
                formData.append('document_type', 'lab_form');
                formData.append('csrfmiddlewaretoken', getCSRFToken());
                
                debugLog('Uploading lab form:', file.name, 'for inspection:', inspectionId);
                uploadInProgress = true;
                
                fetch('/upload-document/', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    uploadInProgress = false;
                    if (data.success) {
                        alert(data.message || 'Lab form uploaded successfully!');
                        debugLog('Lab form upload successful:', data);
                        
                        // Update button to green success state
                        const buttonId = 'lab-form-' + inspectionId;
                        let button = document.getElementById(buttonId);
                        if (button) {
                            button.classList.add('uploaded');
                            button.innerHTML = '<i class="fas fa-file-alt"></i> Lab Form ✓';
                            button.disabled = true;
                            button.title = 'Lab form uploaded';
                        }
                        
                        // Trigger delayed color update
                        setTimeout(() => {
                            updateAllViewFilesButtonColors();
                        }, 1000);
                    } else {
                        alert(data.message || 'Failed to upload lab form');
                        console.error('Lab form upload failed:', data);
                    }
                })
                .catch(error => {
                    uploadInProgress = false;
                    console.error('Error uploading lab form:', error);
                    alert('Error uploading lab form. Please try again.');
                });
            }
        };
        
        document.body.appendChild(fileInput);
        fileInput.click();
        document.body.removeChild(fileInput);
        
    } catch (error) {
        console.error('Error creating file input for lab form upload:', error);
        alert('Error creating file input. Please try again.');
    }
}

// Upload Retest function
function uploadRetest(inspectionId) {
    debugLog('uploadRetest called with inspectionId:', inspectionId);
    
    if (!inspectionId) {
        alert('Error: Inspection ID is missing');
        return;
    }
    
    try {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf';
        fileInput.style.display = 'none';
        
        fileInput.onchange = function(e) {
            const file = e.target.files[0];
            if (file) {
                if (!file.name.toLowerCase().endsWith('.pdf')) {
                    alert('Only PDF files are allowed. Please select a PDF document.');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                formData.append('inspection_id', inspectionId);
                formData.append('document_type', 'retest');
                formData.append('csrfmiddlewaretoken', getCSRFToken());
                
                debugLog('Uploading retest document:', file.name, 'for inspection:', inspectionId);
                uploadInProgress = true;
                
                fetch('/upload-document/', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    uploadInProgress = false;
                    if (data.success) {
                        alert(data.message || 'Retest document uploaded successfully!');
                        debugLog('Retest upload successful:', data);
                        
                        // Update button to green success state
                        const buttonId = 'retest-' + inspectionId;
                        let button = document.getElementById(buttonId);
                        if (button) {
                            button.classList.add('uploaded');
                            button.innerHTML = '<i class="fas fa-redo"></i> Retest ✓';
                            button.disabled = true;
                            button.title = 'Retest document uploaded';
                        }
                        
                        // Trigger delayed color update
                        setTimeout(() => {
                            updateAllViewFilesButtonColors();
                        }, 1000);
                    } else {
                        alert(data.message || 'Failed to upload retest document');
                        console.error('Retest upload failed:', data);
                    }
                })
                .catch(error => {
                    uploadInProgress = false;
                    console.error('Error uploading retest document:', error);
                    alert('Error uploading retest document. Please try again.');
                });
            }
        };
        
        document.body.appendChild(fileInput);
        fileInput.click();
        document.body.removeChild(fileInput);
        
    } catch (error) {
        console.error('Error creating file input for retest upload:', error);
        alert('Error creating file input. Please try again.');
    }
}

// Files Popup function - Enhanced with actual modal and fallback test data
function openFilesPopup(groupId, clientName, inspectionDate) {
    debugLog('openFilesPopup called:', { groupId, clientName, inspectionDate });
    
    const modal = document.getElementById('filesModal');
    const modalTitle = document.getElementById('modalTitle');
    const filesLoading = document.getElementById('filesLoading');
    const filesContent = document.getElementById('filesContent');
    const downloadBtn = document.getElementById('downloadAllBtn');

    if (!modal) {
        // Fallback to alert if modal doesn't exist
        alert('Files popup for ' + clientName + ' on ' + inspectionDate + '\nGroup ID: ' + groupId + '\n\nModal not found - using fallback.');
        return;
    }

    // Clean client name and date for display and download functionality
    let cleanClientName = clientName;
    if (typeof cleanClientName === 'string') {
        cleanClientName = cleanClientName.replace(/\\u002D/g, '-');
        cleanClientName = cleanClientName.replace(/\\u002F/g, '/');
        cleanClientName = cleanClientName.replace(/\\u0020/g, ' ');
        try {
            cleanClientName = JSON.parse('"' + cleanClientName + '"');
        } catch (e) {
            // Use as-is if parsing fails
        }
    }
    
    let cleanDate = inspectionDate;
    if (typeof cleanDate === 'string') {
        cleanDate = cleanDate.replace(/\\u002D/g, '-');
        try {
            cleanDate = JSON.parse('"' + cleanDate + '"');
        } catch (e) {
            // Use as-is if parsing fails
        }
    }
    
    window.currentFilesClient = cleanClientName;
    window.currentFilesDate = cleanDate;
    window.currentFilesGroupId = groupId;

    // Set title and show modal - shows files for specific inspection date
    modalTitle.textContent = 'Files for ' + cleanClientName + ' - ' + cleanDate;
    modal.style.display = 'block';

    // Show download button
    if (downloadBtn) downloadBtn.style.display = 'flex';

    // Show loading state
    if (filesLoading) filesLoading.style.display = 'block';
    if (filesContent) filesContent.style.display = 'none';

    debugLog('INFO File overlay: View Files clicked - Starting files fetch for', clientName, 'on', inspectionDate);

    // Try to load real files first, but show test data if none found
    loadInspectionFilesWithFallback(groupId, clientName, inspectionDate);
}

// Close files popup function
function closeFilesPopup() {
    debugLog('closeFilesPopup called');
    const modal = document.getElementById('filesModal');
    if (modal) {
        modal.style.display = 'none';
    }
    
    // Hide download button
    const downloadBtn = document.getElementById('downloadAllBtn');
    if (downloadBtn) {
        downloadBtn.style.display = 'none';
    }
    
    // Don't refresh inspection data when popup closes to prevent button reset loop
    if (window.currentFilesGroupId && window.currentFilesClient && window.currentFilesDate) {
        debugLog(`INFO Popup closed - skipping inspection refresh to prevent button reset`);
        debugLog(`DEBUG Group ID: ${window.currentFilesGroupId}`);
        
        // Skip refresh to prevent button reset loop
        debugLog('INFO Skipping inspection refresh to prevent button reset loop');
    }
    
    // Process any pending button updates now that popup is closed
    setTimeout(() => {
        processPendingButtonUpdates();
    }, 100);
    
    // Also try to process updates immediately
    processPendingButtonUpdates();
}

// Load inspection files with direct working method (removed unreliable first attempt)
async function loadInspectionFilesWithFallback(groupId, clientName, inspectionDate) {
    try {
        debugLog('INFO File fetch: Starting direct file fetch (using working method)...');
        
        // Fix client name - decode any Unicode escapes
        let cleanClientName = clientName;
        if (typeof cleanClientName === 'string') {
            // Handle common Unicode escapes
            cleanClientName = cleanClientName.replace(/\\u002D/g, '-');
            cleanClientName = cleanClientName.replace(/\\u002F/g, '/');
            cleanClientName = cleanClientName.replace(/\\u0020/g, ' ');
            
            // Try to decode any remaining Unicode escapes
            try {
                cleanClientName = JSON.parse('"' + cleanClientName + '"');
            } catch (e) {
                // If JSON parsing fails, just use the string as-is
                debugLog('Could not parse client name as JSON, using as-is:', cleanClientName);
            }
        }
        
        // Fix date format - decode any Unicode escapes and ensure proper format
        let cleanDate = inspectionDate;
        if (typeof cleanDate === 'string') {
            // Handle common Unicode escapes
            cleanDate = cleanDate.replace(/\\u002D/g, '-');
            cleanDate = cleanDate.replace(/\\u002F/g, '/');
            cleanDate = cleanDate.replace(/\\u0020/g, ' ');
            
            // Try to decode any remaining Unicode escapes
            try {
                cleanDate = JSON.parse('"' + cleanDate + '"');
            } catch (e) {
                // If JSON parsing fails, just use the string as-is
                debugLog('Could not parse date as JSON, using as-is:', cleanDate);
            }
        }
        
        debugLog('INFO Original client name:', clientName);
        debugLog('INFO Cleaned client name:', cleanClientName);
        debugLog('INFO Original date:', inspectionDate);
        debugLog('INFO Cleaned date:', cleanDate);
        
        // Get the first inspection ID from the group by finding lab buttons
        let inspectionId = null;
        const rows = document.querySelectorAll('tr[data-client-name="' + cleanClientName + '"][data-inspection-date="' + cleanDate + '"]');
        for (const row of rows) {
            const labButton = row.querySelector('button[id^="lab-"]');
            if (labButton) {
                const buttonId = labButton.id;
                inspectionId = buttonId.replace('lab-', '');
                debugLog('DEBUG Found inspection ID from lab button:', inspectionId);
                break;
            }
        }
        
        if (!inspectionId) {
            debugWarn('⚠️ No inspection ID found for group, will show all files');
        }

        // Use the working method directly with aggressive cache-busting
        const cacheBuster = Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const response = await fetch('/list-client-folder-files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'X-Cache-Bust': cacheBuster  // Additional cache-busting header
            },
            body: JSON.stringify({
                client_name: cleanClientName,
                inspection_date: cleanDate,
                inspection_id: inspectionId,  // Add inspection ID for filtering
                _cache_bust: cacheBuster,
                _force_refresh: true  // Force server to skip cache
            })
        });
        
        const result = await response.json();
        debugLog('INFO File fetch: File fetch completed:', result.success);
        debugLog('INFO File fetch: Full server response:', result);
        
        const filesLoading = document.getElementById('filesLoading');
        const filesContent = document.getElementById('filesContent');
        const filesList = document.getElementById('filesList');
        
        if (filesLoading) filesLoading.style.display = 'none';
        if (filesContent) filesContent.style.display = 'block';
        
        if (result.success && result.files && filesList) {
            debugLog('DEBUG Server returned files object:', result.files);
            debugLog('DEBUG Files object keys:', Object.keys(result.files));
            debugLog('DEBUG Files object values:', Object.values(result.files));
            debugLog('DEBUG Lab files found:', result.files.lab ? result.files.lab.length : 0);
            debugLog('DEBUG Lab form files found:', result.files.lab_form ? result.files.lab_form.length : 0);
            debugLog('DEBUG Retest files found:', result.files.retest ? result.files.retest.length : 0);
            
            const hasFiles = Object.values(result.files).some(fileList => fileList && fileList.length > 0);
            debugLog('DEBUG Has files check result:', hasFiles);
            
            if (hasFiles) {
                debugLog('SUCCESS Files found and displaying');
                displayFiles(result.files, result.message);
            } else {
                debugLog('FOLDER No files found - showing empty message');
                const filesList = document.getElementById('filesList');
                if (filesList) {
                    filesList.innerHTML = '<div class="empty-category">FOLDER No files found for this inspection.</div>';
                }
            }
        } else if (filesList) {
            debugLog('ERROR Server returned error');
            const filesList = document.getElementById('filesList');
            if (filesList) {
                filesList.innerHTML = '<div class="empty-category">ERROR Error loading files. Please try again.</div>';
            }
        }
        
    } catch (error) {
        debugLog('ERROR File fetch error:', error);
        const filesList = document.getElementById('filesList');
        if (filesList) {
            filesList.innerHTML = '<div class="empty-category">ERROR Network error. Please try again.</div>';
        }
    }
}

// Show no files message when no real files are available
function showTestFiles(clientName, inspectionDate, serverMessage) {
    const filesList = document.getElementById('filesList');
    if (filesList) {
        let message = serverMessage || 'No files found for this inspection.';
        filesList.innerHTML = `<div class="empty-category">FOLDER ${message}</div>`;
    }
}

// Load inspection files function (original)
async function loadInspectionFiles(groupId, clientName, inspectionDate) {
    try {
        debugLog('INFO File fetch: Starting file fetch request...');
        
        // Fix date format - decode any Unicode escapes
        let cleanDate = inspectionDate;
        if (typeof cleanDate === 'string') {
            cleanDate = cleanDate.replace(/\\u002D/g, '-');
            try {
                cleanDate = JSON.parse('"' + cleanDate + '"');
            } catch (e) {
                // Use as-is if parsing fails
            }
        }
        
        const response = await fetch('/inspections/files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                group_id: groupId,
                client_name: clientName,
                inspection_date: cleanDate,
                _force_refresh: true
            })
        });
        
        const result = await response.json();
        debugLog('INFO File fetch: File fetch completed:', result.success);
        debugLog('INFO File fetch: Full server response:', result);
        debugLog('INFO File fetch: Response text length:', JSON.stringify(result).length);
        debugLog('INFO File fetch: Files data:', result.files);
        debugLog('INFO File fetch: Message:', result.message);
        
        const filesLoading = document.getElementById('filesLoading');
        const filesContent = document.getElementById('filesContent');
        const filesList = document.getElementById('filesList');
        
        if (filesLoading) filesLoading.style.display = 'none';
        if (filesContent) filesContent.style.display = 'block';
        
        if (result.success && filesList) {
            debugLog('SUCCESS Calling displayFiles with success response');
            displayFiles(result.files, result.message);
        } else if (filesList) {
            debugLog('ERROR Server returned error or no success flag');
            filesList.innerHTML = '<div class="empty-category">Error loading files: ' + (result.error || result.message || 'Unknown error') + '</div>';
        }
        
    } catch (error) {
        const filesLoading = document.getElementById('filesLoading');
        const filesContent = document.getElementById('filesContent');
        const filesList = document.getElementById('filesList');
        
        debugLog('ERROR File fetch: File fetch error:', error);
        
        if (filesLoading) filesLoading.style.display = 'none';
        if (filesContent) filesContent.style.display = 'block';
        if (filesList) filesList.innerHTML = '<div class="empty-category">Network error: ' + error.message + '</div>';
    }
}

// Display files function - Enhanced with delete functionality
function displayFiles(files, message = null, isTestData = false) {
    const filesList = document.getElementById('filesList');
    if (!filesList) {
        console.error('filesList element not found');
        return;
    }
    
    debugLog('FOLDER displayFiles called with:', { files, message, isTestData });
    
    let html = '';
    
    // Show success message if provided
    if (message) {
        const messageClass = isTestData ? 'info-message' : 'success-message';
        const bgColor = isTestData ? '#d1ecf1' : '#d4edda';
        const textColor = isTestData ? '#0c5460' : '#155724';
        const borderColor = isTestData ? '#bee5eb' : '#c3e6cb';
        const icon = isTestData ? 'fa-info-circle' : 'fa-check-circle';
        
        html += `<div class="${messageClass}" style="background: ${bgColor}; color: ${textColor}; padding: 1rem; margin-bottom: 1rem; border-radius: 4px; border: 1px solid ${borderColor};">
            <i class="fas ${icon}"></i> ${message}
        </div>`;
    }
    
    // Check if there are actually any files (not just empty arrays)
    const hasFiles = files && Object.values(files).some(fileList => fileList && fileList.length > 0);
    
    if (!hasFiles) {
        html += '<div class="empty-category">FOLDER No files found for this inspection.</div>';
    } else {
        html += '<div class="files-grid">';
        let totalFiles = 0;
        
        // Display files by category
        for (const [category, fileList] of Object.entries(files)) {
            debugLog(`FOLDER Processing category: ${category}`, fileList);
            
            if (fileList && Array.isArray(fileList) && fileList.length > 0) {
                totalFiles += fileList.length;
                
                // Map category keys to proper capitalized labels
                const categoryLabels = {
                    'rfi': 'Request For Invoice',
                    'invoice': 'Invoice',
                    'lab': 'Lab Results',
                    'lab_form': 'Lab Forms',
                    'retest': 'Retest',
                    'compliance': 'Compliance'
                };
                
                debugLog(`FOLDER Processing category: ${category} with ${fileList.length} files`);
                
                const displayLabel = categoryLabels[category] || category.charAt(0).toUpperCase() + category.slice(1);
                
                html += `<div class="file-category" style="margin-bottom: 1rem; border: 1px solid #dee2e6; border-radius: 4px; padding: 1rem;">
                    <h4 style="color: #495057; margin-bottom: 0.5rem; display: flex; align-items: center;">
                        <i class="fas fa-folder" style="margin-right: 0.5rem; color: #6c757d;"></i>
                        ${displayLabel} (${fileList.length})
                    </h4>
                    <div class="file-list">`;
                
                fileList.forEach((file, index) => {
                    debugLog(`FILES File ${index}:`, file);
                    const fileName = file.name || file.filename || file.file_name || file;
                    const filePath = file.path || file.url || file.file_path || file;
                    const isTest = file.isTest || isTestData;
                    const isZipFile = fileName.toLowerCase().endsWith('.zip');
                    
                    // Choose appropriate icon based on file type
                    let fileIcon = 'fa-file';
                    let iconColor = '#6c757d';
                    if (isZipFile) {
                        fileIcon = 'fa-file-archive';
                        iconColor = '#fd7e14';
                    } else if (fileName.toLowerCase().endsWith('.pdf')) {
                        fileIcon = 'fa-file-pdf';
                        iconColor = '#dc3545';
                    }
                    
                    html += `<div class="file-item" data-file-path="${filePath}" data-file-name="${fileName}" style="display: flex; align-items: center; padding: 0.5rem; border: 1px solid #e9ecef; border-radius: 4px; margin-bottom: 0.5rem; ${isTest ? 'background-color: #f8f9fa;' : ''}">
                        <i class="fas ${fileIcon}" style="color: ${iconColor}; margin-right: 0.5rem;"></i>
                        <span class="file-name" style="flex: 1; margin-right: 0.5rem; ${isTest ? 'font-style: italic; color: #6c757d;' : ''}">${fileName}</span>
                        <div class="file-actions" style="display: flex; gap: 0.25rem;">`;
                    
                    if (isTest) {
                        html += `<span class="btn btn-sm" style="background: #6c757d; color: white; border: none; padding: 0.25rem 0.5rem; border-radius: 4px; cursor: not-allowed;" title="Test file - not downloadable">
                            <i class="fas fa-eye"></i> Preview
                        </span>`;
                    } else {
                        // Use eye icon for both regular files and ZIP files
                        const viewFunction = isZipFile ? 'viewZipContents' : 'viewFile';
                        const viewTitle = isZipFile ? 'View ZIP Contents' : 'View';
                        const viewIcon = isZipFile ? 'fa-eye' : 'fa-eye';
                        const viewColor = isZipFile ? '#fd7e14' : '#17a2b8';
                        
                        html += `                        <button class="btn btn-sm" onclick="${viewFunction}('${filePath}', '${fileName}')" title="${viewTitle}" style="background: ${viewColor}; color: white; border: none; padding: 0.25rem 0.5rem; border-radius: 4px; margin-right: 0.25rem;">
                            <i class="fas ${viewIcon}"></i>
                        </button>
                        <button class="btn btn-sm" onclick="downloadFile('${filePath}')" title="Download" style="background: #28a745; color: white; border: none; padding: 0.25rem 0.5rem; border-radius: 4px; margin-right: 0.25rem;">
                            <i class="fas fa-download"></i>
                        </button>
                        ${!filePath.toLowerCase().includes('compliance') ? `<button class="btn btn-sm" data-file-path="${filePath}" data-file-name="${fileName}" onclick="deleteFile('${filePath}', '${fileName}')" title="Delete" style="background: #dc3545; color: white; border: none; padding: 0.25rem 0.5rem; border-radius: 4px;">
                            <i class="fas fa-trash"></i>
                        </button>` : ''}
                        `;
                    }
                    
                    html += `</div></div>`;
                });
                
                html += '</div></div>';
            }
        }
        
        if (totalFiles === 0) {
            html += '<div class="empty-category">FOLDER All categories are empty.</div>';
        } else if (isTestData) {
            html += `<div style="margin-top: 1rem; padding: 0.75rem; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; color: #856404;">
                <i class="fas fa-lightbulb" style="margin-right: 0.5rem;"></i>
                <strong>💡 Tip:</strong> Upload real files using the RFI button to see actual downloadable documents here.
            </div>`;
        }
        
        html += '</div>';
    }
    
    filesList.innerHTML = html;
    debugLog('FOLDER displayFiles completed, HTML length:', html.length);
}

// Download individual file function
function downloadFile(filePath) {
    debugLog('Downloading file:', filePath);
    if (filePath.startsWith('/test/')) {
        alert('This is a test file and cannot be downloaded. Upload real files using the RFI button to enable downloads.');
        return;
    }
    
    // Clean the file path - remove /media/ prefix if present
    let cleanFilePath = filePath;
    if (cleanFilePath.startsWith('/media/')) {
        cleanFilePath = cleanFilePath.substring(7); // Remove '/media/'
    }
    
    debugLog('Download - Original path:', filePath);
    debugLog('Download - Clean path:', cleanFilePath);
    
    // Use fetch to download and create blob for proper download behavior
    const downloadUrl = '/inspections/download-file/?file=' + encodeURIComponent(cleanFilePath);
    
    debugLog('Initiating download from:', downloadUrl);
    
    // Use fetch to get the file and create a proper download
    fetch(downloadUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Download failed: ' + response.status);
            }
            return response.blob();
        })
        .then(blob => {
            // Create download link with blob
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filePath.split('/').pop(); // Use original filename
            link.style.display = 'none';
            
            // Add to DOM, click, and remove
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Clean up blob URL
            window.URL.revokeObjectURL(url);
            
            debugLog('Download completed for:', cleanFilePath);
        })
        .catch(error => {
            console.error('Download error:', error);
            alert('Download failed: ' + error.message);
        });
}

// Delete file function - Only compliance documents are protected from deletion
async function deleteFile(filePath, fileName) {
    debugLog('Deleting file:', filePath, fileName);
    
    if (filePath.startsWith('/test/')) {
        alert('This is a test file and cannot be deleted.');
        return;
    }
    
    // Prevent deletion of compliance documents only
    if (filePath.includes('/Compliance/') || filePath.toLowerCase().includes('compliance')) {
        alert('Compliance documents cannot be deleted for security and audit purposes.');
        return;
    }
    
    // Confirm deletion
    if (!confirm(`Are you sure you want to delete "${fileName}"?\n\nThis action cannot be undone.`)) {
        return;
    }
    
    try {
        // Get the current client and inspection date from stored values
        let clientName = window.currentFilesClient;
        let inspectionDate = window.currentFilesDate;
        let groupId = window.currentFilesGroupId;
        
        if (!clientName || !inspectionDate || !groupId) {
            alert('Error: Missing client, inspection date, or group ID information');
            return;
        }
        
        // Clean the inspection date - decode any Unicode escapes
        if (typeof inspectionDate === 'string') {
            inspectionDate = inspectionDate.replace(/\\u002D/g, '-');
            try {
                inspectionDate = JSON.parse('"' + inspectionDate + '"');
            } catch (e) {
                // Use as-is if parsing fails
            }
        }
        
        // Clean the file path - remove /media/ prefix if present
        let cleanFilePath = filePath;
        if (cleanFilePath.startsWith('/media/')) {
            cleanFilePath = cleanFilePath.substring(7); // Remove '/media/'
        }
        
        debugLog('Delete parameters:', {
            file_path: cleanFilePath,
            client_name: clientName,
            inspection_date: inspectionDate
        });
        
        const response = await fetch('/delete-inspection-file/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                file_path: cleanFilePath,
                client_name: clientName,
                inspection_date: inspectionDate
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            debugLog('File deleted:', fileName);
            debugLog('DEBUG [DEBUG] File path in success block:', filePath);
            
            // Determine document type from file path
            let documentType = 'unknown';
            if (filePath.includes('/Request For Invoice/') || filePath.includes('/rfi/')) {
                documentType = 'rfi';
                debugLog('DEBUG [DEBUG] RFI file detected!');
            } else if (filePath.includes('/invoice/')) {
                documentType = 'invoice';
                debugLog('DEBUG [DEBUG] Invoice file detected!');
            } else if (filePath.includes('/retest/')) {
                documentType = 'retest';
                debugLog('DEBUG [DEBUG] Retest file detected!');
            } else if ((filePath.includes('/lab results/') || filePath.includes('/lab/')) && (filePath.toLowerCase().includes('lab_form') || filePath.toLowerCase().includes('labform') || filePath.toLowerCase().includes('lab form'))) {
                documentType = 'lab_form';
                debugLog('DEBUG [DEBUG] Lab Form file detected!');
            } else if (filePath.includes('/lab results/') || filePath.includes('/lab/')) {
                documentType = 'lab';
                debugLog('DEBUG [DEBUG] Lab file detected!');
            } else {
                debugLog('DEBUG [DEBUG] Unknown file type detected!');
            }
            debugLog(`DEBUG [DEBUG] File path: ${filePath}, Document type: ${documentType}`);
            
            // IMMEDIATE UI UPDATE: Remove the file from the current display
            debugLog('INFO Immediately removing file from UI before server refresh...');
            const fileElements = document.querySelectorAll(`[data-file-path*="${fileName}"]`);
            fileElements.forEach(element => {
                const fileContainer = element.closest('.file-item') || element.closest('.file-entry');
                if (fileContainer) {
                    fileContainer.style.opacity = '0.3';
                    fileContainer.innerHTML = `<div class="file-deleted">FILES ${fileName} - Deleted</div>`;
                }
            });
            
            // IMMEDIATE BUTTON RESET: Reset the corresponding button immediately
            if (documentType !== 'unknown') {
                debugLog(`🔧 Immediately resetting ${documentType} button...`);
                
                // For lab, lab form, and retest buttons, we need to find the specific inspection ID from the file path
                if (documentType === 'lab' || documentType === 'lab_form' || documentType === 'retest') {
                    // Extract inspection ID from file path (e.g., "8999_lab_20251002_211932.pdf" -> "8999")
                    // Note: Check lab_form before lab to avoid partial matches
                    const inspectionIdMatch = filePath.match(/\/(\d+)_(?:lab_form|lab|retest)_/);
                    if (inspectionIdMatch && inspectionIdMatch[1]) {
                        const inspectionId = inspectionIdMatch[1];
                        // Convert lab_form to lab-form to match HTML button ID format
                        const buttonType = documentType.replace(/_/g, '-');
                        const specificButtonId = `${buttonType}-${inspectionId}`;
                        debugLog(`🔧 Resetting specific ${documentType} button: ${specificButtonId}`);
                        
                        const specificButton = document.getElementById(specificButtonId);
                        if (specificButton) {
                            // Reset this specific button to grey
                            specificButton.disabled = false;
                            specificButton.classList.remove('uploaded', 'btn-success');
                            specificButton.classList.add('btn-outline-secondary', 'btn-sm');
                            specificButton.style.background = '';
                            specificButton.style.color = '';
                            specificButton.style.border = '';
                            specificButton.style.cursor = 'pointer';
                            // Set the button content with appropriate icon
                            if (documentType === 'lab') {
                                specificButton.innerHTML = `<i class="fas fa-flask"></i> LAB`;
                            } else if (documentType === 'lab_form') {
                                specificButton.innerHTML = `<i class="fas fa-file-alt"></i> LAB FORM`;
                            } else if (documentType === 'retest') {
                                specificButton.innerHTML = `<i class="fas fa-redo"></i> RETEST`;
                            } else {
                                specificButton.innerHTML = documentType.toUpperCase();
                            }
                            specificButton.title = `Upload ${documentType.toUpperCase()}`;
                            specificButton.setAttribute('data-file-deleted', 'true');
                            
                            // Re-enable onclick functionality
                            if (documentType === 'lab') {
                                specificButton.onclick = function() { uploadLab(inspectionId); };
                            } else if (documentType === 'lab_form') {
                                specificButton.onclick = function() { uploadLabForm(inspectionId); };
                            } else if (documentType === 'retest') {
                                specificButton.onclick = function() { uploadRetest(inspectionId); };
                            }
                            
                            debugLog(`SUCCESS Reset specific ${documentType} button ${specificButtonId} to grey`);
                        } else {
                            debugLog(`⚠️ Specific ${documentType} button not found: ${specificButtonId}`);
                            // Fallback to group-level reset
                resetButtonImmediately(documentType, groupId, clientName, inspectionDate);
                        }
                    } else {
                        debugLog('⚠️ Could not extract inspection ID from file path, falling back to group reset');
                        resetButtonImmediately(documentType, groupId, clientName, inspectionDate);
                    }
                } else {
                    // For other document types (RFI, Invoice), use the existing group-level reset
                    resetButtonImmediately(documentType, groupId, clientName, inspectionDate);
                }
            }
            
            // Clear any client-side file cache
            debugLog('🧹 Clearing client-side file cache...');
            if (window.fileCache) {
                const cacheKey = `${clientName}_${inspectionDate}`;
                delete window.fileCache[cacheKey];
                debugLog(`🧹 Cleared cache for key: ${cacheKey}`);
            }
            
            // Clear localStorage cache if it exists
            const cacheKeys = Object.keys(localStorage).filter(key => 
                key.includes('files_') && 
                key.includes(clientName.replace(/\s+/g, '_')) && 
                key.includes(inspectionDate)
            );
            cacheKeys.forEach(key => {
                localStorage.removeItem(key);
                debugLog(`🧹 Cleared localStorage key: ${key}`);
            });
            
            // Update the corresponding button immediately
            if (documentType !== 'unknown') {
                debugLog(`🔧 Calling updateButtonAfterDeletion for ${documentType} with client: ${clientName}, date: ${inspectionDate}`);
                updateButtonAfterDeletion(clientName, inspectionDate, documentType);
                
                // Also directly reset the button to gray state
                const groupId = window.currentFilesGroupId;
                if (groupId) {
                    const buttonId = `${documentType}-${groupId}`;
                    const button = document.getElementById(buttonId);
                    if (button) {
                        debugLog(`🔧 Directly resetting ${documentType} button to gray state`);
                        button.disabled = false;
                        button.className = 'btn btn-outline-secondary btn-sm';
                        button.style.background = '';
                        button.style.color = '';
                        button.style.cursor = 'pointer';
                        button.innerHTML = documentType.toUpperCase();
                        button.title = `Upload ${documentType.toUpperCase()}`;
                        button.setAttribute('data-file-deleted', 'true');
                        button.setAttribute('data-last-updated', Date.now().toString());
                        
                        // Re-enable onclick functionality
                        if (documentType === 'rfi') {
                            button.onclick = function() { uploadRFI(groupId); };
                        } else if (documentType === 'invoice') {
                            button.onclick = function() { uploadInvoice(groupId); };
                        }
                        debugLog(`SUCCESS ${documentType.toUpperCase()} button directly reset to gray state`);
                    } else {
                        debugLog(`⚠️ Button not found for direct reset: ${buttonId}`);
                    }
                }
            }
            
            // Refresh the files list with a delay to ensure server-side cleanup is complete
            if (groupId && clientName && inspectionDate) {
                debugLog('INFO Scheduling fresh file list reload...');
                setTimeout(() => {
                    loadInspectionFilesWithFallback(groupId, clientName, inspectionDate);
                }, 500); // Give server time to complete cleanup
                
                // For RFI and Invoice deletions, ensure button stays reset and prevent reversion
                if (documentType === 'rfi' || documentType === 'invoice') {
                    // Mark this button as permanently reset to prevent UI updates from overriding it
                    const buttonId = `${documentType}-${groupId}`;
                    const button = document.getElementById(buttonId);
                    if (button) {
                        // Set a data attribute to mark this button as reset after deletion
                        button.setAttribute('data-file-deleted', 'true');
                        
                        // Clear any localStorage entries that might cause the button to show as uploaded
                        const uploadStatus = JSON.parse(localStorage.getItem('uploadStatus') || '{}');
                        delete uploadStatus[buttonId];
                        localStorage.setItem('uploadStatus', JSON.stringify(uploadStatus));
                        
                        // Force the button to stay in uploadable state
                        button.disabled = false;
                        button.style.background = '#28a745';
                        button.style.color = 'white';
                        button.style.cursor = 'pointer';
                        button.innerHTML = `<i class="fas fa-upload"></i> ${documentType.toUpperCase()}`;
                        button.title = `Upload ${documentType.toUpperCase()}`;
                        
                        // Re-enable onclick functionality
                        if (documentType === 'rfi') {
                            button.onclick = function() { uploadRFI(groupId); };
                        } else if (documentType === 'invoice') {
                            button.onclick = function() { uploadInvoice(groupId); };
                        }
                        
                        debugLog(`SUCCESS Permanently reset ${documentType} button for ${clientName} - marked as file-deleted`);
                    }
                    
                    // IMMEDIATELY update View Files button colors after file deletion
                    debugLog('COLOR Immediately updating View Files button colors after file deletion...');
                    updateViewFilesButtonAfterFileDeletion(clientName, inspectionDate);
                    
                    // IMMEDIATE TARGETED CHECK: Run appropriate targeted check based on file type
                    debugLog(`DEBUG [DEBUG] Document type: ${documentType}, Group ID: ${groupId}`);
                    if (documentType === 'rfi') {
                        debugLog(`🎯 [IMMEDIATE] Running targeted RFI check for deleted file: ${groupId}`);
                        immediateRFIButtonCheck(groupId, clientName, inspectionDate);
                    } else if (documentType === 'invoice') {
                        debugLog(`🎯 [IMMEDIATE] Running targeted Invoice check for deleted file: ${groupId}`);
                        immediateInvoiceButtonCheck(groupId, clientName, inspectionDate);
                    } else if (documentType === 'lab') {
                        debugLog(`🎯 [IMMEDIATE] Running targeted Lab check for deleted file: ${groupId}`);
                        immediateLabButtonCheck(groupId, clientName, inspectionDate);
                    } else if (documentType === 'lab_form') {
                        debugLog(`🎯 [IMMEDIATE] Running targeted Lab Form check for deleted file: ${groupId}`);
                        immediateLabFormButtonCheck(groupId, clientName, inspectionDate);
                    } else if (documentType === 'retest') {
                        debugLog(`🎯 [IMMEDIATE] Running targeted Retest check for deleted file: ${groupId}`);
                        immediateRetestButtonCheck(groupId, clientName, inspectionDate);
                    } else {
                        debugLog(`⚠️ [DEBUG] Not running targeted check - document type is: ${documentType}`);
                    }
                } else {
                    // IMMEDIATELY update View Files button colors after file deletion for other document types
                    debugLog('COLOR Immediately updating View Files button colors after file deletion...');
                    updateViewFilesButtonAfterFileDeletion(clientName, inspectionDate);
                }
            }
        } else {
            // Handle "File not found" as a special case - file was already deleted
            if (result.error && result.error.includes('File not found')) {
                debugLog('File already deleted from server, updating UI...');
                
                // Determine document type from file path
                let documentType = 'unknown';
                if (filePath.includes('/Request For Invoice/') || filePath.includes('/rfi/')) {
                    documentType = 'rfi';
                } else if (filePath.includes('/invoice/')) {
                    documentType = 'invoice';
                } else if (filePath.includes('/retest/')) {
                    documentType = 'retest';
                } else if ((filePath.includes('/lab results/') || filePath.includes('/lab/')) && (filePath.toLowerCase().includes('lab_form') || filePath.toLowerCase().includes('labform') || filePath.toLowerCase().includes('lab form'))) {
                    documentType = 'lab_form';
                } else if (filePath.includes('/lab results/') || filePath.includes('/lab/')) {
                    documentType = 'lab';
                }
                debugLog(`DEBUG [DEBUG] File path: ${filePath}, Document type: ${documentType}`);
                
                // Update the corresponding button immediately
                if (documentType !== 'unknown') {
                    debugLog(`🔧 Calling updateButtonAfterDeletion for ${documentType} with client: ${clientName}, date: ${inspectionDate}`);
                    updateButtonAfterDeletion(clientName, inspectionDate, documentType);
                    
                    // Also directly reset the button to gray state
                    if (groupId) {
                        const buttonId = `${documentType}-${groupId}`;
                        const button = document.getElementById(buttonId);
                        if (button) {
                            debugLog(`🔧 Directly resetting ${documentType} button to gray state`);
                            button.disabled = false;
                            button.className = 'btn btn-outline-secondary btn-sm';
                            button.style.background = '';
                            button.style.color = '';
                            button.style.cursor = 'pointer';
                            button.innerHTML = documentType.toUpperCase();
                            button.title = `Upload ${documentType.toUpperCase()}`;
                            button.setAttribute('data-file-deleted', 'true');
                            button.setAttribute('data-last-updated', Date.now().toString());
                            
                            // Re-enable onclick functionality
                            if (documentType === 'rfi') {
                                button.onclick = function() { uploadRFI(groupId); };
                            } else if (documentType === 'invoice') {
                                button.onclick = function() { uploadInvoice(groupId); };
                            }
                            debugLog(`SUCCESS ${documentType.toUpperCase()} button directly reset to gray state`);
                        } else {
                            debugLog(`⚠️ Button not found for direct reset: ${buttonId}`);
                        }
                    }
                }
                
                // Clear any cached file data for this client/date
                debugLog('🧹 Clearing file cache for updated state...');
                
                // Refresh the files list to show updated state
                if (groupId && clientName && inspectionDate) {
                    debugLog('INFO Refreshing View Files popup to show updated file count');
                    setTimeout(() => {
                        openFilesPopup(groupId, clientName, inspectionDate);
                    }, 100);
                }
            } else {
                alert('Error deleting file: ' + (result.error || 'Unknown error'));
                console.error('Delete failed:', result);
            }
        }
        
    } catch (error) {
        console.error('Delete error:', error);
        alert('Network error while deleting file: ' + error.message);
    }
}

// View file function
function viewFile(filePath, fileName) {
    debugLog('Viewing file:', filePath, fileName);
    
    if (filePath.startsWith('/test/')) {
        alert('This is a test file. In a real system, this would open a document viewer or download the file for viewing.');
        return;
    }
    
    // Clean the file path - remove /media/ prefix if present
    let cleanFilePath = filePath;
    if (cleanFilePath.startsWith('/media/')) {
        cleanFilePath = cleanFilePath.substring(7); // Remove '/media/'
    }
    
    debugLog('View - Original path:', filePath);
    debugLog('View - Clean path:', cleanFilePath);
    
    // For viewing, use the media URL directly (not the download endpoint)
    // This bypasses the Content-Disposition: attachment header
    const viewUrl = '/media/' + cleanFilePath;
    
    debugLog('Opening for viewing:', viewUrl);
    
    // Open file in new tab for inline viewing
    window.open(viewUrl, '_blank');
}

// Expand/Collapse functionality
function expandAll() {
    debugLog('expandAll called');
    const detailRows = document.querySelectorAll('.detail-row');
    const expandBtns = document.querySelectorAll('.expand-btn');
    
    detailRows.forEach(row => {
        row.style.display = 'table-row';
    });
    
    expandBtns.forEach(btn => {
        btn.classList.add('expanded');
        const icon = btn.querySelector('i');
        if (icon) {
            icon.classList.remove('fa-chevron-right');
            icon.classList.add('fa-chevron-down');
        }
    });
    
    debugLog('Expanded', detailRows.length, 'detail rows');
}

function collapseAll() {
    debugLog('collapseAll called');
    const detailRows = document.querySelectorAll('.detail-row');
    const expandBtns = document.querySelectorAll('.expand-btn');
    
    detailRows.forEach(row => {
        row.style.display = 'none';
    });
    
    expandBtns.forEach(btn => {
        btn.classList.remove('expanded');
        const icon = btn.querySelector('i');
        if (icon) {
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-right');
        }
    });
    
    debugLog('Collapsed', detailRows.length, 'detail rows');
}

// Toggle individual group function
function toggleGroup(e, groupId) {
    debugLog('toggleGroup called for groupId:', groupId);
    
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    const detailRow = document.getElementById('detail-' + groupId);
    debugLog('Detail row found:', detailRow);

    if (!detailRow) {
        debugWarn('No detail row for groupId:', groupId);
        return;
    }

    // Find the expand button safely
    let expandBtn = null;
    if (e && e.target) {
        expandBtn = e.target.closest('.expand-btn');
    }
    if (!expandBtn) {
        const groupRow = document.querySelector('tr.group-row[data-group-id="' + groupId + '"]');
        if (groupRow) {
            expandBtn = groupRow.querySelector('.expand-btn');
        }
    }

    const icon = expandBtn ? expandBtn.querySelector('i') : null;

    const isHidden = detailRow.style.display === 'none' || detailRow.style.display === '';
    if (isHidden) {
        // Expand
        detailRow.style.display = 'table-row';
        if (expandBtn) expandBtn.classList.add('expanded');
        if (icon) {
            icon.classList.remove('fa-chevron-right');
            icon.classList.add('fa-chevron-down');
        }
        debugLog('Expanded group:', groupId);
    } else {
        // Collapse
        detailRow.style.display = 'none';
        if (expandBtn) expandBtn.classList.remove('expanded');
        if (icon) {
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-right');
        }
        debugLog('Collapsed group:', groupId);
    }
}

// Set up event delegation for expand buttons when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    debugLog('Setting up expand button event delegation...');
    
    // Debug: Check what elements exist
    const expandBtns = document.querySelectorAll('.expand-btn');
    const detailRows = document.querySelectorAll('.detail-row');
    debugLog('Found expand buttons:', expandBtns.length);
    debugLog('Found detail rows:', detailRows.length);
    
    // List all expand buttons and their group IDs
    expandBtns.forEach((btn, index) => {
        const groupId = btn.getAttribute('data-group-id');
        debugLog(`Expand button ${index + 1}: group-id="${groupId}"`);
    });
    
    // List all detail rows and their IDs
    detailRows.forEach((row, index) => {
        debugLog(`Detail row ${index + 1}: id="${row.id}"`);
    });
    
    // Event delegation for expand buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.expand-btn')) {
            e.preventDefault();
            e.stopPropagation();
            const button = e.target.closest('.expand-btn');
            const groupId = button.getAttribute('data-group-id');
            debugLog('🔧 Expand button clicked for group:', groupId);
            toggleGroup(e, groupId);
        }
    });
    
    // Close modal when clicking outside
    window.onclick = function(event) {
        const modal = document.getElementById('filesModal');
        if (modal && event.target === modal) {
            closeFilesPopup();
        }
    };
    
    debugLog('Event delegation set up for expand buttons and modal');
    
    // Start automatic color updates for View Files buttons - PAGE SPECIFIC
    debugLog('COLOR [PAGE] Starting compliance document check for current page only...');
    
    // Check immediately for current page
    setTimeout(() => {
        debugLog('COLOR [PAGE] Initial compliance check for visible rows...');
        updateAllViewFilesButtonColors();
    }, 1000);
    
    // Final check after everything loads
    setTimeout(() => {
        debugLog('INFO [PAGE] Final compliance check for visible rows...');
        updateAllViewFilesButtonColors();
    }, 2000);
    
    // Validate upload button states against actual files
    // DISABLED: This was overriding template logic and causing incorrect button states
    // The template correctly shows uploader names based on database state
    /*
    setTimeout(() => {
        debugLog('DEBUG [PAGE] Validating upload button states...');
        validateUploadButtonStates();
    }, 3000);
    */
    
    // Set up pagination detection for automatic color updates on page changes
    const paginationLinks = document.querySelectorAll('.pagination a, a[href*="page="]');
    debugLog('🔗 [PAGE] Found ' + paginationLinks.length + ' pagination links');
    
    paginationLinks.forEach(link => {
        link.addEventListener('click', function() {
            debugLog('🔗 [PAGE] Pagination clicked, will check new page after load...');
            
            // Check for new page content after navigation
            setTimeout(() => {
                debugLog('COLOR [PAGE] Checking compliance for new page after navigation...');
                updateAllViewFilesButtonColors();
            }, 1500);
        });
    });
    
    // Initialize upload button states for lab, lab form, and retest buttons
    setTimeout(() => {
        debugLog('DEBUG [PAGE] Initializing upload button states...');
        initializeUploadButtonStates();
    }, 3000);
    
    // SIMPLE RFI BUTTON INITIALIZATION - Run immediately
    setTimeout(() => {
        debugLog('DEBUG [PAGE] Initializing RFI buttons immediately...');
        initializeRFIButtonsSimple();
    }, 1000);
    
    // SIMPLE INVOICE BUTTON INITIALIZATION - Run immediately
    setTimeout(() => {
        debugLog('DEBUG [PAGE] Initializing Invoice buttons immediately...');
        initializeInvoiceButtonsSimple();
    }, 1200);
});

// Cookie utility function
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Update Product Name function
function updateProductName(input) {
    debugLog('updateProductName called');
    const inspectionId = input.getAttribute('data-inspection-id');
    const value = input.value;
    const formData = new FormData();
    formData.append('inspection_id', inspectionId);
    formData.append('product_name', value);
    
    fetch('/update-product-name/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken') || getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    }).then(r => r.json()).then(data => {
        if (data.success) {
            input.style.backgroundColor = '#d4edda';
            setTimeout(() => { input.style.backgroundColor = ''; }, 500);
        } else {
            alert('Error updating product name: ' + (data.error || 'Unknown error'));
        }
    }).catch(err => {
        console.error('Error updating product name:', err);
        alert('Error updating product name: ' + (err?.message || err));
    });
}

// Update Product Class function
function updateProductClass(dropdown) {
    debugLog('updateProductClass called');
    const inspectionId = dropdown.getAttribute('data-inspection-id');
    const value = dropdown.value;
    const formData = new FormData();
    formData.append('inspection_id', inspectionId);
    formData.append('product_class', value);
    
    fetch('/update-product-class/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken') || getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    }).then(r => r.json()).then(data => {
        if (data.success) {
            dropdown.style.backgroundColor = '#d4edda';
            setTimeout(() => { dropdown.style.backgroundColor = ''; }, 500);
        } else {
            alert('Error updating product class: ' + (data.error || 'Unknown error'));
        }
    }).catch(err => {
        console.error('Error updating product class:', err);
        alert('Error updating product class: ' + (err?.message || err));
    });
}

// Update Lab function
function updateLab(dropdown) {
    debugLog('updateLab called');
    const inspectionId = dropdown.getAttribute('data-inspection-id');
    const labValue = dropdown.value;
    
    // Create form data
    const formData = new FormData();
    formData.append('inspection_id', inspectionId);
    formData.append('lab', labValue);

    // Send update request with CSRF header
    fetch('/update-lab/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken') || getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(async (response) => {
        if (!response.ok) {
            const text = await response.text();
            throw new Error(text || ('HTTP ' + response.status));
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            dropdown.style.backgroundColor = '#d4edda';
            setTimeout(() => { dropdown.style.backgroundColor = ''; }, 500);
        } else {
            alert('Error updating Lab: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error updating Lab:', error);
        alert('Error updating Lab: ' + (error?.message || error));
    });
}

// Test function to simulate file display (for debugging)
function testFileDisplay() {
    debugLog('🧪 Testing file display with sample data...');
    const sampleFiles = {
        "RFI Documents": [
            { name: "RFI_Canonbury_2025-09-12.pdf", path: "/files/rfi/RFI_Canonbury_2025-09-12.pdf" },
            { name: "RFI_Response_2025-09-12.pdf", path: "/files/rfi/RFI_Response_2025-09-12.pdf" }
        ],
        "Invoices": [
            { name: "Invoice_12345.pdf", path: "/files/invoices/Invoice_12345.pdf" }
        ],
        "Lab Results": [
            { name: "Lab_Report_Canonbury.pdf", path: "/files/lab/Lab_Report_Canonbury.pdf" }
        ]
    };
    
    displayFiles(sampleFiles, "Sample files loaded for testing");
}

// Make test function available globally for console testing
window.testFileDisplay = testFileDisplay;

// Direct test function to bypass JavaScript issues
window.testCanonburyFiles = async function() {
    debugLog('🧪 Testing Canonbury Files directly...');
    
    try {
        const response = await fetch('/list-uploaded-files/?group_id=Canonbury_Eggs_20250912');
        const data = await response.json();
        
        debugLog('📊 Server Response:', data);
        
        if (data.success) {
            const files = data.files;
            debugLog('FOLDER Files object:', files);
            
            for (const [category, fileList] of Object.entries(files)) {
                debugLog(`FOLDER ${category}: ${fileList.length} files`);
                if (fileList.length > 0) {
                    fileList.forEach(file => {
                        debugLog(`  FILES ${file.filename} (${file.size} bytes)`);
                    });
                }
            }
            
            // Test the displayFiles function directly
            debugLog('COLOR Testing displayFiles function...');
            displayFiles(files, 'Direct test - files loaded successfully');
            
        } else {
            console.error('ERROR Server error:', data.error);
        }
    } catch (error) {
        console.error('ERROR Network error:', error);
    }
};

// ZIP File Viewer
async function viewZipContents(filePath, fileName) {
    debugLog('🗂️ Viewing ZIP contents:', filePath, fileName);
    
    try {
        // Show loading message
        const filesList = document.getElementById('filesList');
        if (!filesList) {
            console.error('filesList element not found');
            return;
        }
        
        // Create a temporary loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'zipLoadingOverlay';
        loadingOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;
        loadingOverlay.innerHTML = `
            <div style="background: white; padding: 2rem; border-radius: 8px; text-align: center; max-width: 400px;">
                <div style="margin-bottom: 1rem;">
                    <i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: #007bff;"></i>
                </div>
                <h3 style="margin: 0 0 1rem 0; color: #333;">Loading ZIP Contents</h3>
                <p style="margin: 0; color: #666;">Reading ${fileName}...</p>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
        
        // Clean the file path
        let cleanFilePath = filePath;
        if (cleanFilePath.startsWith('/media/')) {
            cleanFilePath = cleanFilePath.substring(7);
        }
        
        // Fetch the ZIP file
        const response = await fetch('/media/' + cleanFilePath);
        if (!response.ok) {
            throw new Error(`Failed to fetch ZIP file: ${response.status} ${response.statusText}`);
        }
        
        const arrayBuffer = await response.arrayBuffer();
        
        // Load JSZip library dynamically if not already loaded
        if (typeof JSZip === 'undefined') {
            await loadJSZipLibrary();
        }
        
        // Read ZIP contents
        const zip = new JSZip();
        const zipContents = await zip.loadAsync(arrayBuffer);
        
        // Remove loading overlay
        document.body.removeChild(loadingOverlay);
        
        // Display ZIP contents
        displayZipContents(zipContents, fileName);
        
    } catch (error) {
        console.error('Error viewing ZIP contents:', error);
        
        // Remove loading overlay if it exists
        const loadingOverlay = document.getElementById('zipLoadingOverlay');
        if (loadingOverlay) {
            document.body.removeChild(loadingOverlay);
        }
        
        alert('Error loading ZIP file: ' + error.message);
    }
}

// Load JSZip library dynamically
function loadJSZipLibrary() {
    return new Promise((resolve, reject) => {
        if (typeof JSZip !== 'undefined') {
            resolve();
            return;
        }
        
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
        script.onload = () => {
            debugLog('SUCCESS JSZip library loaded successfully');
            resolve();
        };
        script.onerror = () => {
            console.error('ERROR Failed to load JSZip library');
            reject(new Error('Failed to load JSZip library'));
        };
        document.head.appendChild(script);
    });
}

// Display ZIP contents in a modal
function displayZipContents(zipContents, fileName) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.id = 'zipViewerModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
    `;
    
    // Get file list from ZIP
    const fileList = Object.keys(zipContents.files);
    const folders = new Set();
    const files = [];
    
    fileList.forEach(fileName => {
        const file = zipContents.files[fileName];
        if (file.dir) {
            // It's a directory
            folders.add(fileName);
        } else {
            // It's a file
            files.push({
                name: fileName,
                size: file._data ? file._data.uncompressedSize : 0,
                compressedSize: file._data ? file._data.compressedSize : 0,
                date: file.date,
                fileData: file
            });
        }
    });
    
    // Sort files and folders
    const sortedFolders = Array.from(folders).sort();
    const sortedFiles = files.sort((a, b) => a.name.localeCompare(b.name));
    
    // Analyze files for inspection matching
    const analysis = analyzeZipFiles(sortedFiles);
    
    // Create modal content
    modal.innerHTML = `
        <div style="background: white; border-radius: 8px; max-width: 90%; max-height: 90%; overflow: hidden; display: flex; flex-direction: column;">
            <div style="padding: 1rem; border-bottom: 1px solid #dee2e6; display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; color: #333;">
                    <i class="fas fa-file-archive" style="color: #fd7e14; margin-right: 0.5rem;"></i>
                    ${fileName}
                </h3>
                <button onclick="closeZipViewer()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #666;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div style="padding: 1rem; overflow-y: auto; flex: 1;">
                <div style="margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
                    <div style="color: #666; font-size: 0.9rem;">
                        ${sortedFiles.length} files, ${sortedFolders.length} folders
                    </div>
                    <button onclick="extractAndOrganizeZip('${fileName}')" style="background: #28a745; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; font-weight: 500;">
                        <i class="fas fa-folder-open" style="margin-right: 0.5rem;"></i>
                        Extract & Organize
                    </button>
                </div>
                <div id="zipContentsList">
                    ${generateZipContentsHTML(sortedFolders, sortedFiles, analysis)}
                </div>
            </div>
        </div>
    `;
    
    // Store zip contents and analysis for later use
    window.currentZipContents = zipContents;
    window.currentZipAnalysis = analysis;
    window.currentZipFileName = fileName;
    
    document.body.appendChild(modal);
}

// Analyze ZIP files to identify inspection numbers
function analyzeZipFiles(files) {
    const analysis = {
        matchedFiles: [],
        unmatchedFiles: [],
        inspectionNumbers: new Set()
    };
    
    files.forEach(file => {
        // Extract inspection number from filename (look for 4-digit numbers)
        const inspectionMatch = file.name.match(/(\d{4})/);
        if (inspectionMatch) {
            const inspectionNumber = inspectionMatch[1];
            analysis.inspectionNumbers.add(inspectionNumber);
            analysis.matchedFiles.push({
                ...file,
                inspectionNumber: inspectionNumber
            });
        } else {
            analysis.unmatchedFiles.push(file);
        }
    });
    
    return analysis;
}

// Generate HTML for ZIP contents with analysis
function generateZipContentsHTML(folders, files, analysis) {
    let html = '<div class="zip-contents">';
    
    // Show analysis summary
    if (analysis.matchedFiles.length > 0 || analysis.unmatchedFiles.length > 0) {
        html += `
            <div style="background: #e3f2fd; border: 1px solid #2196f3; border-radius: 4px; padding: 1rem; margin-bottom: 1rem;">
                <h4 style="margin: 0 0 0.5rem 0; color: #1976d2;">
                    <i class="fas fa-info-circle" style="margin-right: 0.5rem;"></i>
                    File Organization Analysis
                </h4>
                <div style="font-size: 0.9rem; color: #1976d2;">
                    <div style="margin-bottom: 0.25rem;">
                        <i class="fas fa-check-circle" style="color: #4caf50; margin-right: 0.5rem;"></i>
                        ${analysis.matchedFiles.length} files can be matched to inspections: ${Array.from(analysis.inspectionNumbers).join(', ')}
                    </div>
                    <div>
                        <i class="fas fa-folder" style="color: #ff9800; margin-right: 0.5rem;"></i>
                        ${analysis.unmatchedFiles.length} files will go to general compliance folder
                    </div>
                </div>
            </div>
        `;
    }
    
    // Display folders first
    folders.forEach(folderName => {
        html += `
            <div style="display: flex; align-items: center; padding: 0.5rem; border-bottom: 1px solid #f8f9fa;">
                <i class="fas fa-folder" style="color: #ffc107; margin-right: 0.5rem;"></i>
                <span style="color: #333; font-weight: 500;">${folderName}</span>
            </div>
        `;
    });
    
    // Display matched files (with inspection numbers)
    if (analysis.matchedFiles.length > 0) {
        html += `
            <div style="margin: 1rem 0 0.5rem 0; padding: 0.5rem; background: #f8f9fa; border-radius: 4px;">
                <h5 style="margin: 0; color: #495057; font-size: 0.9rem;">
                    <i class="fas fa-check-circle" style="color: #4caf50; margin-right: 0.5rem;"></i>
                    Files for Individual Inspections
                </h5>
            </div>
        `;
        
        analysis.matchedFiles.forEach(file => {
            const sizeKB = Math.round(file.size / 1024 * 100) / 100;
            const compressionRatio = file.compressedSize > 0 ? Math.round((1 - file.compressedSize / file.size) * 100) : 0;
            
            html += `
                <div style="padding: 0.75rem; border-bottom: 1px solid #f8f9fa; background: #f8fff8;">
                    <div style="display: flex; align-items: center; margin-bottom: 0.25rem;">
                        <i class="fas fa-file" style="color: #4caf50; margin-right: 0.5rem;"></i>
                        <span style="color: #333; font-weight: 500;">${file.name}</span>
                        <span style="background: #4caf50; color: white; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.8rem; margin-left: 0.5rem;">
                            Inspection ${file.inspectionNumber}
                        </span>
                    </div>
                    <div style="color: #666; font-size: 0.9rem; margin-left: 1.5rem;">
                        ${sizeKB} KB ${compressionRatio > 0 ? `(${compressionRatio}% compressed)` : ''}
                    </div>
                </div>
            `;
        });
    }
    
    // Display unmatched files (for general compliance folder)
    if (analysis.unmatchedFiles.length > 0) {
        html += `
            <div style="margin: 1rem 0 0.5rem 0; padding: 0.5rem; background: #f8f9fa; border-radius: 4px;">
                <h5 style="margin: 0; color: #495057; font-size: 0.9rem;">
                    <i class="fas fa-folder" style="color: #ff9800; margin-right: 0.5rem;"></i>
                    Files for General Compliance Folder
                </h5>
            </div>
        `;
        
        analysis.unmatchedFiles.forEach(file => {
            const sizeKB = Math.round(file.size / 1024 * 100) / 100;
            const compressionRatio = file.compressedSize > 0 ? Math.round((1 - file.compressedSize / file.size) * 100) : 0;
            
            html += `
                <div style="padding: 0.75rem; border-bottom: 1px solid #f8f9fa; background: #fff8f0;">
                    <div style="display: flex; align-items: center; margin-bottom: 0.25rem;">
                        <i class="fas fa-file" style="color: #ff9800; margin-right: 0.5rem;"></i>
                        <span style="color: #333; font-weight: 500;">${file.name}</span>
                    </div>
                    <div style="color: #666; font-size: 0.9rem; margin-left: 1.5rem;">
                        ${sizeKB} KB ${compressionRatio > 0 ? `(${compressionRatio}% compressed)` : ''}
                    </div>
                </div>
            `;
        });
    }
    
    html += '</div>';
    return html;
}

// Extract and organize ZIP files
async function extractAndOrganizeZip(fileName) {
    debugLog('🗂️ Extracting and organizing ZIP:', fileName);
    
    if (!window.currentZipContents || !window.currentZipAnalysis) {
        alert('Error: ZIP contents not available. Please close and reopen the ZIP viewer.');
        return;
    }
    
    try {
        // Show loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'zipExtractOverlay';
        loadingOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10001;
        `;
        loadingOverlay.innerHTML = `
            <div style="background: white; padding: 2rem; border-radius: 8px; text-align: center; max-width: 500px;">
                <div style="margin-bottom: 1rem;">
                    <i class="fas fa-cogs fa-spin" style="font-size: 2rem; color: #007bff;"></i>
                </div>
                <h3 style="margin: 0 0 1rem 0; color: #333;">Extracting & Organizing Files</h3>
                <p style="margin: 0 0 1rem 0; color: #666;">Processing ${window.currentZipAnalysis.matchedFiles.length} matched files and ${window.currentZipAnalysis.unmatchedFiles.length} general files...</p>
                <div id="extractProgress" style="background: #f8f9fa; border-radius: 4px; padding: 0.5rem; font-size: 0.9rem; color: #666;">
                    Starting extraction...
                </div>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
        
        const progressDiv = document.getElementById('extractProgress');
        
        // Get current inspection context
        const groupId = window.currentFilesGroupId;
        const clientName = window.currentFilesClient;
        const inspectionDate = window.currentFilesDate;
        
        if (!groupId || !clientName || !inspectionDate) {
            throw new Error('Missing inspection context. Please close and reopen the files popup.');
        }
        
        // Process matched files (for individual inspections)
        let processedCount = 0;
        const totalFiles = window.currentZipAnalysis.matchedFiles.length + window.currentZipAnalysis.unmatchedFiles.length;
        
        for (const file of window.currentZipAnalysis.matchedFiles) {
            progressDiv.textContent = `Processing ${file.name} for inspection ${file.inspectionNumber}...`;
            
            // Extract file data
            const fileData = await file.fileData.async('blob');
            
            // Upload to specific inspection folder
            await uploadFileToInspection(fileData, file.name, file.inspectionNumber, groupId, clientName, inspectionDate);
            
            processedCount++;
            progressDiv.textContent = `Processed ${processedCount}/${totalFiles} files...`;
        }
        
        // Process unmatched files (for general compliance folder)
        for (const file of window.currentZipAnalysis.unmatchedFiles) {
            progressDiv.textContent = `Processing ${file.name} for general compliance folder...`;
            
            // Extract file data
            const fileData = await file.fileData.async('blob');
            
            // Upload to general compliance folder
            await uploadFileToGeneralCompliance(fileData, file.name, groupId, clientName, inspectionDate);
            
            processedCount++;
            progressDiv.textContent = `Processed ${processedCount}/${totalFiles} files...`;
        }
        
        // Remove loading overlay
        document.body.removeChild(loadingOverlay);
        
        // Close ZIP viewer
        closeZipViewer();
        
        // Show success message
        alert(`SUCCESS Successfully extracted and organized ${totalFiles} files!\n\n- ${window.currentZipAnalysis.matchedFiles.length} files placed in individual inspection folders\n- ${window.currentZipAnalysis.unmatchedFiles.length} files placed in general compliance folder`);
        
        // Refresh the files popup to show new files
        setTimeout(() => {
            if (window.currentFilesGroupId && window.currentFilesClient && window.currentFilesDate) {
                openFilesPopup(window.currentFilesGroupId, window.currentFilesClient, window.currentFilesDate);
            }
        }, 1000);
        
    } catch (error) {
        console.error('Error extracting ZIP:', error);
        
        // Remove loading overlay if it exists
        const loadingOverlay = document.getElementById('zipExtractOverlay');
        if (loadingOverlay) {
            document.body.removeChild(loadingOverlay);
        }
        
        alert('Error extracting ZIP file: ' + error.message);
    }
}

// Upload file to specific inspection folder
async function uploadFileToInspection(fileData, fileName, inspectionNumber, groupId, clientName, inspectionDate) {
    const formData = new FormData();
    formData.append('file', fileData, fileName);
    formData.append('group_id', groupId);
    formData.append('client_name', clientName);
    formData.append('inspection_date', inspectionDate);
    formData.append('inspection_number', inspectionNumber);
    formData.append('document_type', 'compliance');
    formData.append('csrfmiddlewaretoken', getCSRFToken());
    
    const response = await fetch('/upload-document/', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error(`Failed to upload ${fileName} to inspection ${inspectionNumber}: ${response.statusText}`);
    }
    
    const result = await response.json();
    if (!result.success) {
        throw new Error(`Failed to upload ${fileName}: ${result.error}`);
    }
    
    debugLog(`SUCCESS Uploaded ${fileName} to inspection ${inspectionNumber}`);
}

// Upload file to general compliance folder
async function uploadFileToGeneralCompliance(fileData, fileName, groupId, clientName, inspectionDate) {
    const formData = new FormData();
    formData.append('file', fileData, fileName);
    formData.append('group_id', groupId);
    formData.append('client_name', clientName);
    formData.append('inspection_date', inspectionDate);
    formData.append('document_type', 'compliance');
    formData.append('csrfmiddlewaretoken', getCSRFToken());
    
    const response = await fetch('/upload-document/', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error(`Failed to upload ${fileName} to general compliance: ${response.statusText}`);
    }
    
    const result = await response.json();
    if (!result.success) {
        throw new Error(`Failed to upload ${fileName}: ${result.error}`);
    }
    
    debugLog(`SUCCESS Uploaded ${fileName} to general compliance folder`);
}

// Close ZIP viewer modal
function closeZipViewer() {
    const modal = document.getElementById('zipViewerModal');
    if (modal) {
        document.body.removeChild(modal);
    }
    
    // Clear stored data
    window.currentZipContents = null;
    window.currentZipAnalysis = null;
    window.currentZipFileName = null;
}

// View Files Button Color Management
function updateViewFilesButtonColor(clientName, fileStatus) {
    debugLog('COLOR Updating button color for client: "' + clientName + '"');
    debugLog('   File status: ' + fileStatus);
    
    // Find all View Files buttons for this client using multiple methods
    let buttons = [];
    
    // Method 1: Look for buttons with client name in onclick attribute
    const buttonsByOnclick = document.querySelectorAll('button[onclick*="' + clientName + '"]');
    buttonsByOnclick.forEach(btn => {
        if (btn.textContent.includes('View Files') || btn.textContent.includes('Files')) {
            buttons.push(btn);
        }
    });
    
    // Method 2: Look for buttons with client name in data attributes
    const buttonsByData = document.querySelectorAll('button[data-client-name="' + clientName + '"]');
    buttonsByData.forEach(btn => {
        if (btn.textContent.includes('View Files') || btn.textContent.includes('Files')) {
            buttons.push(btn);
        }
    });
    
    // Method 3: Look in table rows with matching client name
    const rows = document.querySelectorAll('tr[data-client-name="' + clientName + '"]');
    rows.forEach(row => {
        const filesButton = row.querySelector('.btn-view-files, button[class*="view-files"]');
        if (filesButton) {
            buttons.push(filesButton);
        }
    });
    
    // Remove duplicates
    buttons = [...new Set(buttons)];
    
    debugLog('   Found ' + buttons.length + ' View Files buttons for "' + clientName + '"');
    
    buttons.forEach((button, index) => {
        if (button.textContent.includes('View Files') || button.textContent.includes('Files')) {
            debugLog('   Button ' + (index + 1) + ': "' + button.textContent.trim() + '"');
            
            // Skip if this button was recently updated by file deletion
            if (button.getAttribute('data-file-deleted') === 'true') {
                const lastUpdated = parseInt(button.getAttribute('data-last-updated') || '0');
                const timeSinceUpdate = Date.now() - lastUpdated;
                if (timeSinceUpdate < 5000) { // Skip for 5 seconds after deletion
                    debugLog('   ⏭️ Skipping button update - recently updated by file deletion');
                    return;
                }
            }
            
            // Remove existing color classes including the problematic btn-files-none
            button.classList.remove('btn-view-files-green', 'btn-view-files-red', 'btn-view-files-blue', 'btn-view-files-orange', 'btn-files-none', 'btn-files-partial', 'btn-files-checking');
            
            // Find the status icon
            const statusIcon = button.querySelector('i[class*="fa-"]');
            
            // Add appropriate color class and icon based on status
            switch(fileStatus) {
                case 'all_files':
                    button.classList.add('btn-view-files-green');
                    button.title = 'All files available (RFI, Invoice, Lab Results, Compliance)';
                    if (statusIcon) {
                        statusIcon.className = 'fas fa-check-circle';
                        statusIcon.style.color = '#059669';
                    }
                    debugLog('   SUCCESS Applied GREEN color to button');
                    break;
                case 'compliance_only':
                    button.classList.add('btn-view-files-orange');
                    button.title = 'Only compliance documents available';
                    if (statusIcon) {
                        statusIcon.className = 'fas fa-shield-alt';
                        statusIcon.style.color = '#f59e0b';
                    }
                    debugLog('   🟡 Applied ORANGE color to button');
                    break;
                case 'partial_files':
                    button.classList.add('btn-warning');
                    button.style.backgroundColor = '#ff8c00';
                    button.style.color = 'white';
                    button.title = 'Files uploaded';
                    if (statusIcon) {
                        statusIcon.className = 'fas fa-file-alt';
                        statusIcon.style.color = 'white';
                    }
                    debugLog('   🟠 Applied ORANGE color to button (files detected)');
                    break;
                case 'no_files':
                    button.classList.add('btn-view-files-red');
                    button.title = 'No files found';
                    if (statusIcon) {
                        statusIcon.className = 'fas fa-times-circle';
                        statusIcon.style.color = '#dc2626';
                    }
                    debugLog('   🔴 Applied RED color to button');
                    break;
                default:
                    // Default blue color for unknown status
                    button.classList.add('btn-view-files-blue');
                    button.title = 'Click to check files';
                    if (statusIcon) {
                        statusIcon.className = 'fas fa-sync fa-spin';
                        statusIcon.style.color = '#6b7280';
                    }
                    debugLog('   INFO Applied default color to button');
                    break;
            }
        }
    });
}

// Update View Files button color for a specific client and inspection date
function updateViewFilesButtonColorSpecific(clientName, inspectionDate, fileStatus) {
    debugLog('COLOR Updating button color for specific client+date: "' + clientName + '" on ' + inspectionDate);
    debugLog('   File status: ' + fileStatus);
    
    // Find buttons for this specific client and date combination
    let buttons = [];
    
    // Look for buttons in rows that match both client name and inspection date
    const rows = document.querySelectorAll('tr[data-client-name="' + clientName + '"][data-inspection-date="' + inspectionDate + '"]');
    rows.forEach(row => {
        const filesButton = row.querySelector('.btn-view-files, button[class*="view-files"], button[onclick*="openFilesPopup"]');
        if (filesButton && (filesButton.textContent.includes('View Files') || filesButton.textContent.includes('Files'))) {
            buttons.push(filesButton);
        }
    });
    
    // Also try to find buttons by group ID pattern
    const groupId = clientName.replace(/[^a-zA-Z0-9]/g, '_') + '_' + inspectionDate.replace(/-/g, '');
    const groupButtons = document.querySelectorAll('button[onclick*="' + groupId + '"]');
    groupButtons.forEach(btn => {
        if (btn.textContent.includes('View Files') || btn.textContent.includes('Files')) {
            buttons.push(btn);
        }
    });
    
    // Remove duplicates
    buttons = [...new Set(buttons)];
    
    debugLog('   Found ' + buttons.length + ' View Files buttons for "' + clientName + '" on ' + inspectionDate);
    
    buttons.forEach((button, index) => {
        if (button.textContent.includes('View Files') || button.textContent.includes('Files')) {
            debugLog('   Button ' + (index + 1) + ': "' + button.textContent.trim() + '"');
            debugLog('   Button ' + (index + 1) + ' current classes:', button.className);
            debugLog('   Button ' + (index + 1) + ' current styles:', {
                backgroundColor: button.style.backgroundColor,
                color: button.style.color,
                borderColor: button.style.borderColor
            });
            
            // Skip if this button was recently updated by file deletion
            if (button.getAttribute('data-file-deleted') === 'true') {
                const lastUpdated = parseInt(button.getAttribute('data-last-updated') || '0');
                const timeSinceUpdate = Date.now() - lastUpdated;
                if (timeSinceUpdate < 5000) { // Skip for 5 seconds after deletion
                    debugLog('   ⏭️ Skipping button update - recently updated by file deletion');
                    return;
                }
            }
            
            // Remove existing color classes including the problematic btn-files-none
            button.classList.remove('btn-success', 'btn-warning', 'btn-info', 'btn-danger', 'btn-files-none', 'btn-files-partial', 'btn-files-checking');
            
            // Apply color based on file status
            switch (fileStatus) {
                case 'all_files':
                    button.classList.add('btn-success', 'success');
                    button.style.backgroundColor = '#28a745';
                    button.style.color = 'white';
                    button.title = 'All files available (RFI, Invoice, Lab, Compliance)';
                    debugLog('   🟢 Applied GREEN color to button');
                    debugLog('   🟢 Button after update - classes:', button.className);
                    debugLog('   🟢 Button after update - styles:', {
                        backgroundColor: button.style.backgroundColor,
                        color: button.style.color,
                        borderColor: button.style.borderColor
                    });
                    break;
                case 'compliance_only':
                    button.classList.add('btn-warning');
                    button.style.backgroundColor = '#ffc107';
                    button.style.color = 'black';
                    button.title = 'Only compliance documents available';
                    debugLog('   🟠 Applied ORANGE color to button');
                    debugLog('   🟠 Button after update - classes:', button.className);
                    debugLog('   🟠 Button after update - styles:', {
                        backgroundColor: button.style.backgroundColor,
                        color: button.style.color,
                        borderColor: button.style.borderColor
                    });
                    break;
                case 'partial_files':
                    // ANY file detected - make View Files button ORANGE
                    button.classList.add('btn-warning');
                    button.style.backgroundColor = '#ff8c00';
                    button.style.color = 'white';
                    button.title = 'Files uploaded';
                    debugLog('   ORANGE Applied ORANGE color to button (files detected)');
                    debugLog('   Button after update - classes:', button.className);
                    debugLog('   Button after update - styles:', {
                        backgroundColor: button.style.backgroundColor,
                        color: button.style.color,
                        borderColor: button.style.borderColor
                    });
                    break;
                case 'no_files':
                    button.classList.add('btn-danger');
                    button.style.backgroundColor = '#dc3545';
                    button.style.color = 'white';
                    button.title = 'No files available';
                    debugLog('   🔴 Applied RED color to button');
                    debugLog('   🔴 Button after update - classes:', button.className);
                    debugLog('   🔴 Button after update - styles:', {
                        backgroundColor: button.style.backgroundColor,
                        color: button.style.color,
                        borderColor: button.style.borderColor
                    });
                    
                    // When View Files button goes red (no files), reset RFI and Invoice buttons to grey
                    debugLog('   INFO View Files is red - resetting RFI and Invoice buttons to grey...');
                    resetRFIAndInvoiceButtonsToGrey(clientName, inspectionDate);
                    break;
                default:
                    button.style.backgroundColor = '#6c757d';
                    button.style.color = 'white';
                    button.title = 'Unknown file status';
                    debugLog('   INFO Applied default color to button');
                    break;
            }
        }
    });
}

// Check file status for all clients and update button colors
let statusCheckInProgress = false;

// Global variable to track if we're in the middle of an upload process
let uploadInProgress = false;

// Function to update RFI button color with delayed check
function updateRFIButtonColorDelayed(groupId) {
    debugLog('INFO [DELAYED] Updating RFI button color for group:', groupId);
    
    // Extract client name and date from groupId
    const parts = groupId.split('_');
    if (parts.length < 3) {
        debugWarn('Invalid groupId format for RFI button update:', groupId);
        return;
    }
    
    // Reconstruct client name (handle cases with underscores in client name)
    // For groupId like "Jusmar_Farm_Eggs_Pty_Ltd_20250918", we need to be more careful
    const datePart = parts[parts.length - 1];
    const inspectionDate = datePart.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
    
    // Reconstruct client name by joining all parts except the last one (date)
    // and then replacing underscores with spaces, but being careful about special characters
    let clientName = parts.slice(0, -1).join('_');
    
    // Handle special cases for common patterns
    if (clientName.includes('Pty_Ltd')) {
        clientName = clientName.replace(/_/g, ' ').replace(/Pty Ltd/g, '(Pty) Ltd.');
    } else {
        clientName = clientName.replace(/_/g, ' ');
    }
    
    debugLog('DEBUG [DELAYED] Extracted client name:', clientName);
    debugLog('DEBUG [DELAYED] Extracted inspection date:', inspectionDate);
    
    // Check if RFI files exist for this client+date combination
    fetch('/inspections/files/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            client_name: clientName,
            inspection_date: inspectionDate,
            _force_refresh: true
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.files) {
            const hasRFI = data.files.rfi && data.files.rfi.length > 0;
            debugLog('DEBUG [DELAYED] RFI file check result:', hasRFI);
            
            const buttonId = 'rfi-' + groupId;
            const button = document.getElementById(buttonId);
            
            if (button) {
                if (hasRFI) {
                    // Update to green success state
                    button.disabled = true;
                    button.className = 'btn btn-sm btn-success success';
                    button.style.backgroundColor = '#28a745';
                    button.style.borderColor = '#28a745';
                    button.style.cursor = 'not-allowed';
                    button.innerHTML = 'RFI ✓';
                    button.title = 'RFI file exists';
                    button.onclick = null;
                    debugLog('SUCCESS [DELAYED] Updated RFI button to green success state');
                } else {
                    // Update to grey state (no file)
                    button.disabled = false;
                    button.className = 'btn btn-sm btn-secondary';
                    button.style.backgroundColor = '#6c757d';
                    button.style.borderColor = '#6c757d';
                    button.style.cursor = 'pointer';
                    button.innerHTML = 'RFI';
                    button.title = 'Upload RFI file';
                    button.onclick = () => uploadRFI(groupId);
                    debugLog('GREY [DELAYED] Updated RFI button to grey state (no file)');
                }
            } else {
                debugWarn('RFI button not found for delayed update:', buttonId);
            }
        } else {
            debugWarn('Failed to get file status for RFI button update:', data.error);
        }
    })
    .catch(error => {
        console.error('Error checking RFI file status for delayed update:', error);
    });
}

// Function to reset RFI and Invoice buttons to grey when View Files button goes red
function resetRFIAndInvoiceButtonsToGrey(clientName, inspectionDate) {
    debugLog('INFO [RESET] Resetting RFI and Invoice buttons to grey for:', clientName, 'on', inspectionDate);
    
    // Find the row for this client and date
    const rows = document.querySelectorAll('tr[data-client-name="' + clientName + '"][data-inspection-date="' + inspectionDate + '"]');
    
    rows.forEach(row => {
        // Find RFI button
        const rfiButton = row.querySelector('button[id*="rfi-"]');
        if (rfiButton) {
            // Check if RFI button was recently reset due to file deletion
            const rfiButtonRecentlyDeleted = rfiButton.getAttribute('data-file-deleted') === 'true';
            const rfiButtonLastUpdated = parseInt(rfiButton.getAttribute('data-last-updated') || '0');
            const rfiButtonTimeSinceUpdate = Date.now() - rfiButtonLastUpdated;
            const rfiButtonRecentlyReset = rfiButtonRecentlyDeleted && rfiButtonTimeSinceUpdate < 10000; // 10 seconds
            
            if (rfiButtonRecentlyReset) {
                debugLog('⏭️ [RESET] Skipping RFI button reset - recently updated by file deletion');
            } else {
                debugLog('INFO [RESET] Found RFI button, resetting to grey...');
                rfiButton.disabled = false;
                rfiButton.className = 'btn btn-sm btn-secondary';
                rfiButton.style.backgroundColor = '#6c757d';
                rfiButton.style.borderColor = '#6c757d';
                rfiButton.style.color = 'white';
                rfiButton.style.cursor = 'pointer';
                rfiButton.innerHTML = 'RFI';
                rfiButton.title = 'Upload RFI file';
                
                // Restore the onclick function
                const groupId = rfiButton.id.replace('rfi-', '');
                rfiButton.onclick = () => uploadRFI(groupId);
                
                debugLog('SUCCESS [RESET] RFI button reset to grey');
            }
        } else {
            debugLog('⚠️ [RESET] RFI button not found');
        }
        
        // Find Invoice button
        const invoiceButton = row.querySelector('button[id*="invoice-"]');
        if (invoiceButton) {
            // Check if Invoice button was recently reset due to file deletion
            const invoiceButtonRecentlyDeleted = invoiceButton.getAttribute('data-file-deleted') === 'true';
            const invoiceButtonLastUpdated = parseInt(invoiceButton.getAttribute('data-last-updated') || '0');
            const invoiceButtonTimeSinceUpdate = Date.now() - invoiceButtonLastUpdated;
            const invoiceButtonRecentlyReset = invoiceButtonRecentlyDeleted && invoiceButtonTimeSinceUpdate < 10000; // 10 seconds
            
            if (invoiceButtonRecentlyReset) {
                debugLog('⏭️ [RESET] Skipping Invoice button reset - recently updated by file deletion');
            } else {
                debugLog('INFO [RESET] Found Invoice button, resetting to grey...');
                invoiceButton.disabled = false;
                invoiceButton.className = 'btn btn-sm btn-secondary';
                invoiceButton.style.backgroundColor = '#6c757d';
                invoiceButton.style.borderColor = '#6c757d';
                invoiceButton.style.color = 'white';
                invoiceButton.style.cursor = 'pointer';
                invoiceButton.innerHTML = 'Invoice';
                invoiceButton.title = 'Upload Invoice file';
                
                // Restore the onclick function
                const groupId = invoiceButton.id.replace('invoice-', '');
                invoiceButton.onclick = () => uploadInvoice(groupId);
                
                debugLog('SUCCESS [RESET] Invoice button reset to grey');
            }
        } else {
            debugLog('⚠️ [RESET] Invoice button not found');
        }
    });
    
    // Also try to find buttons by group ID pattern as fallback
    const groupId = clientName.replace(/[^a-zA-Z0-9]/g, '_') + '_' + inspectionDate.replace(/-/g, '');
    
    // Reset RFI button by group ID
    const rfiButtonById = document.getElementById('rfi-' + groupId);
    if (rfiButtonById) {
        debugLog('INFO [RESET] Found RFI button by ID, resetting to grey...');
        rfiButtonById.disabled = false;
        rfiButtonById.className = 'btn btn-sm btn-secondary';
        rfiButtonById.style.backgroundColor = '#6c757d';
        rfiButtonById.style.borderColor = '#6c757d';
        rfiButtonById.style.color = 'white';
        rfiButtonById.style.cursor = 'pointer';
        rfiButtonById.innerHTML = 'RFI';
        rfiButtonById.title = 'Upload RFI file';
        rfiButtonById.onclick = () => uploadRFI(groupId);
        debugLog('SUCCESS [RESET] RFI button reset to grey (by ID)');
    }
    
    // Reset Invoice button by group ID
    const invoiceButtonById = document.getElementById('invoice-' + groupId);
    if (invoiceButtonById) {
        debugLog('INFO [RESET] Found Invoice button by ID, resetting to grey...');
        invoiceButtonById.disabled = false;
        invoiceButtonById.className = 'btn btn-sm btn-secondary';
        invoiceButtonById.style.backgroundColor = '#6c757d';
        invoiceButtonById.style.borderColor = '#6c757d';
        invoiceButtonById.style.color = 'white';
        invoiceButtonById.style.cursor = 'pointer';
        invoiceButtonById.innerHTML = 'Invoice';
        invoiceButtonById.title = 'Upload Invoice file';
        invoiceButtonById.onclick = () => uploadInvoice(groupId);
        debugLog('SUCCESS [RESET] Invoice button reset to grey (by ID)');
    }
}

// Function to update Invoice button color with delayed check
function updateInvoiceButtonColorDelayed(groupId) {
    debugLog('INFO [DELAYED] Updating Invoice button color for group:', groupId);
    
    // Extract client name and date from groupId
    const parts = groupId.split('_');
    if (parts.length < 3) {
        debugWarn('Invalid groupId format for Invoice button update:', groupId);
        return;
    }
    
    // Reconstruct client name (handle cases with underscores in client name)
    // For groupId like "Jusmar_Farm_Eggs_Pty_Ltd_20250918", we need to be more careful
    const datePart = parts[parts.length - 1];
    const inspectionDate = datePart.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
    
    // Reconstruct client name by joining all parts except the last one (date)
    // and then replacing underscores with spaces, but being careful about special characters
    let clientName = parts.slice(0, -1).join('_');
    
    // Handle special cases for common patterns
    if (clientName.includes('Pty_Ltd')) {
        clientName = clientName.replace(/_/g, ' ').replace(/Pty Ltd/g, '(Pty) Ltd.');
    } else {
        clientName = clientName.replace(/_/g, ' ');
    }
    
    debugLog('DEBUG [DELAYED] Extracted client name:', clientName);
    debugLog('DEBUG [DELAYED] Extracted inspection date:', inspectionDate);
    
    // Check if Invoice files exist for this client+date combination
    fetch('/inspections/files/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            client_name: clientName,
            inspection_date: inspectionDate,
            _force_refresh: true
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.files) {
            const hasInvoice = data.files.invoice && data.files.invoice.length > 0;
            debugLog('DEBUG [DELAYED] Invoice file check result:', hasInvoice);
            
            const buttonId = 'invoice-' + groupId;
            const button = document.getElementById(buttonId);
            
            if (button) {
                if (hasInvoice) {
                    // Update to green success state
                    button.disabled = true;
                    button.className = 'btn btn-sm btn-success success';
                    button.style.backgroundColor = '#28a745';
                    button.style.borderColor = '#28a745';
                    button.style.cursor = 'not-allowed';
                    button.innerHTML = 'Invoice ✓';
                    button.title = 'Invoice file exists';
                    button.onclick = null;
                    debugLog('SUCCESS [DELAYED] Updated Invoice button to green success state');
                } else {
                    // Update to red error state (file was deleted or not found)
                    button.disabled = false;
                    button.className = 'btn btn-sm btn-danger';
                    button.style.backgroundColor = '#dc3545';
                    button.style.borderColor = '#dc3545';
                    button.style.cursor = 'pointer';
                    button.innerHTML = 'Invoice';
                    button.title = 'Upload Invoice file';
                    button.onclick = () => uploadInvoice(groupId);
                    debugLog('ERROR [DELAYED] Updated Invoice button to red error state');
                }
            } else {
                debugWarn('Invoice button not found for delayed update:', buttonId);
            }
        } else {
            debugWarn('Failed to get file status for Invoice button update:', data.error);
        }
    })
    .catch(error => {
        console.error('Error checking Invoice file status for delayed update:', error);
    });
}

async function updateAllViewFilesButtonColors() {
    debugLog('DEBUG [DEBUG] updateAllViewFilesButtonColors called');
    debugLog('DEBUG [DEBUG] statusCheckInProgress:', statusCheckInProgress);
    debugLog('DEBUG [DEBUG] uploadInProgress:', uploadInProgress);
    
    // Prevent multiple simultaneous requests
    if (statusCheckInProgress) {
        debugLog('⏳ [FRONTEND] Status check already in progress, skipping...');
        return;
    }
    
    // Skip if upload is in progress to prevent overriding upload results
    if (uploadInProgress) {
        debugLog('⏳ [FRONTEND] Upload in progress, skipping status check to prevent override...');
        return;
    }
    
    statusCheckInProgress = true;
    debugLog('COLOR [FRONTEND] Starting automatic View Files button color update...');
    
    try {
        const clientDateCombinations = getCurrentPageClientData();
        
        if (clientDateCombinations.length === 0) {
            debugLog('FILES No client+date combinations found on current page for color update');
            return;
        }
        
        // Limit to reasonable number of combinations
        if (clientDateCombinations.length > 50) {
            debugLog('⚠️ [FRONTEND] Too many combinations on page, limiting to first 50');
            clientDateCombinations.splice(50);
        }
        
        debugLog('INFO [FRONTEND] Checking file status for ' + clientDateCombinations.length + ' client+date combinations...');
        
        // Debug: Check if New Poultry Retailer is in the combinations
        const newPoultryCombinations = clientDateCombinations.filter(c => c.client_name === 'New Poultry Retailer');
        if (newPoultryCombinations.length > 0) {
            debugLog('DEBUG [DEBUG] Found New Poultry Retailer combinations:', newPoultryCombinations);
        } else {
            debugLog('ERROR [DEBUG] New Poultry Retailer NOT found in combinations');
            debugLog('DEBUG [DEBUG] Available client names:', clientDateCombinations.map(c => c.client_name));
        }
        
        // Clear any caches before checking file status
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            await Promise.all(cacheNames.map(name => caches.delete(name)));
        }
        
        const response = await fetch('/page-clients-status/?t=' + Date.now(), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            },
            body: JSON.stringify({
                client_date_combinations: clientDateCombinations
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            debugLog('SUCCESS Received file status data for all client+date combinations');
            debugLog('DEBUG [DEBUG] Full server response for delayed update:', result);
            
            // Debug: Check if New Poultry Retailer is in the response
            const newPoultryStatuses = Object.entries(result.combination_statuses).filter(([key, data]) => data.client_name === 'New Poultry Retailer');
            if (newPoultryStatuses.length > 0) {
                debugLog('DEBUG [DEBUG] Found New Poultry Retailer in response:', newPoultryStatuses);
                newPoultryStatuses.forEach(([key, data]) => {
                    debugLog(`DEBUG [DEBUG] New Poultry Retailer ${key}:`, {
                        client_name: data.client_name,
                        inspection_date: data.inspection_date,
                        file_status: data.file_status,
                        has_rfi: data.has_rfi,
                        has_invoice: data.has_invoice,
                        has_lab: data.has_lab,
                        has_retest: data.has_retest,
                        has_compliance: data.has_compliance
                    });
                });
            }
            
            // Debug: Check Jusmar Farm Eggs specifically
            const jusmarStatuses = Object.entries(result.combination_statuses).filter(([key, data]) => data.client_name === 'Jusmar Farm Eggs (Pty) Ltd.');
            if (jusmarStatuses.length > 0) {
                debugLog('DEBUG [DEBUG] Found Jusmar Farm Eggs in response:', jusmarStatuses);
                jusmarStatuses.forEach(([key, data]) => {
                    debugLog(`DEBUG [DEBUG] Jusmar Farm Eggs ${key}:`, {
                        client_name: data.client_name,
                        inspection_date: data.inspection_date,
                        file_status: data.file_status,
                        has_rfi: data.has_rfi,
                        has_invoice: data.has_invoice,
                        has_lab: data.has_lab,
                        has_retest: data.has_retest,
                        has_compliance: data.has_compliance
                    });
                });
            } else {
                debugLog('DEBUG [DEBUG] Jusmar Farm Eggs NOT found in server response');
            }
            
            if (newPoultryStatuses.length === 0) {
                debugLog('ERROR [DEBUG] New Poultry Retailer NOT found in response');
                debugLog('DEBUG [DEBUG] Available clients in response:', Object.values(result.combination_statuses).map(d => d.client_name));
            }
            
            // Update button colors for each client+date combination
            Object.entries(result.combination_statuses).forEach(([uniqueKey, statusData]) => {
                debugLog('COLOR Updating colors for ' + uniqueKey + ': ' + statusData.file_status);
                updateViewFilesButtonColorSpecific(statusData.client_name, statusData.inspection_date, statusData.file_status);
            });
            
            debugLog('COLOR Completed automatic color update for all buttons');
        } else {
            console.error('ERROR Error getting file status:', result.error);
        }
        
    } catch (error) {
        console.error('ERROR Error updating View Files button colors:', error);
    } finally {
        statusCheckInProgress = false;
    }
}

// Get current page client data for color updates - ONLY VISIBLE ROWS
function getCurrentPageClientData() {
    const clientDateCombinations = [];
    
    // Only get rows that are actually visible on the current page
    const visibleShipmentRows = document.querySelectorAll('tbody .shipment-row[data-client-name]:not([style*="display: none"])');
    
    debugLog('DEBUG [PAGE] Scanning visible rows on current page...');
    debugLog('DEBUG [PAGE] Found ' + visibleShipmentRows.length + ' visible shipment rows');
    
    visibleShipmentRows.forEach((row, index) => {
        const clientName = row.getAttribute('data-client-name');
        const inspectionDate = row.getAttribute('data-inspection-date');
        
        debugLog(`DEBUG [PAGE] Row ${index + 1}: "${clientName}" on ${inspectionDate}`);
        
        if (clientName && inspectionDate) {
            const combination = {
                client_name: clientName,
                inspection_date: inspectionDate,
                unique_key: `${clientName}_${inspectionDate}`
            };
            
            // Only add if we haven't seen this combination before
            if (!clientDateCombinations.find(c => c.unique_key === combination.unique_key)) {
                clientDateCombinations.push(combination);
            }
        }
    });
    
    debugLog('FILES [PAGE] Final result: ' + clientDateCombinations.length + ' unique client+date combinations on current visible page');
    debugLog('FILES [PAGE] Combinations: ' + clientDateCombinations.map(c => c.unique_key).join(', '));
    
    return clientDateCombinations;
}

// Function to check if upload buttons should be enabled/disabled based on actual files
function validateUploadButtonStates() {
    debugLog('DEBUG Validating upload button states against actual files...');
    
    // Get all RFI and Invoice buttons
    const rfiButtons = document.querySelectorAll('button[id^="rfi-"]');
    const invoiceButtons = document.querySelectorAll('button[id^="invoice-"]');
    
    debugLog(`Found ${rfiButtons.length} RFI buttons and ${invoiceButtons.length} Invoice buttons`);
    
    // Check each button's associated files
    rfiButtons.forEach(button => {
        const groupId = button.getAttribute('data-debug-group-id') || button.id.replace('rfi-', '');
        const clientName = button.getAttribute('data-client-name');
        const inspectionDate = button.getAttribute('data-inspection-date');
        
        if (clientName && inspectionDate) {
            // Check if files actually exist for this client/date
            checkButtonFileStatus(button, groupId, clientName, inspectionDate, 'rfi');
        }
    });
    
    invoiceButtons.forEach(button => {
        const groupId = button.getAttribute('data-debug-group-id') || button.id.replace('invoice-', '');
        const clientName = button.getAttribute('data-client-name');
        const inspectionDate = button.getAttribute('data-inspection-date');
        
        if (clientName && inspectionDate) {
            // Check if files actually exist for this client/date
            checkButtonFileStatus(button, groupId, clientName, inspectionDate, 'invoice');
        }
    });
}

// Initialize upload button states based on existing files
async function initializeUploadButtonStates() {
    debugLog('DEBUG Initializing upload button states based on existing files...');
    
    // Get all lab, lab form, retest, and RFI buttons
    const allButtons = document.querySelectorAll('button[id^="lab-"], button[id^="retest-"], button[id^="rfi-"]');
    const labButtons = Array.from(allButtons).filter(btn => btn.id.startsWith('lab-') && !btn.id.startsWith('lab-form-'));
    const labFormButtons = Array.from(document.querySelectorAll('button[id^="lab-form-"]'));
    const retestButtons = Array.from(document.querySelectorAll('button[id^="retest-"]'));
    const rfiButtons = Array.from(document.querySelectorAll('button[id^="rfi-"]'));
    
    debugLog(`DEBUG Found ${labButtons.length} lab buttons, ${labFormButtons.length} lab form buttons, ${retestButtons.length} retest buttons, ${rfiButtons.length} RFI buttons`);
    
    // Process each button type
    await processButtonGroup(labButtons, 'lab');
    await processButtonGroup(labFormButtons, 'lab_form');
    await processButtonGroup(retestButtons, 'retest');
    await processRFIButtons(rfiButtons);
    
    debugLog('SUCCESS Upload button state initialization complete');
}

// Process a group of buttons to check for existing files
async function processButtonGroup(buttons, documentType) {
    // Ensure buttons is an array
    if (!Array.isArray(buttons)) {
        debugWarn(`⚠️ processButtonGroup received non-array for ${documentType}:`, buttons);
        return;
    }
    
        // Process buttons in batches of 2 to avoid overwhelming the server
        const batchSize = 2;
    for (let i = 0; i < buttons.length; i += batchSize) {
        const batch = buttons.slice(i, i + batchSize);
        
        // Process batch in parallel
        await Promise.all(batch.map(async (button) => {
            try {
                const inspectionId = button.id.split('-').pop();
                const groupId = button.getAttribute('data-group-id');
                const clientName = button.getAttribute('data-client-name');
                const inspectionDate = button.getAttribute('data-inspection-date');
                
                if (!inspectionId || !clientName || !inspectionDate) {
                    debugLog(`⚠️ Skipping ${documentType} button ${button.id} - missing required data`);
                    return;
                }
                
                // Check if files exist for this inspection
                debugLog(`DEBUG Checking files for ${documentType} button ${button.id}: ${clientName} on ${inspectionDate} (inspection ID: ${inspectionId})`);
                const hasFiles = await checkFilesExist(clientName, inspectionDate, documentType, inspectionId);
                debugLog(`DEBUG Files exist for ${documentType} button ${button.id}: ${hasFiles}`);
                
                if (hasFiles) {
                    // Update button to green success state
                    // Add the uploaded class and disable the button
                    button.classList.add('uploaded');
                    button.disabled = true;
                    button.title = `${documentType.charAt(0).toUpperCase() + documentType.slice(1)} uploaded`;
                    
                    // Update button text with checkmark
                    const originalText = button.innerHTML;
                    if (!originalText.includes('✓')) {
                        button.innerHTML = originalText.replace(/>([^<]+)</, '>$1 ✓<');
                    }
                    
                    debugLog(`SUCCESS Updated ${documentType} button ${button.id} to success state`);
                }
            } catch (error) {
                console.error(`ERROR Error processing ${documentType} button ${button.id}:`, error);
            }
        }));
        
                // Add a delay between batches to prevent overwhelming the server
                if (i + batchSize < buttons.length) {
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
    }
}

// Check if files exist for a specific document type
async function checkFilesExist(clientName, inspectionDate, documentType, inspectionId = null) {
    try {
                // Create an AbortController for timeout
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
        
        const requestBody = {
            client_name: clientName,
            inspection_date: inspectionDate
        };
        
        // Add inspection ID if provided for more specific file checking
        if (inspectionId) {
            requestBody.inspection_id = inspectionId;
        }
        
        const response = await fetch('/list-client-folder-files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(requestBody),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            console.error(`ERROR Failed to check files for ${documentType}:`, response.status);
            return false;
        }
        
        const data = await response.json();
        
        if (data.success && data.files) {
            const files = data.files[documentType] || [];
            debugLog(`DEBUG Found ${files.length} ${documentType} files for ${clientName} on ${inspectionDate}`);
            return files.length > 0;
        }
        
        debugLog(`DEBUG No files found for ${documentType} - ${clientName} on ${inspectionDate}`);
        return false;
    } catch (error) {
        if (error.name === 'AbortError') {
            debugWarn(`TIMER Timeout checking files for ${documentType} - ${clientName} on ${inspectionDate}`);
        } else {
            console.error(`ERROR Error checking files for ${documentType}:`, error);
        }
        return false;
    }
}

// Process RFI buttons to check for existing files and set colors - SIMPLE VERSION
async function processRFIButtons(rfiButtons) {
    debugLog(`DEBUG Processing ${rfiButtons.length} RFI buttons...`);
    
    for (const button of rfiButtons) {
        const buttonId = button.id;
        
        // Skip buttons that were just marked as file-deleted to prevent race condition
        const fileDeleted = button.getAttribute('data-file-deleted');
        const lastUpdated = button.getAttribute('data-last-updated');
        if (fileDeleted === 'true' && lastUpdated) {
            const timeSinceUpdate = Date.now() - parseInt(lastUpdated);
            if (timeSinceUpdate < 5000) { // Skip if updated within last 5 seconds
                debugLog(`SKIP Skipping ${buttonId} - recently marked as file-deleted`);
                continue;
            }
        }
        
        const groupId = buttonId.replace('rfi-', '');
        
        // Extract client name and date from groupId
        const parts = groupId.split('_');
        if (parts.length < 3) {
            debugWarn('Invalid groupId format for RFI button:', groupId);
            continue;
        }
        
        // Reconstruct client name and date
        const datePart = parts[parts.length - 1];
        const inspectionDate = datePart.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
        let clientName = parts.slice(0, -1).join('_');
        
        // Handle special cases for common patterns
        if (clientName.includes('Pty_Ltd')) {
            clientName = clientName.replace(/_/g, ' ').replace(/Pty Ltd/g, '(Pty) Ltd.');
        } else {
            clientName = clientName.replace(/_/g, ' ');
        }
        
        debugLog(`DEBUG Checking RFI files for: ${clientName} on ${inspectionDate}`);
        
        try {
            // Check if RFI files exist
            const response = await fetch('/inspections/files/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    client_name: clientName,
                    inspection_date: inspectionDate,
                    _force_refresh: true
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.files) {
                    const hasRFI = data.files.rfi && data.files.rfi.length > 0;
                    debugLog(`DEBUG RFI file check result for ${clientName}: ${hasRFI}`);
                    
                    if (hasRFI) {
                        // Update to green success state
                        button.disabled = true;
                        button.className = 'btn btn-sm btn-success success';
                        button.style.backgroundColor = '#28a745';
                        button.style.borderColor = '#28a745';
                        button.style.cursor = 'not-allowed';
                        button.innerHTML = 'RFI ✓';
                        button.title = 'RFI file exists';
                        button.onclick = null;
                        debugLog(`SUCCESS Updated RFI button to GREEN for: ${clientName}`);
                    } else {
                        // Update to grey state (no file)
                        button.disabled = false;
                        button.className = 'btn btn-sm btn-secondary';
                        button.style.backgroundColor = '#6c757d';
                        button.style.borderColor = '#6c757d';
                        button.style.cursor = 'pointer';
                        button.innerHTML = 'RFI';
                        button.title = 'Upload RFI file';
                        button.onclick = () => uploadRFI(groupId);
                        debugLog(`GREY Updated RFI button to GREY for: ${clientName}`);
                    }
                }
            } else {
                debugWarn(`⚠️ Failed to check RFI files for ${clientName}: ${response.status}`);
            }
        } catch (error) {
            console.error(`ERROR Error checking RFI files for ${clientName}:`, error);
        }
        
        // Small delay between requests
        await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    debugLog('SUCCESS RFI button processing complete');
}

// IMMEDIATE TARGETED RFI BUTTON CHECK - For specific inspection after file deletion
function immediateRFIButtonCheck(groupId, clientName, inspectionDate) {
    debugLog(`🎯 [IMMEDIATE] Starting targeted RFI check for: ${clientName} on ${inspectionDate}`);
    
    // Add a small delay to ensure server-side file deletion is complete
    setTimeout(() => {
        // Clean the inspection date - decode any Unicode escapes
        let cleanDate = inspectionDate;
        if (typeof inspectionDate === 'string') {
            cleanDate = inspectionDate.replace(/\\u002D/g, '-');
            try {
                cleanDate = JSON.parse('"' + cleanDate + '"');
            } catch (e) {
                // Use as-is if parsing fails
            }
        }
        
        // Make immediate API call to check RFI status for this specific inspection
        fetch('/list-client-folder-files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                client_name: clientName,
                inspection_date: cleanDate,
                inspection_id: groupId
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success && result.files) {
                const hasRFI = result.files.rfi && result.files.rfi.length > 0;
                debugLog(`🎯 [IMMEDIATE] RFI file check result for ${clientName}: ${hasRFI}`);
                
                const buttonId = 'rfi-' + groupId;
                const button = document.getElementById(buttonId);
                
                if (button) {
                    if (hasRFI) {
                        // Update to green success state
                        button.disabled = true;
                        button.className = 'btn btn-sm btn-success success';
                        button.style.backgroundColor = '#28a745';
                        button.style.borderColor = '#28a745';
                        button.style.cursor = 'not-allowed';
                        button.innerHTML = 'RFI ✓';
                        button.title = 'RFI file exists';
                        button.onclick = null;
                        debugLog(`SUCCESS [IMMEDIATE] Updated RFI button to GREEN for: ${clientName}`);
                    } else {
                        // Update to grey state (no file)
                        button.disabled = false;
                        button.className = 'btn btn-sm btn-secondary';
                        button.style.backgroundColor = '#6c757d';
                        button.style.borderColor = '#6c757d';
                        button.style.cursor = 'pointer';
                        button.innerHTML = 'RFI';
                        button.title = 'Upload RFI file';
                        button.onclick = () => uploadRFI(groupId);
                        debugLog(`GREY [IMMEDIATE] Updated RFI button to GREY for: ${clientName}`);
                    }
                    
                    // Remove any file-deleted markers since we've done a fresh check
                    button.removeAttribute('data-file-deleted');
                    button.removeAttribute('data-last-updated');
                } else {
                    debugWarn(`⚠️ [IMMEDIATE] RFI button not found: ${buttonId}`);
                }
            } else {
                debugWarn(`⚠️ [IMMEDIATE] Failed to get file status for ${clientName}: ${result.error}`);
            }
        })
        .catch(error => {
            console.error(`ERROR [IMMEDIATE] Error checking RFI files for ${clientName}:`, error);
        });
    }, 200); // 200ms delay to ensure server-side deletion is complete
}

// IMMEDIATE TARGETED INVOICE BUTTON CHECK - For specific inspection after file deletion
function immediateInvoiceButtonCheck(groupId, clientName, inspectionDate) {
    debugLog(`🎯 [IMMEDIATE] Starting targeted Invoice check for: ${clientName} on ${inspectionDate}`);
    
    // Add a small delay to ensure server-side file deletion is complete
    setTimeout(() => {
        // Clean the inspection date - decode any Unicode escapes
        let cleanDate = inspectionDate;
        if (typeof inspectionDate === 'string') {
            cleanDate = inspectionDate.replace(/\\u002D/g, '-');
            try {
                cleanDate = JSON.parse('"' + cleanDate + '"');
            } catch (e) {
                // Use as-is if parsing fails
            }
        }
        
        // Make immediate API call to check Invoice status for this specific inspection
        fetch('/list-client-folder-files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                client_name: clientName,
                inspection_date: cleanDate,
                inspection_id: groupId
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success && result.files) {
                const hasInvoice = result.files.invoice && result.files.invoice.length > 0;
                debugLog(`🎯 [IMMEDIATE] Invoice file check result for ${clientName}: ${hasInvoice}`);
                
                const buttonId = 'invoice-' + groupId;
                const button = document.getElementById(buttonId);
                
                if (button) {
                    if (hasInvoice) {
                        // Update to green success state
                        button.disabled = true;
                        button.className = 'btn btn-sm btn-success success';
                        button.style.backgroundColor = '#28a745';
                        button.style.borderColor = '#28a745';
                        button.style.cursor = 'not-allowed';
                        button.innerHTML = 'Invoice ✓';
                        button.title = 'Invoice file exists';
                        button.onclick = null;
                        debugLog(`SUCCESS [IMMEDIATE] Updated Invoice button to GREEN for: ${clientName}`);
                    } else {
                        // Update to grey state (no file)
                        button.disabled = false;
                        button.className = 'btn btn-sm btn-secondary';
                        button.style.backgroundColor = '#6c757d';
                        button.style.borderColor = '#6c757d';
                        button.style.cursor = 'pointer';
                        button.innerHTML = 'Invoice';
                        button.title = 'Upload Invoice file';
                        button.onclick = () => uploadInvoice(groupId);
                        debugLog(`GREY [IMMEDIATE] Updated Invoice button to GREY for: ${clientName}`);
                    }
                    
                    // Remove any file-deleted markers since we've done a fresh check
                    button.removeAttribute('data-file-deleted');
                    button.removeAttribute('data-last-updated');
                } else {
                    debugWarn(`⚠️ [IMMEDIATE] Invoice button not found: ${buttonId}`);
                }
            } else {
                debugWarn(`⚠️ [IMMEDIATE] Failed to get file status for ${clientName}: ${result.error}`);
            }
        })
        .catch(error => {
            console.error(`ERROR [IMMEDIATE] Error checking Invoice files for ${clientName}:`, error);
        });
    }, 200); // 200ms delay to ensure server-side deletion is complete
}

// IMMEDIATE TARGETED LAB BUTTON CHECK - For specific inspection after file deletion
function immediateLabButtonCheck(groupId, clientName, inspectionDate) {
    debugLog(`🎯 [IMMEDIATE] Starting targeted Lab check for: ${clientName} on ${inspectionDate}`);
    
    // Add a small delay to ensure server-side file deletion is complete
    setTimeout(() => {
        // Clean the inspection date - decode any Unicode escapes
        let cleanDate = inspectionDate;
        if (typeof inspectionDate === 'string') {
            cleanDate = inspectionDate.replace(/\\u002D/g, '-');
            try {
                cleanDate = JSON.parse('"' + cleanDate + '"');
            } catch (e) {
                // Use as-is if parsing fails
            }
        }
        
        // Make immediate API call to check Lab status for this specific inspection
        fetch('/list-client-folder-files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                client_name: clientName,
                inspection_date: cleanDate,
                inspection_id: groupId
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success && result.files) {
                const hasLab = result.files.lab && result.files.lab.length > 0;
                debugLog(`🎯 [IMMEDIATE] Lab file check result for ${clientName}: ${hasLab}`);
                
                const buttonId = 'lab-' + groupId;
                const button = document.getElementById(buttonId);
                
                if (button) {
                    if (hasLab) {
                        // Update to green success state
                        button.disabled = true;
                        button.className = 'btn btn-sm btn-success success';
                        button.style.backgroundColor = '#28a745';
                        button.style.borderColor = '#28a745';
                        button.style.cursor = 'not-allowed';
                        button.innerHTML = 'Lab ✓';
                        button.title = 'Lab file exists';
                        button.onclick = null;
                        debugLog(`SUCCESS [IMMEDIATE] Updated Lab button to GREEN for: ${clientName}`);
                    } else {
                        // Update to grey state (no file)
                        button.disabled = false;
                        button.className = 'btn btn-sm btn-secondary';
                        button.style.backgroundColor = '#6c757d';
                        button.style.borderColor = '#6c757d';
                        button.style.cursor = 'pointer';
                        button.innerHTML = 'Lab';
                        button.title = 'Upload Lab file';
                        button.onclick = () => uploadLab(groupId);
                        debugLog(`GREY [IMMEDIATE] Updated Lab button to GREY for: ${clientName}`);
                    }
                    
                    // Remove any file-deleted markers since we've done a fresh check
                    button.removeAttribute('data-file-deleted');
                    button.removeAttribute('data-last-updated');
                } else {
                    debugWarn(`⚠️ [IMMEDIATE] Lab button not found: ${buttonId}`);
                }
            } else {
                debugWarn(`⚠️ [IMMEDIATE] Failed to get file status for ${clientName}: ${result.error}`);
            }
        })
        .catch(error => {
            console.error(`ERROR [IMMEDIATE] Error checking Lab files for ${clientName}:`, error);
        });
    }, 200); // 200ms delay to ensure server-side deletion is complete
}

// IMMEDIATE TARGETED RETEST BUTTON CHECK - For specific inspection after file deletion
function immediateRetestButtonCheck(groupId, clientName, inspectionDate) {
    debugLog(`🎯 [IMMEDIATE] Starting targeted Retest check for: ${clientName} on ${inspectionDate}`);
    
    // Add a small delay to ensure server-side file deletion is complete
    setTimeout(() => {
        // Clean the inspection date - decode any Unicode escapes
        let cleanDate = inspectionDate;
        if (typeof inspectionDate === 'string') {
            cleanDate = inspectionDate.replace(/\\u002D/g, '-');
            try {
                cleanDate = JSON.parse('"' + cleanDate + '"');
            } catch (e) {
                // Use as-is if parsing fails
            }
        }
        
        // Make immediate API call to check Retest status for this specific inspection
        fetch('/list-client-folder-files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                client_name: clientName,
                inspection_date: cleanDate,
                inspection_id: groupId
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success && result.files) {
                const hasRetest = result.files.retest && result.files.retest.length > 0;
                debugLog(`🎯 [IMMEDIATE] Retest file check result for ${clientName}: ${hasRetest}`);
                
                const buttonId = 'retest-' + groupId;
                const button = document.getElementById(buttonId);
                
                if (button) {
                    if (hasRetest) {
                        // Update to green success state
                        button.disabled = true;
                        button.className = 'btn btn-sm btn-success success';
                        button.style.backgroundColor = '#28a745';
                        button.style.borderColor = '#28a745';
                        button.style.cursor = 'not-allowed';
                        button.innerHTML = 'Retest ✓';
                        button.title = 'Retest file exists';
                        button.onclick = null;
                        debugLog(`SUCCESS [IMMEDIATE] Updated Retest button to GREEN for: ${clientName}`);
                    } else {
                        // Update to grey state (no file)
                        button.disabled = false;
                        button.className = 'btn btn-sm btn-secondary';
                        button.style.backgroundColor = '#6c757d';
                        button.style.borderColor = '#6c757d';
                        button.style.cursor = 'pointer';
                        button.innerHTML = 'Retest';
                        button.title = 'Upload Retest file';
                        button.onclick = () => uploadRetest(groupId);
                        debugLog(`GREY [IMMEDIATE] Updated Retest button to GREY for: ${clientName}`);
                    }
                    
                    // Remove any file-deleted markers since we've done a fresh check
                    button.removeAttribute('data-file-deleted');
                    button.removeAttribute('data-last-updated');
                } else {
                    debugWarn(`⚠️ [IMMEDIATE] Retest button not found: ${buttonId}`);
                }
            } else {
                debugWarn(`⚠️ [IMMEDIATE] Failed to get file status for ${clientName}: ${result.error}`);
            }
        })
        .catch(error => {
            console.error(`ERROR [IMMEDIATE] Error checking Retest files for ${clientName}:`, error);
        });
    }, 200); // 200ms delay to ensure server-side deletion is complete
}

// IMMEDIATE TARGETED LAB FORM BUTTON CHECK - For specific inspection after file deletion
function immediateLabFormButtonCheck(groupId, clientName, inspectionDate) {
    debugLog(`🎯 [IMMEDIATE] Starting targeted Lab Form check for: ${clientName} on ${inspectionDate}`);
    
    // Add a small delay to ensure server-side file deletion is complete
    setTimeout(() => {
        // Clean the inspection date - decode any Unicode escapes
        let cleanDate = inspectionDate;
        if (typeof inspectionDate === 'string') {
            cleanDate = inspectionDate.replace(/\\u002D/g, '-');
            try {
                cleanDate = JSON.parse('"' + cleanDate + '"');
            } catch (e) {
                // Use as-is if parsing fails
            }
        }
        
        // Make immediate API call to check Lab Form status for this specific inspection
        fetch('/list-client-folder-files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                client_name: clientName,
                inspection_date: cleanDate,
                inspection_id: groupId
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success && result.files) {
                const hasLabForm = result.files.lab_form && result.files.lab_form.length > 0;
                debugLog(`🎯 [IMMEDIATE] Lab Form file check result for ${clientName}: ${hasLabForm}`);
                
                const buttonId = 'lab-form-' + groupId;
                const button = document.getElementById(buttonId);
                
                if (button) {
                    if (hasLabForm) {
                        // Update to green success state
                        button.disabled = true;
                        button.className = 'btn btn-sm btn-success success';
                        button.style.backgroundColor = '#28a745';
                        button.style.borderColor = '#28a745';
                        button.style.cursor = 'not-allowed';
                        button.innerHTML = 'Lab Form ✓';
                        button.title = 'Lab Form file exists';
                        button.onclick = null;
                        debugLog(`SUCCESS [IMMEDIATE] Updated Lab Form button to GREEN for: ${clientName}`);
                    } else {
                        // Update to grey state (no file)
                        button.disabled = false;
                        button.className = 'btn btn-sm btn-secondary';
                        button.style.backgroundColor = '#6c757d';
                        button.style.borderColor = '#6c757d';
                        button.style.cursor = 'pointer';
                        button.innerHTML = 'Lab Form';
                        button.title = 'Upload Lab Form file';
                        button.onclick = () => uploadLabForm(groupId);
                        debugLog(`GREY [IMMEDIATE] Updated Lab Form button to GREY for: ${clientName}`);
                    }
                    
                    // Remove any file-deleted markers since we've done a fresh check
                    button.removeAttribute('data-file-deleted');
                    button.removeAttribute('data-last-updated');
                } else {
                    debugWarn(`⚠️ [IMMEDIATE] Lab Form button not found: ${buttonId}`);
                }
            } else {
                debugWarn(`⚠️ [IMMEDIATE] Failed to get file status for ${clientName}: ${result.error}`);
            }
        })
        .catch(error => {
            console.error(`ERROR [IMMEDIATE] Error checking Lab Form files for ${clientName}:`, error);
        });
    }, 200); // 200ms delay to ensure server-side deletion is complete
}

// SIMPLE RFI BUTTON INITIALIZATION - Direct and fast
async function initializeRFIButtonsSimple() {
    debugLog('DEBUG [SIMPLE] Initializing RFI buttons...');
    
    const rfiButtons = document.querySelectorAll('button[id^="rfi-"]');
    debugLog(`DEBUG [SIMPLE] Found ${rfiButtons.length} RFI buttons`);
    
    for (const button of rfiButtons) {
        const buttonId = button.id;
        const groupId = buttonId.replace('rfi-', '');
        
        // Extract client name and date from groupId
        const parts = groupId.split('_');
        if (parts.length < 3) continue;
        
        const datePart = parts[parts.length - 1];
        const inspectionDate = datePart.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
        let clientName = parts.slice(0, -1).join('_');
        
        if (clientName.includes('Pty_Ltd')) {
            clientName = clientName.replace(/_/g, ' ').replace(/Pty Ltd/g, '(Pty) Ltd.');
        } else {
            clientName = clientName.replace(/_/g, ' ');
        }
        
        try {
            const response = await fetch('/inspections/files/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    client_name: clientName,
                    inspection_date: inspectionDate,
                    _force_refresh: true
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.files) {
                    const hasRFI = data.files.rfi && data.files.rfi.length > 0;
                    
                    if (hasRFI) {
                        // GREEN - RFI file exists
                        button.disabled = true;
                        button.className = 'btn btn-sm btn-success success';
                        button.style.backgroundColor = '#28a745';
                        button.style.borderColor = '#28a745';
                        button.style.cursor = 'not-allowed';
                        button.innerHTML = 'RFI ✓';
                        button.title = 'RFI file exists';
                        button.onclick = null;
                        debugLog(`SUCCESS [SIMPLE] Set ${clientName} RFI button to GREEN`);
                    } else {
                        // GREY - No RFI file
                        button.disabled = false;
                        button.className = 'btn btn-sm btn-secondary';
                        button.style.backgroundColor = '#6c757d';
                        button.style.borderColor = '#6c757d';
                        button.style.cursor = 'pointer';
                        button.innerHTML = 'RFI';
                        button.title = 'Upload RFI file';
                        button.onclick = () => uploadRFI(groupId);
                        debugLog(`GREY [SIMPLE] Set ${clientName} RFI button to GREY`);
                    }
                }
            }
        } catch (error) {
            console.error(`ERROR [SIMPLE] Error checking RFI for ${clientName}:`, error);
        }
    }
    
    debugLog('SUCCESS [SIMPLE] RFI button initialization complete');
}

// SIMPLE INVOICE BUTTON INITIALIZATION - Direct and fast
async function initializeInvoiceButtonsSimple() {
    debugLog('DEBUG [SIMPLE] Initializing Invoice buttons...');
    
    const invoiceButtons = document.querySelectorAll('button[id^="invoice-"]');
    debugLog(`DEBUG [SIMPLE] Found ${invoiceButtons.length} Invoice buttons`);
    
    for (const button of invoiceButtons) {
        const buttonId = button.id;
        const groupId = buttonId.replace('invoice-', '');
        
        // Extract client name and date from groupId
        const parts = groupId.split('_');
        if (parts.length < 3) continue;
        
        const datePart = parts[parts.length - 1];
        const inspectionDate = datePart.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
        let clientName = parts.slice(0, -1).join('_');
        
        if (clientName.includes('Pty_Ltd')) {
            clientName = clientName.replace(/_/g, ' ').replace(/Pty Ltd/g, '(Pty) Ltd.');
        } else {
            clientName = clientName.replace(/_/g, ' ');
        }
        
        try {
            const response = await fetch('/inspections/files/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    client_name: clientName,
                    inspection_date: inspectionDate,
                    _force_refresh: true
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.files) {
                    const hasInvoice = data.files.invoice && data.files.invoice.length > 0;
                    
                    if (hasInvoice) {
                        // GREEN - Invoice file exists
                        button.disabled = true;
                        button.className = 'btn btn-sm btn-success success';
                        button.style.backgroundColor = '#28a745';
                        button.style.borderColor = '#28a745';
                        button.style.cursor = 'not-allowed';
                        button.innerHTML = 'Invoice ✓';
                        button.title = 'Invoice file exists';
                        button.onclick = null;
                        debugLog(`SUCCESS [SIMPLE] Set ${clientName} Invoice button to GREEN`);
                    } else {
                        // GREY - No Invoice file
                        button.disabled = false;
                        button.className = 'btn btn-sm btn-secondary';
                        button.style.backgroundColor = '#6c757d';
                        button.style.borderColor = '#6c757d';
                        button.style.cursor = 'pointer';
                        button.innerHTML = 'Invoice';
                        button.title = 'Upload Invoice file';
                        button.onclick = () => uploadInvoice(groupId);
                        debugLog(`GREY [SIMPLE] Set ${clientName} Invoice button to GREY`);
                    }
                }
            }
        } catch (error) {
            console.error(`ERROR [SIMPLE] Error checking Invoice for ${clientName}:`, error);
        }
    }
    
    debugLog('SUCCESS [SIMPLE] Invoice button initialization complete');
}

// Simple function to immediately make View Files button ORANGE after file upload
function makeViewFilesButtonOrange(groupId) {
    debugLog('Making View Files button ORANGE for groupId:', groupId);
    
    // Find the View Files button for this group
    const viewFilesButton = document.querySelector(`button[onclick*="${groupId}"][onclick*="openFilesPopup"]`);
    
    if (viewFilesButton) {
        // Remove existing color classes including the problematic btn-files-none
        viewFilesButton.classList.remove('btn-danger', 'btn-warning', 'btn-success', 'btn-files-none', 'btn-files-partial', 'btn-files-checking');
        
        // Make it ORANGE
        viewFilesButton.classList.add('btn-warning');
        viewFilesButton.style.backgroundColor = '#ff8c00';
        viewFilesButton.style.color = 'white';
        viewFilesButton.title = 'Files uploaded';
        
        debugLog('SUCCESS: Made View Files button ORANGE');
    } else {
        debugLog('View Files button not found for groupId:', groupId);
    }
}

// Check if files actually exist for a specific button
async function checkButtonFileStatus(button, groupId, clientName, inspectionDate, documentType) {
    // Skip checking if this button has been marked as file-deleted to prevent reversion
    if (button.getAttribute('data-file-deleted') === 'true') {
        debugLog(`⏭️ Skipping file status check for ${documentType} button - marked as file-deleted`);
        return;
    }
    
    try {
        // Clean the date format
        let cleanDate = inspectionDate;
        if (typeof cleanDate === 'string') {
            cleanDate = cleanDate.replace(/\\u002D/g, '-');
            try {
                cleanDate = JSON.parse('"' + cleanDate + '"');
            } catch (e) {
                // Use as-is if parsing fails
            }
        }
        
        const response = await fetch('/inspections/files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                group_id: groupId,
                client_name: clientName,
                inspection_date: cleanDate
            })
        });
        
        const result = await response.json();
        
        if (result.success && result.files) {
            const hasFiles = result.files[documentType] && result.files[documentType].length > 0;
            
            if (!hasFiles && button.disabled) {
                // Button shows as uploaded but no files exist - fix this
                debugLog(`🔧 Fixing ${documentType} button for ${clientName} - no actual files found`);
                button.disabled = false;
                button.style.background = '#28a745';
                button.style.color = 'white';
                button.style.cursor = 'pointer';
                button.innerHTML = `<i class="fas fa-upload"></i> ${documentType.toUpperCase()}`;
                button.title = `Upload ${documentType.toUpperCase()}`;
                
                // Re-enable onclick if it was disabled
                if (documentType === 'rfi') {
                    button.onclick = function() { uploadRFI(groupId); };
                } else if (documentType === 'invoice') {
                    button.onclick = function() { uploadInvoice(groupId); };
                }
            } else if (hasFiles && !button.disabled) {
                // Files exist but button doesn't show as uploaded - check if this is correct
                // Only update if the button should show as uploaded (has upload tracking)
                debugLog(`🔧 ${documentType} files exist for ${clientName} but button not showing as uploaded`);
                
                // Check if there's upload tracking in the database
                // If no upload tracking, keep button as uploadable (this is correct)
                // If there is upload tracking, update button to show uploader
                debugLog(`🔧 Keeping ${documentType} button as uploadable for ${clientName} - no upload tracking found`);
            }
        }
        
    } catch (error) {
        console.error(`Error checking ${documentType} files for ${clientName}:`, error);
    }
}

// Immediately update View Files button after file deletion without backend check
function updateViewFilesButtonAfterFileDeletion(clientName, inspectionDate) {
    debugLog(`COLOR [IMMEDIATE] Updating View Files button for ${clientName} on ${inspectionDate} after file deletion`);
    
    // Clean the inspection date - handle both escaped and unescaped formats
    let cleanDate = inspectionDate;
    if (typeof cleanDate === 'string') {
        // First try to parse as JSON string to handle escaped unicode
        try {
            cleanDate = JSON.parse('"' + cleanDate + '"');
        } catch (e) {
            // If that fails, just replace the escaped dashes
            cleanDate = cleanDate.replace(/\\u002D/g, '-');
        }
    }
    
    // Find all View Files buttons for this client and date
    const buttons = document.querySelectorAll('button');
    const matchingButtons = Array.from(buttons).filter(button => {
        const buttonText = button.textContent.trim();
        const dataClientName = button.getAttribute('data-client-name') || '';
        const dataInspectionDate = button.getAttribute('data-inspection-date') || '';
        const onclick = button.getAttribute('onclick') || '';
        
        // Check if this button is for the correct client and date using data attributes
        return (buttonText.includes('Files') || onclick.includes('openFilesPopup')) &&
               dataClientName === clientName && 
               dataInspectionDate === cleanDate;
    });
    
    debugLog(`DEBUG [IMMEDIATE] Found ${matchingButtons.length} View Files buttons for ${clientName} on ${cleanDate}`);
    
    // Debug: Log all buttons to see what we're working with
    if (matchingButtons.length === 0) {
        debugLog(`DEBUG [DEBUG] No matching buttons found. Searching all buttons...`);
        const allButtons = document.querySelectorAll('button');
        debugLog(`DEBUG [DEBUG] Total buttons found: ${allButtons.length}`);
        
        allButtons.forEach((button, index) => {
            const buttonText = button.textContent.trim();
            const dataClientName = button.getAttribute('data-client-name') || '';
            const dataInspectionDate = button.getAttribute('data-inspection-date') || '';
            
            if (buttonText.includes('Files')) {
                debugLog(`DEBUG [DEBUG] Button ${index}: text="${buttonText}", data-client-name="${dataClientName}", data-inspection-date="${dataInspectionDate}"`);
            }
        });
        
        // Fallback: Try to find buttons by partial matching with better date handling
        debugLog(`DEBUG [DEBUG] Trying fallback search with partial matching...`);
        const fallbackButtons = Array.from(allButtons).filter(button => {
            const buttonText = button.textContent.trim();
            const dataClientName = button.getAttribute('data-client-name') || '';
            const dataInspectionDate = button.getAttribute('data-inspection-date') || '';
            
            // Clean the button's date for comparison
            let buttonDate = dataInspectionDate;
            try {
                buttonDate = JSON.parse('"' + buttonDate + '"');
            } catch (e) {
                buttonDate = buttonDate.replace(/\\u002D/g, '-');
            }
            
            return buttonText.includes('Files') && 
                   dataClientName === clientName && 
                   buttonDate === cleanDate;
        });
        
        if (fallbackButtons.length > 0) {
            debugLog(`DEBUG [DEBUG] Found ${fallbackButtons.length} buttons with fallback search`);
            matchingButtons.push(...fallbackButtons);
        }
    }
    
    // For now, we'll check the current file state by making a quick API call
    // but we'll optimize this later to avoid the race condition
    fetch('/inspections/files/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            client_name: clientName,
            inspection_date: cleanDate
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success && result.files) {
            // Determine file status based on what files exist
            const hasRfi = result.files.rfi && result.files.rfi.length > 0;
            const hasInvoice = result.files.invoice && result.files.invoice.length > 0;
            const hasLab = result.files.lab && result.files.lab.length > 0;
            const hasRetest = result.files.retest && result.files.retest.length > 0;
            const hasCompliance = result.files.compliance && result.files.compliance.length > 0;
            
            let fileStatus;
            if (hasRfi && hasInvoice && hasLab && hasCompliance) {
                fileStatus = 'all_files';
            } else if (hasCompliance) {
                fileStatus = 'compliance_only';
            } else if (hasRfi || hasInvoice || hasLab || hasRetest) {
                fileStatus = 'partial_files';
            } else {
                fileStatus = 'no_files';
            }
            
            debugLog(`📊 [IMMEDIATE] File status after deletion: ${fileStatus} (RFI:${hasRfi}, Invoice:${hasInvoice}, Lab:${hasLab}, Compliance:${hasCompliance})`);
            
            // Update the button colors immediately - bypass the skip logic for file deletion
            matchingButtons.forEach(button => {
                debugLog(`COLOR [IMMEDIATE] Updating button color to ${fileStatus} for ${clientName}`);
                
                // Remove existing color classes including the problematic btn-files-none
                button.classList.remove('btn-view-files-green', 'btn-view-files-red', 'btn-view-files-blue', 'btn-view-files-orange', 'btn-files-none', 'btn-files-partial', 'btn-files-checking');
                
                // Find the status icon
                const statusIcon = button.querySelector('i[class*="fa-"]');
                
                // Apply appropriate color class and icon based on status
                switch(fileStatus) {
                    case 'all_files':
                        button.classList.add('btn-view-files-green');
                        button.title = 'All files available (RFI, Invoice, Lab Results, Compliance)';
                        if (statusIcon) {
                            statusIcon.className = 'fas fa-check-circle';
                            statusIcon.style.color = '#059669';
                        }
                        debugLog('   SUCCESS Applied GREEN color to button');
                        break;
                    case 'compliance_only':
                        button.classList.add('btn-view-files-orange');
                        button.title = 'Only compliance documents available';
                        if (statusIcon) {
                            statusIcon.className = 'fas fa-shield-alt';
                            statusIcon.style.color = '#f59e0b';
                        }
                        debugLog('   🟡 Applied ORANGE color to button');
                        break;
                    case 'partial_files':
                        button.classList.add('btn-warning');
                        button.style.backgroundColor = '#ff8c00';
                        button.style.color = 'white';
                        button.title = 'Files uploaded';
                        if (statusIcon) {
                            statusIcon.className = 'fas fa-file-alt';
                            statusIcon.style.color = 'white';
                        }
                        debugLog('   ORANGE Applied ORANGE color to button');
                        break;
                    case 'no_files':
                        button.classList.add('btn-view-files-red');
                        button.title = 'No files found';
                        if (statusIcon) {
                            statusIcon.className = 'fas fa-times-circle';
                            statusIcon.style.color = '#dc2626';
                        }
                        debugLog('   🔴 Applied RED color to button');
                        break;
                    default:
                        debugLog('   ⚠️ Unknown file status:', fileStatus);
                }
            });
        } else {
            // No files found - set to red
            debugLog(`📊 [IMMEDIATE] No files found after deletion - setting to no_files`);
            matchingButtons.forEach(button => {
                debugLog(`COLOR [IMMEDIATE] Setting button to RED (no files) for ${clientName}`);
                
                // Remove existing color classes including the problematic btn-files-none
                button.classList.remove('btn-view-files-green', 'btn-view-files-red', 'btn-view-files-blue', 'btn-view-files-orange', 'btn-files-none', 'btn-files-partial', 'btn-files-checking');
                
                // Find the status icon
                const statusIcon = button.querySelector('i[class*="fa-"]');
                
                // Apply red color for no files
                button.classList.add('btn-view-files-red');
                button.title = 'No files found';
                if (statusIcon) {
                    statusIcon.className = 'fas fa-times-circle';
                    statusIcon.style.color = '#dc2626';
                }
                debugLog('   🔴 Applied RED color to button (no files)');
            });
        }
    })
    .catch(error => {
        console.error(`ERROR [IMMEDIATE] Error checking file status after deletion:`, error);
        // Fallback to no_files status
        matchingButtons.forEach(button => {
            debugLog(`COLOR [IMMEDIATE] Error fallback - setting button to RED (no files) for ${clientName}`);
            
            // Remove existing color classes including the problematic btn-files-none
            button.classList.remove('btn-view-files-green', 'btn-view-files-red', 'btn-view-files-blue', 'btn-view-files-orange', 'btn-files-none', 'btn-files-partial', 'btn-files-checking');
            
            // Find the status icon
            const statusIcon = button.querySelector('i[class*="fa-"]');
            
            // Apply red color for no files
            button.classList.add('btn-view-files-red');
            button.title = 'No files found';
            if (statusIcon) {
                statusIcon.className = 'fas fa-times-circle';
                statusIcon.style.color = '#dc2626';
            }
            debugLog('   🔴 Applied RED color to button (error fallback)');
        });
    });
}

// Update button state after file deletion
function updateButtonAfterDeletion(clientName, inspectionDate, documentType) {
    debugLog(`INFO Updating ${documentType} button after deletion for ${clientName}`);
    
    // For lab, lab form, and retest buttons, we need to find the specific inspection ID from the file path
    if (documentType === 'lab' || documentType === 'lab_form' || documentType === 'retest') {
        debugLog(`INFO ${documentType} button deletion - finding button by group ID`);
        
        // Use the current group ID from the popup context
        const groupId = window.currentFilesGroupId;
        if (!groupId) {
            debugLog(`⚠️ No group ID available for button update`);
            return;
        }
        
        // Find button by group ID for individual inspection buttons
        const allButtons = document.querySelectorAll(`button[id^="${documentType}-"]`);
        let button = null;
        
        for (let btn of allButtons) {
            const btnGroupId = btn.getAttribute('data-group-id');
            if (btnGroupId === groupId) {
                button = btn;
                debugLog(`SUCCESS Found ${documentType} button by group ID: ${btn.id} (group: ${btnGroupId})`);
                break;
            }
        }
        
        if (button) {
            // Reset button to grey state
            button.disabled = false;
            button.classList.remove('uploaded', 'btn-success');
            button.classList.add('btn-outline-secondary', 'btn-sm');
            button.style.background = '';
            button.style.color = '';
            button.style.border = '';
            button.style.cursor = 'pointer';
            
            // Set appropriate content based on document type
            if (documentType === 'lab') {
                button.innerHTML = '<i class="fas fa-flask"></i> Lab';
                button.title = 'Lab result upload available';
            } else if (documentType === 'lab_form') {
                button.innerHTML = '<i class="fas fa-file-alt"></i> Lab Form';
                button.title = 'Lab form upload available';
            } else if (documentType === 'retest') {
                button.innerHTML = '<i class="fas fa-redo"></i> Retest';
                button.title = 'Retest upload available';
            } else {
                button.innerHTML = documentType.toUpperCase();
                button.title = `Upload ${documentType.toUpperCase()}`;
            }
            
            // Mark button as file-deleted to prevent UI updates from overriding this state
            button.setAttribute('data-file-deleted', 'true');
            button.setAttribute('data-last-updated', Date.now().toString());
            
            debugLog(`SUCCESS Reset ${documentType} button to grey state`);
        } else {
            debugLog(`⚠️ Could not find ${documentType} button for group ${groupId}`);
        }
        
        return;
    }
    
    // Use the current group ID from the popup context
    const groupId = window.currentFilesGroupId;
    if (!groupId) {
        debugLog(`⚠️ No group ID available for button update`);
        return;
    }
    
    const buttonId = `${documentType}-${groupId}`;
    debugLog(`DEBUG Looking for button with ID: ${buttonId}`);
    
    // Try multiple methods to find the button
    let button = null;
    
    // Method 1: Direct ID lookup
    button = document.getElementById(buttonId);
    if (button) {
        debugLog(`SUCCESS Found button by direct ID: ${buttonId}`);
    } else {
        // Method 2: Search all buttons with pattern
        debugLog(`DEBUG Button not found by ID, searching by pattern...`);
        const allButtons = document.querySelectorAll(`button[id^="${documentType}-"]`);
        debugLog(`DEBUG Found ${allButtons.length} buttons with pattern "${documentType}-"`);
        
        for (let btn of allButtons) {
            if (btn.id === buttonId) {
                button = btn;
                debugLog(`SUCCESS Found button by pattern search: ${btn.id}`);
                break;
            }
        }
    }
    
    // Method 3: Search in all tables and modals
    if (!button) {
        debugLog(`DEBUG Button still not found, searching in all containers...`);
        const containers = document.querySelectorAll('table, .modal, .popup, [id*="detail"]');
        for (let container of containers) {
            const foundButton = container.querySelector(`#${buttonId}`);
            if (foundButton) {
                button = foundButton;
                debugLog(`SUCCESS Found button in container: ${container.tagName} ${container.className || container.id}`);
                break;
            }
        }
    }
    
    // Method 4: Search by data attributes
    if (!button) {
        debugLog(`DEBUG Searching by data attributes...`);
        const buttonsWithData = document.querySelectorAll(`button[data-client-name="${clientName}"], button[data-inspection-date*="${inspectionDate}"]`);
        for (let btn of buttonsWithData) {
            if (btn.id.includes(documentType) && btn.id.includes(groupId.split('_')[0])) {
                button = btn;
                debugLog(`SUCCESS Found button by data attributes: ${btn.id}`);
                break;
            }
        }
    }
    
    if (button) {
        debugLog(`SUCCESS Found ${documentType} button: ${buttonId}`);
            
            // Reset button to default state (no files)
            button.disabled = false;
            button.classList.remove('uploaded');
            button.classList.add('btn-outline-secondary', 'btn-sm');
            button.style.background = '';
            button.style.color = '';
            button.style.cursor = 'pointer';
            button.innerHTML = documentType.toUpperCase();
            button.title = `Upload ${documentType.toUpperCase()}`;
            
            // Mark button as file-deleted to prevent UI updates from overriding this state
            button.setAttribute('data-file-deleted', 'true');
            button.setAttribute('data-last-updated', Date.now().toString());
            
            // Re-enable onclick functionality
            if (documentType === 'rfi') {
                button.onclick = function() { uploadRFI(groupId); };
            } else if (documentType === 'invoice') {
                button.onclick = function() { uploadInvoice(groupId); };
            }
            
        debugLog(`SUCCESS ${documentType.toUpperCase()} button reset to uploadable state for ${clientName}`);
    } else {
        debugLog(`⚠️ Button still not found: ${buttonId}`);
        debugLog(`DEBUG Available buttons:`, Array.from(document.querySelectorAll('button')).map(b => b.id).filter(id => id.includes(documentType)));
        
        // Store the update for when the popup closes
        if (!window.pendingButtonUpdates) {
            window.pendingButtonUpdates = [];
        }
        window.pendingButtonUpdates.push({
            buttonId: buttonId,
            documentType: documentType,
            groupId: groupId,
            action: 'reset'
        });
        debugLog(`📝 Stored pending button update for when popup closes`);
    }
    
    // Clear localStorage for this button
    const uploadStatus = JSON.parse(localStorage.getItem('uploadStatus') || '{}');
    delete uploadStatus[buttonId];
    localStorage.setItem('uploadStatus', JSON.stringify(uploadStatus));
    
    // Force refresh the View Files popup to show updated file count
    if (window.currentFilesClient && window.currentFilesDate) {
        debugLog(`INFO Refreshing View Files popup to show updated file count`);
        setTimeout(() => {
            openFilesPopup(groupId, window.currentFilesClient, window.currentFilesDate);
        }, 500);
    }
}

// Refresh inspection data for a specific inspection (like page refresh but targeted)
async function refreshInspectionData(groupId, clientName, inspectionDate) {
    try {
        debugLog(`INFO Refreshing inspection data for: ${clientName} on ${inspectionDate}`);
        
        // Clean the client name and date
        const cleanClientName = clientName.replace(/[^a-zA-Z0-9\s]/g, '').trim();
        const cleanDate = inspectionDate.replace(/[^0-9-]/g, '').replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
        
        debugLog(`DEBUG Cleaned client name: ${cleanClientName}, Cleaned date: ${cleanDate}`);
        
        // Make API call to get fresh file data for this inspection
        const response = await fetch('/inspections/files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                group_id: groupId,
                client_name: cleanClientName,
                inspection_date: cleanDate
            })
        });
        
        if (!response.ok) {
            console.error('ERROR Failed to refresh inspection files:', response.status);
            return;
        }
        
        const data = await response.json();
        debugLog(`INFO Fresh inspection data received:`, data);
        
        if (data.success && data.files) {
            const rfiFiles = data.files.rfi || [];
            const invoiceFiles = data.files.invoice || [];
            
            debugLog(`INFO Found ${rfiFiles.length} RFI files and ${invoiceFiles.length} Invoice files`);
            
            // Update RFI button based on file count
            await updateButtonForInspection(groupId, 'rfi', rfiFiles.length > 0, clientName);
            
            // Update Invoice button based on file count
            await updateButtonForInspection(groupId, 'invoice', invoiceFiles.length > 0, clientName);
            
            debugLog(`SUCCESS Inspection data refreshed for ${clientName}`);
        }
    } catch (error) {
        console.error('ERROR Error refreshing inspection data:', error);
    }
}

// Update a specific button for an inspection based on file existence
async function updateButtonForInspection(groupId, buttonType, hasFiles, clientName) {
    const buttonId = `${buttonType}-${groupId}`;
    debugLog(`INFO Updating ${buttonType} button: ${buttonId}, hasFiles: ${hasFiles}`);
    
    // Try multiple methods to find the button with retries
    let button = null;
    let attempts = 0;
    const maxAttempts = 3;
    
    while (!button && attempts < maxAttempts) {
        attempts++;
        debugLog(`DEBUG Attempt ${attempts} to find ${buttonType} button: ${buttonId}`);
        
        // Method 1: Direct ID search
        button = document.getElementById(buttonId);
        if (button) {
            debugLog(`SUCCESS Found ${buttonType} button by direct ID on attempt ${attempts}`);
            break;
        }
        
        // Method 2: Search all buttons by ID
        const allButtons = Array.from(document.querySelectorAll('button'));
        button = allButtons.find(b => b.id === buttonId);
        if (button) {
            debugLog(`SUCCESS Found ${buttonType} button by searching all buttons on attempt ${attempts}`);
            break;
        }
        
        // Method 3: Search by group ID and button type
        button = allButtons.find(b => 
            b.id.includes(groupId) && 
            (b.id.includes(buttonType) || b.innerHTML.toLowerCase().includes(buttonType))
        );
        if (button) {
            debugLog(`SUCCESS Found ${buttonType} button by group ID pattern on attempt ${attempts}`);
            break;
        }
        
        // Method 4: Search for buttons showing "Developer" (if it's the RFI button)
        if (buttonType === 'rfi') {
            button = allButtons.find(b => 
                b.innerHTML.toLowerCase().includes('developer') && 
                b.id.includes(groupId)
            );
            if (button) {
                debugLog(`SUCCESS Found ${buttonType} button by Developer text search on attempt ${attempts}`);
                break;
            }
        }
        
        // Method 5: Search for any button with the group ID
        button = allButtons.find(b => b.id.includes(groupId));
        if (button) {
            debugLog(`SUCCESS Found button with group ID on attempt ${attempts}: ${button.id}`);
            // Check if this might be the right button type
            if (button.id.includes(buttonType) || button.innerHTML.toLowerCase().includes(buttonType)) {
                debugLog(`SUCCESS This appears to be the ${buttonType} button`);
                break;
            } else {
                debugLog(`⚠️ Found group button but not ${buttonType} type: ${button.id}`);
                button = null; // Continue searching
            }
        }
        
        if (!button && attempts < maxAttempts) {
            debugLog(`⏳ Button not found on attempt ${attempts}, waiting 500ms before retry...`);
            // Wait before next attempt
            await new Promise(resolve => setTimeout(resolve, 500));
        }
    }
    
    if (button) {
        debugLog(`SUCCESS Found ${buttonType} button: ${button.id}`);
        
        if (hasFiles) {
            // Files exist - button should show uploader's name (or stay as is if already showing name)
            debugLog(`DEBUG Button current innerHTML: "${button.innerHTML}", expected: "${buttonType.toUpperCase()}"`);
            if (button.innerHTML === buttonType.toUpperCase()) {
                // Button is still showing "RFI" or "Invoice" - update to show uploader
                button.disabled = true;
                button.classList.add('uploaded');
                button.style.background = '#d4edda';
                button.style.color = '#155724';
                button.style.border = '1px solid #c3e6cb';
                button.style.cursor = 'not-allowed';
                button.innerHTML = 'Developer'; // Or get actual uploader name
                button.title = `${buttonType.toUpperCase()} uploaded by Developer`;
                button.onclick = null;
                debugLog(`SUCCESS Updated ${buttonType} button to show uploaded state`);
            } else {
                debugLog(`ℹ️ ${buttonType} button already shows uploader name: "${button.innerHTML}"`);
            }
        } else {
            // No files - reset button to uploadable state
            button.disabled = false;
            button.classList.remove('uploaded');
            button.classList.add(`btn-${buttonType}`, 'btn-sm');
            button.style.background = '#28a745';
            button.style.color = 'white';
            button.style.border = '1px solid #1e7e34';
            button.style.cursor = 'pointer';
            button.innerHTML = buttonType.toUpperCase();
            button.title = `Upload ${buttonType.toUpperCase()}`;
            
            // Re-enable onclick functionality
            if (buttonType === 'rfi') {
                button.onclick = function() { uploadRFI(groupId); };
            } else if (buttonType === 'invoice') {
                button.onclick = function() { uploadInvoice(groupId); };
            }
            
            debugLog(`SUCCESS Reset ${buttonType} button to uploadable state`);
        }
    } else {
        debugLog(`⚠️ ${buttonType} button not found: ${buttonId}`);
        
        // Enhanced debugging - show all available buttons
        const allButtons = Array.from(document.querySelectorAll('button'));
        debugLog(`DEBUG All available buttons:`, allButtons.map(b => ({
            id: b.id,
            text: b.innerHTML.trim(),
            classes: b.className,
            disabled: b.disabled,
            parent: b.parentElement?.tagName,
            parentId: b.parentElement?.id
        })));
        
        // Show buttons in the shipments table specifically
        const shipmentsTable = document.getElementById('shipmentsTable');
        if (shipmentsTable) {
            const tableButtons = Array.from(shipmentsTable.querySelectorAll('button'));
            debugLog(`DEBUG Buttons in shipments table:`, tableButtons.map(b => ({
                id: b.id,
                text: b.innerHTML.trim(),
                classes: b.className,
                disabled: b.disabled
            })));
        } else {
            debugLog(`⚠️ Shipments table not found`);
        }
        
        // Look for buttons with similar IDs
        const similarButtons = allButtons.filter(b => 
            b.id.includes(groupId) || 
            b.id.includes(buttonType) ||
            b.innerHTML.toLowerCase().includes(buttonType)
        );
        debugLog(`DEBUG Similar buttons found:`, similarButtons.map(b => ({
            id: b.id,
            text: b.innerHTML.trim(),
            classes: b.className
        })));
        
        // Look specifically for any RFI buttons
        const rfiButtons = allButtons.filter(b => b.id.toLowerCase().includes('rfi'));
        debugLog(`DEBUG All RFI buttons found:`, rfiButtons.map(b => ({
            id: b.id,
            text: b.innerHTML.trim(),
            classes: b.className,
            parent: b.parentElement?.tagName
        })));
    }
}

// Check specific inspection for RFI files and update button accordingly
async function checkSpecificInspectionRFIStatus(groupId, clientName, inspectionDate) {
    try {
        debugLog(`DEBUG Checking RFI status for specific inspection: ${clientName} on ${inspectionDate}`);
        
        // Clean the client name and date
        const cleanClientName = clientName.replace(/[^a-zA-Z0-9\s]/g, '').trim();
        const cleanDate = inspectionDate.replace(/[^0-9-]/g, '').replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
        
        debugLog(`DEBUG Cleaned client name: ${cleanClientName}, Cleaned date: ${cleanDate}`);
        
        // Make API call to check files for this specific inspection
        const response = await fetch('/inspections/files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                group_id: groupId,
                client_name: cleanClientName,
                inspection_date: cleanDate
            })
        });
        
        if (!response.ok) {
            console.error('ERROR Failed to check inspection files:', response.status);
            return;
        }
        
        const data = await response.json();
        debugLog(`DEBUG File check response for ${clientName}:`, data);
        debugLog(`DEBUG Full API response:`, JSON.stringify(data, null, 2));
        
        if (data.success && data.files) {
            const rfiFiles = data.files.rfi || [];
            debugLog(`DEBUG Found ${rfiFiles.length} RFI files for ${clientName}`);
            debugLog(`DEBUG RFI files:`, rfiFiles);
            debugLog(`DEBUG All files object:`, data.files);
            
            // Find the RFI button for this specific inspection
            const buttonId = `rfi-${groupId}`;
            debugLog(`DEBUG Looking for RFI button with ID: ${buttonId}`);
            const button = document.getElementById(buttonId);
            
            if (button) {
                debugLog(`SUCCESS Found RFI button: ${buttonId}`);
                debugLog(`DEBUG Current button state - disabled: ${button.disabled}, innerHTML: "${button.innerHTML}"`);
                
                if (rfiFiles.length === 0) {
                    // No RFI files - reset button to "RFI"
                    debugLog(`INFO No RFI files found - resetting button to "RFI" for ${clientName}`);
                    button.disabled = false;
                    button.classList.remove('uploaded');
                    button.classList.add('btn-rfi', 'btn-sm');
                    button.style.background = '#28a745';
                    button.style.color = 'white';
                    button.style.border = '1px solid #1e7e34';
                    button.style.cursor = 'pointer';
                    button.innerHTML = 'RFI';
                    button.title = 'Upload RFI';
                    
                    // Re-enable onclick functionality
                    button.onclick = function() { uploadRFI(groupId); };
                    
                    debugLog(`SUCCESS Reset RFI button to "RFI" for ${clientName}`);
                    debugLog(`DEBUG Button after reset - disabled: ${button.disabled}, innerHTML: "${button.innerHTML}"`);
                } else {
                    // RFI files exist - button should show uploader's name
                    debugLog(`ℹ️ RFI files exist - button should already show uploader's name for ${clientName}`);
                }
            } else {
                debugLog(`⚠️ RFI button not found for ${clientName}: ${buttonId}`);
                debugLog(`DEBUG Available buttons:`, Array.from(document.querySelectorAll('button')).map(b => b.id).filter(id => id.includes('rfi')));
                debugLog(`DEBUG All buttons with 'rfi' in ID:`, Array.from(document.querySelectorAll('button[id*="rfi"]')).map(b => ({id: b.id, text: b.innerHTML, disabled: b.disabled})));
                
                // Try to find button by searching in the main table
                debugLog(`DEBUG Trying to find button in main table...`);
                const mainTable = document.querySelector('table.table');
                if (mainTable) {
                    debugLog(`DEBUG Main table found, searching for button...`);
                    const tableButton = mainTable.querySelector(`#${buttonId}`);
                    if (tableButton) {
                        debugLog(`SUCCESS Found RFI button in main table: ${buttonId}`);
                        const button = tableButton;
                        
                        if (rfiFiles.length === 0) {
                            debugLog(`INFO No RFI files found - resetting button to "RFI" for ${clientName}`);
                            button.disabled = false;
                            button.classList.remove('uploaded');
                            button.classList.add('btn-rfi', 'btn-sm');
                            button.style.background = '#28a745';
                            button.style.color = 'white';
                            button.style.border = '1px solid #1e7e34';
                            button.style.cursor = 'pointer';
                            button.innerHTML = 'RFI';
                            button.title = 'Upload RFI';
                            button.onclick = function() { uploadRFI(groupId); };
                            debugLog(`SUCCESS Reset RFI button to "RFI" for ${clientName}`);
                        }
                    } else {
                        debugLog(`⚠️ Button still not found in main table`);
                        debugLog(`DEBUG All buttons in main table:`, Array.from(mainTable.querySelectorAll('button')).map(b => ({id: b.id, text: b.innerHTML, disabled: b.disabled})));
                    }
                } else {
                    debugLog(`⚠️ Main table not found`);
                }
                
                // Try to find button by searching for any button with the group ID
                debugLog(`DEBUG Trying to find button by group ID pattern...`);
                const groupButtons = Array.from(document.querySelectorAll('button')).filter(b => b.id.includes(groupId));
                debugLog(`DEBUG Buttons containing group ID ${groupId}:`, groupButtons.map(b => ({id: b.id, text: b.innerHTML, disabled: b.disabled})));
                
                // Check if any of these group buttons is the RFI button
                const rfiGroupButton = groupButtons.find(b => b.id.includes('rfi'));
                if (rfiGroupButton) {
                    debugLog(`SUCCESS Found RFI button in group buttons:`, rfiGroupButton.id);
                    const button = rfiGroupButton;
                    
                    if (rfiFiles.length === 0) {
                        debugLog(`INFO No RFI files found - resetting button to "RFI" for ${clientName}`);
                        button.disabled = false;
                        button.classList.remove('uploaded');
                        button.classList.add('btn-rfi', 'btn-sm');
                        button.style.background = '#28a745';
                        button.style.color = 'white';
                        button.style.border = '1px solid #1e7e34';
                        button.style.cursor = 'pointer';
                        button.innerHTML = 'RFI';
                        button.title = 'Upload RFI';
                        button.onclick = function() { uploadRFI(groupId); };
                        debugLog(`SUCCESS Reset RFI button to "RFI" for ${clientName}`);
                    }
                }
                
                // Try to find button by searching for buttons with 'rfi' in the text
                debugLog(`DEBUG Trying to find button by text content...`);
                const rfiButtons = Array.from(document.querySelectorAll('button')).filter(b => 
                    b.innerHTML.toLowerCase().includes('rfi') || 
                    b.innerHTML.toLowerCase().includes('developer') ||
                    b.innerHTML.toLowerCase().includes('upload')
                );
                debugLog(`DEBUG Buttons with RFI-related text:`, rfiButtons.map(b => ({id: b.id, text: b.innerHTML, disabled: b.disabled})));
                
                // Check if any of these text-based buttons is the RFI button
                const rfiTextButton = rfiButtons.find(b => b.id.includes('rfi') || b.innerHTML.toLowerCase().includes('developer'));
                if (rfiTextButton) {
                    debugLog(`SUCCESS Found RFI button by text search:`, rfiTextButton.id);
                    const button = rfiTextButton;
                    
                    if (rfiFiles.length === 0) {
                        debugLog(`INFO No RFI files found - resetting button to "RFI" for ${clientName}`);
                        button.disabled = false;
                        button.classList.remove('uploaded');
                        button.classList.add('btn-rfi', 'btn-sm');
                        button.style.background = '#28a745';
                        button.style.color = 'white';
                        button.style.border = '1px solid #1e7e34';
                        button.style.cursor = 'pointer';
                        button.innerHTML = 'RFI';
                        button.title = 'Upload RFI';
                        button.onclick = function() { uploadRFI(groupId); };
                        debugLog(`SUCCESS Reset RFI button to "RFI" for ${clientName}`);
                    }
                }
                
                // Last resort: Try to find any button that might be the RFI button
                debugLog(`DEBUG Last resort: Searching for any button that might be RFI...`);
                const allButtons = Array.from(document.querySelectorAll('button'));
                debugLog(`DEBUG Total buttons found: ${allButtons.length}`);
                
                // Look for buttons that might be RFI buttons (containing group ID or showing "Developer")
                const potentialRfiButtons = allButtons.filter(b => 
                    b.id.includes(groupId) || 
                    b.innerHTML.toLowerCase().includes('developer') ||
                    b.innerHTML.toLowerCase().includes('rfi') ||
                    b.innerHTML.toLowerCase().includes('upload')
                );
                
                debugLog(`DEBUG Potential RFI buttons found: ${potentialRfiButtons.length}`);
                potentialRfiButtons.forEach((btn, index) => {
                    debugLog(`DEBUG Button ${index + 1}:`, {
                        id: btn.id,
                        text: btn.innerHTML,
                        disabled: btn.disabled,
                        classes: btn.className,
                        parent: btn.parentElement?.tagName
                    });
                });
                
                // Try to find the RFI button by looking for buttons with "Developer" text
                const developerButton = potentialRfiButtons.find(b => 
                    b.innerHTML.toLowerCase().includes('developer') && 
                    (b.id.includes(groupId) || b.id.includes('rfi'))
                );
                
                if (developerButton) {
                    debugLog(`SUCCESS Found Developer button that might be RFI:`, developerButton.id);
                    const button = developerButton;
                    
                    if (rfiFiles.length === 0) {
                        debugLog(`INFO No RFI files found - resetting Developer button to "RFI" for ${clientName}`);
                        button.disabled = false;
                        button.classList.remove('uploaded');
                        button.classList.add('btn-rfi', 'btn-sm');
                        button.style.background = '#28a745';
                        button.style.color = 'white';
                        button.style.border = '1px solid #1e7e34';
                        button.style.cursor = 'pointer';
                        button.innerHTML = 'RFI';
                        button.title = 'Upload RFI';
                        button.onclick = function() { uploadRFI(groupId); };
                        debugLog(`SUCCESS Reset Developer button to "RFI" for ${clientName}`);
                    }
                }
            }
        } else {
            debugLog(`ERROR API call failed or no files data:`, data);
        }
    } catch (error) {
        console.error('ERROR Error checking specific inspection RFI status:', error);
    }
}

// Check specific inspection for Invoice files and update button accordingly
async function checkSpecificInspectionInvoiceStatus(groupId, clientName, inspectionDate) {
    try {
        debugLog(`DEBUG Checking Invoice status for specific inspection: ${clientName} on ${inspectionDate}`);
        
        // Clean the client name and date
        const cleanClientName = clientName.replace(/[^a-zA-Z0-9\s]/g, '').trim();
        const cleanDate = inspectionDate.replace(/[^0-9-]/g, '').replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
        
        debugLog(`DEBUG Cleaned client name: ${cleanClientName}, Cleaned date: ${cleanDate}`);
        
        // Make API call to check files for this specific inspection
        const response = await fetch('/inspections/files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                group_id: groupId,
                client_name: cleanClientName,
                inspection_date: cleanDate
            })
        });
        
        if (!response.ok) {
            console.error('ERROR Failed to check inspection files:', response.status);
            return;
        }
        
        const data = await response.json();
        debugLog(`DEBUG File check response for ${clientName}:`, data);
        debugLog(`DEBUG Full API response:`, JSON.stringify(data, null, 2));
        
        if (data.success && data.files) {
            const invoiceFiles = data.files.invoice || [];
            debugLog(`DEBUG Found ${invoiceFiles.length} Invoice files for ${clientName}`);
            debugLog(`DEBUG Invoice files:`, invoiceFiles);
            debugLog(`DEBUG All files object:`, data.files);
            
            // Find the Invoice button for this specific inspection
            const buttonId = `invoice-${groupId}`;
            const button = document.getElementById(buttonId);
            
            if (button) {
                if (invoiceFiles.length === 0) {
                    // No Invoice files - reset button to "Invoice"
                    debugLog(`INFO No Invoice files found - resetting button to "Invoice" for ${clientName}`);
                    button.disabled = false;
                    button.classList.remove('uploaded');
                    button.classList.add('btn-invoice', 'btn-sm');
                    button.style.background = '#28a745';
                    button.style.color = 'white';
                    button.style.border = '1px solid #1e7e34';
                    button.style.cursor = 'pointer';
                    button.innerHTML = 'Invoice';
                    button.title = 'Upload Invoice';
                    
                    // Re-enable onclick functionality
                    button.onclick = function() { uploadInvoice(groupId); };
                    
                    debugLog(`SUCCESS Reset Invoice button to "Invoice" for ${clientName}`);
                } else {
                    // Invoice files exist - button should show uploader's name
                    debugLog(`ℹ️ Invoice files exist - button should already show uploader's name for ${clientName}`);
                }
            } else {
                debugLog(`⚠️ Invoice button not found for ${clientName}: ${buttonId}`);
            }
        }
    } catch (error) {
        console.error('ERROR Error checking specific inspection Invoice status:', error);
    }
}

// Process pending button updates when popup closes
function processPendingButtonUpdates() {
    if (window.pendingButtonUpdates && window.pendingButtonUpdates.length > 0) {
        debugLog(`INFO Processing ${window.pendingButtonUpdates.length} pending button updates`);
        
        window.pendingButtonUpdates.forEach(update => {
            const button = document.getElementById(update.buttonId);
            if (button) {
                debugLog(`SUCCESS Processing pending update for: ${update.buttonId}`);
                
                if (update.action === 'reset') {
                    // Reset button to uploadable state
                    button.disabled = false;
                    button.classList.remove('uploaded');
                    button.classList.add(`btn-${update.documentType}`, 'btn-sm');
                    button.style.background = '#28a745';
                    button.style.color = 'white';
                    button.style.cursor = 'pointer';
                    button.innerHTML = update.documentType.toUpperCase();
                    button.title = `Upload ${update.documentType.toUpperCase()}`;
                    
                    // Re-enable onclick functionality
                    if (update.documentType === 'rfi') {
                        button.onclick = function() { uploadRFI(update.groupId); };
                    } else if (update.documentType === 'invoice') {
                        button.onclick = function() { uploadInvoice(update.groupId); };
                    }
                    
                    debugLog(`SUCCESS Processed pending reset update for: ${update.buttonId}`);
                } else if (update.action === 'upload') {
                    // Update button to show uploaded state with username
                    button.disabled = true;
                    button.classList.add('uploaded');
                    button.style.background = '#d4edda';
                    button.style.color = '#155724';
                    button.style.border = '1px solid #c3e6cb';
                    button.style.cursor = 'not-allowed';
                    button.innerHTML = update.username;
                    
                    const currentDate = new Date().toLocaleDateString('en-US', { 
                        month: 'numeric', 
                        day: 'numeric', 
                        year: '2-digit' 
                    });
                    button.title = `${update.documentType.toUpperCase()} uploaded by ${update.username} on ${currentDate}`;
                    
                    // Remove the onclick handler since button is now disabled
                    button.onclick = null;
                    
                    debugLog(`SUCCESS Processed pending upload update for: ${update.buttonId} with username: ${update.username}`);
                }
            } else {
                debugLog(`⚠️ Button still not found for pending update: ${update.buttonId}`);
            }
        });
        
        // Clear pending updates
        window.pendingButtonUpdates = [];
        debugLog(`SUCCESS Cleared all pending button updates`);
    }
}

// Enhanced button reset function for immediate UI updates
function resetButtonImmediately(documentType, groupId, clientName, inspectionDate) {
    debugLog(`🔧 Resetting ${documentType} button immediately for group ${groupId}`);
    
    const buttonId = `${documentType}-${groupId}`;
    debugLog(`DEBUG Looking for button with ID: ${buttonId}`);
    
    // Try multiple methods to find the button
    let button = document.getElementById(buttonId);
    
    if (!button) {
        debugLog(`DEBUG Button not found by ID, searching by pattern...`);
        const allButtons = document.querySelectorAll(`button[id^="${documentType}-"]`);
        debugLog(`DEBUG Found ${allButtons.length} buttons with pattern "${documentType}-"`);
        
        // For individual inspection buttons (lab, lab_form, retest), search by group data attribute
        if (documentType === 'lab' || documentType === 'lab_form' || documentType === 'retest') {
            for (let btn of allButtons) {
                const btnGroupId = btn.getAttribute('data-group-id');
                if (btnGroupId === groupId) {
                    button = btn;
                    debugLog(`SUCCESS Found ${documentType} button by group ID: ${btn.id} (group: ${btnGroupId})`);
                    break;
                }
            }
        } else {
            // For group buttons (rfi, invoice), use exact ID match
            for (let btn of allButtons) {
                if (btn.id === buttonId) {
                    button = btn;
                    debugLog(`SUCCESS Found button by pattern search: ${btn.id}`);
                    break;
                }
            }
        }
    }
    
    if (button) {
        debugLog(`SUCCESS Found ${documentType} button: ${buttonId}`);
        
        // Reset button to default state (uploadable)
        button.disabled = false;
        button.classList.remove('uploaded', 'btn-success');
        button.classList.add('btn-outline-secondary', 'btn-sm');
        button.style.background = '';
        button.style.color = '';
        button.style.border = '';
        button.style.cursor = 'pointer';
        
        // Set appropriate content based on document type
        if (documentType === 'lab') {
            button.innerHTML = '<i class="fas fa-flask"></i> Lab';
            button.title = 'Lab result upload available';
        } else if (documentType === 'lab_form') {
            button.innerHTML = '<i class="fas fa-file-alt"></i> Lab Form';
            button.title = 'Lab form upload available';
        } else if (documentType === 'retest') {
            button.innerHTML = '<i class="fas fa-redo"></i> Retest';
            button.title = 'Retest upload available';
        } else {
            button.innerHTML = documentType.toUpperCase();
            button.title = `Upload ${documentType.toUpperCase()}`;
        }
        
        // Mark button as file-deleted to prevent UI updates from overriding this state
        button.setAttribute('data-file-deleted', 'true');
        button.setAttribute('data-last-updated', Date.now().toString());
        
        // Re-enable onclick functionality
        if (documentType === 'rfi') {
            button.onclick = function() { uploadRFI(groupId); };
        } else if (documentType === 'invoice') {
            button.onclick = function() { uploadInvoice(groupId); };
        } else if (documentType === 'lab') {
            // For lab buttons, use the inspection ID from the button's data attributes
            const inspectionId = button.getAttribute('data-inspection-id') || button.id.replace('lab-', '');
            button.onclick = function() { uploadLab(inspectionId); };
        } else if (documentType === 'lab_form') {
            button.onclick = function() { uploadLabForm(groupId); };
        } else if (documentType === 'retest') {
            button.onclick = function() { uploadRetest(groupId); };
        }
        
        debugLog(`SUCCESS ${documentType.toUpperCase()} button reset to uploadable state`);
        
        // Also update any buttons in the main table (not just in popup)
        updateMainTableButtons(documentType, groupId, clientName, inspectionDate);
        
    } else {
        debugLog(`⚠️ Button not found: ${buttonId}`);
        debugLog(`DEBUG Available buttons:`, Array.from(document.querySelectorAll('button')).map(b => b.id).filter(id => id.includes(documentType)));
        
        // Store the update for when the popup closes
        if (!window.pendingButtonUpdates) {
            window.pendingButtonUpdates = [];
        }
        window.pendingButtonUpdates.push({
            buttonId: buttonId,
            documentType: documentType,
            groupId: groupId,
            action: 'reset'
        });
        debugLog(`📝 Stored pending update for button: ${buttonId}`);
    }
}

// Function to update buttons in the main table (not just popup)
function updateMainTableButtons(documentType, groupId, clientName, inspectionDate) {
    debugLog(`🔧 Updating main table buttons for ${documentType}...`);
    
    // Find the main table row for this group
    const groupRow = document.querySelector(`tr[data-group-id="${groupId}"]`);
    if (!groupRow) {
        debugLog(`⚠️ Main table row not found for group: ${groupId}`);
        return;
    }
    
    // Find the button in the main table
    const buttonId = `${documentType}-${groupId}`;
    const button = groupRow.querySelector(`#${buttonId}`);
    
    if (button) {
        debugLog(`SUCCESS Found main table button: ${buttonId}`);
        
        // Reset button to default state
        button.disabled = false;
        button.classList.remove('uploaded', 'btn-success');
        button.classList.add('btn-outline-secondary', 'btn-sm');
        button.style.background = '';
        button.style.color = '';
        button.style.border = '';
        button.style.cursor = 'pointer';
        button.innerHTML = documentType.toUpperCase();
        button.title = `Upload ${documentType.toUpperCase()}`;
        
        // Mark button as file-deleted
        button.setAttribute('data-file-deleted', 'true');
        button.setAttribute('data-last-updated', Date.now().toString());
        
        // Re-enable onclick functionality
        if (documentType === 'rfi') {
            button.onclick = function() { uploadRFI(groupId); };
        } else if (documentType === 'invoice') {
            button.onclick = function() { uploadInvoice(groupId); };
        } else if (documentType === 'lab') {
            button.onclick = function() { uploadLab(groupId); };
        } else if (documentType === 'lab_form') {
            button.onclick = function() { uploadLabForm(groupId); };
        } else if (documentType === 'retest') {
            button.onclick = function() { uploadRetest(groupId); };
        }
        
        debugLog(`SUCCESS Main table ${documentType} button reset to uploadable state`);
    } else {
        debugLog(`⚠️ Main table button not found: ${buttonId}`);
    }
}

// updateButtonAfterUpload function removed - we now use markAsUploaded to show username instead

// Download all files for current inspection group as ZIP
async function downloadAllFiles() {
    const downloadBtn = document.getElementById('downloadAllBtn');
    const clientName = window.currentFilesClient;
    const inspectionDate = window.currentFilesDate;
    const groupId = window.currentFilesGroupId;
    
    if (!clientName || !inspectionDate) {
        alert('Error: Missing client or inspection date information');
        return;
    }
    
    // Show loading state
    const originalText = downloadBtn.innerHTML;
    downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating ZIP...';
    downloadBtn.disabled = true;
    
    try {
        debugLog('🗂️ Starting download of all files for ' + clientName + ' on ' + inspectionDate);
        
        const response = await fetch('/inspections/download-all-files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                client_name: clientName,
                inspection_date: inspectionDate,
                group_id: groupId
            })
        });
        
        if (response.ok) {
            // Get the filename from the response headers
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'inspection_files.zip';
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }
            
            // Download the file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            debugLog('SUCCESS Download completed:', filename);
        } else {
            const errorData = await response.json();
            alert('Download failed: ' + (errorData.error || 'Unknown error'));
        }
        
    } catch (error) {
        console.error('Download error:', error);
        alert('Download error: ' + error.message);
    } finally {
        // Restore button state
        downloadBtn.innerHTML = originalText;
        downloadBtn.disabled = false;
    }
}

// Function to update button states based on retest selection
function updateButtonStates(inspectionId, needsRetest) {
    const labButton = document.getElementById('lab-' + inspectionId);
    const labFormButton = document.getElementById('lab-form-' + inspectionId);
    const retestButton = document.getElementById('retest-' + inspectionId);
    const dropdown = document.querySelector('select[data-inspection-id="' + inspectionId + '"]');
    
    // Check if sample was taken
    const isSampleTaken = dropdown && !dropdown.disabled;
    
    // If no sample taken, buttons won't exist in DOM, so nothing to do
    if (!isSampleTaken) {
        debugLog(`No sample taken for inspection ${inspectionId} - buttons not rendered`);
        return;
    }
    
    // Sample taken - buttons should exist, update their states
    if (labButton) {
        labButton.disabled = false;
        labButton.style.opacity = '';
        labButton.style.cursor = '';
        labButton.onclick = function() { uploadLab(inspectionId); };
        labButton.title = 'Lab result upload available';
    }
    
    if (labFormButton) {
        labFormButton.disabled = false;
        labFormButton.style.opacity = '';
        labFormButton.style.cursor = '';
        labFormButton.onclick = function() { uploadLabForm(inspectionId); };
        labFormButton.title = 'Lab form submission upload available';
    }
    
    if (retestButton) {
        // Retest button is enabled ONLY if sample taken AND retest is YES (must upload document)
        if (needsRetest === 'YES') {
            retestButton.disabled = false;
            retestButton.style.opacity = '1';
            retestButton.style.cursor = 'pointer';
            retestButton.onclick = function() { uploadRetest(inspectionId); };
            retestButton.title = 'Retest required - Please upload retest document';
        } else {
            retestButton.disabled = true;
            retestButton.style.opacity = '0.5';
            retestButton.style.cursor = 'not-allowed';
            retestButton.onclick = null;
            retestButton.title = needsRetest === 'NO' ? 'No retest required - Upload disabled' : 'Select retest status first';
        }
    }
}

// Update needs retest function
function updateNeedsRetest(dropdown) {
    const inspectionId = dropdown.getAttribute('data-inspection-id');
    const needsRetest = dropdown.value;
    
    // Check if dropdown is disabled (no sample taken)
    if (dropdown.disabled) {
        return; // Don't allow changes if disabled
    }
    
    // Get CSRF token
    const csrfToken = getCSRFToken();
    
    // Create form data
    const formData = new FormData();
    formData.append('inspection_id', inspectionId);
    formData.append('needs_retest', needsRetest);
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    // Send update request
    fetch('/update-needs-retest/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show instant success feedback
            dropdown.style.backgroundColor = '#d4edda';
            setTimeout(() => {
                dropdown.style.backgroundColor = '';
            }, 100); // Instant feedback
            
            // Update button states immediately for quicker transition
            if (typeof updateButtonStates === 'function') {
                updateButtonStates(inspectionId, needsRetest);
            }
        } else {
            // Revert dropdown state on error
            dropdown.value = '';
            alert('Error updating needs retest: ' + data.error);
        }
    })
    .catch(error => {
        // Revert dropdown state on error
        dropdown.value = '';
        alert('Error updating needs retest: ' + error.message);
    });
}

debugLog('All functions ready: uploadRFI, uploadInvoice, openFilesPopup, expandAll, collapseAll, toggleGroup, updateProductName, updateProductClass, updateLab, loadInspectionFiles, displayFiles, downloadFile, deleteFile, viewFile, downloadAllFiles, updateViewFilesButtonColor, updateAllViewFilesButtonColors, validateUploadButtonStates, updateButtonAfterDeletion, updateNeedsRetest, updateButtonStates');
debugLog('🧪 Debug: Type testFileDisplay() in console to test file display with sample data');

// Function validation - ensure all required functions are available
function validateRequiredFunctions() {
    try {
        const requiredFunctions = [
            'uploadRFI', 'uploadInvoice', 'openFilesPopup', 'expandAll', 'collapseAll', 
            'toggleGroup', 'updateProductName', 'updateProductClass', 'updateLab', 
            'loadInspectionFiles', 'displayFiles', 'downloadFile', 'deleteFile', 
            'viewFile', 'downloadAllFiles', 'updateViewFilesButtonColor', 
            'updateAllViewFilesButtonColors', 'validateUploadButtonStates', 
            'updateButtonAfterDeletion', 'updateNeedsRetest', 'updateButtonStates'
        ];
        
        const missingFunctions = [];
        requiredFunctions.forEach(funcName => {
            if (typeof window[funcName] !== 'function') {
                missingFunctions.push(funcName);
            }
        });
        
        if (missingFunctions.length > 0) {
            console.error('Missing required functions:', missingFunctions);
            return false;
        }
        
        debugLog('SUCCESS All functions validated successfully');
        return true;
    } catch (error) {
        console.error('Error validating functions:', error);
        return false;
    }
}

// Validate functions when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', validateRequiredFunctions);
} else {
    validateRequiredFunctions();
}
