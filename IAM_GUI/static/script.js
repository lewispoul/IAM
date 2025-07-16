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
        if (/^\d+\s*\n/.test(trimmed)) {
            type = 'xyz';
        } else if (/V2000|V3000/.test(trimmed)) {
            type = 'mol';
        }
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
            viewer.addModel(trimmed, "xyz");
            viewer.setStyle({}, { stick: {} });
            viewer.zoomTo();
            viewer.render();
        } else if (type === 'mol') {
            fetch('/molfile_to_xyz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ molfile: trimmed })
            })
            .then(async r => {
                let data;
                try { data = await r.json(); } catch (jsonErr) {
                    alert('Server error: Invalid JSON response');
                    throw jsonErr;
                }
                if (!r.ok || !data.success || !data.xyz) {
                    alert('Failed to convert MOL to 3D preview: ' + (data && (data.error || data.details) ? (data.error || data.details) : 'Unknown error'));
                    return;
                }
                viewer.addModel(data.xyz, "xyz");
                viewer.setStyle({}, { stick: {} });
                viewer.zoomTo();
                viewer.render();
            })
            .catch(err => {
                alert('Network or server error: ' + err.message);
            });
        } else {
            // Show error in UI
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
            let formData = new FormData();
            if (fileInput.files.length) {
                formData.append('file', fileInput.files[0]);
            } else if (pasteInput) {
                const blob = new Blob([pasteInput], { type: 'text/plain' });
                formData.append('file', blob, 'pasted.xyz');
            } else {
                alert('Please select a file or paste content.');
                return;
            }
            try {
                const response = await fetch('/run_xtb', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                if (result.xyz) {
                    renderMolecule(result.xyz);
                } else {
                    alert('No geometry returned from backend.');
                }
            } catch (error) {
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
            const TIMEOUT_MS = 3000;
            function handler(event) {
                // Only accept messages from the same origin and from the correct iframe
                if (event.source !== ketcherFrame.contentWindow) return;
                if (event.origin !== window.location.origin) return;
                if (event.data && event.data.type === 'molfile') {
                    replied = true;
                    window.removeEventListener('message', handler);
                    const molfile = event.data.molfile;
                    if (!molfile) {
                        alert('No molecule in sketcher.');
                        return;
                    }
                    // Convert MOL to XYZ for 3D preview
                    fetch('/molfile_to_xyz', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ molfile })
                    })
                    .then(async r => {
                        let data;
                        try { data = await r.json(); } catch (jsonErr) {
                            alert('Server error: Invalid JSON response');
                            throw jsonErr;
                        }
                        if (!r.ok || !data.success || !data.xyz) {
                            alert('Failed to convert MOL to 3D preview: ' + (data && (data.error || data.details) ? (data.error || data.details) : 'Unknown error'));
                            return;
                        }
                        renderMoleculeAuto(data.xyz);
                        if (document.getElementById('summaryContent')) {
                            document.getElementById('summaryContent').innerHTML = '<em>Preview loaded. Submit to run calculation.</em>';
                        }
                    })
                    .catch(err => {
                        alert('Network or server error: ' + err.message);
                    });
                }
            }
            window.addEventListener('message', handler);
            // Send request to Ketcher for molfile
            ketcherFrame.contentWindow.postMessage({ type: 'get-molfile' }, window.location.origin);
            // Timeout if no response
            setTimeout(() => {
                if (!replied) {
                    window.removeEventListener('message', handler);
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

    document.getElementById('optimize3D').addEventListener('click', async function () {
        const viewerDiv = document.getElementById('viewer');
        const xyzData = viewerDiv.dataset.xyz || ''; // Récupérer les données XYZ du viewer
        if (!xyzData) {
            showErrorModal('No structure loaded in viewer.');
            return;
        }
        showSpinner();
        try {
            const response = await fetch('/run_xtb', {
                method: 'POST',
                body: JSON.stringify({ xyz: xyzData }),
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (result.success) {
                updateViewer(result.xyz);
                updateSummary(result.xtb_json);
            } else {
                showErrorModal(result.error);
            }
        } catch (error) {
            showErrorModal(error.message);
        } finally {
            hideSpinner();
        }
    });

    document.getElementById('drawPointGroup').addEventListener('click', async function () {
        const viewerDiv = document.getElementById('viewer');
        const xyzData = viewerDiv.dataset.xyz || ''; // Récupérer les données XYZ du viewer
        if (!xyzData) {
            showErrorModal('No structure loaded in viewer.');
            return;
        }
        showSpinner();
        try {
            const response = await fetch('/compute_symmetry', {
                method: 'POST',
                body: JSON.stringify({ xyz: xyzData }),
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (result.success) {
                updateSummary({ symmetry: result.symmetry });
            } else {
                showErrorModal(result.error);
            }
        } catch (error) {
            showErrorModal(error.message);
        } finally {
            hideSpinner();
        }
    });

    // Gestion du panneau IAM Tools

    document.getElementById('predictStability').addEventListener('click', async function () {
        const smiles = document.getElementById('smilesInput').value;
        if (!smiles) {
            showErrorModal('Please enter SMILES or MOL data.');
            return;
        }
        showSpinner();
        try {
            const response = await fetch('/predict_stability', {
                method: 'POST',
                body: JSON.stringify({ smiles }),
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (result.success) {
                updateIAMToolsOutput(result.stability);
            } else {
                showErrorModal(result.error);
            }
        } catch (error) {
            showErrorModal(error.message);
        } finally {
            hideSpinner();
        }
    });

    document.getElementById('predictVoD').addEventListener('click', async function () {
        const smiles = document.getElementById('smilesInput').value;
        if (!smiles) {
            showErrorModal('Please enter SMILES or MOL data.');
            return;
        }
        showSpinner();
        try {
            const response = await fetch('/predict_vod', {
                method: 'POST',
                body: JSON.stringify({ smiles }),
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (result.success) {
                updateIAMToolsOutput(result.vod);
            } else {
                showErrorModal(result.error);
            }
        } catch (error) {
            showErrorModal(error.message);
        } finally {
            hideSpinner();
        }
    });

    document.getElementById('generateReport').addEventListener('click', async function () {
        const smiles = document.getElementById('smilesInput').value;
        if (!smiles) {
            showErrorModal('Please enter SMILES or MOL data.');
            return;
        }
        showSpinner();
        try {
            const response = await fetch('/generate_report', {
                method: 'POST',
                body: JSON.stringify({ smiles }),
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (result.success) {
                updateIAMToolsOutput(result.report);
            } else {
                showErrorModal(result.error);
            }
        } catch (error) {
            showErrorModal(error.message);
        } finally {
            hideSpinner();
        }
    });

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
});
