6987// Clean Upload Functions - No Syntax Errors
try {
    console.log('Upload functions JavaScript loaded');
} catch (error) {
    console.error('Error loading upload functions:', error);
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
    console.log('uploadRFI called with groupId:', groupId);
    
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
        
        console.log('File input element created successfully');
        
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
                
                console.log('Uploading file:', file.name, 'for group:', groupId);
                
                // Show loading message
                const originalAlert = alert;
                alert = function(msg) { console.log('Alert:', msg); };
                
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
                        if (data.success) {
                            alert(data.message || 'RFI document uploaded successfully!');
                            console.log('Upload successful:', data);
                            
                            // Update button directly to show username
                            const buttonId = 'rfi-' + groupId;
                            console.log('🔍 Updating RFI button to show username for:', buttonId);
                            
                                // Find and update the button - simplified approach
                                let button = document.getElementById(buttonId);
                                
                                if (button) {
                                    console.log('✅ Found RFI button, updating to green success state');
                                    
                                    // Update button to green success state
                                    button.disabled = true;
                                    button.className = 'btn btn-sm btn-success';
                                    button.style.backgroundColor = '#28a745';
                                    button.style.borderColor = '#28a745';
                                    button.style.cursor = 'not-allowed';
                                    button.innerHTML = 'RFI ✓';
                                    button.title = 'RFI file exists';
                                    
                                    // Remove the onclick handler since button is now disabled
                                    button.onclick = null;
                                    
                                    console.log('✅ Updated RFI button to green success state');
                                    
                                    // Check if View Files popup is open - if so, auto-refresh it
                                    const modal = document.getElementById('filesModal');
                                    if (modal && modal.style.display === 'block') {
                                        console.log('🔄 View Files popup is open - auto-refreshing after RFI upload...');
                                        
                                        // Wait 2 seconds for file to be saved, then refresh the popup
                                        setTimeout(() => {
                                            console.log('🔄 Auto-refreshing View Files popup with new RFI file...');
                                            
                                            // Get the current popup data from the groupId
                                            const dateStr = groupId.match(/\d{8}$/);
                                            if (dateStr) {
                                                const formattedDate = dateStr[0].substring(0,4) + '-' + dateStr[0].substring(4,6) + '-' + dateStr[0].substring(6,8);
                                                const clientName = groupId.replace(/_\d{8}$/, '').replace(/_/g, ' ');
                                                
                                                console.log('🔄 Refreshing files for:', clientName, 'on', formattedDate, 'with groupId:', groupId);
                                                loadInspectionFiles(groupId, clientName, formattedDate);
                                            }
                                        }, 2000);
                                    }
                                } else {
                                    console.log('⚠️ RFI button not found, refreshing page to show updated state');
                                    setTimeout(() => {
                                        window.location.reload();
                                    }, 1000);
                                }
                    } else {
                        alert('Upload failed: ' + (data.error || 'Unknown error'));
                        console.error('Upload failed:', data);
                    }
                })
                .catch(error => {
                    alert = originalAlert; // Restore alert
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
                console.log('File input removed from body');
            }
        }, 100);
        
    } catch (error) {
        console.error('Error in uploadRFI function:', error);
        alert('Error in upload function: ' + error.message);
    }
}

// Upload Invoice function - CLEAN VERSION
function uploadInvoice(groupId) {
    console.log('uploadInvoice called with groupId:', groupId);
    
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
                
                console.log('Uploading invoice:', file.name, 'for group:', groupId);
                
                fetch('/upload-document/', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message || 'Invoice uploaded successfully!');
                        console.log('Invoice upload successful:', data);
                        
                        // Update button directly to green success state
                        const buttonId = 'invoice-' + groupId;
                        console.log('🔍 Updating Invoice button to green success state for:', buttonId);
                        
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
                            console.log('✅ Found Invoice button, updating to green success state');
                            
                            // Update button to green success state
                            button.disabled = true;
                            button.className = 'btn btn-sm btn-success';
                            button.style.backgroundColor = '#28a745';
                            button.style.borderColor = '#28a745';
                            button.style.cursor = 'not-allowed';
                            button.innerHTML = 'Invoice ✓';
                            button.title = 'Invoice file exists';
                            
                            // Remove the onclick handler since button is now disabled
                            button.onclick = null;
                            
                            console.log('✅ Updated Invoice button to green success state');
                            
                            // Check if View Files popup is open - if so, auto-refresh it
                            const modal = document.getElementById('filesModal');
                            if (modal && modal.style.display === 'block') {
                                console.log('🔄 View Files popup is open - auto-refreshing after Invoice upload...');
                                
                                // Wait 2 seconds for file to be saved, then refresh the popup
                                setTimeout(() => {
                                    console.log('🔄 Auto-refreshing View Files popup with new Invoice file...');
                                    
                                    // Get the current popup data from the groupId
                                    const dateStr = groupId.match(/\d{8}$/);
                                    if (dateStr) {
                                        const formattedDate = dateStr[0].substring(0,4) + '-' + dateStr[0].substring(4,6) + '-' + dateStr[0].substring(6,8);
                                        const clientName = groupId.replace(/_\d{8}$/, '').replace(/_/g, ' ');
                                        
                                        console.log('🔄 Refreshing files for:', clientName, 'on', formattedDate, 'with groupId:', groupId);
                                        loadInspectionFiles(groupId, clientName, formattedDate);
                                    }
                                }, 2000);
                            }
                        } else {
                            console.log('⚠️ Invoice button not found, refreshing page to show updated state');
                            setTimeout(() => {
                                window.location.reload();
                            }, 1000);
                        }
                    } else {
                        alert('Invoice upload failed: ' + (data.error || 'Unknown error'));
                        console.error('Invoice upload failed:', data);
                    }
                })
                .catch(error => {
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

// Files Popup function - Enhanced with actual modal and fallback test data
function openFilesPopup(groupId, clientName, inspectionDate) {
    console.log('openFilesPopup called:', { groupId, clientName, inspectionDate });
    
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

    console.log('🔄 File overlay: View Files clicked - Starting files fetch for', clientName, 'on', inspectionDate);

    // Try to load real files first, but show test data if none found
    loadInspectionFilesWithFallback(groupId, clientName, inspectionDate);
}

// Close files popup function
function closeFilesPopup() {
    console.log('closeFilesPopup called');
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
        console.log(`🔄 Popup closed - skipping inspection refresh to prevent button reset`);
        console.log(`🔍 Group ID: ${window.currentFilesGroupId}`);
        
        // Skip refresh to prevent button reset loop
        console.log('🔄 Skipping inspection refresh to prevent button reset loop');
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
        console.log('🔄 File fetch: Starting direct file fetch (using working method)...');
        
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
                console.log('Could not parse client name as JSON, using as-is:', cleanClientName);
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
                console.log('Could not parse date as JSON, using as-is:', cleanDate);
            }
        }
        
        console.log('🔄 Original client name:', clientName);
        console.log('🔄 Cleaned client name:', cleanClientName);
        console.log('🔄 Original date:', inspectionDate);
        console.log('🔄 Cleaned date:', cleanDate);
        
        // Use the working method directly with cache-busting
        const cacheBuster = Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const response = await fetch('/inspections/files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            body: JSON.stringify({
                group_id: groupId,
                client_name: cleanClientName,
                inspection_date: cleanDate,
                _cache_bust: cacheBuster
            })
        });
        
        const result = await response.json();
        console.log('🔄 File fetch: File fetch completed:', result.success);
        console.log('🔄 File fetch: Full server response:', result);
        
        const filesLoading = document.getElementById('filesLoading');
        const filesContent = document.getElementById('filesContent');
        const filesList = document.getElementById('filesList');
        
        if (filesLoading) filesLoading.style.display = 'none';
        if (filesContent) filesContent.style.display = 'block';
        
        if (result.success && result.files && filesList) {
            console.log('🔍 Server returned files object:', result.files);
            console.log('🔍 Files object keys:', Object.keys(result.files));
            console.log('🔍 Files object values:', Object.values(result.files));
            
            const hasFiles = Object.values(result.files).some(fileList => fileList && fileList.length > 0);
            console.log('🔍 Has files check result:', hasFiles);
            
            if (hasFiles) {
                console.log('✅ Files found and displaying');
                displayFiles(result.files, result.message);
            } else {
                console.log('📁 No files found - showing empty message');
                const filesList = document.getElementById('filesList');
                if (filesList) {
                    filesList.innerHTML = '<div class="empty-category">📂 No files found for this inspection.</div>';
                }
            }
        } else if (filesList) {
            console.log('❌ Server returned error');
            const filesList = document.getElementById('filesList');
            if (filesList) {
                filesList.innerHTML = '<div class="empty-category">❌ Error loading files. Please try again.</div>';
            }
        }
        
    } catch (error) {
        console.log('❌ File fetch error:', error);
        const filesList = document.getElementById('filesList');
        if (filesList) {
            filesList.innerHTML = '<div class="empty-category">❌ Network error. Please try again.</div>';
        }
    }
}

