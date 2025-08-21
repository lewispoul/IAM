// IAM Old UI Script - Simple and Clean
console.log('🧪 IAM Old UI Loading...');

let viewer3D = null;

// Tab switching function
function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Add active class to corresponding button
    const selectedBtn = document.getElementById(`tab${tabName.charAt(0).toUpperCase() + tabName.slice(1)}Btn`);
    if (selectedBtn) {
        selectedBtn.classList.add('active');
    }
}

// 3D Molecule rendering
function renderMolecule(contents, format = 'auto') {
    const viewerDiv = document.getElementById("viewer");
    if (!viewerDiv) {
        console.error('Viewer element not found');
        return;
    }
    
    try {
        // Clear previous viewer
        viewerDiv.innerHTML = '';
        
        // Create new viewer
        viewer3D = $3Dmol.createViewer(viewerDiv, { 
            backgroundColor: "white",
            antialias: true
        });
        
        if (!contents || !contents.trim()) {
            console.log('No content to render');
            return;
        }
        
        // Auto-detect format
        let detectedFormat = format;
        if (format === 'auto') {
            if (contents.includes('V2000') || contents.includes('V3000')) {
                detectedFormat = 'mol';
            } else if (contents.trim().split('\\n')[0].match(/^\\d+$/)) {
                detectedFormat = 'xyz';
            } else {
                detectedFormat = 'xyz'; // default
            }
        }
        
        // Add model
        viewer3D.addModel(contents, detectedFormat);
        
        // Set style
        viewer3D.setStyle({}, {
            stick: {radius: 0.2},
            sphere: {scale: 0.3}
        });
        
        // Zoom and render
        viewer3D.zoomTo();
        viewer3D.render();
        
        console.log(`✅ Molecule rendered in ${detectedFormat} format`);
        
    } catch (error) {
        console.error('Error rendering molecule:', error);
        showMessage('Error rendering molecule: ' + error.message, 'error');
    }
}

// Auto-detect and render molecule
function renderMoleculeAuto(contents) {
    renderMolecule(contents, 'auto');
}

// Show message helper
function showMessage(message, type = 'info') {
    const summaryContent = document.getElementById('summaryContent');
    if (summaryContent) {
        let className = '';
        if (type === 'error') className = 'error';
        if (type === 'success') className = 'success';
        if (type === 'loading') className = 'loading';
        
        summaryContent.innerHTML = `<div class="${className}">${message}</div>`;
    }
    console.log(`${type.toUpperCase()}: ${message}`);
}

// DOM Content Loaded
document.addEventListener("DOMContentLoaded", function () {
    console.log('🚀 IAM Old UI Ready');
    
    // Initialize 3D viewer with empty content
    renderMolecule('');
    
    // File upload handler
    const fileInput = document.getElementById('xyzFile');
    if (fileInput) {
        fileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const contents = e.target.result;
                renderMoleculeAuto(contents);
                showMessage(`File "${file.name}" loaded successfully`, 'success');
            };
            reader.onerror = function() {
                showMessage('Error reading file', 'error');
            };
            reader.readAsText(file);
        });
    }
    
    // Load from paste button
    const loadPasteBtn = document.getElementById('loadFromPasteBtn');
    if (loadPasteBtn) {
        loadPasteBtn.addEventListener('click', function() {
            const pasteArea = document.getElementById('xyzPaste');
            const contents = pasteArea.value.trim();
            
            if (!contents) {
                showMessage('Please paste some content first', 'error');
                return;
            }
            
            renderMoleculeAuto(contents);
            showMessage('Pasted content loaded successfully', 'success');
        });
    }
    
    // Clear button
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            document.getElementById('xyzPaste').value = '';
            document.getElementById('xyzFile').value = '';
            renderMolecule('');
            showMessage('Input cleared', 'info');
        });
    }
    
    // Reset viewer button
    const resetViewerBtn = document.getElementById('resetViewerBtn');
    if (resetViewerBtn) {
        resetViewerBtn.addEventListener('click', function() {
            if (viewer3D) {
                viewer3D.zoomTo();
                viewer3D.render();
                showMessage('Viewer reset', 'info');
            }
        });
    }
    
    // Main calculation button
    const launchBtn = document.getElementById('launchIAMBtn');
    if (launchBtn) {
        launchBtn.addEventListener('click', async function() {
            await runCalculation();
        });
    }
    
    // Export buttons
    const exportPDFBtn = document.getElementById('exportPDFBtn');
    if (exportPDFBtn) {
        exportPDFBtn.addEventListener('click', function() {
            showMessage('PDF export not yet implemented', 'error');
        });
    }
    
    const exportCSVBtn = document.getElementById('exportCSVBtn');
    if (exportCSVBtn) {
        exportCSVBtn.addEventListener('click', function() {
            showMessage('CSV export not yet implemented', 'error');
        });
    }
});

