// ================================================================
// IAM UI - Optimized JavaScript
// Enhanced performance, better UX, modern patterns
// ================================================================

// Global state management
const IAMState = {
    viewer3D: null,
    autoRotate: false,
    autoRotateInterval: null,
    lastXyzString: null,
    currentTheme: localStorage.getItem('iam-theme') || 'light',
    isLoading: false,
    debounceTimers: new Map(),
    cache: new Map()
};

// Performance utilities
const Utils = {
    // Debounce function calls
    debounce(func, wait, key) {
        if (IAMState.debounceTimers.has(key)) {
            clearTimeout(IAMState.debounceTimers.get(key));
        }
        
        const timeout = setTimeout(() => {
            func();
            IAMState.debounceTimers.delete(key);
        }, wait);
        
        IAMState.debounceTimers.set(key, timeout);
    },

    // Throttle function calls
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    },

    // Show toast notification
    showToast(message, type = 'success', duration = 3000) {
        // Remove existing toasts
        document.querySelectorAll('.toast-notification').forEach(toast => toast.remove());

        const toast = document.createElement('div');
        toast.className = `toast-notification fixed-bottom-right p-3 m-3 rounded shadow-lg ${type === 'error' ? 'bg-danger' : 'bg-success'} text-white`;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1050;
            max-width: 350px;
            animation: slideInRight 0.3s ease-out;
        `;
        
        toast.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span><i class="bi bi-${type === 'error' ? 'exclamation-triangle' : 'check-circle'}"></i> ${message}</span>
                <button type="button" class="btn-close btn-close-white ms-2" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    },

    // Validate molecular input
    validateMolecularInput(input) {
        const trimmed = input.trim();
        if (!trimmed) return { valid: false, type: null, message: 'Empty input' };

        // Check for XYZ format
        if (/^\d+\s*\n/.test(trimmed)) {
            const lines = trimmed.split('\n');
            const atomCount = parseInt(lines[0]);
            if (lines.length >= atomCount + 2) {
                return { valid: true, type: 'xyz', message: 'Valid XYZ format' };
            }
        }

        // Check for MOL format
        if (/V2000|V3000/.test(trimmed) || trimmed.includes('M  END')) {
            return { valid: true, type: 'mol', message: 'Valid MOL format' };
        }

        // Check for SMILES format
        if (/^[A-Za-z0-9@+\-\[\]\(\)=#$:\/\\\.]+$/.test(trimmed) && trimmed.length < 200) {
            return { valid: true, type: 'smiles', message: 'Valid SMILES format' };
        }

        return { valid: false, type: null, message: 'Unknown format' };
    },

    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Copy to clipboard
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            Utils.showToast('Copied to clipboard!');
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            Utils.showToast('Copied to clipboard!');
        }
    }
};

// Theme management
const ThemeManager = {
    init() {
        this.applyTheme(IAMState.currentTheme);
        this.bindEvents();
    },

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        IAMState.currentTheme = theme;
        localStorage.setItem('iam-theme', theme);
        
        const darkModeSwitch = document.getElementById('darkModeSwitch');
        if (darkModeSwitch) {
            darkModeSwitch.checked = theme === 'dark';
        }

        // Update 3D viewer background if exists
        if (IAMState.viewer3D && theme === 'dark') {
            IAMState.viewer3D.setBackgroundColor('#1e293b');
            IAMState.viewer3D.render();
        }
    },

    toggle() {
        const newTheme = IAMState.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    },

    bindEvents() {
        const darkModeSwitch = document.getElementById('darkModeSwitch');
        if (darkModeSwitch) {
            darkModeSwitch.addEventListener('change', () => {
                this.toggle();
            });
        }
    }
};

// Enhanced 3D Viewer Management
const ViewerManager = {
    init() {
        this.createViewer();
        this.bindEvents();
    },

    createViewer() {
        const viewerDiv = document.getElementById("viewer");
        if (!viewerDiv) {
            console.warn('Viewer element not found');
            return;
        }

        try {
            // Clear existing viewer
            viewerDiv.innerHTML = "";
            
            const bgColor = IAMState.currentTheme === 'dark' ? '#1e293b' : '#ffffff';
            IAMState.viewer3D = $3Dmol.createViewer(viewerDiv, { 
                backgroundColor: bgColor,
                antialias: true,
                quality: 'high'
            });
            
            console.log('3D Viewer initialized successfully');
        } catch (error) {
            console.error('Failed to initialize 3D viewer:', error);
            Utils.showToast('Failed to initialize 3D viewer', 'error');
        }
    },

    renderMolecule(xyzString, options = {}) {
        if (!IAMState.viewer3D) {
            this.createViewer();
            if (!IAMState.viewer3D) return;
        }

        try {
            IAMState.lastXyzString = xyzString || '';
            IAMState.viewer3D.clear();

            if (xyzString) {
                const model = IAMState.viewer3D.addModel(xyzString, "xyz");
                
                // Apply styling based on options
                const style = options.style || { stick: { radius: 0.15 }, sphere: { scale: 0.3 } };
                IAMState.viewer3D.setStyle({}, style);
                
                // Add labels if requested
                if (options.showLabels) {
                    const atoms = model.selectedAtoms({});
                    atoms.forEach((atom, index) => {
                        IAMState.viewer3D.addLabel(atom.elem + (index + 1), {
                            position: atom,
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            fontColor: 'white',
                            fontSize: 12
                        });
                    });
                }

                IAMState.viewer3D.zoomTo();
                IAMState.viewer3D.render();
                
                // Start auto-rotation if enabled
                if (IAMState.autoRotate) {
                    this.startAutoRotation();
                }
            }
        } catch (error) {
            console.error('Error rendering molecule:', error);
            Utils.showToast('Error rendering molecule', 'error');
        }
    },

    setBackground(color) {
        if (IAMState.viewer3D) {
            IAMState.viewer3D.setBackgroundColor(color);
            IAMState.viewer3D.render();
        }
    },

    resetView() {
        if (IAMState.viewer3D) {
            IAMState.viewer3D.zoomTo();
            IAMState.viewer3D.render();
        }
    },

    centerView() {
        if (IAMState.viewer3D) {
            IAMState.viewer3D.center();
            IAMState.viewer3D.render();
        }
    },

    toggleAutoRotation() {
        IAMState.autoRotate = !IAMState.autoRotate;
        
        if (IAMState.autoRotate) {
            this.startAutoRotation();
        } else {
            this.stopAutoRotation();
        }
        
        const btn = document.getElementById('viewerRotate');
        if (btn) {
            btn.textContent = IAMState.autoRotate ? 'Stop Rotation' : 'Start Rotation';
            btn.classList.toggle('btn-outline-secondary', !IAMState.autoRotate);
            btn.classList.toggle('btn-primary', IAMState.autoRotate);
        }
    },

    startAutoRotation() {
        this.stopAutoRotation();
        if (IAMState.viewer3D) {
            IAMState.autoRotateInterval = setInterval(() => {
                IAMState.viewer3D.rotate(1, 'y');
                IAMState.viewer3D.render();
            }, 50);
        }
    },

    stopAutoRotation() {
        if (IAMState.autoRotateInterval) {
            clearInterval(IAMState.autoRotateInterval);
            IAMState.autoRotateInterval = null;
        }
    },

    bindEvents() {
        // Background color selector
        const bgSelector = document.getElementById('viewerBg');
        if (bgSelector) {
            bgSelector.addEventListener('change', (e) => {
                this.setBackground(e.target.value);
            });
        }

        // Reset view button
        const resetBtn = document.getElementById('viewerReset');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetView());
        }

        // Center view button
        const centerBtn = document.getElementById('viewerCenter');
        if (centerBtn) {
            centerBtn.addEventListener('click', () => this.centerView());
        }

        // Auto rotation toggle
        const rotateBtn = document.getElementById('viewerRotate');
        if (rotateBtn) {
            rotateBtn.addEventListener('click', () => this.toggleAutoRotation());
        }
    }
};

// Enhanced Tab Management
const TabManager = {
    init() {
        this.bindEvents();
        this.showTab('summary'); // Default tab
    },

    showTab(tabId) {
        // Hide all tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.add('d-none');
            panel.classList.remove('active');
        });

        // Remove active class from all tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Show selected tab panel
        const panel = document.getElementById(`tab-${tabId}`);
        if (panel) {
            panel.classList.remove('d-none');
            panel.classList.add('active');
        }

        // Add active class to corresponding button
        const btn = document.querySelector(`.tab-btn[onclick*="${tabId}"]`);
        if (btn) {
            btn.classList.add('active');
        }

        // Trigger resize for 3D viewer if switching to a tab containing it
        if (tabId === 'viewer' && IAMState.viewer3D) {
            setTimeout(() => {
                IAMState.viewer3D.render();
            }, 100);
        }
    },

    bindEvents() {
        // Add click handlers to tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const onclick = btn.getAttribute('onclick');
                if (onclick) {
                    const match = onclick.match(/showResultTab\(['"](.+?)['"]\)/);
                    if (match) {
                        this.showTab(match[1]);
                    }
                }
            });
        });
    }
};

// Enhanced File Handling
const FileManager = {
    init() {
        this.bindEvents();
    },

    bindEvents() {
        // File upload handler
        const fileInput = document.getElementById('xyzFile');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        }

        // Drag and drop support
        const dropZones = [
            document.getElementById('molPaste'),
            document.getElementById('viewer')
        ].filter(Boolean);

        dropZones.forEach(zone => {
            zone.addEventListener('dragover', this.handleDragOver);
            zone.addEventListener('drop', (e) => this.handleFileDrop(e));
        });

        // Import buttons
        const importSmilesBtn = document.getElementById('importSmiles');
        if (importSmilesBtn) {
            importSmilesBtn.addEventListener('click', () => this.importSmiles());
        }

        const importMolBtn = document.getElementById('importMol');
        if (importMolBtn) {
            importMolBtn.addEventListener('click', () => this.importMol());
        }
    },

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        Utils.showToast(`Loading ${file.name} (${Utils.formatFileSize(file.size)})`);

        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            this.processFileContent(content, file.name);
        };
        reader.onerror = () => {
            Utils.showToast('Error reading file', 'error');
        };
        reader.readAsText(file);
    },

    handleDragOver(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'copy';
        event.target.classList.add('drag-over');
    },

    handleFileDrop(event) {
        event.preventDefault();
        event.target.classList.remove('drag-over');

        const files = event.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            const reader = new FileReader();
            reader.onload = (e) => {
                this.processFileContent(e.target.result, file.name);
            };
            reader.readAsText(file);
        }
    },

    processFileContent(content, filename = '') {
        const validation = Utils.validateMolecularInput(content);
        
        if (!validation.valid) {
            Utils.showToast(`Invalid file format: ${validation.message}`, 'error');
            return;
        }

        // Fill appropriate input field
        if (validation.type === 'xyz' || validation.type === 'mol') {
            const molPaste = document.getElementById('molPaste');
            if (molPaste) {
                molPaste.value = content;
            }
        } else if (validation.type === 'smiles') {
            const smilesPaste = document.getElementById('smilesPaste');
            if (smilesPaste) {
                smilesPaste.value = content;
            }
        }

        // Preview in 3D viewer
        this.previewMolecule(content, validation.type);
        
        Utils.showToast(`${filename} loaded successfully (${validation.type.toUpperCase()})`);
    },

    async previewMolecule(content, type) {
        try {
            if (type === 'xyz') {
                ViewerManager.renderMolecule(content);
            } else if (type === 'mol') {
                const response = await fetch('/molfile_to_xyz', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ molfile: content })
                });

                const data = await response.json();
                if (data.success && data.xyz) {
                    ViewerManager.renderMolecule(data.xyz);
                } else {
                    throw new Error(data.error || 'Conversion failed');
                }
            } else if (type === 'smiles') {
                const response = await fetch('/smiles_to_xyz', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ smiles: content })
                });

                const data = await response.json();
                if (data.success && data.xyz) {
                    ViewerManager.renderMolecule(data.xyz);
                } else {
                    throw new Error(data.error || 'SMILES conversion failed');
                }
            }
        } catch (error) {
            console.error('Preview error:', error);
            Utils.showToast('Preview failed: ' + error.message, 'error');
        }
    },

    importSmiles() {
        const smilesInput = document.getElementById('smilesPaste');
        if (!smilesInput || !smilesInput.value.trim()) {
            Utils.showToast('Please enter a SMILES string', 'error');
            return;
        }

        const validation = Utils.validateMolecularInput(smilesInput.value);
        if (!validation.valid || validation.type !== 'smiles') {
            Utils.showToast('Invalid SMILES format', 'error');
            return;
        }

        this.previewMolecule(smilesInput.value, 'smiles');
    },

    importMol() {
        const molInput = document.getElementById('molPaste');
        if (!molInput || !molInput.value.trim()) {
            Utils.showToast('Please paste MOL or XYZ content', 'error');
            return;
        }

        const validation = Utils.validateMolecularInput(molInput.value);
        if (!validation.valid) {
            Utils.showToast(`Invalid format: ${validation.message}`, 'error');
            return;
        }

        this.previewMolecule(molInput.value, validation.type);
    }
};

// Enhanced Ketcher Integration
const KetcherManager = {
    init() {
        this.bindEvents();
        this.waitForKetcher();
    },

    waitForKetcher() {
        // Wait for Ketcher iframe to load
        const iframe = document.getElementById('ketcherFrame');
        if (iframe) {
            iframe.addEventListener('load', () => {
                console.log('Ketcher iframe loaded');
                setTimeout(() => {
                    this.setupKetcherCommunication();
                }, 1000);
            });
        }
    },

    setupKetcherCommunication() {
        // Listen for messages from Ketcher
        window.addEventListener('message', (event) => {
            if (event.data && event.source === document.getElementById('ketcherFrame')?.contentWindow) {
                this.handleKetcherMessage(event.data);
            }
        });
    },

    handleKetcherMessage(data) {
        switch (data.type) {
            case 'molfile':
                if (data.molfile) {
                    this.handleMolfileFromKetcher(data.molfile);
                } else {
                    Utils.showToast('No molecule in sketcher', 'error');
                }
                break;
            case 'smiles':
                if (data.smiles) {
                    this.handleSmilesFromKetcher(data.smiles);
                } else {
                    Utils.showToast('No molecule in sketcher', 'error');
                }
                break;
        }
    },

    async handleMolfileFromKetcher(molfile) {
        try {
            // Update MOL paste area
            const molPaste = document.getElementById('molPaste');
            if (molPaste) {
                molPaste.value = molfile;
            }

            // Convert to XYZ for 3D preview
            const response = await fetch('/molfile_to_xyz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ molfile })
            });

            const data = await response.json();
            if (data.success && data.xyz) {
                ViewerManager.renderMolecule(data.xyz);
                Utils.showToast('Molecule loaded from sketcher');
            } else {
                throw new Error(data.error || 'Conversion failed');
            }
        } catch (error) {
            console.error('Error handling molfile from Ketcher:', error);
            Utils.showToast('Error loading from sketcher: ' + error.message, 'error');
        }
    },

    handleSmilesFromKetcher(smiles) {
        const smilesInput = document.getElementById('smilesPaste');
        if (smilesInput) {
            smilesInput.value = smiles;
        }
        
        // Convert to 3D for preview
        FileManager.previewMolecule(smiles, 'smiles');
        Utils.showToast('SMILES loaded from sketcher');
    },

    requestMolfile() {
        const iframe = document.getElementById('ketcherFrame');
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.postMessage({ type: 'get-molfile' }, '*');
        } else {
            Utils.showToast('Ketcher not available', 'error');
        }
    },

    requestSmiles() {
        const iframe = document.getElementById('ketcherFrame');
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.postMessage({ type: 'get-smiles' }, '*');
        } else {
            Utils.showToast('Ketcher not available', 'error');
        }
    },

    bindEvents() {
        // Load from sketcher button
        const loadBtn = document.getElementById('loadFromSketcher');
        if (loadBtn) {
            loadBtn.addEventListener('click', () => {
                this.requestMolfile();
            });
        }

        // Export buttons
        const exportSmilesBtn = document.getElementById('exportSmiles');
        if (exportSmilesBtn) {
            exportSmilesBtn.addEventListener('click', () => {
                this.requestSmiles();
            });
        }

        // Copy buttons
        const copySmilesBtn = document.getElementById('copySmiles');
        if (copySmilesBtn) {
            copySmilesBtn.addEventListener('click', () => {
                const smiles = document.getElementById('smilesPaste')?.value;
                if (smiles) {
                    Utils.copyToClipboard(smiles);
                } else {
                    Utils.showToast('No SMILES to copy', 'error');
                }
            });
        }

        const copyMolBtn = document.getElementById('copyMol');
        if (copyMolBtn) {
            copyMolBtn.addEventListener('click', () => {
                const mol = document.getElementById('molPaste')?.value;
                if (mol) {
                    Utils.copyToClipboard(mol);
                } else {
                    Utils.showToast('No MOL data to copy', 'error');
                }
            });
        }
    }
};

// Enhanced Job Management
const JobManager = {
    init() {
        this.bindEvents();
    },

    bindEvents() {
        const submitBtn = document.getElementById('launchIAMBtn');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitJob());
        }

        const resetBtn = document.getElementById('resetBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetForm());
        }
    },

    async submitJob() {
        if (IAMState.isLoading) {
            Utils.showToast('Job already in progress', 'error');
            return;
        }

        try {
            this.setLoadingState(true);
            
            const formData = this.collectFormData();
            if (!formData) {
                return; // Error already shown
            }

            // Clear previous results
            this.clearResults();

            const response = await fetch('/run_xtb', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (!response.ok || !result.success) {
                throw new Error(result.error || result.details || 'Job failed');
            }

            this.displayResults(result);
            Utils.showToast('Job completed successfully!');
            
        } catch (error) {
            console.error('Job submission error:', error);
            Utils.showToast('Job failed: ' + error.message, 'error');
            this.displayError(error.message);
        } finally {
            this.setLoadingState(false);
        }
    },

    collectFormData() {
        const fileInput = document.getElementById('xyzFile');
        const molPaste = document.getElementById('molPaste');
        
        let formData = new FormData();
        
        // Handle file input
        if (fileInput?.files?.length > 0) {
            formData.append('file', fileInput.files[0]);
        } else if (molPaste?.value?.trim()) {
            const blob = new Blob([molPaste.value.trim()], { type: 'text/plain' });
            formData.append('file', blob, 'molecule.xyz');
        } else {
            Utils.showToast('Please provide a molecule (file upload or paste)', 'error');
            return null;
        }

        // Add job parameters
        const method = document.getElementById('method')?.value || 'XTB';
        const basis = document.getElementById('basis')?.value || 'def2-SVP';
        const charge = document.getElementById('charge')?.value || '0';
        const multiplicity = document.getElementById('multiplicity')?.value || '1';

        formData.append('method', method);
        formData.append('basis', basis);
        formData.append('charge', charge);
        formData.append('multiplicity', multiplicity);

        return formData;
    },

    setLoadingState(loading) {
        IAMState.isLoading = loading;
        
        const submitBtn = document.getElementById('launchIAMBtn');
        const loadingOverlay = document.getElementById('loadingOverlay');
        
        if (submitBtn) {
            submitBtn.disabled = loading;
            submitBtn.innerHTML = loading ? 
                '<span class="spinner-border spinner-border-sm me-2"></span>Processing...' : 
                'Submit Job';
        }

        if (loadingOverlay) {
            if (loading) {
                loadingOverlay.classList.remove('d-none');
                loadingOverlay.classList.add('d-flex');
            } else {
                loadingOverlay.classList.add('d-none');
                loadingOverlay.classList.remove('d-flex');
            }
        }
    },

    clearResults() {
        const summaryContent = document.getElementById('summaryContent');
        const outputContent = document.getElementById('outputFileContent');
        const logContent = document.getElementById('logFileContent');

        if (summaryContent) {
            summaryContent.innerHTML = '<em class="text-muted">Processing...</em>';
        }
        if (outputContent) {
            outputContent.textContent = '';
        }
        if (logContent) {
            logContent.textContent = '';
        }
    },

    displayResults(result) {
        // Display summary
        if (result.xtb_json) {
            this.displaySummary(result.xtb_json);
        }

        // Display output file
        if (result.output_file) {
            const outputContent = document.getElementById('outputFileContent');
            if (outputContent) {
                outputContent.textContent = result.output_file;
            }
        }

        // Display log file
        if (result.log_file) {
            const logContent = document.getElementById('logFileContent');
            if (logContent) {
                logContent.textContent = result.log_file;
            }
        }

        // Switch to summary tab
        TabManager.showTab('summary');
    },

    displaySummary(xtbData) {
        const summaryContent = document.getElementById('summaryContent');
        if (!summaryContent) return;

        let html = '<div class="summary-results">';
        
        // Key results
        html += '<h6 class="text-primary mb-3">Calculation Results</h6>';
        html += '<table class="summary-table table table-sm">';
        
        if (xtbData.energy) {
            html += `<tr><td class="label-col">Total Energy</td><td class="value-col">${xtbData.energy} Hartree</td></tr>`;
        }
        
        if (xtbData.homo_lumo_gap) {
            html += `<tr><td class="label-col">HOMO-LUMO Gap</td><td class="value-col">${xtbData.homo_lumo_gap} eV</td></tr>`;
        }
        
        if (xtbData.molecular_dipole) {
            html += `<tr><td class="label-col">Dipole Moment</td><td class="value-col">${xtbData.molecular_dipole} Debye</td></tr>`;
        }

        html += '</table>';

        // Additional data
        if (xtbData.charges && xtbData.charges.length > 0) {
            html += '<h6 class="text-secondary mt-4 mb-2">Atomic Charges</h6>';
            html += '<div class="charges-container" style="max-height: 200px; overflow-y: auto;">';
            html += '<table class="table table-sm table-striped">';
            html += '<thead><tr><th>Atom</th><th>Charge</th></tr></thead><tbody>';
            
            xtbData.charges.forEach((charge, index) => {
                html += `<tr><td>Atom ${index + 1}</td><td>${charge.toFixed(4)}</td></tr>`;
            });
            
            html += '</tbody></table></div>';
        }

        html += '</div>';
        summaryContent.innerHTML = html;
    },

    displayError(message) {
        const summaryContent = document.getElementById('summaryContent');
        if (summaryContent) {
            summaryContent.innerHTML = `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle"></i> Error: ${message}</div>`;
        }
    },

    resetForm() {
        // Clear file input
        const fileInput = document.getElementById('xyzFile');
        if (fileInput) {
            fileInput.value = '';
        }

        // Clear text areas
        const molPaste = document.getElementById('molPaste');
        if (molPaste) {
            molPaste.value = '';
        }

        const smilesInput = document.getElementById('smilesPaste');
        if (smilesInput) {
            smilesInput.value = '';
        }

        // Reset to defaults
        const charge = document.getElementById('charge');
        if (charge) {
            charge.value = '0';
        }

        const multiplicity = document.getElementById('multiplicity');
        if (multiplicity) {
            multiplicity.value = '1';
        }

        // Clear 3D viewer
        ViewerManager.renderMolecule('');

        // Clear results
        this.clearResults();

        Utils.showToast('Form reset');
    }
};

