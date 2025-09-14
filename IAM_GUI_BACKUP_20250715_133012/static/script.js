document.addEventListener("DOMContentLoaded", function () {
    console.log('DOMContentLoaded fired, DOM is ready.');

    // Tab switching
    function showTab(tabName) {
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        if (document.getElementById(tabName)) {
            document.getElementById(tabName).classList.add('active');
        }
        if (tabName === 'summary' && document.getElementById('tabSummaryBtn')) document.getElementById('tabSummaryBtn').classList.add('active');
        if (tabName === 'input' && document.getElementById('tabInputBtn')) document.getElementById('tabInputBtn').classList.add('active');
        if (tabName === 'output' && document.getElementById('tabOutputBtn')) document.getElementById('tabOutputBtn').classList.add('active');
    }

    // --- Improved showTab for IAM Tools and all custom tabs ---
    function showTab(id) {
        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(div => {
            div.style.display = 'none';
        });

        // Remove 'active' class from all tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });

        // Show the selected tab
        const el = document.getElementById(id);
        if (el) el.style.display = 'block';

        // Add 'active' class to the clicked button
        const button = Array.from(document.querySelectorAll('.tab-button')).find(btn => btn.onclick?.toString().includes(id));
        if (button) {
            button.classList.add('active');
        }
    }

    // Attach tab button listeners if elements exist
    if (document.getElementById('tabSummaryBtn')) document.getElementById('tabSummaryBtn').addEventListener('click', function() { showTab('summary'); });
    if (document.getElementById('tabInputBtn')) document.getElementById('tabInputBtn').addEventListener('click', function() { showTab('input'); });
    if (document.getElementById('tabOutputBtn')) document.getElementById('tabOutputBtn').addEventListener('click', function() { showTab('output'); });

    // --- Helper: Detect file format and render in 3Dmol.js ---
    // Enhanced rendering logic
    function renderMoleculeAuto(contents) {
        const trimmed = contents.trim();
        let type = null;
        
        // Meilleure détection de format
        if (/^\d+\s*\n/.test(trimmed)) {
            type = 'xyz';
        } else if (/V2000|V3000|M  END|\$\$\$\$/.test(trimmed)) {
            type = 'mol';
        } else if (trimmed.includes('\n') && trimmed.split('\n').length > 2) {
            // Essayer de détecter si c'est du XYZ mal formaté
            const lines = trimmed.split('\n');
            try {
                const firstLine = parseInt(lines[0].trim());
                if (!isNaN(firstLine) && firstLine > 0 && lines.length >= firstLine + 2) {
                    type = 'xyz';
                }
            } catch (e) {
                // Pas du XYZ
            }
        }
        
        console.log('Format détecté:', type, 'pour contenu:', trimmed.substring(0, 100));
        
        const viewerDiv = document.getElementById("viewer");
        if (!viewerDiv) {
            alert('3D viewer element (id="viewer") not found in DOM.');
            return;
        }
        let viewer;
        try {
            viewer = $3Dmol.createViewer(viewerDiv, { backgroundColor: "white" });
        } catch (e) {
            alert('3Dmol.js failed to initialize: ' + e);
            return;
        }
        
        if (type === 'xyz') {
            try {
                viewer.addModel(trimmed, "xyz");
                viewer.setStyle({}, { stick: {} });
                viewer.zoomTo();
                viewer.render();
                
                // Stocker les données XYZ dans le viewer pour utilisation ultérieure
                viewerDiv.dataset.xyz = trimmed;
                
                if (document.getElementById('summaryContent')) {
                    document.getElementById('summaryContent').innerHTML = '<em>✅ XYZ loaded successfully. Ready for calculation.</em>';
                }
            } catch (e) {
                console.error('Erreur rendu XYZ:', e);
                alert('Error rendering XYZ format: ' + e.message);
            }
        } else if (type === 'mol') {
            fetch('/molfile_to_xyz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ molfile: trimmed })
            })
            .then(async r => {
                let data;
                try { data = await r.json(); } catch (jsonErr) {
                    console.error('JSON Parse Error:', jsonErr);
                    alert('Server error: Invalid JSON response');
                    throw jsonErr;
                }
                if (!r.ok || !data.success || !data.xyz) {
                    console.error('Conversion MOL failed:', data);
                    alert('Failed to convert MOL to 3D preview: ' + (data && data.error ? data.error : 'Unknown error'));
                    return;
                }
                
                // Succès - rendu XYZ
                viewer.addModel(data.xyz, "xyz");
                viewer.setStyle({}, { stick: {} });
                viewer.zoomTo();
                viewer.render();
                
                // Stocker les données XYZ converties
                viewerDiv.dataset.xyz = data.xyz;
                
                if (document.getElementById('summaryContent')) {
                    document.getElementById('summaryContent').innerHTML = '<em>✅ MOL converted and loaded. Ready for calculation.</em>';
                }
            })
            .catch(err => {
                console.error('Network error:', err);
                alert('Network or server error: ' + err.message);
            });
        } else {
            // Show error in UI
            console.error('Format non supporté:', trimmed.substring(0, 200));
            if (document.getElementById('summaryContent')) {
                document.getElementById('summaryContent').innerHTML = '<span style="color:#b00;">❌ Error: Unsupported file format for preview. Please use XYZ or MOL format.</span>';
            }
            // Optionally show toast or alert
            if (window.showToastMsg) {
                showToastMsg('Unsupported file format for preview. Expected XYZ or MOL format.', true);
            } else {
                alert('Unsupported file format for preview. Expected XYZ or MOL format.');
            }
        }
    }
            if (document.getElementById('summaryContent')) {
                document.getElementById('summaryContent').innerHTML = '<span style="color:#b00;">Error: Unsupported file format for preview.</span>';
            }
            // Optionally show toast or alert
            if (window.showToastMsg) {
                showToastMsg('Unsupported file format for preview.', true);
            } else {
                alert('Unsupported file format for preview.');
            }
        }
    }

    // 3D Viewer rendering
    function renderMolecule(contents) {
        const viewerDiv = document.getElementById("viewer");
        if (!viewerDiv) {
            alert('3D viewer element (id="viewer") not found in DOM.');
            return;
        }
        let viewer;
        try {
            viewer = $3Dmol.createViewer(viewerDiv, { backgroundColor: "white" });
        } catch (e) {
            alert('3Dmol.js failed to initialize: ' + e);
            return;
        }
        viewer.addModel(contents, "xyz");
        viewer.setStyle({}, { stick: {} });
        viewer.zoomTo();
        viewer.render();
    }

    // File upload to 3D viewer (auto-preview, robust)
    if (document.getElementById('xyzFile')) {
        document.getElementById('xyzFile').addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (file && (file.name.endsWith('.xyz') || file.name.endsWith('.mol'))) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    try {
                        renderMoleculeAuto(e.target.result);
                        if (document.getElementById('summaryContent')) {
                            document.getElementById('summaryContent').innerHTML = '<em>Preview loaded. Submit to run calculation.</em>';
                        }
                    } catch (err) {
                        alert('Failed to render molecule: ' + err);
                    }
                };
                reader.readAsText(file);
            }
        });
    }

    // Paste and Import (XYZ/MOL) to 3D viewer (auto-preview, robust)
    if (document.getElementById('loadFromPasteBtn')) {
        document.getElementById('loadFromPasteBtn').addEventListener('click', function () {
            const contents = document.getElementById('xyzPaste').value.trim();
            if (!contents) {
                alert('Please paste .xyz or .mol content.');
                return;
            }
            try {
                renderMoleculeAuto(contents);
                if (document.getElementById('summaryContent')) {
                    document.getElementById('summaryContent').innerHTML = '<em>Preview loaded. Submit to run calculation.</em>';
                }
            } catch (err) {
                alert('Failed to render molecule: ' + err);
            }
        });
    }

    // Submit job
    // Enhanced event listeners
    if (document.getElementById('launchIAMBtn')) {
        document.getElementById('launchIAMBtn').addEventListener('click', async function () {
            const fileInput = document.getElementById('xyzFile');
            const pasteInput = document.getElementById('xyzPaste').value.trim();
            const viewerDiv = document.getElementById('viewer');
            
            // Priorité: données dans le viewer, puis fichier, puis paste
            let xyzData = viewerDiv.dataset.xyz;
            
            let formData = new FormData();
            
            if (xyzData) {
                // Utiliser les données du viewer (optimisé)
                const blob = new Blob([xyzData], { type: 'text/plain' });
                formData.append('file', blob, 'viewer.xyz');
                console.log('Utilisation des données du viewer 3D');
            } else if (fileInput.files.length) {
                formData.append('file', fileInput.files[0]);
                console.log('Utilisation du fichier uploadé');
            } else if (pasteInput) {
                const blob = new Blob([pasteInput], { type: 'text/plain' });
                formData.append('file', blob, 'pasted.xyz');
                console.log('Utilisation des données collées');
            } else {
                alert('Please select a file, paste content, or load a molecule in the 3D viewer.');
                return;
            }
            
            // Affichage de l'état de progression
            if (document.getElementById('summaryContent')) {
                document.getElementById('summaryContent').innerHTML = '<em>🔄 Running XTB calculation...</em>';
            }
            
            try {
                const response = await fetch('/run_xtb', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                console.log('Résultat XTB:', result);
                
                if (result.success) {
                    // Afficher la géométrie optimisée si disponible
                    if (result.optimized_xyz || result.xyz) {
                        const newXyz = result.optimized_xyz || result.xyz;
                        renderMolecule(newXyz);
                        
                        // Mettre à jour les données du viewer
                        viewerDiv.dataset.xyz = newXyz;
                    }
                    
                    // Afficher les résultats dans l'onglet Summary
                    updateSummaryFromXTB(result);
                    
                    // Afficher l'onglet Output avec les logs
                    updateOutputFromXTB(result);
                    
                    // Notification de succès
                    if (window.showToastMsg) {
                        showToastMsg('✅ XTB calculation completed successfully!', false);
                    }
                    
                } else {
                    // Gestion des erreurs
                    console.error('Erreur XTB:', result);
                    
                    let errorMessage = result.error || 'Unknown error';
                    
                    // Si on a une géométrie optimisée malgré l'erreur JSON
                    if (result.partial_success && result.optimized_xyz) {
                        renderMolecule(result.optimized_xyz);
                        viewerDiv.dataset.xyz = result.optimized_xyz;
                        errorMessage += '\n\n✅ Geometry optimization succeeded, but JSON output failed.';
                        
                        // Afficher les infos partielles
                        updateSummaryPartial(result);
                    }
                    
                    if (document.getElementById('summaryContent')) {
                        document.getElementById('summaryContent').innerHTML = 
                            `<span style="color:#b00;">❌ ${errorMessage}</span>`;
                    }
                    
                    // Afficher les logs pour debugging
                    updateOutputFromXTB(result);
                    
                    alert('XTB calculation failed: ' + errorMessage);
                }
            } catch (error) {
                console.error('Network error:', error);
                if (document.getElementById('summaryContent')) {
                    document.getElementById('summaryContent').innerHTML = 
                        `<span style="color:#b00;">❌ Network error: ${error.message}</span>`;
                }
                alert('Error submitting job: ' + error.message);
            }
        });
    }

    // Load molecule from SMILES input and render in 3D viewer
    if (document.getElementById('loadFromSMILESBtn')) {
        document.getElementById('loadFromSMILESBtn').addEventListener('click', async function () {
            const smiles = document.getElementById('smilesInput').value.trim();
            if (!smiles) {
                alert('Please enter a SMILES string.');
                return;
            }
            // Call backend to convert SMILES to XYZ
            const response = await fetch('/smiles_to_xyz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ smiles })
            });
            const data = await response.json();
            if (data.success && data.xyz) {
                renderMolecule(data.xyz);
            } else {
                alert('Failed to convert SMILES to 3D structure.');
            }
        });
    }

    // Ketcher/Sketcher integration: render in 3D viewer after backend conversion (robust, with timeout)
    if (document.getElementById('loadFromKetcherBtn')) {
        document.getElementById('loadFromKetcherBtn').addEventListener('click', async function () {
            const ketcherFrame = document.getElementById('ketcherFrame');
            if (!ketcherFrame) {
                alert('Ketcher iframe not found.');
                return;
            }
            const ketcher = ketcherFrame.contentWindow;
            if (!ketcher) {
                alert('Ketcher not loaded.');
                return;
            }
            let replied = false;
            const TIMEOUT_MS = 5000; // Augmenté à 5 secondes
            
            function handler(event) {
                // Only accept messages from the same origin and from the correct iframe
                if (event.source !== ketcherFrame.contentWindow) return;
                if (event.origin !== window.location.origin) return;
                
                if (event.data && event.data.type === 'molfile') {
                    replied = true;
                    window.removeEventListener('message', handler);
                    const molfile = event.data.molfile;
                    if (!molfile || molfile.trim() === '') {
                        alert('No molecule in sketcher.');
                        return;
                    }
                    
                    console.log('Molfile reçu:', molfile.substring(0, 100) + '...');
                    
                    // Convert MOL to XYZ for 3D preview
                    fetch('/molfile_to_xyz', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ molfile: molfile })
                    })
                    .then(async r => {
                        let data;
                        try { 
                            data = await r.json(); 
                        } catch (jsonErr) {
                            console.error('JSON Parse Error:', jsonErr);
                            alert('Server error: Invalid JSON response');
                            throw jsonErr;
                        }
                        
                        console.log('Réponse backend:', data);
                        
                        if (!r.ok || !data.success || !data.xyz) {
                            const errorMsg = data && data.error ? data.error : 'Conversion failed';
                            alert('Failed to convert MOL to 3D preview: ' + errorMsg);
                            return;
                        }
                        
                        // Succès - afficher dans le viewer 3D
                        renderMolecule(data.xyz);
                        
                        // Mettre à jour le résumé
                        if (document.getElementById('summaryContent')) {
                            document.getElementById('summaryContent').innerHTML = '<em>Molecule loaded from Ketcher. Ready for calculation.</em>';
                        }
                        
                        // Afficher une notification de succès
                        if (window.showToastMsg) {
                            showToastMsg('Molecule loaded successfully from Ketcher!', false);
                        }
                    })
                    .catch(err => {
                        console.error('Network error:', err);
                        alert('Network or server error: ' + err.message);
                    });
                }
            }
            
            window.addEventListener('message', handler);
            
            // Send request to Ketcher for molfile
            console.log('Demande molfile à Ketcher...');
            ketcherFrame.contentWindow.postMessage({ type: 'get-molfile' }, window.location.origin);
            
            // Timeout if no response
            setTimeout(() => {
                if (!replied) {
                    window.removeEventListener('message', handler);
                    console.error('Timeout: pas de réponse de Ketcher');
                    alert('Error: No response from Ketcher sketcher. Is it loaded and same-origin?');
                }
            }, TIMEOUT_MS);
        });
    }

    // Search molecule placeholder
    if (document.getElementById('searchMoleculeBtn')) {
        document.getElementById('searchMoleculeBtn').addEventListener('click', function () {
            alert('Search functionality not implemented yet.');
        });
    }

    // Ajout de la gestion du mode sombre
    const darkModeSwitch = document.getElementById('darkModeSwitch');
    if (darkModeSwitch) {
        darkModeSwitch.addEventListener('change', function () {
            document.body.classList.toggle('dark-mode', darkModeSwitch.checked);
            localStorage.setItem('darkMode', darkModeSwitch.checked ? 'enabled' : 'disabled');
        });

        // Charger l'état du mode sombre depuis le stockage local
        const darkModeState = localStorage.getItem('darkMode');
        if (darkModeState === 'enabled') {
            darkModeSwitch.checked = true;
            document.body.classList.add('dark-mode');
        }
    }

    // Gestion des boutons Optimize Structure in 3D et Draw Point Group Elements
    if (document.getElementById('optimize3D')) {
        document.getElementById('optimize3D').addEventListener('click', async function () {
            const viewerDiv = document.getElementById('viewer');
            const xyzData = viewerDiv.dataset.xyz || ''; // Récupérer les données XYZ du viewer
            if (!xyzData) {
                showToastMsg('No structure loaded in viewer.', true);
                return;
            }
            showToastMsg('🔄 Running 3D optimization...', false);
            try {
                const response = await fetch('/run_xtb', {
                    method: 'POST',
                    body: JSON.stringify({ xyz: xyzData }),
                    headers: { 'Content-Type': 'application/json' }
                });
                const result = await response.json();
                if (result.success) {
                    if (result.optimized_xyz || result.xyz) {
                        renderMolecule(result.optimized_xyz || result.xyz);
                        viewerDiv.dataset.xyz = result.optimized_xyz || result.xyz;
                    }
                    updateSummaryFromXTB(result);
                    showToastMsg('✅ 3D optimization completed!', false);
                } else {
                    showToastMsg('❌ Optimization failed: ' + result.error, true);
                }
            } catch (error) {
                showToastMsg('❌ Error: ' + error.message, true);
            }
        });
    }

    if (document.getElementById('drawPointGroup')) {
        document.getElementById('drawPointGroup').addEventListener('click', async function () {
            const viewerDiv = document.getElementById('viewer');
            const xyzData = viewerDiv.dataset.xyz || ''; // Récupérer les données XYZ du viewer
            if (!xyzData) {
                showToastMsg('No structure loaded in viewer.', true);
                return;
            }
            showToastMsg('🔄 Computing symmetry...', false);
            try {
                const response = await fetch('/compute_symmetry', {
                    method: 'POST',
                    body: JSON.stringify({ xyz: xyzData }),
                    headers: { 'Content-Type': 'application/json' }
                });
                const result = await response.json();
                if (result.success) {
                    updateSummaryFromSymmetry(result);
                    showToastMsg('✅ Symmetry analysis completed!', false);
                } else {
                    showToastMsg('❌ Symmetry analysis failed: ' + result.error, true);
                }
            } catch (error) {
                showToastMsg('❌ Symmetry endpoint not implemented yet', true);
            }
        });
    }

    // Gestion du panneau IAM Tools avec event listeners corrigés
    if (document.getElementById('predictStability')) {
        document.getElementById('predictStability').addEventListener('click', async function () {
            const viewerDiv = document.getElementById('viewer');
            const xyzData = viewerDiv.dataset.xyz || '';
            if (!xyzData) {
                showToastMsg('Please load a molecule in the 3D viewer first.', true);
                return;
            }
            showToastMsg('🔄 Predicting stability...', false);
            try {
                const response = await fetch('/predict_stability', {
                    method: 'POST',
                    body: JSON.stringify({ xyz: xyzData }),
                    headers: { 'Content-Type': 'application/json' }
                });
                const result = await response.json();
                if (result.success || result.stability) {
                    updateIAMToolsOutput(result.stability || result);
                    showToastMsg('✅ Stability prediction completed!', false);
                } else {
                    showToastMsg('❌ Stability prediction failed: ' + (result.error || 'Unknown error'), true);
                }
            } catch (error) {
                showToastMsg('❌ Stability prediction not yet implemented', true);
            }
        });
    }

    if (document.getElementById('predictVoD')) {
        document.getElementById('predictVoD').addEventListener('click', async function () {
            const viewerDiv = document.getElementById('viewer');
            const xyzData = viewerDiv.dataset.xyz || '';
            if (!xyzData) {
                showToastMsg('Please load a molecule in the 3D viewer first.', true);
                return;
            }
            showToastMsg('🔄 Predicting velocity of detonation...', false);
            try {
                const response = await fetch('/predict_vod', {
                    method: 'POST',
                    body: JSON.stringify({ xyz: xyzData }),
                    headers: { 'Content-Type': 'application/json' }
                });
                const result = await response.json();
                if (result.vod_predicted) {
                    const vodData = {
                        vod: result.vod_predicted,
                        model: result.model,
                        confidence: result.confidence,
                        note: result.note
                    };
                    updateIAMToolsOutput(vodData);
                    showToastMsg('✅ VoD prediction completed!', false);
                } else {
                    showToastMsg('❌ VoD prediction failed: ' + (result.error || 'Unknown error'), true);
                }
            } catch (error) {
                showToastMsg('❌ Error: ' + error.message, true);
            }
        });
    }

    if (document.getElementById('generateReport')) {
        document.getElementById('generateReport').addEventListener('click', async function () {
            const viewerDiv = document.getElementById('viewer');
            const xyzData = viewerDiv.dataset.xyz || '';
            if (!xyzData) {
                showToastMsg('Please load a molecule in the 3D viewer first.', true);
                return;
            }
            showToastMsg('🔄 Generating comprehensive report...', false);
            try {
                const response = await fetch('/generate_report', {
                    method: 'POST',
                    body: JSON.stringify({ xyz: xyzData }),
                    headers: { 'Content-Type': 'application/json' }
                });
                const result = await response.json();
                if (result.success || result.report) {
                    updateIAMToolsOutput(result.report || result);
                    showToastMsg('✅ Report generated successfully!', false);
                } else {
                    showToastMsg('❌ Report generation failed: ' + (result.error || 'Unknown error'), true);
                }
            } catch (error) {
                showToastMsg('❌ Report generation not yet implemented', true);
            }
        });
    }

    // Fonctions pour les boutons Predict Stability, Predict VoD, et Generate Report

    async function predictStability() {
        const viewerDiv = document.getElementById('viewer');
        const xyzData = viewerDiv.dataset.xyz || ''; // Récupérer les données XYZ du viewer
        if (!xyzData) {
            showErrorModal('No structure loaded in viewer.');
            return;
        }
        showSpinner();
        try {
            const response = await fetch('/predict_stability', {
                method: 'POST',
                body: JSON.stringify({ xyz: xyzData }),
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (result.result) {
                document.getElementById('result-output').textContent = JSON.stringify(result.result, null, 2);
            } else {
                showErrorModal(result.error);
            }
        } catch (error) {
            showErrorModal(error.message);
        } finally {
            hideSpinner();
        }
    }

    async function predictVoD() {
        const viewerDiv = document.getElementById('viewer');
        const xyzData = viewerDiv.dataset.xyz || ''; // Récupérer les données XYZ du viewer
        if (!xyzData) {
            showErrorModal('No structure loaded in viewer.');
            return;
        }
        showSpinner();
        try {
            const response = await fetch('/predict_vod', {
                method: 'POST',
                body: JSON.stringify({ xyz: xyzData }),
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (result.result) {
                document.getElementById('result-output').textContent = JSON.stringify(result.result, null, 2);
            } else {
                showErrorModal(result.error);
            }
        } catch (error) {
            showErrorModal(error.message);
        } finally {
            hideSpinner();
        }
    }

    async function generateReport() {
        const viewerDiv = document.getElementById('viewer');
        const xyzData = viewerDiv.dataset.xyz || ''; // Récupérer les données XYZ du viewer
        if (!xyzData) {
            showErrorModal('No structure loaded in viewer.');
            return;
        }
        showSpinner();
        try {
            const response = await fetch('/generate_report', {
                method: 'POST',
                body: JSON.stringify({ xyz: xyzData }),
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (result.result) {
                document.getElementById('result-output').textContent = JSON.stringify(result.result, null, 2);
            } else {
                showErrorModal(result.error);
            }
        } catch (error) {
            showErrorModal(error.message);
        } finally {
            hideSpinner();
        }
    }

    // Add event listeners for functional buttons

    document.getElementById('resymmetrizeBtn').addEventListener('click', () => {
        resymmetrizeStructure();
    });

    document.getElementById('drawSymmetryBtn').addEventListener('click', () => {
        drawPointGroupElements();
    });

    document.getElementById('optimizeBtn').addEventListener('click', () => {
        optimizeStructure3D();
    });

    document.getElementById('deleteHBtn').addEventListener('click', () => {
        deleteAllHydrogens();
    });

    document.getElementById('saveStructBtn').addEventListener('click', () => {
        saveStructureToFile();
    });

    // Define functions for button actions
    function resymmetrizeStructure() {
        console.log('Resymmetrizing structure...');
        // Logic for resymmetrizing the structure
    }

    function drawPointGroupElements() {
        console.log('Drawing point group elements...');
        // Logic for drawing symmetry elements
    }

    function optimizeStructure3D() {
        console.log('Optimizing structure in 3D...');
        fetch('/run_xtb', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: 'optimize' }),
        })
            .then(response => response.json())
            .then(data => {
                console.log('Optimization result:', data);
                // Update viewer with optimized structure
            })
            .catch(error => console.error('Error optimizing structure:', error));
    }

    function deleteAllHydrogens() {
        console.log('Deleting all hydrogens...');
        // Logic for removing hydrogen atoms from the viewer
    }

    function saveStructureToFile() {
        console.log('Saving structure to file...');
        // Logic for exporting the structure and triggering a download
    }
    
    // Fonctions utilitaires pour afficher les résultats XTB
    function updateSummaryFromXTB(result) {
        const summaryContent = document.getElementById('summaryContent');
        if (!summaryContent) return;
        
        let html = '<h5>✅ XTB Calculation Results</h5>';
        
        if (result.xtb_json) {
            const data = result.xtb_json;
            html += '<table class="table table-sm summary-table">';
            
            if (data.total_energy) {
                html += `<tr><td><strong>Total Energy</strong></td><td>${data.total_energy} Eh</td></tr>`;
            }
            if (data.homo_lumo_gap) {
                html += `<tr><td><strong>HOMO-LUMO Gap</strong></td><td>${data.homo_lumo_gap} eV</td></tr>`;
            }
            if (data.dipole_moment) {
                html += `<tr><td><strong>Dipole Moment</strong></td><td>${data.dipole_moment} Debye</td></tr>`;
            }
            
            html += `<tr><td><strong>Method</strong></td><td>${result.method || 'XTB GFN2-xTB'}</td></tr>`;
            html += `<tr><td><strong>Status</strong></td><td>✅ Converged</td></tr>`;
            html += '</table>';
        }
        
        summaryContent.innerHTML = html;
    }
    
    function updateSummaryPartial(result) {
        const summaryContent = document.getElementById('summaryContent');
        if (!summaryContent) return;
        
        let html = '<h5>⚠️ XTB Partial Results</h5>';
        html += '<table class="table table-sm summary-table">';
        
        if (result.energy_info && result.energy_info.total_energy) {
            html += `<tr><td><strong>Total Energy</strong></td><td>${result.energy_info.total_energy} ${result.energy_info.unit}</td></tr>`;
        }
        
        html += `<tr><td><strong>Method</strong></td><td>XTB GFN2-xTB</td></tr>`;
        html += `<tr><td><strong>Status</strong></td><td>⚠️ Optimization OK, JSON failed</td></tr>`;
        html += `<tr><td><strong>Geometry</strong></td><td>✅ Optimized</td></tr>`;
        html += '</table>';
        
        summaryContent.innerHTML = html;
    }
    
    function updateOutputFromXTB(result) {
        const outputTab = document.getElementById('output');
        if (!outputTab) return;
        
        let html = '<h5>XTB Output Logs</h5>';
        html += '<div style="font-family: monospace; background: #f8f9fa; padding: 10px; border-radius: 5px; max-height: 300px; overflow-y: auto;">';
        
        if (result.stdout) {
            html += '<h6>Standard Output:</h6>';
            html += '<pre>' + result.stdout + '</pre>';
        }
        
        if (result.stderr) {
            html += '<h6>Standard Error:</h6>';
            html += '<pre style="color: red;">' + result.stderr + '</pre>';
        }
        
        if (result.files_created) {
            html += '<h6>Files Created:</h6>';
            html += '<ul>';
            result.files_created.forEach(file => {
                html += `<li>${file}</li>`;
            });
            html += '</ul>';
        }
        
        html += '</div>';
        outputTab.innerHTML = html;
    }
    
    function showToastMsg(message, isError = false) {
        // Créer ou réutiliser le container toast
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
            `;
            document.body.appendChild(toastContainer);
        }
        
        // Créer le toast
        const toast = document.createElement('div');
        toast.className = `alert ${isError ? 'alert-danger' : 'alert-success'} alert-dismissible fade show`;
        toast.style.cssText = 'margin-bottom: 10px; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto-remove après 5 secondes
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }
    
    // Fonction pour mettre à jour l'affichage des résultats IAM Tools
    function updateIAMToolsOutput(data) {
        const outputElement = document.getElementById('result-output');
        if (!outputElement) {
            console.warn('result-output element not found');
            return;
        }
        
        let html = '<h5>IAM Tools Results</h5>';
        
        if (typeof data === 'object') {
            html += '<table class="table table-sm">';
            for (const [key, value] of Object.entries(data)) {
                html += `<tr><td><strong>${key}</strong></td><td>${value}</td></tr>`;
            }
            html += '</table>';
        } else {
            html += `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        }
        
        outputElement.innerHTML = html;
    }
    
    // Fonction pour mettre à jour les résultats de symétrie
    function updateSummaryFromSymmetry(result) {
        const summaryContent = document.getElementById('summaryContent');
        if (!summaryContent) return;
        
        let html = '<h5>🔬 Symmetry Analysis Results</h5>';
        html += '<table class="table table-sm summary-table">';
        
        if (result.symmetry) {
            html += `<tr><td><strong>Point Group</strong></td><td>${result.symmetry.point_group || 'Unknown'}</td></tr>`;
            html += `<tr><td><strong>Symmetry Elements</strong></td><td>${result.symmetry.elements || 'None detected'}</td></tr>`;
        }
        
        html += '</table>';
        summaryContent.innerHTML = html;
    }

    // Fonctions globales pour les boutons onclick dans le HTML
    window.predictStability = async function() {
        document.getElementById('predictStability').click();
    };
    
    window.predictVoD = async function() {
        document.getElementById('predictVoD').click();
    };
    
    window.generateReport = async function() {
        document.getElementById('generateReport').click();
    };
});