// Show no files message when no real files are available
function showTestFiles(clientName, inspectionDate, serverMessage) {
    const filesList = document.getElementById('filesList');
    if (filesList) {
        let message = serverMessage || 'No files found for this inspection.';
        filesList.innerHTML = `<div class="empty-category">📂 ${message}</div>`;
    }
}

// Load inspection files function (original)
async function loadInspectionFiles(groupId, clientName, inspectionDate) {
    try {
        console.log('🔄 File fetch: Starting file fetch request...');
        
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
                inspection_date: cleanDate
            })
        });
        
        const result = await response.json();
        console.log('🔄 File fetch: File fetch completed:', result.success);
        console.log('🔄 File fetch: Full server response:', result);
        console.log('🔄 File fetch: Response text length:', JSON.stringify(result).length);
        console.log('🔄 File fetch: Files data:', result.files);
        console.log('🔄 File fetch: Message:', result.message);
        
        const filesLoading = document.getElementById('filesLoading');
        const filesContent = document.getElementById('filesContent');
        const filesList = document.getElementById('filesList');
        
        if (filesLoading) filesLoading.style.display = 'none';
        if (filesContent) filesContent.style.display = 'block';
        
        if (result.success && filesList) {
            console.log('✅ Calling displayFiles with success response');
            displayFiles(result.files, result.message);
        } else if (filesList) {
            console.log('❌ Server returned error or no success flag');
            filesList.innerHTML = '<div class="empty-category">Error loading files: ' + (result.error || result.message || 'Unknown error') + '</div>';
        }
        
    } catch (error) {
        const filesLoading = document.getElementById('filesLoading');
        const filesContent = document.getElementById('filesContent');
        const filesList = document.getElementById('filesList');
        
        console.log('❌ File fetch: File fetch error:', error);
        
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
    
    console.log('📁 displayFiles called with:', { files, message, isTestData });
    
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
        html += '<div class="empty-category">📂 No files found for this inspection.</div>';
    } else {
        html += '<div class="files-grid">';
        let totalFiles = 0;
        
        // Display files by category
        for (const [category, fileList] of Object.entries(files)) {
            console.log(`📁 Processing category: ${category}`, fileList);
            
            if (fileList && Array.isArray(fileList) && fileList.length > 0) {
                totalFiles += fileList.length;
                html += `<div class="file-category" style="margin-bottom: 1rem; border: 1px solid #dee2e6; border-radius: 4px; padding: 1rem;">
                    <h4 style="color: #495057; margin-bottom: 0.5rem; display: flex; align-items: center;">
                        <i class="fas fa-folder" style="margin-right: 0.5rem; color: #6c757d;"></i>
                        ${category} (${fileList.length})
                    </h4>
                    <div class="file-list">`;
                
                fileList.forEach((file, index) => {
                    console.log(`📄 File ${index}:`, file);
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
            html += '<div class="empty-category">📂 All categories are empty.</div>';
        } else if (isTestData) {
            html += `<div style="margin-top: 1rem; padding: 0.75rem; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; color: #856404;">
                <i class="fas fa-lightbulb" style="margin-right: 0.5rem;"></i>
                <strong>💡 Tip:</strong> Upload real files using the RFI button to see actual downloadable documents here.
            </div>`;
        }
        
        html += '</div>';
    }
    
    filesList.innerHTML = html;
    console.log('📁 displayFiles completed, HTML length:', html.length);
}

// Download individual file function
function downloadFile(filePath) {
    console.log('Downloading file:', filePath);
    if (filePath.startsWith('/test/')) {
        alert('This is a test file and cannot be downloaded. Upload real files using the RFI button to enable downloads.');
        return;
    }
    
    // Clean the file path - remove /media/ prefix if present
    let cleanFilePath = filePath;
    if (cleanFilePath.startsWith('/media/')) {
        cleanFilePath = cleanFilePath.substring(7); // Remove '/media/'
    }
    
    console.log('Download - Original path:', filePath);
    console.log('Download - Clean path:', cleanFilePath);
    
    // Use fetch to download and create blob for proper download behavior
    const downloadUrl = '/inspections/download-file/?file=' + encodeURIComponent(cleanFilePath);
    
    console.log('Initiating download from:', downloadUrl);
    
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
            
            console.log('Download completed for:', cleanFilePath);
        })
        .catch(error => {
            console.error('Download error:', error);
            alert('Download failed: ' + error.message);
        });
}