// Enhanced IAM Tools Integration
const IAMToolsManager = {
    init() {
        this.bindEvents();
    },

    bindEvents() {
        // Prediction buttons
        const predictStabilityBtn = document.getElementById('predictStability');
        if (predictStabilityBtn) {
            predictStabilityBtn.addEventListener('click', () => this.predictStability());
        }

        const predictVoDBtn = document.getElementById('predictVoD');
        if (predictVoDBtn) {
            predictVoDBtn.addEventListener('click', () => this.predictVoD());
        }

        const optimizeBtn = document.getElementById('optimizePerformance');
        if (optimizeBtn) {
            optimizeBtn.addEventListener('click', () => this.optimizePerformance());
        }

        const reportBtn = document.getElementById('generateReport');
        if (reportBtn) {
            reportBtn.addEventListener('click', () => this.generateReport());
        }
    },

    async predictStability() {
        const input = this.getToolInput();
        if (!input) return;

        try {
            this.setToolLoading(true);
            
            const response = await fetch('/predict_stability', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ molecule: input })
            });

            const result = await response.json();
            this.displayToolResult(result);
            
        } catch (error) {
            this.displayToolError(error.message);
        } finally {
            this.setToolLoading(false);
        }
    },

    async predictVoD() {
        const input = this.getToolInput();
        if (!input) return;

        try {
            this.setToolLoading(true);
            
            const response = await fetch('/predict_vod', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ molecule: input })
            });

            const result = await response.json();
            this.displayToolResult(result);
            
        } catch (error) {
            this.displayToolError(error.message);
        } finally {
            this.setToolLoading(false);
        }
    },

    async optimizePerformance() {
        const input = this.getToolInput();
        if (!input) return;

        try {
            this.setToolLoading(true);
            
            const response = await fetch('/optimize_performance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ molecule: input })
            });

            const result = await response.json();
            this.displayToolResult(result);
            
        } catch (error) {
            this.displayToolError(error.message);
        } finally {
            this.setToolLoading(false);
        }
    },

    async generateReport() {
        const input = this.getToolInput();
        if (!input) return;

        try {
            this.setToolLoading(true);
            
            const response = await fetch('/generate_report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ molecule: input })
            });

            const result = await response.json();
            this.displayToolResult(result);
            
        } catch (error) {
            this.displayToolError(error.message);
        } finally {
            this.setToolLoading(false);
        }
    },

    getToolInput() {
        const smilesInput = document.getElementById('smilesInput');
        if (!smilesInput || !smilesInput.value.trim()) {
            Utils.showToast('Please enter a molecule in the Tools input field', 'error');
            return null;
        }
        return smilesInput.value.trim();
    },

    setToolLoading(loading) {
        const buttons = [
            'predictStability',
            'predictVoD',
            'optimizePerformance',
            'generateReport'
        ];

        buttons.forEach(id => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.disabled = loading;
                if (loading) {
                    btn.innerHTML = btn.innerHTML.replace(/^.*?>/, '<span class="spinner-border spinner-border-sm me-1"></span>');
                }
            }
        });

        if (loading) {
            this.displayToolResult('Processing...');
        }
    },

    displayToolResult(result) {
        const output = document.getElementById('result-output');
        if (output) {
            if (typeof result === 'object') {
                output.textContent = JSON.stringify(result, null, 2);
            } else {
                output.textContent = result;
            }
        }
    },

    displayToolError(message) {
        const output = document.getElementById('result-output');
        if (output) {
            output.innerHTML = `<span class="text-danger">Error: ${message}</span>`;
        }
    }
};

// Global functions for inline event handlers (backwards compatibility)
function showResultTab(tabId) {
    TabManager.showTab(tabId);
}

function predictStability() {
    IAMToolsManager.predictStability();
}

function predictVoD() {
    IAMToolsManager.predictVoD();
}

function optimizePerformance() {
    IAMToolsManager.optimizePerformance();
}

function generateReport() {
    IAMToolsManager.generateReport();
}

// CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .drag-over {
        background-color: var(--primary-blue) !important;
        opacity: 0.1 !important;
        border: 2px dashed var(--primary-blue) !important;
    }
`;
document.head.appendChild(style);

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('IAM Application initializing...');
    
    // Initialize all managers
    ThemeManager.init();
    ViewerManager.init();
    TabManager.init();
    FileManager.init();
    KetcherManager.init();
    JobManager.init();
    IAMToolsManager.init();
    
    console.log('IAM Application initialized successfully');
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        IAMState,
        Utils,
        ThemeManager,
        ViewerManager,
        TabManager,
        FileManager,
        KetcherManager,
        JobManager,
        IAMToolsManager
    };
}
