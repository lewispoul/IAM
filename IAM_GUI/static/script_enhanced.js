// Enhanced IAM Script - Performance Optimized Original Layout
(function() {
    'use strict';
    
    // Performance optimization: Cache DOM elements
    const domCache = new Map();
    const getDOMElement = (id) => {
        if (!domCache.has(id)) {
            domCache.set(id, document.getElementById(id));
        }
        return domCache.get(id);
    };
    
    // Debounce utility for performance
    const debounce = (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };
    
    // Throttle utility for performance
    const throttle = (func, limit) => {
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
    };
    
    // Loading state management
    const loadingStates = new Set();
    
    const showLoading = (element, text = 'Loading...') => {
        if (typeof element === 'string') {
            element = getDOMElement(element);
        }
        if (!element) return;
        
        loadingStates.add(element);
        element.style.position = 'relative';
        
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="loading-spinner"></div>
            <span class="loading-text">${text}</span>
        `;
        loadingOverlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            border-radius: inherit;
        `;
        
        element.appendChild(loadingOverlay);
    };
    
    const hideLoading = (element) => {
        if (typeof element === 'string') {
            element = getDOMElement(element);
        }
        if (!element) return;
        
        loadingStates.delete(element);
        const overlay = element.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    };
    
    // Enhanced error handling
    const showError = (message, container = null) => {
        console.error('IAM Error:', message);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            <strong>Error:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const targetContainer = container || document.querySelector('.container-fluid');
        if (targetContainer) {
            targetContainer.insertBefore(errorDiv, targetContainer.firstChild);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.remove();
                }
            }, 5000);
        }
    };
    
    const showSuccess = (message, container = null) => {
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success alert-dismissible fade show';
        successDiv.innerHTML = `
            <i class="bi bi-check-circle-fill me-2"></i>
            <strong>Success:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const targetContainer = container || document.querySelector('.container-fluid');
        if (targetContainer) {
            targetContainer.insertBefore(successDiv, targetContainer.firstChild);
            
            // Auto-remove after 3 seconds
            setTimeout(() => {
                if (successDiv.parentNode) {
                    successDiv.remove();
                }
            }, 3000);
        }
    };
    
    // Enhanced tab management
    let activeTab = 'summary';
    
    const showTab = (tabName) => {
        // Hide all tab contents with smooth transition
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.style.opacity = '0';
            setTimeout(() => {
                tab.classList.remove('active');
                tab.style.display = 'none';
            }, 150);
        });
        
        // Remove active class from all tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Show selected tab with animation
        setTimeout(() => {
            const selectedTab = getDOMElement(tabName);
            if (selectedTab) {
                selectedTab.style.display = 'block';
                selectedTab.classList.add('active');
                setTimeout(() => {
                    selectedTab.style.opacity = '1';
                }, 50);
            }
            
            // Add active class to corresponding button
            const button = document.querySelector(`[onclick*="${tabName}"]`);
            if (button) {
                button.classList.add('active');
            }
            
            activeTab = tabName;
        }, 150);
    };
    
    // Enhanced 3D viewer with performance optimizations
    let viewer3D = null;
    let currentMolecule = null;
    
    const initializeViewer = () => {
        const viewerElement = getDOMElement('viewer');
        if (!viewerElement || viewer3D) return;
        
        try {
            const config = {
                backgroundColor: 'white',
                antialias: true,
                alpha: true
            };
            
            viewer3D = $3Dmol.createViewer(viewerElement, config);
            
            // Add performance monitoring
            viewer3D.setBackgroundColor(0xffffff);
            viewer3D.render();
            
            console.log('3D Viewer initialized successfully');
        } catch (error) {
            console.error('Failed to initialize 3D viewer:', error);
            showError('Failed to initialize 3D molecular viewer');
        }
    };
    
    // Enhanced molecule rendering with caching
    const moleculeCache = new Map();
    
    const renderMoleculeAuto = (contents, format = 'auto') => {
        if (!viewer3D) {
            initializeViewer();
        }
        
        if (!contents || !contents.trim()) {
            console.warn('Empty molecule data provided');
            return;
        }
        
        // Check cache first
        const cacheKey = `${contents}_${format}`;
        if (moleculeCache.has(cacheKey)) {
            const cached = moleculeCache.get(cacheKey);
            viewer3D.clear();
            viewer3D.addModel(cached.model, cached.format);
            viewer3D.setStyle({}, {stick: {}, sphere: {scale: 0.3}});
            viewer3D.zoomTo();
            viewer3D.render();
            return;
        }
        
        try {
            let detectedFormat = format;
            
            if (format === 'auto') {
                if (contents.includes('END') && contents.includes('ATOM')) {
                    detectedFormat = 'pdb';
                } else if (contents.includes('@@')) {
                    detectedFormat = 'mol';
                } else if (contents.match(/^\s*\d+\s*$/m)) {
                    detectedFormat = 'xyz';
                } else {
                    detectedFormat = 'sdf';
                }
            }
            
            viewer3D.clear();
            const model = viewer3D.addModel(contents, detectedFormat);
            
            // Cache the model
            moleculeCache.set(cacheKey, { model: contents, format: detectedFormat });
            
            // Enhanced styling
            viewer3D.setStyle({}, {
                stick: { 
                    radius: 0.1,
                    colorscheme: 'default'
                },
                sphere: { 
                    scale: 0.3,
                    colorscheme: 'default'
                }
            });
            
            viewer3D.zoomTo();
            viewer3D.render();
            
            currentMolecule = { contents, format: detectedFormat };
            console.log(`Molecule rendered with format: ${detectedFormat}`);
            
        } catch (error) {
            console.error('Error rendering molecule:', error);
            showError(`Failed to render molecule: ${error.message}`);
        }
    };
    
    // Enhanced file handling with drag & drop
    const setupFileHandling = () => {
        const fileInput = getDOMElement('fileInput');
        const xyzTextarea = getDOMElement('xyzTextarea');
        
        if (fileInput) {
            fileInput.addEventListener('change', handleFileSelect, false);
        }
        
        // Enhanced drag and drop
        const dropZones = document.querySelectorAll('.file-upload-area, #sketcher-container');
        
        dropZones.forEach(zone => {
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.stopPropagation();
                zone.classList.add('dragover');
            });
            
            zone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                e.stopPropagation();
                zone.classList.remove('dragover');
            });
            
            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                e.stopPropagation();
                zone.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    handleFileSelect({ target: { files } });
                }
            });
        });
    };
    
    const handleFileSelect = (event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        const xyzTextarea = getDOMElement('xyzTextarea');
        
        showLoading('panel-left', 'Loading file...');
        
        const reader = new FileReader();
        reader.onload = function(e) {
            const contents = e.target.result;
            
            if (xyzTextarea) {
                xyzTextarea.value = contents;
            }
            
            // Auto-render if it looks like molecular data
            if (contents.trim()) {
                renderMoleculeAuto(contents);
                showSuccess(`File "${file.name}" loaded successfully`);
            }
            
            hideLoading('panel-left');
        };
        
        reader.onerror = function() {
            hideLoading('panel-left');
            showError('Failed to read file');
        };
        
        reader.readAsText(file);
    };
    
    // Enhanced XTB calculation with progress tracking
    const runXTBCalculation = async () => {
        const fileInput = getDOMElement('fileInput');
        const xyzTextarea = getDOMElement('xyzTextarea');
        
        let fileToSend = null;
        let xyzContent = '';
        
        if (fileInput && fileInput.files.length > 0) {
            fileToSend = fileInput.files[0];
        } else if (xyzTextarea && xyzTextarea.value.trim()) {
            xyzContent = xyzTextarea.value.trim();
            
            // Create a blob from textarea content
            const blob = new Blob([xyzContent], { type: 'text/plain' });
            fileToSend = new File([blob], 'molecule.xyz', { type: 'text/plain' });
        } else {
            showError('Please provide a molecule file or paste XYZ coordinates');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', fileToSend);
        
        // Get calculation options
        const optimizeGeometry = getDOMElement('optimizeGeometry')?.checked || false;
        const calculateCharges = getDOMElement('calculateCharges')?.checked || false;
        const calculateBonds = getDOMElement('calculateBonds')?.checked || false;
        
        formData.append('optimize_geometry', optimizeGeometry);
        formData.append('calculate_charges', calculateCharges);
        formData.append('calculate_bonds', calculateBonds);
        
        const runButton = getDOMElement('runXTBBtn');
        if (runButton) {
            runButton.disabled = true;
            runButton.innerHTML = '<span class="loading-spinner"></span> Running...';
        }
        
        try {
            showLoading('viewer-container', 'Running XTB calculation...');
            
            const response = await fetch('/run_xtb', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                showSuccess('XTB calculation completed successfully');
                
                // Display results
                displayXTBResults(result);
                
                // Update 3D viewer with optimized geometry if available
                if (result.optimized_xyz) {
                    renderMoleculeAuto(result.optimized_xyz);
                }
                
                // Switch to output tab
                showTab('output');
                
            } else {
                showError(result.error || 'XTB calculation failed');
            }
            
        } catch (error) {
            console.error('XTB calculation error:', error);
            showError('Failed to run XTB calculation. Please check your connection and try again.');
        } finally {
            hideLoading('viewer-container');
            
            if (runButton) {
                runButton.disabled = false;
                runButton.innerHTML = '<i class="bi bi-play-fill"></i> Run XTB';
            }
        }
    };
    
    // Enhanced results display
    const displayXTBResults = (results) => {
        const outputDiv = getDOMElement('output');
        if (!outputDiv) return;
        
        let html = '<div class="results-container">';
        
        if (results.energy) {
            html += `
                <div class="result-section">
                    <h5><i class="bi bi-lightning-fill"></i> Energy</h5>
                    <p><strong>Total Energy:</strong> ${results.energy} Hartree</p>
                </div>
            `;
        }
        
        if (results.charges) {
            html += `
                <div class="result-section">
                    <h5><i class="bi bi-atom"></i> Atomic Charges</h5>
                    <div class="table-responsive">
                        <table class="table table-sm table-striped">
                            <thead>
                                <tr><th>Atom</th><th>Charge</th></tr>
                            </thead>
                            <tbody>
            `;
            
            results.charges.forEach((charge, index) => {
                html += `<tr><td>Atom ${index + 1}</td><td>${charge.toFixed(4)}</td></tr>`;
            });
            
            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }
        
        if (results.wiberg_bond_orders) {
            html += `
                <div class="result-section">
                    <h5><i class="bi bi-diagram-3"></i> Bond Orders</h5>
                    <div class="bond-orders">
                        ${results.wiberg_bond_orders.map(bond => 
                            `<span class="badge bg-secondary me-1">${bond.atoms.join('-')}: ${bond.order.toFixed(3)}</span>`
                        ).join('')}
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        outputDiv.innerHTML = html;
    };
    
    // Ketcher integration enhancements
    const setupKetcherIntegration = () => {
        const ketcherFrame = getDOMElement('ketcherFrame');
        if (!ketcherFrame) return;
        
        // Wait for Ketcher to load
        ketcherFrame.addEventListener('load', () => {
            console.log('Ketcher loaded successfully');
            
            // Setup message handling for Ketcher communication
            window.addEventListener('message', (event) => {
                if (event.source === ketcherFrame.contentWindow) {
                    handleKetcherMessage(event.data);
                }
            });
        });
    };
    
    const handleKetcherMessage = (data) => {
        // Handle messages from Ketcher iframe
        console.log('Message from Ketcher:', data);
    };
    
    const loadFromSketcher = async () => {
        const ketcherFrame = getDOMElement('ketcherFrame');
        if (!ketcherFrame || !ketcherFrame.contentWindow) {
            showError('Ketcher sketcher not available');
            return;
        }
        
        try {
            showLoading('sketcher-container', 'Loading from sketcher...');
            
            // Get MOL data from Ketcher
            const molData = await new Promise((resolve, reject) => {
                const timeout = setTimeout(() => reject(new Error('Timeout')), 5000);
                
                ketcherFrame.contentWindow.postMessage({
                    action: 'getMol'
                }, '*');
                
                const handleMessage = (event) => {
                    if (event.data.type === 'molData') {
                        clearTimeout(timeout);
                        window.removeEventListener('message', handleMessage);
                        resolve(event.data.mol);
                    }
                };
                
                window.addEventListener('message', handleMessage);
            });
            
            if (molData) {
                // Convert MOL to XYZ via backend
                const response = await fetch('/molfile_to_xyz', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ molfile: molData })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    const xyzTextarea = getDOMElement('xyzTextarea');
                    if (xyzTextarea) {
                        xyzTextarea.value = result.xyz;
                    }
                    
                    renderMoleculeAuto(result.xyz);
                    showSuccess('Molecule loaded from sketcher');
                } else {
                    showError(result.error || 'Failed to convert molecule');
                }
            }
            
        } catch (error) {
            console.error('Error loading from sketcher:', error);
            showError('Failed to load molecule from sketcher');
        } finally {
            hideLoading('sketcher-container');
        }
    };
    
    // Dark mode functionality
    const setupDarkMode = () => {
        const darkModeSwitch = getDOMElement('darkModeSwitch');
        const darkModeLabel = getDOMElement('darkModeLabel');
        
        if (!darkModeSwitch) return;
        
        // Load saved preference
        const savedMode = localStorage.getItem('darkMode');
        if (savedMode === 'true') {
            document.documentElement.setAttribute('data-theme', 'dark');
            darkModeSwitch.checked = true;
            if (darkModeLabel) darkModeLabel.textContent = 'Light Mode';
        }
        
        darkModeSwitch.addEventListener('change', () => {
            const isDark = darkModeSwitch.checked;
            
            if (isDark) {
                document.documentElement.setAttribute('data-theme', 'dark');
                if (darkModeLabel) darkModeLabel.textContent = 'Light Mode';
            } else {
                document.documentElement.removeAttribute('data-theme');
                if (darkModeLabel) darkModeLabel.textContent = 'Dark Mode';
            }
            
            localStorage.setItem('darkMode', isDark);
            
            // Update 3D viewer background
            if (viewer3D) {
                viewer3D.setBackgroundColor(isDark ? 0x1a1a1a : 0xffffff);
                viewer3D.render();
            }
        });
    };
    
    // Performance monitoring
    const performanceMonitor = {
        start: Date.now(),
        marks: new Map(),
        
        mark(name) {
            this.marks.set(name, Date.now());
        },
        
        measure(name, startMark) {
            const start = this.marks.get(startMark) || this.start;
            const duration = Date.now() - start;
            console.log(`⏱️ ${name}: ${duration}ms`);
            return duration;
        }
    };
    
    // Initialize everything when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        performanceMonitor.mark('dom-ready');
        console.log('🚀 IAM Enhanced Script - DOM Ready');
        
        // Initialize components
        setupDarkMode();
        setupFileHandling();
        setupKetcherIntegration();
        
        // Initialize 3D viewer with delay for better performance
        setTimeout(() => {
            initializeViewer();
            performanceMonitor.measure('3D Viewer Init', 'dom-ready');
        }, 100);
        
        // Setup event listeners
        const runXTBBtn = getDOMElement('runXTBBtn');
        if (runXTBBtn) {
            runXTBBtn.addEventListener('click', runXTBCalculation);
        }
        
        const loadFromSketcherBtn = getDOMElement('loadFromSketcher');
        if (loadFromSketcherBtn) {
            loadFromSketcherBtn.addEventListener('click', loadFromSketcher);
        }
        
        // Setup tab navigation
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const tabName = button.getAttribute('data-tab') || 
                              (button.onclick ? button.onclick.toString().match(/'([^']+)'/)?.[1] : null);
                if (tabName) {
                    showTab(tabName);
                }
            });
        });
        
        // Show initial tab
        showTab('summary');
        
        // Performance measurement
        performanceMonitor.measure('Full Initialization', 'dom-ready');
        
        console.log('✅ IAM Enhanced Script - Fully Initialized');
    });
    
    // Expose global functions for backward compatibility
    window.showTab = showTab;
    window.renderMoleculeAuto = renderMoleculeAuto;
    window.runXTBCalculation = runXTBCalculation;
    window.loadFromSketcher = loadFromSketcher;
    
    // Enhanced prediction functions
    window.predictStabilityEnhanced = function() {
        const smilesInput = getDOMElement('smilesInputTools');
        const resultOutput = getDOMElement('enhancedResultOutput');
        
        if (!smilesInput || !smilesInput.value.trim()) {
            alert('Please enter SMILES or molecular data first');
            return;
        }
        
        showLoading(resultOutput, 'Analyzing molecular stability...');
        
        fetch('/predict_stability', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                xyz: smilesInput.value.trim()
            })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading(resultOutput);
            if (data.success) {
                resultOutput.textContent = JSON.stringify(data.result, null, 2);
            } else {
                resultOutput.textContent = 'Error: ' + (data.error || 'Unknown error');
            }
        })
        .catch(error => {
            hideLoading(resultOutput);
            resultOutput.textContent = 'Network error: ' + error.message;
        });
    };
    
    window.predictVoDEnhanced = function() {
        const smilesInput = getDOMElement('smilesInputTools');
        const resultOutput = getDOMElement('enhancedResultOutput');
        
        if (!smilesInput || !smilesInput.value.trim()) {
            alert('Please enter SMILES or molecular data first');
            return;
        }
        
        showLoading(resultOutput, 'Calculating velocity of detonation...');
        
        fetch('/predict_vod', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                xyz: smilesInput.value.trim()
            })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading(resultOutput);
            if (data.success) {
                resultOutput.textContent = JSON.stringify(data.result, null, 2);
            } else {
                resultOutput.textContent = 'Error: ' + (data.error || 'Unknown error');
            }
        })
        .catch(error => {
            hideLoading(resultOutput);
            resultOutput.textContent = 'Network error: ' + error.message;
        });
    };
    
    window.optimizePerformanceEnhanced = function() {
        const smilesInput = getDOMElement('smilesInputTools');
        const resultOutput = getDOMElement('enhancedResultOutput');
        
        if (!smilesInput || !smilesInput.value.trim()) {
            alert('Please enter SMILES or molecular data first');
            return;
        }
        
        showLoading(resultOutput, 'Optimizing molecular performance...');
        
        fetch('/optimize_performance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                xyz: smilesInput.value.trim()
            })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading(resultOutput);
            if (data.success) {
                resultOutput.textContent = JSON.stringify(data.result, null, 2);
            } else {
                resultOutput.textContent = 'Error: ' + (data.error || 'Unknown error');
            }
        })
        .catch(error => {
            hideLoading(resultOutput);
            resultOutput.textContent = 'Network error: ' + error.message;
        });
    };
    
    window.generateReportEnhanced = function() {
        const smilesInput = getDOMElement('smilesInputTools');
        const resultOutput = getDOMElement('enhancedResultOutput');
        
        if (!smilesInput || !smilesInput.value.trim()) {
            alert('Please enter SMILES or molecular data first');
            return;
        }
        
        showLoading(resultOutput, 'Generating comprehensive report...');
        
        fetch('/generate_report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                xyz: smilesInput.value.trim()
            })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading(resultOutput);
            if (data.success) {
                resultOutput.textContent = JSON.stringify(data.result, null, 2);
            } else {
                resultOutput.textContent = 'Error: ' + (data.error || 'Unknown error');
            }
        })
        .catch(error => {
            hideLoading(resultOutput);
            resultOutput.textContent = 'Network error: ' + error.message;
        });
    };
    
    window.openProfessionalMolecularOrbitals = function() {
        window.open('/professional_molecular_orbitals', '_blank');
    };
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (viewer3D) {
            viewer3D.clear();
        }
        moleculeCache.clear();
        domCache.clear();
    });
    
})();
