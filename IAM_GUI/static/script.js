// ==========================================================================
// Professional IAM Platform JavaScript
// Modern Interface with Glass Morphism & Enhanced UX
// ==========================================================================

// Global variables and state management
let currentViewer = null;
let currentMolecule = null;
let ketcherInstance = null;
let currentTab = 'summary';
let isDarkMode = false;
let isCalculating = false;

// DOM Elements - Professional Interface
const elements = {
    darkModeToggle: null,
    ketcherFrame: null,
    getStructureBtn: null,
    clearStructureBtn: null,
    smilesInput: null,
    xyzTextarea: null,
    fileInput: null,
    chargeInput: null,
    multiplicitySelect: null,
    runAnalysisBtn: null,
    clearAllBtn: null,
    exportResultsBtn: null,
    viewer: null,
    viewerControls: null,
    tabButtons: null,
    tabContents: null,
    summaryOutput: null,
    computationalOutput: null,
    performanceOutput: null,
    orbitalsOutput: null,
    aiAgentOutput: null,
    toolsOutput: null,
    loadingOverlay: null,
    loadingMessage: null,
    toastContainer: null
};

// ==========================================================================
// Initialization and DOM Ready
// ==========================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing Professional IAM Interface...');
    
    initializeDOMElements();
    initializeDarkMode();
    initializeViewer();
    initializeTabs();
    initializeEventListeners();
    initializeTooltips();
    initializeKetcher();
    
    console.log('✅ Professional IAM Interface initialized successfully');
    showToast('Welcome to IAM Platform', 'Professional molecular analysis interface loaded successfully', 'success');
});

function initializeDOMElements() {
    elements.darkModeToggle = document.getElementById('darkModeToggle');
    elements.ketcherFrame = document.getElementById('ketcherFrame');
    elements.getStructureBtn = document.getElementById('getStructureBtn');
    elements.clearStructureBtn = document.getElementById('clearStructureBtn');
    elements.smilesInput = document.getElementById('smilesInput');
    elements.xyzTextarea = document.getElementById('xyzTextarea');
    elements.fileInput = document.getElementById('fileInput');
    elements.chargeInput = document.getElementById('chargeInput');
    elements.multiplicitySelect = document.getElementById('multiplicitySelect');
    elements.runAnalysisBtn = document.getElementById('runAnalysisBtn');
    elements.clearAllBtn = document.getElementById('clearAllBtn');
    elements.exportResultsBtn = document.getElementById('exportResultsBtn');
    elements.viewer = document.getElementById('viewer');
    elements.viewerControls = document.querySelectorAll('.viewer-control');
    elements.tabButtons = document.querySelectorAll('.professional-tabs .nav-link');
    elements.tabContents = document.querySelectorAll('.tab-panel');
    elements.summaryOutput = document.getElementById('summaryOutput');
    elements.computationalOutput = document.getElementById('computationalOutput');
    elements.performanceOutput = document.getElementById('performanceOutput');
    elements.orbitalsOutput = document.getElementById('orbitalsOutput');
    elements.aiAgentOutput = document.getElementById('aiAgentOutput');
    elements.toolsOutput = document.getElementById('toolsOutput');
    elements.loadingOverlay = document.getElementById('loadingOverlay');
    elements.loadingMessage = document.getElementById('loadingMessage');
    elements.toastContainer = document.getElementById('toastContainer');
    console.log('📋 DOM elements initialized');
}

// ==========================================================================
// Dark Mode Implementation
// ==========================================================================

function initializeDarkMode() {
    const savedTheme = localStorage.getItem('iam-theme');
    if (savedTheme) {
        isDarkMode = savedTheme === 'dark';
        applyTheme();
    } else {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        isDarkMode = prefersDark;
        applyTheme();
    }
    
    if (elements.darkModeToggle) {
        elements.darkModeToggle.checked = isDarkMode;
    }
    
    console.log(`🌙 Theme initialized: ${isDarkMode ? 'Dark' : 'Light'} mode`);
}

