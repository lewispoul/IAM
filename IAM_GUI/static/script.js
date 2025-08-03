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
    function renderMoleculeAuto(contents) {
        // Simple heuristics: XYZ starts with a number, MOL contains 'V2000' or 'V3000'
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
            // Convert MOL to XYZ via backend for reliable 3D rendering
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
    if (document.getElementById('launchIAMBtn')) {
        document.getElementById('launchIAMBtn').addEventListener('click', async function () {
            alert('launchIAM called');
            const fileInput = document.getElementById('xyzFile');
            const pasteInput = document.getElementById('xyzPaste').value.trim();
            console.log('fileInput.files:', fileInput.files);
            if (!fileInput.files.length && !pasteInput) {
                alert('No file selected and no pasted content.');
            }
            if (fileInput.files.length) {
                alert('File selected: ' + fileInput.files[0].name);
            }
            if (pasteInput) {
                alert('Using pasted content.');
            }
            let formData = new FormData();
            if (fileInput.files.length) {
                formData.append('file', fileInput.files[0]);
            } else if (pasteInput) {
                // Convert pasted text to a Blob and append as file
                const blob = new Blob([pasteInput], { type: 'text/plain' });
                formData.append('file', blob, 'pasted.xyz');
            } else {
                alert('Veuillez sélectionner un fichier .xyz ou coller le contenu dans la zone de texte.');
                return;
            }
            formData.append('method', document.getElementById('method').value);
            formData.append('basis', document.getElementById('basis').value);
            formData.append('charge', document.getElementById('charge').value);
            formData.append('multiplicity', document.getElementById('multiplicity').value);
            formData.append('calcType', document.getElementById('calcType').value);
            formData.append('solvent', document.getElementById('solvent').value);
            if (document.getElementById('method').value === 'psi4') {
                formData.append('functional', document.getElementById('functional').value);
            }
            try {
                const response = await fetch('/run_xtb', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();

                // --- PATCH: Always update 3Dmol viewer with returned geometry ---
                if (result.xyz) {
                    const viewerDiv = document.getElementById("viewer");
                    if (viewerDiv) {
                        // Try to preserve background color if viewer already exists
                        let bgColor = "white";
                        if (viewerDiv.viewer && viewerDiv.viewer.getConfig) {
                            const cfg = viewerDiv.viewer.getConfig();
                            if (cfg && cfg.backgroundColor) bgColor = cfg.backgroundColor;
                        }
                        // Clear viewerDiv
                        viewerDiv.innerHTML = '';
                        let viewer;
                        try {
                            viewer = $3Dmol.createViewer(viewerDiv, { backgroundColor: bgColor });
                            viewerDiv.viewer = viewer; // Store for later
                        } catch (e) {
                            alert('3Dmol.js failed to initialize: ' + e);
                            throw e;
                        }
                        try {
                            viewer.addModel(result.xyz.trim(), "xyz");
                            viewer.setStyle({}, { stick: {} });
                            viewer.zoomTo();
                            viewer.render();
                        } catch (e) {
                            alert('Failed to render returned geometry: ' + e);
                        }
                    }
                } else {
                    // If xyz missing, show error/toast
                    if (window.showToastMsg) {
                        showToastMsg('No geometry returned from calculation.', true);
                    } else {
                        alert('No geometry returned from calculation.');
                    }
                }
                // --- END PATCH ---

                // Format summary output for XTB and future Psi4
                if (result.success && result.xtb_json) {
                    const xtb = result.xtb_json;
                    let html = '<table class="summary-table">';
                    if (xtb["total energy"]) html += `<tr><td class="label-col">Total Energy (Eh)</td><td class="value-col">${xtb["total energy"]}</td></tr>`;
                    if (xtb["HOMO-LUMO gap/eV"]) html += `<tr><td class="label-col">HOMO-LUMO gap (eV)</td><td class="value-col">${xtb["HOMO-LUMO gap/eV"]}</td></tr>`;
                    if (xtb["dipole"]) html += `<tr><td class="label-col">Dipole moment (D)</td><td class="value-col">${xtb["dipole"]}</td></tr>`;
                    if (xtb["xtb version"]) html += `<tr><td class="label-col">XTB version</td><td class="value-col">${xtb["xtb version"]}</td></tr>`;
                    html += '</table>';
                    // Collapsible section for arrays
                    if (xtb["charges"]) {
                        html += `<details><summary>Atomic Charges</summary><pre>${JSON.stringify(xtb["charges"], null, 2)}</pre></details>`;
                    }
                    if (xtb["wbo"]) {
                        html += `<details><summary>Wiberg Bond Orders</summary><pre>${JSON.stringify(xtb["wbo"], null, 2)}</pre></details>`;
                    }
                    document.getElementById('summaryContent').innerHTML = html;
                } else if (result.success && result.psi4_json) {
                    const psi4 = result.psi4_json;
                    let html = '<table class="summary-table">';
                    if (psi4.final_energy !== undefined) html += `<tr><td class="label-col">Final Energy (Eh)</td><td class="value-col">${psi4.final_energy}</td></tr>`;
                    if (psi4.psi4_version) html += `<tr><td class="label-col">Psi4 Version</td><td class="value-col">${psi4.psi4_version}</td></tr>`;
                    html += '</table>';
                    html += `<details><summary>Stdout</summary><pre>${psi4.stdout || ''}</pre></details>`;
                    html += `<details><summary>Stderr</summary><pre>${psi4.stderr || ''}</pre></details>`;
                    document.getElementById('summaryContent').innerHTML = html;
                } else if (result.details) {
                    document.getElementById('summaryContent').textContent = result.details;
                } else {
                    document.getElementById('summaryContent').textContent = JSON.stringify(result, null, 2);
                }

                // Always clear input file content before updating
                document.getElementById('inputFileContent').textContent = '';
                if (result.file_preview) {
                    document.getElementById('inputFileContent').textContent = result.file_preview;
                } else if (result.details && result.details.includes('Aucun fichier reçu')) {
                    document.getElementById('inputFileContent').textContent = 'No file received by backend.';
                } else {
                    document.getElementById('inputFileContent').textContent = 'No file';
                }
                document.getElementById('outputFileContent').textContent = result["output_file"] || JSON.stringify(result, null, 2);

                showTab('summary');
            } catch (err) {
                alert('Erreur réseau ou de calcul : ' + err);
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
});