// Main calculation function
async function runCalculation() {
    const launchBtn = document.getElementById('launchIAMBtn');
    const fileInput = document.getElementById('xyzFile');
    const pasteInput = document.getElementById('xyzPaste').value.trim();
    
    // Disable button during calculation
    if (launchBtn) {
        launchBtn.disabled = true;
        launchBtn.textContent = '⏳ Calculating...';
    }
    
    showMessage('Starting calculation', 'loading');
    
    try {
        // Prepare form data
        let formData = new FormData();
        
        if (fileInput.files.length > 0) {
            formData.append('file', fileInput.files[0]);
        } else if (pasteInput) {
            const blob = new Blob([pasteInput], { type: 'text/plain' });
            formData.append('file', blob, 'pasted.xyz');
        } else {
            throw new Error('No molecule data provided. Please upload a file or paste content.');
        }
        
        // Add calculation parameters
        formData.append('method', document.getElementById('method').value);
        formData.append('charge', document.getElementById('charge').value);
        formData.append('multiplicity', document.getElementById('multiplicity').value);
        
        // Submit to backend
        const response = await fetch('/run_xtb', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result);
            showMessage('Calculation completed successfully!', 'success');
        } else {
            throw new Error(result.error || 'Calculation failed');
        }
        
    } catch (error) {
        console.error('Calculation error:', error);
        showMessage(`Calculation failed: ${error.message}`, 'error');
    } finally {
        // Re-enable button
        if (launchBtn) {
            launchBtn.disabled = false;
            launchBtn.textContent = '🚀 Run Calculation';
        }
    }
}

// Display calculation results
function displayResults(result) {
    // Summary tab
    const summaryContent = document.getElementById('summaryContent');
    if (summaryContent && result.xtb_json) {
        const xtb = result.xtb_json;
        let html = '<h4>✅ XTB Calculation Results</h4>';
        html += '<table class="result-table">';
        
        if (xtb.total_energy !== undefined) {
            html += `<tr><th>Total Energy</th><td>${xtb.total_energy} Hartree</td></tr>`;
        }
        if (xtb.homo_lumo_gap !== undefined) {
            html += `<tr><th>HOMO-LUMO Gap</th><td>${xtb.homo_lumo_gap} eV</td></tr>`;
        }
        if (xtb.dipole_moment !== undefined) {
            html += `<tr><th>Dipole Moment</th><td>${xtb.dipole_moment} Debye</td></tr>`;
        }
        
        html += '</table>';
        summaryContent.innerHTML = html;
    }
    
    // Output tab
    const outputText = document.getElementById('outputText');
    if (outputText && result.output) {
        outputText.textContent = result.output;
    }
    
    // Log tab
    const logText = document.getElementById('logText');
    if (logText && result.log) {
        logText.textContent = result.log;
    }
    
    // Render optimized geometry if available
    if (result.xyz_result) {
        renderMolecule(result.xyz_result, 'xyz');
    }
    
    // Performance prediction
    runPerformancePrediction(result);
}

// Performance prediction
async function runPerformancePrediction(calcResult) {
    try {
        const performanceContent = document.getElementById('performanceContent');
        if (!performanceContent) return;
        
        performanceContent.innerHTML = '<div class="loading">Predicting performance</div>';
        
        // Get molecular formula if available
        let formula = 'C1H1N1O1'; // default
        if (calcResult.molecular_formula) {
            formula = calcResult.molecular_formula;
        }
        
        const response = await fetch('/predict_performance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                molecular_formula: formula,
                density: 1.5, // default density
                heat_formation: 0 // default
            })
        });
        
        if (response.ok) {
            const perfResult = await response.json();
            if (perfResult.success) {
                displayPerformanceResults(perfResult.data);
            } else {
                performanceContent.innerHTML = `<div class="error">Performance prediction failed: ${perfResult.error}</div>`;
            }
        } else {
            performanceContent.innerHTML = '<div class="error">Performance prediction service unavailable</div>';
        }
        
    } catch (error) {
        console.error('Performance prediction error:', error);
        const performanceContent = document.getElementById('performanceContent');
        if (performanceContent) {
            performanceContent.innerHTML = `<div class="error">Performance prediction error: ${error.message}</div>`;
        }
    }
}

// Display performance results
function displayPerformanceResults(perfData) {
    const performanceContent = document.getElementById('performanceContent');
    if (!performanceContent) return;
    
    let html = '<h4>🔥 Performance Predictions</h4>';
    html += '<table class="result-table">';
    
    if (perfData.vod_kamlet_jacobs_ms) {
        html += `<tr><th>VoD (Kamlet-Jacobs)</th><td>${perfData.vod_kamlet_jacobs_ms} m/s</td></tr>`;
    }
    if (perfData.pcj_kamlet_jacobs_gpa) {
        html += `<tr><th>Pcj (Kamlet-Jacobs)</th><td>${perfData.pcj_kamlet_jacobs_gpa} GPa</td></tr>`;
    }
    if (perfData.oxygen_balance) {
        html += `<tr><th>Oxygen Balance</th><td>${perfData.oxygen_balance}%</td></tr>`;
    }
    if (perfData.estimated_density) {
        html += `<tr><th>Estimated Density</th><td>${perfData.estimated_density} g/cm³</td></tr>`;
    }
    
    html += '</table>';
    
    if (perfData.prediction_methods) {
        html += '<h5>Methods Used:</h5><ul>';
        perfData.prediction_methods.forEach(method => {
            html += `<li>${method}</li>`;
        });
        html += '</ul>';
    }
    
    performanceContent.innerHTML = html;
}

console.log('✅ IAM Old UI Script Loaded');