function toggleDarkMode() {
    isDarkMode = !isDarkMode;
    applyTheme();
    localStorage.setItem('iam-theme', isDarkMode ? 'dark' : 'light');
    
    document.body.style.transition = 'background 0.3s ease-in-out, color 0.3s ease-in-out';
    setTimeout(() => {
        document.body.style.transition = '';
    }, 300);
    
    console.log(`🌙 Theme toggled to: ${isDarkMode ? 'Dark' : 'Light'} mode`);
}

function applyTheme() {
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }
}

// ==========================================================================
// 3D Molecular Viewer (3Dmol.js)
// ==========================================================================

function initializeViewer() {
    if (!elements.viewer) {
        console.warn('⚠️ 3D Viewer element not found');
        return;
    }
    
    try {
        currentViewer = $3Dmol.createViewer(elements.viewer, {
            defaultcolors: $3Dmol.rasmolElementColors
        });
        
        currentViewer.setBackgroundColor(0xffffff, 0.0);
        currentViewer.render();
        
        console.log('🧬 3D Viewer initialized successfully');
    } catch (error) {
        console.error('❌ Failed to initialize 3D viewer:', error);
        showToast('Viewer Error', 'Failed to initialize 3D molecular viewer', 'danger');
    }
}

function renderMolecule(xyzData, format = 'xyz') {
    if (!currentViewer) {
        console.warn('⚠️ 3D Viewer not initialized');
        return;
    }
    
    try {
        currentViewer.clear();
        
        if (xyzData && xyzData.trim()) {
            const model = currentViewer.addModel(xyzData, format);
            
            currentViewer.setStyle({}, {
                stick: {
                    radius: 0.15,
                    colorscheme: 'Jmol'
                },
                sphere: {
                    radius: 0.3,
                    colorscheme: 'Jmol'
                }
            });
            
            currentViewer.zoomTo();
            currentViewer.render();
            
            currentMolecule = xyzData;
            
            console.log('🧬 Molecule rendered successfully');
            showToast('Molecule Loaded', 'Structure rendered in 3D viewer', 'success');
        }
    } catch (error) {
        console.error('❌ Failed to render molecule:', error);
        showToast('Render Error', 'Failed to render molecular structure', 'danger');
    }
}

function resetViewer() {
    if (currentViewer) {
        currentViewer.clear();
        currentViewer.render();
        currentMolecule = null;
        console.log('🧬 3D Viewer reset');
    }
}

function centerMolecule() {
    if (currentViewer && currentMolecule) {
        currentViewer.zoomTo();
        currentViewer.render();
    }
}

function toggleStyle() {
    if (!currentViewer || !currentMolecule) return;
    
    const currentStyle = currentViewer.getModel(0).getStyle();
    
    if (currentStyle.stick) {
        currentViewer.setStyle({}, {
            sphere: { radius: 0.3, colorscheme: 'Jmol' },
            stick: { radius: 0.15, colorscheme: 'Jmol' }
        });
    } else {
        currentViewer.setStyle({}, {
            stick: { radius: 0.2, colorscheme: 'Jmol' }
        });
    }
    
    currentViewer.render();
}

function exportImage() {
    if (currentViewer && currentMolecule) {
        const imageData = currentViewer.pngURI();
        const link = document.createElement('a');
        link.download = 'molecule.png';
        link.href = imageData;
        link.click();
        
        showToast('Image Exported', 'Molecular structure image saved', 'success');
    }
}

// ==========================================================================
// Professional Tab System
// ==========================================================================

function initializeTabs() {
    elements.tabButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetTab = this.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });
    
    switchTab('summary');
    console.log('📑 Professional tabs initialized');
}