// Delete file function - Only compliance documents are protected from deletion
async function deleteFile(filePath, fileName) {
    console.log('Deleting file:', filePath, fileName);
    
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
        
        if (!clientName || !inspectionDate) {
            alert('Error: Missing client or inspection date information');
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
        
        console.log('Delete parameters:', {
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
            console.log('File deleted:', fileName);
            
            // Determine document type from file path
            let documentType = 'unknown';
            if (filePath.includes('/rfi/')) {
                documentType = 'rfi';
            } else if (filePath.includes('/invoice/')) {
                documentType = 'invoice';
            }
            
            // IMMEDIATE UI UPDATE: Remove the file from the current display
            console.log('🔄 Immediately removing file from UI before server refresh...');
            const fileElements = document.querySelectorAll(`[data-file-path*="${fileName}"]`);
            fileElements.forEach(element => {
                const fileContainer = element.closest('.file-item') || element.closest('.file-entry');
                if (fileContainer) {
                    fileContainer.style.opacity = '0.3';
                    fileContainer.innerHTML = `<div class="file-deleted">📄 ${fileName} - Deleted</div>`;
                }
            });
            
            // Clear any client-side file cache
            console.log('🧹 Clearing client-side file cache...');
            if (window.fileCache) {
                const cacheKey = `${clientName}_${inspectionDate}`;
                delete window.fileCache[cacheKey];
                console.log(`🧹 Cleared cache for key: ${cacheKey}`);
            }
            
            // Clear localStorage cache if it exists
            const cacheKeys = Object.keys(localStorage).filter(key => 
                key.includes('files_') && 
                key.includes(clientName.replace(/\s+/g, '_')) && 
                key.includes(inspectionDate)
            );
            cacheKeys.forEach(key => {
                localStorage.removeItem(key);
                console.log(`🧹 Cleared localStorage key: ${key}`);
            });
            
            // Update the corresponding button immediately
            if (documentType !== 'unknown') {
                console.log(`🔧 Calling updateButtonAfterDeletion for ${documentType} with client: ${clientName}, date: ${inspectionDate}`);
                updateButtonAfterDeletion(clientName, inspectionDate, documentType);
            }
            
            // Refresh the files list with a delay to ensure server-side cleanup is complete
            const groupId = window.currentFilesGroupId;
            if (groupId && clientName && inspectionDate) {
                console.log('🔄 Scheduling fresh file list reload...');
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
                        
                        console.log(`✅ Permanently reset ${documentType} button for ${clientName} - marked as file-deleted`);
                    }
                } else {
                    // Update button colors after file deletion for other document types
                    setTimeout(() => {
                        console.log('🎨 Updating button colors after file deletion...');
                        updateAllViewFilesButtonColors();
                    }, 500);
                    
                    // Update UI dynamically instead of reloading page
                    setTimeout(() => {
                        console.log('🔄 Updating UI to show updated button states...');
                        updateAllViewFilesButtonColors();
                    }, 1000);
                }
            }
        } else {
            // Handle "File not found" as a special case - file was already deleted
            if (result.error && result.error.includes('File not found')) {
                console.log('File already deleted from server, updating UI...');
                
                // Determine document type from file path
                let documentType = 'unknown';
                if (filePath.includes('/rfi/')) {
                    documentType = 'rfi';
                } else if (filePath.includes('/invoice/')) {
                    documentType = 'invoice';
                }
                
                // Update the corresponding button immediately
                if (documentType !== 'unknown') {
                    console.log(`🔧 Calling updateButtonAfterDeletion for ${documentType} with client: ${clientName}, date: ${inspectionDate}`);
                    updateButtonAfterDeletion(clientName, inspectionDate, documentType);
                }
                
                // Clear any cached file data for this client/date
                console.log('🧹 Clearing file cache for updated state...');
                
                // Refresh the files list to show updated state
                const groupId = window.currentFilesGroupId;
                if (groupId && clientName && inspectionDate) {
                    console.log('🔄 Refreshing View Files popup to show updated file count');
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
    console.log('Viewing file:', filePath, fileName);
    
    if (filePath.startsWith('/test/')) {
        alert('This is a test file. In a real system, this would open a document viewer or download the file for viewing.');
        return;
    }
    
    // Clean the file path - remove /media/ prefix if present
    let cleanFilePath = filePath;
    if (cleanFilePath.startsWith('/media/')) {
        cleanFilePath = cleanFilePath.substring(7); // Remove '/media/'
    }
    
    console.log('View - Original path:', filePath);
    console.log('View - Clean path:', cleanFilePath);
    
    // For viewing, use the media URL directly (not the download endpoint)
    // This bypasses the Content-Disposition: attachment header
    const viewUrl = '/media/' + cleanFilePath;
    
    console.log('Opening for viewing:', viewUrl);
    
    // Open file in new tab for inline viewing
    window.open(viewUrl, '_blank');
}

// Expand/Collapse functionality
function expandAll() {
    console.log('expandAll called');
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
    
    console.log('Expanded', detailRows.length, 'detail rows');
}

function collapseAll() {
    console.log('collapseAll called');
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
    
    console.log('Collapsed', detailRows.length, 'detail rows');
}

// Toggle individual group function
function toggleGroup(e, groupId) {
    console.log('toggleGroup called for groupId:', groupId);
    
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    const detailRow = document.getElementById('detail-' + groupId);
    console.log('Detail row found:', detailRow);

    if (!detailRow) {
        console.warn('No detail row for groupId:', groupId);
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
        console.log('Expanded group:', groupId);
    } else {
        // Collapse
        detailRow.style.display = 'none';
        if (expandBtn) expandBtn.classList.remove('expanded');
        if (icon) {
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-right');
        }
        console.log('Collapsed group:', groupId);
    }
}

// Set up event delegation for expand buttons when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Setting up expand button event delegation...');
    
    // Debug: Check what elements exist
    const expandBtns = document.querySelectorAll('.expand-btn');
    const detailRows = document.querySelectorAll('.detail-row');
    console.log('Found expand buttons:', expandBtns.length);
    console.log('Found detail rows:', detailRows.length);
    
    // List all expand buttons and their group IDs
    expandBtns.forEach((btn, index) => {
        const groupId = btn.getAttribute('data-group-id');
        console.log(`Expand button ${index + 1}: group-id="${groupId}"`);
    });
    
    // List all detail rows and their IDs
    detailRows.forEach((row, index) => {
        console.log(`Detail row ${index + 1}: id="${row.id}"`);
    });
    
    // Event delegation for expand buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.expand-btn')) {
            e.preventDefault();
            e.stopPropagation();
            const button = e.target.closest('.expand-btn');
            const groupId = button.getAttribute('data-group-id');
            console.log('🔧 Expand button clicked for group:', groupId);
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
    
    console.log('Event delegation set up for expand buttons and modal');
    
    // Start automatic color updates for View Files buttons - PAGE SPECIFIC
    console.log('🎨 [PAGE] Starting compliance document check for current page only...');
    
    // Check immediately for current page
    setTimeout(() => {
        console.log('🎨 [PAGE] Initial compliance check for visible rows...');
        updateAllViewFilesButtonColors();
    }, 1000);
    
    // Final check after everything loads
    setTimeout(() => {
        console.log('🔄 [PAGE] Final compliance check for visible rows...');
        updateAllViewFilesButtonColors();
    }, 2000);
    
    // Validate upload button states against actual files
    // DISABLED: This was overriding template logic and causing incorrect button states
    // The template correctly shows uploader names based on database state
    /*
    setTimeout(() => {
        console.log('🔍 [PAGE] Validating upload button states...');
        validateUploadButtonStates();
    }, 3000);
    */
    
    // Set up pagination detection for automatic color updates on page changes
    const paginationLinks = document.querySelectorAll('.pagination a, a[href*="page="]');
    console.log('🔗 [PAGE] Found ' + paginationLinks.length + ' pagination links');
    
    paginationLinks.forEach(link => {
        link.addEventListener('click', function() {
            console.log('🔗 [PAGE] Pagination clicked, will check new page after load...');
            
            // Check for new page content after navigation
            setTimeout(() => {
                console.log('🎨 [PAGE] Checking compliance for new page after navigation...');
                updateAllViewFilesButtonColors();
            }, 1500);
        });
    });
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
    console.log('updateProductName called');
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
    console.log('updateProductClass called');
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
    console.log('updateLab called');
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
    console.log('🧪 Testing file display with sample data...');
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
    console.log('🧪 Testing Canonbury Files directly...');
    
    try {
        const response = await fetch('/list-uploaded-files/?group_id=Canonbury_Eggs_20250912');
        const data = await response.json();
        
        console.log('📊 Server Response:', data);
        
        if (data.success) {
            const files = data.files;
            console.log('📁 Files object:', files);
            
            for (const [category, fileList] of Object.entries(files)) {
                console.log(`📂 ${category}: ${fileList.length} files`);
                if (fileList.length > 0) {
                    fileList.forEach(file => {
                        console.log(`  📄 ${file.filename} (${file.size} bytes)`);
                    });
                }
            }
            
            // Test the displayFiles function directly
            console.log('🎨 Testing displayFiles function...');
            displayFiles(files, 'Direct test - files loaded successfully');
            
        } else {
            console.error('❌ Server error:', data.error);
        }
    } catch (error) {
        console.error('❌ Network error:', error);
    }
};

// ZIP File Viewer
async function viewZipContents(filePath, fileName) {
    console.log('🗂️ Viewing ZIP contents:', filePath, fileName);
    
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
            console.log('✅ JSZip library loaded successfully');
            resolve();
        };
        script.onerror = () => {
            console.error('❌ Failed to load JSZip library');
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
    console.log('🗂️ Extracting and organizing ZIP:', fileName);
    
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
        alert(`✅ Successfully extracted and organized ${totalFiles} files!\n\n- ${window.currentZipAnalysis.matchedFiles.length} files placed in individual inspection folders\n- ${window.currentZipAnalysis.unmatchedFiles.length} files placed in general compliance folder`);
        
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
    
    console.log(`✅ Uploaded ${fileName} to inspection ${inspectionNumber}`);
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
    
    console.log(`✅ Uploaded ${fileName} to general compliance folder`);
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
    console.log('🎨 Updating button color for client: "' + clientName + '"');
    console.log('   File status: ' + fileStatus);
    
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
    
    console.log('   Found ' + buttons.length + ' View Files buttons for "' + clientName + '"');
    
    buttons.forEach((button, index) => {
        if (button.textContent.includes('View Files') || button.textContent.includes('Files')) {
            console.log('   Button ' + (index + 1) + ': "' + button.textContent.trim() + '"');
            // Remove existing color classes
            button.classList.remove('btn-view-files-green', 'btn-view-files-red', 'btn-view-files-blue', 'btn-view-files-orange');
            
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
                    console.log('   ✅ Applied GREEN color to button');
                    break;
                case 'compliance_only':
                    button.classList.add('btn-view-files-orange');
                    button.title = 'Only compliance documents available';
                    if (statusIcon) {
                        statusIcon.className = 'fas fa-shield-alt';
                        statusIcon.style.color = '#f59e0b';
                    }
                    console.log('   🟡 Applied ORANGE color to button');
                    break;
                case 'partial_files':
                    button.classList.add('btn-view-files-blue');
                    button.title = 'Some files available (RFI, Invoice, Lab) but no compliance documents';
                    if (statusIcon) {
                        statusIcon.className = 'fas fa-file-alt';
                        statusIcon.style.color = '#3b82f6';
                    }
                    console.log('   🔵 Applied BLUE color to button');
                    break;
                case 'no_files':
                    button.classList.add('btn-view-files-red');
                    button.title = 'No files found';
                    if (statusIcon) {
                        statusIcon.className = 'fas fa-times-circle';
                        statusIcon.style.color = '#dc2626';
                    }
                    console.log('   🔴 Applied RED color to button');
                    break;
                default:
                    // Default blue color for unknown status
                    button.classList.add('btn-view-files-blue');
                    button.title = 'Click to check files';
                    if (statusIcon) {
                        statusIcon.className = 'fas fa-sync fa-spin';
                        statusIcon.style.color = '#6b7280';
                    }
                    console.log('   🔄 Applied default color to button');
                    break;
            }
        }
    });
}

// Update View Files button color for a specific client and inspection date
function updateViewFilesButtonColorSpecific(clientName, inspectionDate, fileStatus) {
    console.log('🎨 Updating button color for specific client+date: "' + clientName + '" on ' + inspectionDate);
    console.log('   File status: ' + fileStatus);
    
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
    
    console.log('   Found ' + buttons.length + ' View Files buttons for "' + clientName + '" on ' + inspectionDate);
    
    buttons.forEach((button, index) => {
        if (button.textContent.includes('View Files') || button.textContent.includes('Files')) {
            console.log('   Button ' + (index + 1) + ': "' + button.textContent.trim() + '"');
            
            // Remove existing color classes
            button.classList.remove('btn-success', 'btn-warning', 'btn-info', 'btn-danger');
            
            // Apply color based on file status
            switch (fileStatus) {
                case 'all_files':
                    button.classList.add('btn-success');
                    button.style.backgroundColor = '#28a745';
                    button.style.color = 'white';
                    button.title = 'All files available (RFI, Invoice, Lab, Compliance)';
                    console.log('   🟢 Applied GREEN color to button');
                    break;
                case 'compliance_only':
                    button.classList.add('btn-warning');
                    button.style.backgroundColor = '#ffc107';
                    button.style.color = 'black';
                    button.title = 'Only compliance documents available';
                    console.log('   🟠 Applied ORANGE color to button');
                    break;
                case 'partial_files':
                    button.classList.add('btn-info');
                    button.style.backgroundColor = '#17a2b8';
                    button.style.color = 'white';
                    button.title = 'Some files available (RFI, Invoice, Lab) but no compliance documents';
                    console.log('   🔵 Applied BLUE color to button');
                    break;
                case 'no_files':
                    button.classList.add('btn-danger');
                    button.style.backgroundColor = '#dc3545';
                    button.style.color = 'white';
                    button.title = 'No files available';
                    console.log('   🔴 Applied RED color to button');
                    break;
                default:
                    button.style.backgroundColor = '#6c757d';
                    button.style.color = 'white';
                    button.title = 'Unknown file status';
                    console.log('   🔄 Applied default color to button');
                    break;
            }
        }
    });
}

// Check file status for all clients and update button colors
let statusCheckInProgress = false;

async function updateAllViewFilesButtonColors() {
    // Prevent multiple simultaneous requests
    if (statusCheckInProgress) {
        console.log('⏳ [FRONTEND] Status check already in progress, skipping...');
        return;
    }
    
    statusCheckInProgress = true;
    console.log('🎨 [FRONTEND] Starting automatic View Files button color update...');
    
    try {
        const clientDateCombinations = getCurrentPageClientData();
        
        if (clientDateCombinations.length === 0) {
            console.log('📄 No client+date combinations found on current page for color update');
            return;
        }
        
        // Limit to reasonable number of combinations
        if (clientDateCombinations.length > 50) {
            console.log('⚠️ [FRONTEND] Too many combinations on page, limiting to first 50');
            clientDateCombinations.splice(50);
        }
        
        console.log('🔄 [FRONTEND] Checking file status for ' + clientDateCombinations.length + ' client+date combinations...');
        
        const response = await fetch('/page-clients-status/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                client_date_combinations: clientDateCombinations
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ Received file status data for all client+date combinations');
            
            // Update button colors for each client+date combination
            Object.entries(result.combination_statuses).forEach(([uniqueKey, statusData]) => {
                console.log('🎨 Updating colors for ' + uniqueKey + ': ' + statusData.file_status);
                updateViewFilesButtonColorSpecific(statusData.client_name, statusData.inspection_date, statusData.file_status);
            });
            
            console.log('🎨 Completed automatic color update for all buttons');
        } else {
            console.error('❌ Error getting file status:', result.error);
        }
        
    } catch (error) {
        console.error('❌ Error updating View Files button colors:', error);
    } finally {
        statusCheckInProgress = false;
    }
}

// Get current page client data for color updates - ONLY VISIBLE ROWS
function getCurrentPageClientData() {
    const clientDateCombinations = [];
    
    // Only get rows that are actually visible on the current page
    const visibleShipmentRows = document.querySelectorAll('tbody .shipment-row[data-client-name]:not([style*="display: none"])');
    
    console.log('🔍 [PAGE] Scanning visible rows on current page...');
    console.log('🔍 [PAGE] Found ' + visibleShipmentRows.length + ' visible shipment rows');
    
    visibleShipmentRows.forEach((row, index) => {
        const clientName = row.getAttribute('data-client-name');
        const inspectionDate = row.getAttribute('data-inspection-date');
        
        console.log(`🔍 [PAGE] Row ${index + 1}: "${clientName}" on ${inspectionDate}`);
        
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
    
    console.log('📄 [PAGE] Final result: ' + clientDateCombinations.length + ' unique client+date combinations on current visible page');
    console.log('📄 [PAGE] Combinations: ' + clientDateCombinations.map(c => c.unique_key).join(', '));
    
    return clientDateCombinations;
}

// Function to check if upload buttons should be enabled/disabled based on actual files
function validateUploadButtonStates() {
    console.log('🔍 Validating upload button states against actual files...');
    
    // Get all RFI and Invoice buttons
    const rfiButtons = document.querySelectorAll('button[id^="rfi-"]');
    const invoiceButtons = document.querySelectorAll('button[id^="invoice-"]');
    
    console.log(`Found ${rfiButtons.length} RFI buttons and ${invoiceButtons.length} Invoice buttons`);
    
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

// Check if files actually exist for a specific button
async function checkButtonFileStatus(button, groupId, clientName, inspectionDate, documentType) {
    // Skip checking if this button has been marked as file-deleted to prevent reversion
    if (button.getAttribute('data-file-deleted') === 'true') {
        console.log(`⏭️ Skipping file status check for ${documentType} button - marked as file-deleted`);
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
                console.log(`🔧 Fixing ${documentType} button for ${clientName} - no actual files found`);
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
                console.log(`🔧 ${documentType} files exist for ${clientName} but button not showing as uploaded`);
                
                // Check if there's upload tracking in the database
                // If no upload tracking, keep button as uploadable (this is correct)
                // If there is upload tracking, update button to show uploader
                console.log(`🔧 Keeping ${documentType} button as uploadable for ${clientName} - no upload tracking found`);
            }
        }
        
    } catch (error) {
        console.error(`Error checking ${documentType} files for ${clientName}:`, error);
    }
}

// Update button state after file deletion
function updateButtonAfterDeletion(clientName, inspectionDate, documentType) {
    console.log(`🔄 Updating ${documentType} button after deletion for ${clientName}`);
    
    // Use the current group ID from the popup context
    const groupId = window.currentFilesGroupId;
    if (!groupId) {
        console.log(`⚠️ No group ID available for button update`);
        return;
    }
    
    const buttonId = `${documentType}-${groupId}`;
    console.log(`🔍 Looking for button with ID: ${buttonId}`);
    
    // Try multiple methods to find the button
    let button = null;
    
    // Method 1: Direct ID lookup
    button = document.getElementById(buttonId);
    if (button) {
        console.log(`✅ Found button by direct ID: ${buttonId}`);
    } else {
        // Method 2: Search all buttons with pattern
        console.log(`🔍 Button not found by ID, searching by pattern...`);
        const allButtons = document.querySelectorAll(`button[id^="${documentType}-"]`);
        console.log(`🔍 Found ${allButtons.length} buttons with pattern "${documentType}-"`);
        
        for (let btn of allButtons) {
            if (btn.id === buttonId) {
                button = btn;
                console.log(`✅ Found button by pattern search: ${btn.id}`);
                break;
            }
        }
    }
    
    // Method 3: Search in all tables and modals
    if (!button) {
        console.log(`🔍 Button still not found, searching in all containers...`);
        const containers = document.querySelectorAll('table, .modal, .popup, [id*="detail"]');
        for (let container of containers) {
            const foundButton = container.querySelector(`#${buttonId}`);
            if (foundButton) {
                button = foundButton;
                console.log(`✅ Found button in container: ${container.tagName} ${container.className || container.id}`);
                break;
            }
        }
    }
    
    // Method 4: Search by data attributes
    if (!button) {
        console.log(`🔍 Searching by data attributes...`);
        const buttonsWithData = document.querySelectorAll(`button[data-client-name="${clientName}"], button[data-inspection-date*="${inspectionDate}"]`);
        for (let btn of buttonsWithData) {
            if (btn.id.includes(documentType) && btn.id.includes(groupId.split('_')[0])) {
                button = btn;
                console.log(`✅ Found button by data attributes: ${btn.id}`);
                break;
            }
        }
    }
    
    if (button) {
        console.log(`✅ Found ${documentType} button: ${buttonId}`);
            
            // Reset button to uploadable state
            button.disabled = false;
        button.classList.remove('uploaded');
        button.classList.add(`btn-${documentType}`, 'btn-sm');
            button.style.background = '#28a745';
            button.style.color = 'white';
            button.style.cursor = 'pointer';
        button.innerHTML = documentType.toUpperCase();
            button.title = `Upload ${documentType.toUpperCase()}`;
            
            // Mark button as file-deleted to prevent UI updates from overriding this state
            button.setAttribute('data-file-deleted', 'true');
            
            // Re-enable onclick functionality
            if (documentType === 'rfi') {
                button.onclick = function() { uploadRFI(groupId); };
            } else if (documentType === 'invoice') {
                button.onclick = function() { uploadInvoice(groupId); };
            }
            
        console.log(`✅ ${documentType.toUpperCase()} button reset to uploadable state for ${clientName}`);
    } else {
        console.log(`⚠️ Button still not found: ${buttonId}`);
        console.log(`🔍 Available buttons:`, Array.from(document.querySelectorAll('button')).map(b => b.id).filter(id => id.includes(documentType)));
        
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
        console.log(`📝 Stored pending button update for when popup closes`);
    }
    
    // Clear localStorage for this button
    const uploadStatus = JSON.parse(localStorage.getItem('uploadStatus') || '{}');
    delete uploadStatus[buttonId];
    localStorage.setItem('uploadStatus', JSON.stringify(uploadStatus));
    
    // Force refresh the View Files popup to show updated file count
    if (window.currentFilesClient && window.currentFilesDate) {
        console.log(`🔄 Refreshing View Files popup to show updated file count`);
        setTimeout(() => {
            openFilesPopup(groupId, window.currentFilesClient, window.currentFilesDate);
        }, 500);
    }
}

// Refresh inspection data for a specific inspection (like page refresh but targeted)
async function refreshInspectionData(groupId, clientName, inspectionDate) {
    try {
        console.log(`🔄 Refreshing inspection data for: ${clientName} on ${inspectionDate}`);
        
        // Clean the client name and date
        const cleanClientName = clientName.replace(/[^a-zA-Z0-9\s]/g, '').trim();
        const cleanDate = inspectionDate.replace(/[^0-9-]/g, '').replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
        
        console.log(`🔍 Cleaned client name: ${cleanClientName}, Cleaned date: ${cleanDate}`);
        
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
            console.error('❌ Failed to refresh inspection files:', response.status);
            return;
        }
        
        const data = await response.json();
        console.log(`🔄 Fresh inspection data received:`, data);
        
        if (data.success && data.files) {
            const rfiFiles = data.files.rfi || [];
            const invoiceFiles = data.files.invoice || [];
            
            console.log(`🔄 Found ${rfiFiles.length} RFI files and ${invoiceFiles.length} Invoice files`);
            
            // Update RFI button based on file count
            await updateButtonForInspection(groupId, 'rfi', rfiFiles.length > 0, clientName);
            
            // Update Invoice button based on file count
            await updateButtonForInspection(groupId, 'invoice', invoiceFiles.length > 0, clientName);
            
            console.log(`✅ Inspection data refreshed for ${clientName}`);
        }
    } catch (error) {
        console.error('❌ Error refreshing inspection data:', error);
    }
}

// Update a specific button for an inspection based on file existence
async function updateButtonForInspection(groupId, buttonType, hasFiles, clientName) {
    const buttonId = `${buttonType}-${groupId}`;
    console.log(`🔄 Updating ${buttonType} button: ${buttonId}, hasFiles: ${hasFiles}`);
    
    // Try multiple methods to find the button with retries
    let button = null;
    let attempts = 0;
    const maxAttempts = 3;
    
    while (!button && attempts < maxAttempts) {
        attempts++;
        console.log(`🔍 Attempt ${attempts} to find ${buttonType} button: ${buttonId}`);
        
        // Method 1: Direct ID search
        button = document.getElementById(buttonId);
        if (button) {
            console.log(`✅ Found ${buttonType} button by direct ID on attempt ${attempts}`);
            break;
        }
        
        // Method 2: Search all buttons by ID
        const allButtons = Array.from(document.querySelectorAll('button'));
        button = allButtons.find(b => b.id === buttonId);
        if (button) {
            console.log(`✅ Found ${buttonType} button by searching all buttons on attempt ${attempts}`);
            break;
        }
        
        // Method 3: Search by group ID and button type
        button = allButtons.find(b => 
            b.id.includes(groupId) && 
            (b.id.includes(buttonType) || b.innerHTML.toLowerCase().includes(buttonType))
        );
        if (button) {
            console.log(`✅ Found ${buttonType} button by group ID pattern on attempt ${attempts}`);
            break;
        }
        
        // Method 4: Search for buttons showing "Developer" (if it's the RFI button)
        if (buttonType === 'rfi') {
            button = allButtons.find(b => 
                b.innerHTML.toLowerCase().includes('developer') && 
                b.id.includes(groupId)
            );
            if (button) {
                console.log(`✅ Found ${buttonType} button by Developer text search on attempt ${attempts}`);
                break;
            }
        }
        
        // Method 5: Search for any button with the group ID
        button = allButtons.find(b => b.id.includes(groupId));
        if (button) {
            console.log(`✅ Found button with group ID on attempt ${attempts}: ${button.id}`);
            // Check if this might be the right button type
            if (button.id.includes(buttonType) || button.innerHTML.toLowerCase().includes(buttonType)) {
                console.log(`✅ This appears to be the ${buttonType} button`);
                break;
            } else {
                console.log(`⚠️ Found group button but not ${buttonType} type: ${button.id}`);
                button = null; // Continue searching
            }
        }
        
        if (!button && attempts < maxAttempts) {
            console.log(`⏳ Button not found on attempt ${attempts}, waiting 500ms before retry...`);
            // Wait before next attempt
            await new Promise(resolve => setTimeout(resolve, 500));
        }
    }
    
    if (button) {
        console.log(`✅ Found ${buttonType} button: ${button.id}`);
        
        if (hasFiles) {
            // Files exist - button should show uploader's name (or stay as is if already showing name)
            console.log(`🔍 Button current innerHTML: "${button.innerHTML}", expected: "${buttonType.toUpperCase()}"`);
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
                console.log(`✅ Updated ${buttonType} button to show uploaded state`);
            } else {
                console.log(`ℹ️ ${buttonType} button already shows uploader name: "${button.innerHTML}"`);
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
            
            console.log(`✅ Reset ${buttonType} button to uploadable state`);
        }
    } else {
        console.log(`⚠️ ${buttonType} button not found: ${buttonId}`);
        
        // Enhanced debugging - show all available buttons
        const allButtons = Array.from(document.querySelectorAll('button'));
        console.log(`🔍 All available buttons:`, allButtons.map(b => ({
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
            console.log(`🔍 Buttons in shipments table:`, tableButtons.map(b => ({
                id: b.id,
                text: b.innerHTML.trim(),
                classes: b.className,
                disabled: b.disabled
            })));
        } else {
            console.log(`⚠️ Shipments table not found`);
        }
        
        // Look for buttons with similar IDs
        const similarButtons = allButtons.filter(b => 
            b.id.includes(groupId) || 
            b.id.includes(buttonType) ||
            b.innerHTML.toLowerCase().includes(buttonType)
        );
        console.log(`🔍 Similar buttons found:`, similarButtons.map(b => ({
            id: b.id,
            text: b.innerHTML.trim(),
            classes: b.className
        })));
        
        // Look specifically for any RFI buttons
        const rfiButtons = allButtons.filter(b => b.id.toLowerCase().includes('rfi'));
        console.log(`🔍 All RFI buttons found:`, rfiButtons.map(b => ({
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
        console.log(`🔍 Checking RFI status for specific inspection: ${clientName} on ${inspectionDate}`);
        
        // Clean the client name and date
        const cleanClientName = clientName.replace(/[^a-zA-Z0-9\s]/g, '').trim();
        const cleanDate = inspectionDate.replace(/[^0-9-]/g, '').replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
        
        console.log(`🔍 Cleaned client name: ${cleanClientName}, Cleaned date: ${cleanDate}`);
        
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
            console.error('❌ Failed to check inspection files:', response.status);
            return;
        }
        
        const data = await response.json();
        console.log(`🔍 File check response for ${clientName}:`, data);
        console.log(`🔍 Full API response:`, JSON.stringify(data, null, 2));
        
        if (data.success && data.files) {
            const rfiFiles = data.files.rfi || [];
            console.log(`🔍 Found ${rfiFiles.length} RFI files for ${clientName}`);
            console.log(`🔍 RFI files:`, rfiFiles);
            console.log(`🔍 All files object:`, data.files);
            
            // Find the RFI button for this specific inspection
            const buttonId = `rfi-${groupId}`;
            console.log(`🔍 Looking for RFI button with ID: ${buttonId}`);
            const button = document.getElementById(buttonId);
            
            if (button) {
                console.log(`✅ Found RFI button: ${buttonId}`);
                console.log(`🔍 Current button state - disabled: ${button.disabled}, innerHTML: "${button.innerHTML}"`);
                
                if (rfiFiles.length === 0) {
                    // No RFI files - reset button to "RFI"
                    console.log(`🔄 No RFI files found - resetting button to "RFI" for ${clientName}`);
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
                    
                    console.log(`✅ Reset RFI button to "RFI" for ${clientName}`);
                    console.log(`🔍 Button after reset - disabled: ${button.disabled}, innerHTML: "${button.innerHTML}"`);
                } else {
                    // RFI files exist - button should show uploader's name
                    console.log(`ℹ️ RFI files exist - button should already show uploader's name for ${clientName}`);
                }
            } else {
                console.log(`⚠️ RFI button not found for ${clientName}: ${buttonId}`);
                console.log(`🔍 Available buttons:`, Array.from(document.querySelectorAll('button')).map(b => b.id).filter(id => id.includes('rfi')));
                console.log(`🔍 All buttons with 'rfi' in ID:`, Array.from(document.querySelectorAll('button[id*="rfi"]')).map(b => ({id: b.id, text: b.innerHTML, disabled: b.disabled})));
                
                // Try to find button by searching in the main table
                console.log(`🔍 Trying to find button in main table...`);
                const mainTable = document.querySelector('table.table');
                if (mainTable) {
                    console.log(`🔍 Main table found, searching for button...`);
                    const tableButton = mainTable.querySelector(`#${buttonId}`);
                    if (tableButton) {
                        console.log(`✅ Found RFI button in main table: ${buttonId}`);
                        const button = tableButton;
                        
                        if (rfiFiles.length === 0) {
                            console.log(`🔄 No RFI files found - resetting button to "RFI" for ${clientName}`);
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
                            console.log(`✅ Reset RFI button to "RFI" for ${clientName}`);
                        }
                    } else {
                        console.log(`⚠️ Button still not found in main table`);
                        console.log(`🔍 All buttons in main table:`, Array.from(mainTable.querySelectorAll('button')).map(b => ({id: b.id, text: b.innerHTML, disabled: b.disabled})));
                    }
                } else {
                    console.log(`⚠️ Main table not found`);
                }
                
                // Try to find button by searching for any button with the group ID
                console.log(`🔍 Trying to find button by group ID pattern...`);
                const groupButtons = Array.from(document.querySelectorAll('button')).filter(b => b.id.includes(groupId));
                console.log(`🔍 Buttons containing group ID ${groupId}:`, groupButtons.map(b => ({id: b.id, text: b.innerHTML, disabled: b.disabled})));
                
                // Check if any of these group buttons is the RFI button
                const rfiGroupButton = groupButtons.find(b => b.id.includes('rfi'));
                if (rfiGroupButton) {
                    console.log(`✅ Found RFI button in group buttons:`, rfiGroupButton.id);
                    const button = rfiGroupButton;
                    
                    if (rfiFiles.length === 0) {
                        console.log(`🔄 No RFI files found - resetting button to "RFI" for ${clientName}`);
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
                        console.log(`✅ Reset RFI button to "RFI" for ${clientName}`);
                    }
                }
                
                // Try to find button by searching for buttons with 'rfi' in the text
                console.log(`🔍 Trying to find button by text content...`);
                const rfiButtons = Array.from(document.querySelectorAll('button')).filter(b => 
                    b.innerHTML.toLowerCase().includes('rfi') || 
                    b.innerHTML.toLowerCase().includes('developer') ||
                    b.innerHTML.toLowerCase().includes('upload')
                );
                console.log(`🔍 Buttons with RFI-related text:`, rfiButtons.map(b => ({id: b.id, text: b.innerHTML, disabled: b.disabled})));
                
                // Check if any of these text-based buttons is the RFI button
                const rfiTextButton = rfiButtons.find(b => b.id.includes('rfi') || b.innerHTML.toLowerCase().includes('developer'));
                if (rfiTextButton) {
                    console.log(`✅ Found RFI button by text search:`, rfiTextButton.id);
                    const button = rfiTextButton;
                    
                    if (rfiFiles.length === 0) {
                        console.log(`🔄 No RFI files found - resetting button to "RFI" for ${clientName}`);
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
                        console.log(`✅ Reset RFI button to "RFI" for ${clientName}`);
                    }
                }
                
                // Last resort: Try to find any button that might be the RFI button
                console.log(`🔍 Last resort: Searching for any button that might be RFI...`);
                const allButtons = Array.from(document.querySelectorAll('button'));
                console.log(`🔍 Total buttons found: ${allButtons.length}`);
                
                // Look for buttons that might be RFI buttons (containing group ID or showing "Developer")
                const potentialRfiButtons = allButtons.filter(b => 
                    b.id.includes(groupId) || 
                    b.innerHTML.toLowerCase().includes('developer') ||
                    b.innerHTML.toLowerCase().includes('rfi') ||
                    b.innerHTML.toLowerCase().includes('upload')
                );
                
                console.log(`🔍 Potential RFI buttons found: ${potentialRfiButtons.length}`);
                potentialRfiButtons.forEach((btn, index) => {
                    console.log(`🔍 Button ${index + 1}:`, {
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
                    console.log(`✅ Found Developer button that might be RFI:`, developerButton.id);
                    const button = developerButton;
                    
                    if (rfiFiles.length === 0) {
                        console.log(`🔄 No RFI files found - resetting Developer button to "RFI" for ${clientName}`);
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
                        console.log(`✅ Reset Developer button to "RFI" for ${clientName}`);
                    }
                }
            }
        } else {
            console.log(`❌ API call failed or no files data:`, data);
        }
    } catch (error) {
        console.error('❌ Error checking specific inspection RFI status:', error);
    }
}

// Check specific inspection for Invoice files and update button accordingly
async function checkSpecificInspectionInvoiceStatus(groupId, clientName, inspectionDate) {
    try {
        console.log(`🔍 Checking Invoice status for specific inspection: ${clientName} on ${inspectionDate}`);
        
        // Clean the client name and date
        const cleanClientName = clientName.replace(/[^a-zA-Z0-9\s]/g, '').trim();
        const cleanDate = inspectionDate.replace(/[^0-9-]/g, '').replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
        
        console.log(`🔍 Cleaned client name: ${cleanClientName}, Cleaned date: ${cleanDate}`);
        
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
            console.error('❌ Failed to check inspection files:', response.status);
            return;
        }
        
        const data = await response.json();
        console.log(`🔍 File check response for ${clientName}:`, data);
        console.log(`🔍 Full API response:`, JSON.stringify(data, null, 2));
        
        if (data.success && data.files) {
            const invoiceFiles = data.files.invoice || [];
            console.log(`🔍 Found ${invoiceFiles.length} Invoice files for ${clientName}`);
            console.log(`🔍 Invoice files:`, invoiceFiles);
            console.log(`🔍 All files object:`, data.files);
            
            // Find the Invoice button for this specific inspection
            const buttonId = `invoice-${groupId}`;
            const button = document.getElementById(buttonId);
            
            if (button) {
                if (invoiceFiles.length === 0) {
                    // No Invoice files - reset button to "Invoice"
                    console.log(`🔄 No Invoice files found - resetting button to "Invoice" for ${clientName}`);
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
                    
                    console.log(`✅ Reset Invoice button to "Invoice" for ${clientName}`);
                } else {
                    // Invoice files exist - button should show uploader's name
                    console.log(`ℹ️ Invoice files exist - button should already show uploader's name for ${clientName}`);
                }
            } else {
                console.log(`⚠️ Invoice button not found for ${clientName}: ${buttonId}`);
            }
        }
    } catch (error) {
        console.error('❌ Error checking specific inspection Invoice status:', error);
    }
}

// Process pending button updates when popup closes
function processPendingButtonUpdates() {
    if (window.pendingButtonUpdates && window.pendingButtonUpdates.length > 0) {
        console.log(`🔄 Processing ${window.pendingButtonUpdates.length} pending button updates`);
        
        window.pendingButtonUpdates.forEach(update => {
            const button = document.getElementById(update.buttonId);
            if (button) {
                console.log(`✅ Processing pending update for: ${update.buttonId}`);
                
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
                    
                    console.log(`✅ Processed pending reset update for: ${update.buttonId}`);
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
                    
                    console.log(`✅ Processed pending upload update for: ${update.buttonId} with username: ${update.username}`);
                }
            } else {
                console.log(`⚠️ Button still not found for pending update: ${update.buttonId}`);
            }
        });
        
        // Clear pending updates
        window.pendingButtonUpdates = [];
        console.log(`✅ Cleared all pending button updates`);
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
        console.log('🗂️ Starting download of all files for ' + clientName + ' on ' + inspectionDate);
        
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
            
            console.log('✅ Download completed:', filename);
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
    const retestButton = document.getElementById('retest-' + inspectionId);
    const dropdown = document.querySelector('select[data-inspection-id="' + inspectionId + '"]');
    
    if (labButton && retestButton) {
        // Check if sample was taken
        const isSampleTaken = dropdown && !dropdown.disabled;
        
        if (!isSampleTaken) {
            // No sample taken - disable both buttons
            labButton.disabled = true;
            labButton.style.opacity = '0.5';
            labButton.style.cursor = 'not-allowed';
            labButton.onclick = null;
            labButton.title = 'No sample taken - Lab upload disabled';
            
            retestButton.disabled = true;
            retestButton.style.opacity = '0.5';
            retestButton.style.cursor = 'not-allowed';
            retestButton.onclick = null;
            retestButton.title = 'No sample taken - Retest upload disabled';
        } else {
            // Sample taken - enable lab button
            labButton.disabled = false;
            labButton.style.opacity = '';
            labButton.style.cursor = '';
            labButton.onclick = function() { uploadLab(inspectionId); };
            labButton.title = 'Lab result upload available';
            
            // Retest button is enabled ONLY if sample taken AND retest is YES (must upload document)
            if (isSampleTaken && needsRetest === 'YES') {
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

console.log('All functions ready: uploadRFI, uploadInvoice, openFilesPopup, expandAll, collapseAll, toggleGroup, updateProductName, updateProductClass, updateLab, loadInspectionFiles, displayFiles, downloadFile, deleteFile, viewFile, downloadAllFiles, updateViewFilesButtonColor, updateAllViewFilesButtonColors, validateUploadButtonStates, updateButtonAfterDeletion, updateNeedsRetest, updateButtonStates');
console.log('🧪 Debug: Type testFileDisplay() in console to test file display with sample data');

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
        
        console.log('✅ All functions validated successfully');
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