function switchTab(tabName) {
    if (currentTab === tabName) return;
    
    elements.tabButtons.forEach(button => {
        if (button.getAttribute('data-tab') === tabName) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
    
    elements.tabContents.forEach(content => {
        if (content.id === `${tabName}Tab`) {
            content.classList.add('active');
            content.style.display = 'block';
        } else {
            content.classList.remove('active');
            content.style.display = 'none';
        }
    });
    
    currentTab = tabName;
    console.log(`📑 Switched to tab: ${tabName}`);
}

// ==========================================================================
// Ketcher Integration
// ==========================================================================

function initializeKetcher() {
    if (!elements.ketcherFrame) {
        console.warn('⚠️ Ketcher frame not found');
        return;
    }
    
    elements.ketcherFrame.onload = function() {
        try {
            const ketcherWindow = elements.ketcherFrame.contentWindow;
            if (ketcherWindow && ketcherWindow.ketcher) {
                ketcherInstance = ketcherWindow.ketcher;
                console.log('⚗️ Ketcher initialized successfully');
            } else {
                setTimeout(initializeKetcher, 1000);
            }
        } catch (error) {
            console.warn('⚠️ Ketcher not yet ready, retrying...');
            setTimeout(initializeKetcher, 1000);
        }
    };
}

async function getStructureFromKetcher() {
    if (!ketcherInstance) {
        showToast('Ketcher Error', 'Molecular sketcher not initialized', 'warning');
        return null;
    }
    
    try {
        const smiles = await ketcherInstance.getSmiles();
        if (smiles && smiles.trim()) {
            console.log('⚗️ Structure obtained from Ketcher:', smiles);
            return smiles;
        } else {
            showToast('No Structure', 'Please draw a molecule in the sketcher', 'warning');
            return null;
        }
    } catch (error) {
        console.error('❌ Failed to get structure from Ketcher:', error);
        showToast('Ketcher Error', 'Failed to get molecular structure', 'danger');
        return null;
    }
}

function clearKetcher() {
    if (ketcherInstance) {
        try {
            ketcherInstance.editor.clear();
            console.log('⚗️ Ketcher structure cleared');
        } catch (error) {
            console.error('❌ Failed to clear Ketcher:', error);
        }
    }
}

// ==========================================================================
// Event Listeners
// ==========================================================================

function initializeEventListeners() {
    if (elements.darkModeToggle) {
        elements.darkModeToggle.addEventListener('change', toggleDarkMode);
    }
    
    if (elements.getStructureBtn) {
        elements.getStructureBtn.addEventListener('click', async function() {
            const smiles = await getStructureFromKetcher();
            if (smiles && elements.smilesInput) {
                elements.smilesInput.value = smiles;
                convertSMILESToXYZ();
            }
        });
    }
    
    if (elements.clearStructureBtn) {
        elements.clearStructureBtn.addEventListener('click', clearKetcher);
    }
    
    if (elements.smilesInput) {
        elements.smilesInput.addEventListener('input', function() {
            if (this.value.trim()) {
                convertSMILESToXYZ();
            }
        });
    }
    
    if (elements.xyzTextarea) {
        elements.xyzTextarea.addEventListener('input', function() {
            if (this.value.trim()) {
                renderMolecule(this.value);
            }
        });
    }
    
    if (elements.fileInput) {
        elements.fileInput.addEventListener('change', handleFileUpload);
    }
    
    if (elements.runAnalysisBtn) {
        elements.runAnalysisBtn.addEventListener('click', runQuantumAnalysis);
    }
    
    if (elements.clearAllBtn) {
        elements.clearAllBtn.addEventListener('click', clearAll);
    }
    
    if (elements.exportResultsBtn) {
        elements.exportResultsBtn.addEventListener('click', exportResults);
    }
    
    elements.viewerControls.forEach(control => {
        control.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            switch(action) {
                case 'center':
                    centerMolecule();
                    break;
                case 'style':
                    toggleStyle();
                    break;
                case 'export':
                    exportImage();
                    break;
            }
        });
    });
    
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'Enter':
                    e.preventDefault();
                    if (!isCalculating) {
                        runQuantumAnalysis();
                    }
                    break;
                case 'r':
                    e.preventDefault();
                    resetViewer();
                    break;
                case 'd':
                    e.preventDefault();
                    toggleDarkMode();
                    break;
            }
        }
    });
    
    console.log('🎯 Event listeners initialized');
}

// ==========================================================================
// File Upload Handler
// ==========================================================================

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    
    reader.onload = function(e) {
        const content = e.target.result;
        const extension = file.name.split('.').pop().toLowerCase();
        
        try {
            if (extension === 'xyz') {
                elements.xyzTextarea.value = content;
                renderMolecule(content);
                showToast('File Loaded', `XYZ file "${file.name}" loaded successfully`, 'success');
            } else if (extension === 'mol' || extension === 'sdf') {
                convertMOLToXYZ(content);
            } else {
                showToast('Unsupported Format', 'Please upload XYZ, MOL, or SDF files', 'warning');
            }
        } catch (error) {
            console.error('❌ File upload error:', error);
            showToast('Upload Error', 'Failed to process uploaded file', 'danger');
        }
    };
    
    reader.readAsText(file);
}

// ==========================================================================
// API Communication Functions
// ==========================================================================

async function convertSMILESToXYZ() {
    const smiles = elements.smilesInput.value.trim();
    if (!smiles) return;
    
    try {
        showLoading('Converting SMILES to 3D structure...');
        
        const response = await fetch('/convert_smiles_to_xyz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ smiles: smiles })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success && data.xyz) {
            elements.xyzTextarea.value = data.xyz;
            renderMolecule(data.xyz);
            showToast('Conversion Success', 'SMILES converted to 3D structure', 'success');
        } else {
            showToast('Conversion Failed', data.error || 'Failed to convert SMILES', 'danger');
        }
    } catch (error) {
        hideLoading();
        console.error('❌ SMILES conversion error:', error);
        showToast('Network Error', 'Failed to connect to conversion service', 'danger');
    }
}

async function convertMOLToXYZ(molData) {
    try {
        showLoading('Converting MOL to XYZ format...');
        
        const response = await fetch('/convert_mol_to_xyz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mol_data: molData })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success && data.xyz) {
            elements.xyzTextarea.value = data.xyz;
            renderMolecule(data.xyz);
            showToast('Conversion Success', 'MOL file converted to XYZ format', 'success');
        } else {
            showToast('Conversion Failed', data.error || 'Failed to convert MOL file', 'danger');
        }
    } catch (error) {
        hideLoading();
        console.error('❌ MOL conversion error:', error);
        showToast('Network Error', 'Failed to connect to conversion service', 'danger');
    }
}

async function runQuantumAnalysis() {
    if (isCalculating) {
        showToast('Analysis Running', 'Please wait for current calculation to complete', 'warning');
        return;
    }
    
    const xyz = elements.xyzTextarea.value.trim();
    if (!xyz) {
        showToast('No Structure', 'Please provide a molecular structure first', 'warning');
        return;
    }
    
    const charge = parseInt(elements.chargeInput.value) || 0;
    const multiplicity = parseInt(elements.multiplicitySelect.value) || 1;
    
    try {
        isCalculating = true;
        showLoading('Running quantum chemical analysis...');
        
        elements.runAnalysisBtn.disabled = true;
        elements.runAnalysisBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
        
        const response = await fetch('/run_analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                xyz: xyz,
                charge: charge,
                multiplicity: multiplicity
            })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            displayResults(data);
            showToast('Analysis Complete', 'Quantum chemical analysis completed successfully', 'success');
        } else {
            showToast('Analysis Failed', data.error || 'Quantum analysis failed', 'danger');
        }
    } catch (error) {
        hideLoading();
        console.error('❌ Analysis error:', error);
        showToast('Network Error', 'Failed to connect to analysis service', 'danger');
    } finally {
        isCalculating = false;
        elements.runAnalysisBtn.disabled = false;
        elements.runAnalysisBtn.innerHTML = '<i class="fas fa-play me-2"></i>Run Analysis';
    }
}

// ==========================================================================
// Results Display
// ==========================================================================

function displayResults(data) {
    if (elements.summaryOutput && data.summary) {
        elements.summaryOutput.innerHTML = formatResults(data.summary, 'Molecular Summary');
    }
    
    if (elements.computationalOutput && data.computational) {
        elements.computationalOutput.innerHTML = formatResults(data.computational, 'Computational Details');
    }
    
    if (elements.performanceOutput && data.performance) {
        elements.performanceOutput.innerHTML = formatResults(data.performance, 'Performance Metrics');
    }
    
    if (elements.orbitalsOutput && data.orbitals) {
        elements.orbitalsOutput.innerHTML = formatResults(data.orbitals, 'Molecular Orbitals');
    }
    
    switchTab('summary');
}

function formatResults(data, title) {
    return `
        <div class="fade-in">
            <h6><i class="fas fa-info-circle me-2"></i>${title}</h6>
            <pre class="font-monospace">${JSON.stringify(data, null, 2)}</pre>
        </div>
    `;
}

// ==========================================================================
// Utility Functions
// ==========================================================================

function clearAll() {
    if (elements.smilesInput) elements.smilesInput.value = '';
    if (elements.xyzTextarea) elements.xyzTextarea.value = '';
    if (elements.fileInput) elements.fileInput.value = '';
    if (elements.chargeInput) elements.chargeInput.value = '0';
    if (elements.multiplicitySelect) elements.multiplicitySelect.value = '1';
    
    elements.tabContents.forEach(content => {
        const output = content.querySelector('pre');
        if (output) output.textContent = 'No results yet. Run an analysis to see output here.';
    });
    
    resetViewer();
    clearKetcher();
    switchTab('summary');
    
    showToast('Interface Reset', 'All inputs and results cleared', 'info');
    console.log('🧹 Interface cleared');
}

function exportResults() {
    const results = {
        timestamp: new Date().toISOString(),
        inputs: {
            smiles: elements.smilesInput?.value || '',
            xyz: elements.xyzTextarea?.value || '',
            charge: elements.chargeInput?.value || '0',
            multiplicity: elements.multiplicitySelect?.value || '1'
        },
        outputs: {}
    };
    
    elements.tabContents.forEach(content => {
        const tabId = content.id.replace('Tab', '');
        const output = content.querySelector('pre');
        if (output && output.textContent !== 'No results yet. Run an analysis to see output here.') {
            results.outputs[tabId] = output.textContent;
        }
    });
    
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `iam_results_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
    link.click();
    URL.revokeObjectURL(url);
    
    showToast('Results Exported', 'Analysis results saved to file', 'success');
}

// ==========================================================================
// Loading Overlay
// ==========================================================================

function showLoading(message = 'Processing...') {
    if (elements.loadingOverlay && elements.loadingMessage) {
        elements.loadingMessage.textContent = message;
        elements.loadingOverlay.style.display = 'flex';
        elements.loadingOverlay.classList.add('fade-in');
    }
}

function hideLoading() {
    if (elements.loadingOverlay) {
        elements.loadingOverlay.style.display = 'none';
        elements.loadingOverlay.classList.remove('fade-in');
    }
}

// ==========================================================================
// Toast Notifications
// ==========================================================================

function showToast(title, message, type = 'info') {
    if (!elements.toastContainer) return;
    
    const toastId = 'toast_' + Date.now();
    const iconMap = {
        success: 'fas fa-check-circle text-success',
        danger: 'fas fa-exclamation-circle text-danger',
        warning: 'fas fa-exclamation-triangle text-warning',
        info: 'fas fa-info-circle text-primary'
    };
    
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <div class="d-flex align-items-center">
                        <i class="${iconMap[type]} me-2"></i>
                        <div>
                            <strong>${title}</strong><br>
                            <small>${message}</small>
                        </div>
                    </div>
                </div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    elements.toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// ==========================================================================
// Tooltips Initialization
// ==========================================================================

function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    console.log('💡 Tooltips initialized');
}

// ==========================================================================
// Error Handling & Exports
// ==========================================================================

window.addEventListener('error', function(e) {
    console.error('🚨 Global error:', e.error);
    showToast('Application Error', 'An unexpected error occurred', 'danger');
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('🚨 Unhandled promise rejection:', e.reason);
    showToast('Promise Error', 'An async operation failed', 'danger');
});

if (typeof window !== 'undefined') {
    window.IAM = {
        elements,
        currentViewer,
        currentMolecule,
        ketcherInstance,
        switchTab,
        renderMolecule,
        showToast,
        version: '2.0.0-professional'
    };
}
