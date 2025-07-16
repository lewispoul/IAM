/* ================================================================
   IAM Molecule Viewer - JavaScript Controller
   Complete rewrite with all functionality connected
   ================================================================ */

// Global variables
let currentViewer = null;
let currentMolecule = null;
let isGodModeActive = false;
let isDarkModeActive = false;
let isRotationActive = false;
let agentEndpoint = "http://127.0.0.1:5001";

// ================ INITIALIZATION ================
document.addEventListener("DOMContentLoaded", function() {
    console.log("IAM Molecule Viewer - Initializing...");
    
    initializeViewer();
    setupEventListeners();
    setupModuleTabs();
    setupResultTabs();
    setupInputTabs();
    setupViewerControls();
    setupParameterControls();
    setupStructureTools();
    setupAgentControls();
    setupFileManagement();
    loadDefaultMolecule();
    
    console.log("IAM Molecule Viewer - Ready!");
});

// ================ 3DMOL VIEWER INITIALIZATION ================
function initializeViewer() {
    const viewerDiv = document.getElementById("viewer");
    if (!viewerDiv) {
        console.error("3D viewer element not found!");
        return;
    }
    
    try {
        currentViewer = $3Dmol.createViewer(viewerDiv, {
            backgroundColor: "white",
            antialias: true,
            fog: true,
            shadowmap: true
        });
        
        // Set default style
        currentViewer.setStyle({}, {stick: {radius: 0.2, colorscheme: "default"}});
        currentViewer.zoomTo();
        currentViewer.render();
        
        console.log("3Dmol viewer initialized successfully");
        updateDebugInfo("xtbStatus", "Viewer Ready", "success");
    } catch (error) {
        console.error("Failed to initialize 3Dmol viewer:", error);
        showAlert("Failed to initialize 3D viewer: " + error.message, "danger");
    }
}

// ================ EVENT LISTENERS SETUP ================
function setupEventListeners() {
    // Dark Mode Toggle
    const darkModeBtn = document.getElementById("toggleDarkMode");
    if (darkModeBtn) {
        darkModeBtn.addEventListener("click", toggleDarkMode);
    }
    
    // God Mode Toggle
    const godModeBtn = document.getElementById("toggleGodMode");
    if (godModeBtn) {
        godModeBtn.addEventListener("click", toggleGodMode);
    }
    
    // Advanced Options Toggle
    const advancedCheckbox = document.getElementById("showAdvanced");
    if (advancedCheckbox) {
        advancedCheckbox.addEventListener("change", toggleAdvancedOptions);
    }
    
    // Solvent Flag Toggle
    const solventFlag = document.getElementById("solventFlag");
    if (solventFlag) {
        solventFlag.addEventListener("change", toggleSolventOptions);
    }
    
    // Manual Coordinates Toggle
    const manualCoords = document.getElementById("manualCoordinates");
    if (manualCoords) {
        manualCoords.addEventListener("change", toggleCoordinateEditor);
    }
    
    // Manual Masses Toggle
    const manualMasses = document.getElementById("manualMasses");
    if (manualMasses) {
        manualMasses.addEventListener("change", toggleMassColumn);
    }
}

// ================ MODULE TAB MANAGEMENT ================
function setupModuleTabs() {
    const tabButtons = document.querySelectorAll('#moduleNavTabs .nav-link');
    tabButtons.forEach(button => {
        button.addEventListener('shown.bs.tab', function(e) {
            const targetTab = e.target.getAttribute('data-bs-target');
            console.log(`Switched to module: ${targetTab}`);
            
            // Refresh viewer when returning to computational tab
            if (targetTab === '#computational' && currentViewer) {
                setTimeout(() => {
                    currentViewer.resize();
                    currentViewer.render();
                }, 100);
            }
        });
    });
}

// ================ RESULT TABS MANAGEMENT ================
function setupResultTabs() {
    const resultTabs = document.querySelectorAll('#resultTabs .nav-link');
    resultTabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            const targetTab = e.target.getAttribute('data-bs-target');
            console.log(`Switched to result tab: ${targetTab}`);
        });
    });
}

// ================ INPUT TABS MANAGEMENT ================
function setupInputTabs() {
    // SMILES Input
    const smilesBtn = document.getElementById("loadFromSmiles");
    if (smilesBtn) {
        smilesBtn.addEventListener("click", loadFromSmiles);
    }
    
    // File Input
    const fileBtn = document.getElementById("loadFromFile");
    if (fileBtn) {
        fileBtn.addEventListener("click", loadFromFile);
    }
    
    // File input change
    const fileInput = document.getElementById("fileInput");
    if (fileInput) {
        fileInput.addEventListener("change", handleFileSelect);
    }
    
    // Sketcher Input
    const sketcherBtn = document.getElementById("loadFromSketcher");
    if (sketcherBtn) {
        sketcherBtn.addEventListener("click", loadFromSketcher);
    }
    
    // Setup Ketcher iframe communication
    setupKetcherCommunication();
}

// ================ VIEWER CONTROLS ================
function setupViewerControls() {
    // Reset View
    const resetViewBtn = document.getElementById("resetView");
    if (resetViewBtn) {
        resetViewBtn.addEventListener("click", resetView);
    }
    
    // Center View
    const centerViewBtn = document.getElementById("centerView");
    if (centerViewBtn) {
        centerViewBtn.addEventListener("click", centerView);
    }
    
    // Toggle Rotation
    const rotationBtn = document.getElementById("toggleRotation");
    if (rotationBtn) {
        rotationBtn.addEventListener("click", toggleRotation);
    }
    
    // Style Controls
    setupStyleControls();
}

function setupStyleControls() {
    const styleButtons = [
        {id: "styleBallStick", style: {sphere: {scale: 0.3}, stick: {radius: 0.2}}},
        {id: "styleStick", style: {stick: {radius: 0.2}}},
        {id: "styleSphere", style: {sphere: {scale: 0.8}}},
        {id: "styleWireframe", style: {stick: {radius: 0.05}}}
    ];
    
    styleButtons.forEach(({id, style}) => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener("click", () => setMoleculeStyle(style, btn));
        }
    });
}

// ================ PARAMETER CONTROLS ================
function setupParameterControls() {
    // Run Calculation
    const runBtn = document.getElementById("runCalculation");
    if (runBtn) {
        runBtn.addEventListener("click", runCalculation);
    }
    
    // Reset Parameters
    const resetBtn = document.getElementById("resetParameters");
    if (resetBtn) {
        resetBtn.addEventListener("click", resetParameters);
    }
    
    // Save Parameters
    const saveBtn = document.getElementById("saveParameters");
    if (saveBtn) {
        saveBtn.addEventListener("click", saveParameters);
    }
}

// ================ STRUCTURE TOOLS ================
function setupStructureTools() {
    const tools = [
        {id: "resymmetrize", endpoint: "/resymmetrize_structure"},
        {id: "optimizeStructure", endpoint: "/optimize_structure"},
        {id: "deleteHydrogens", func: deleteHydrogens},
        {id: "addHydrogens", func: addHydrogens},
        {id: "drawPointGroup", endpoint: "/add_point_group"}
    ];
    
    tools.forEach(({id, endpoint, func}) => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener("click", () => {
                if (func) {
                    func();
                } else if (endpoint) {
                    callStructureEndpoint(endpoint);
                }
            });
        }
    });
    
    // Update Coordinates
    const updateBtn = document.getElementById("updateCoordinates");
    if (updateBtn) {
        updateBtn.addEventListener("click", updateCoordinates);
    }
}

// ================ AGENT CONTROLS ================
function setupAgentControls() {
    const agentButtons = [
        {id: "generateModule", endpoint: "/generate_module", data: {}},
        {id: "listModules", endpoint: "/list_modules", data: {}},
        {id: "runBackup", endpoint: "/run_backup", data: {}},
        {id: "runShell", endpoint: "/run_shell", data: {command: "ls -la"}},
        {id: "testScript", endpoint: "/test_script", data: {}},
        {id: "logFeedback", endpoint: "/log_feedback", data: {}}
    ];
    
    agentButtons.forEach(({id, endpoint, data}) => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener("click", () => postToAgent(endpoint, data));
        }
    });
    
    // Execute Command
    const executeBtn = document.getElementById("executeCommand");
    const commandInput = document.getElementById("agentCommand");
    if (executeBtn && commandInput) {
        executeBtn.addEventListener("click", executeAgentCommand);
        commandInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") executeAgentCommand();
        });
    }
}

// ================ FILE MANAGEMENT ================
function setupFileManagement() {
    // Export buttons
    const exportButtons = [
        {id: "exportXYZ", format: "xyz"},
        {id: "exportJSON", format: "json"},
        {id: "exportAll", format: "all"}
    ];
    
    exportButtons.forEach(({id, format}) => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener("click", () => exportResults(format));
        }
    });
    
    // Save to File
    const saveBtn = document.getElementById("saveToFile");
    if (saveBtn) {
        saveBtn.addEventListener("click", saveToFile);
    }
    
    // Copy to Clipboard
    const copyBtn = document.getElementById("copyToClipboard");
    if (copyBtn) {
        copyBtn.addEventListener("click", copyToClipboard);
    }
    
    // Export Temp Files
    const exportTempBtn = document.getElementById("exportTempFiles");
    if (exportTempBtn) {
        exportTempBtn.addEventListener("click", exportTempFiles);
    }
}

// ================ MOLECULE LOADING FUNCTIONS ================
async function loadFromSmiles() {
    const smilesInput = document.getElementById("smilesInput");
    const smiles = smilesInput?.value?.trim();
    
    if (!smiles) {
        showAlert("Please enter a SMILES string", "warning");
        return;
    }
    
    showLoading("Converting SMILES to 3D structure...");
    
    try {
        const response = await fetch("/smiles_to_xyz", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({smiles: smiles})
        });
        
        const result = await response.json();
        
        if (result.success && result.xyz) {
            renderMolecule(result.xyz);
            currentMolecule = result.xyz;
            addLogEntry(`Loaded molecule from SMILES: ${smiles}`);
            populateCoordinateTable(result.xyz);
        } else {
            throw new Error(result.error || "Failed to convert SMILES");
        }
    } catch (error) {
        console.error("SMILES conversion error:", error);
        showAlert("Failed to convert SMILES: " + error.message, "danger");
        updateDebugInfo("lastError", error.message, "danger");
    } finally {
        hideLoading();
    }
}

async function loadFromFile() {
    const fileInput = document.getElementById("fileInput");
    const pasteInput = document.getElementById("pasteInput");
    
    let fileContent = null;
    let filename = "pasted_structure";
    
    if (fileInput?.files?.length > 0) {
        const file = fileInput.files[0];
        filename = file.name;
        fileContent = await readFileAsText(file);
    } else if (pasteInput?.value?.trim()) {
        fileContent = pasteInput.value.trim();
    } else {
        showAlert("Please select a file or paste content", "warning");
        return;
    }
    
    showLoading("Loading structure...");
    
    try {
        // Detect file format and process accordingly
        if (filename.endsWith('.xyz') || /^\d+\s*\n/.test(fileContent)) {
            // XYZ format
            renderMolecule(fileContent);
            currentMolecule = fileContent;
            populateCoordinateTable(fileContent);
        } else if (filename.endsWith('.mol') || /V2000|V3000/.test(fileContent)) {
            // MOL format - convert to XYZ
            await convertMolToXYZ(fileContent);
        } else {
            throw new Error("Unsupported file format");
        }
        
        addLogEntry(`Loaded structure from file: ${filename}`);
    } catch (error) {
        console.error("File loading error:", error);
        showAlert("Failed to load file: " + error.message, "danger");
        updateDebugInfo("lastError", error.message, "danger");
    } finally {
        hideLoading();
    }
}

async function convertMolToXYZ(molContent) {
    try {
        const response = await fetch("/molfile_to_xyz", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({molfile: molContent})
        });
        
        const result = await response.json();
        
        if (result.success && result.xyz) {
            renderMolecule(result.xyz);
            currentMolecule = result.xyz;
            populateCoordinateTable(result.xyz);
        } else {
            throw new Error(result.error || "Failed to convert MOL to XYZ");
        }
    } catch (error) {
        throw new Error("MOL to XYZ conversion failed: " + error.message);
    }
}

function setupKetcherCommunication() {
    // Listen for messages from Ketcher iframe
    window.addEventListener("message", function(event) {
        if (event.data.type === "ketcher-mol") {
            console.log("Received MOL from Ketcher:", event.data.mol);
            convertMolToXYZ(event.data.mol);
        }
    });
}

async function loadFromSketcher() {
    const ketcherFrame = document.getElementById("ketcherFrame");
    if (!ketcherFrame) {
        showAlert("Ketcher sketcher not available", "warning");
        return;
    }
    
    try {
        // Request MOL data from Ketcher
        ketcherFrame.contentWindow.postMessage({type: "get-mol"}, "*");
        showLoading("Importing from sketcher...");
        
        // Set a timeout in case Ketcher doesn't respond
        setTimeout(() => {
            hideLoading();
            showAlert("Sketcher did not respond. Please try again.", "warning");
        }, 5000);
        
    } catch (error) {
        console.error("Sketcher import error:", error);
        showAlert("Failed to import from sketcher: " + error.message, "danger");
        hideLoading();
    }
}

// ================ MOLECULE RENDERING ================
function renderMolecule(xyzContent) {
    if (!currentViewer) {
        console.error("3D viewer not initialized");
        return;
    }
    
    try {
        currentViewer.clear();
        currentViewer.addModel(xyzContent, "xyz");
        currentViewer.setStyle({}, {stick: {radius: 0.2, colorscheme: "default"}});
        currentViewer.zoomTo();
        currentViewer.render();
        
        console.log("Molecule rendered successfully");
        updateDebugInfo("xtbStatus", "Molecule Loaded", "success");
        
        // Update active style button
        const stickBtn = document.getElementById("styleStick");
        if (stickBtn) {
            document.querySelectorAll('[id^="style"]').forEach(btn => btn.classList.remove("active"));
            stickBtn.classList.add("active");
        }
        
    } catch (error) {
        console.error("Rendering error:", error);
        showAlert("Failed to render molecule: " + error.message, "danger");
        updateDebugInfo("lastError", error.message, "danger");
    }
}

// ================ VIEWER CONTROL FUNCTIONS ================
function resetView() {
    if (currentViewer) {
        currentViewer.zoomTo();
        currentViewer.render();
    }
}

function centerView() {
    if (currentViewer) {
        currentViewer.center();
        currentViewer.render();
    }
}

function toggleRotation() {
    isRotationActive = !isRotationActive;
    const btn = document.getElementById("toggleRotation");
    
    if (currentViewer) {
        if (isRotationActive) {
            currentViewer.spin(true);
            btn?.classList.add("active");
        } else {
            currentViewer.spin(false);
            btn?.classList.remove("active");
        }
    }
}

function setMoleculeStyle(style, button) {
    if (currentViewer) {
        currentViewer.setStyle({}, style);
        currentViewer.render();
        
        // Update active button
        document.querySelectorAll('[id^="style"]').forEach(btn => btn.classList.remove("active"));
        button?.classList.add("active");
    }
}

// ================ CALCULATION FUNCTIONS ================
async function runCalculation() {
    if (!currentMolecule) {
        showAlert("Please load a molecule first", "warning");
        return;
    }
    
    const parameters = collectCalculationParameters();
    showLoading("Running quantum calculation...");
    updateCalculationStatus("Running calculation...", "info");
    
    try {
        // Create FormData with molecule file
        const formData = new FormData();
        const blob = new Blob([currentMolecule], {type: "text/plain"});
        formData.append("file", blob, "molecule.xyz");
        
        // Add parameters
        Object.entries(parameters).forEach(([key, value]) => {
            formData.append(key, value);
        });
        
        const response = await fetch("/run_xtb", {
            method: "POST",
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            await handleCalculationSuccess(result);
        } else {
            throw new Error(result.error || "Calculation failed");
        }
        
    } catch (error) {
        console.error("Calculation error:", error);
        showAlert("Calculation failed: " + error.message, "danger");
        updateCalculationStatus("Calculation failed", "danger");
        updateDebugInfo("lastError", error.message, "danger");
    } finally {
        hideLoading();
    }
}

function collectCalculationParameters() {
    const method = document.getElementById("method")?.value || "xtb";
    const calcType = document.getElementById("calcType")?.value || "singlepoint";
    const charge = parseInt(document.getElementById("charge")?.value || "0");
    const multiplicity = parseInt(document.getElementById("multiplicity")?.value || "1");
    const uhf = document.getElementById("uhfFlag")?.checked || false;
    const solvent = document.getElementById("solventFlag")?.checked;
    const solventType = document.getElementById("solvent")?.value || "water";
    
    const params = {
        method,
        calc_type: calcType,
        charge,
        multiplicity
    };
    
    if (uhf) params.uhf = true;
    if (solvent) params.solvent = solventType;
    
    return params;
}

async function handleCalculationSuccess(result) {
    updateCalculationStatus("Calculation completed successfully", "success");
    
    // Update optimized geometry if available
    if (result.xyz) {
        renderMolecule(result.xyz);
        currentMolecule = result.xyz;
        populateCoordinateTable(result.xyz);
    }
    
    // Display results
    displayCalculationResults(result);
    
    // Update output and log tabs
    if (result.output) {
        updateOutputTab(result.output);
    }
    
    if (result.log) {
        updateLogTab(result.log);
    }
    
    // Update debug info
    updateDebugFiles(result.files || []);
    updateDebugInfo("xtbStatus", "Calculation Complete", "success");
    
    // Auto-save results
    await autoSaveResults(result);
    
    addLogEntry("Quantum calculation completed successfully");
}

function displayCalculationResults(result) {
    const resultsContainer = document.getElementById("resultsContainer");
    if (resultsContainer) {
        resultsContainer.style.display = "block";
    }
    
    // Update energy values
    if (result.energy !== undefined) {
        updateResultValue("totalEnergy", result.energy.toFixed(6));
    }
    
    // Update electronic properties
    if (result.homo !== undefined) {
        updateResultValue("homoEnergy", (result.homo * 27.2114).toFixed(3)); // Convert to eV
    }
    
    if (result.lumo !== undefined) {
        updateResultValue("lumoEnergy", (result.lumo * 27.2114).toFixed(3)); // Convert to eV
    }
    
    if (result.homo !== undefined && result.lumo !== undefined) {
        const gap = (result.lumo - result.homo) * 27.2114;
        updateResultValue("homoLumoGap", gap.toFixed(3));
    }
    
    // Update molecular properties
    if (result.dipole !== undefined) {
        updateResultValue("dipoleMoment", result.dipole.toFixed(3));
    }
}

function updateResultValue(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
        element.parentElement.classList.add("fade-in");
    }
}

function updateOutputTab(output) {
    const outputElement = document.getElementById("calculationOutput");
    if (outputElement) {
        outputElement.textContent = output;
    }
}

function updateLogTab(log) {
    const logElement = document.getElementById("calculationLog");
    if (logElement) {
        logElement.textContent = log;
    }
}

// ================ STRUCTURE MANIPULATION ================
async function callStructureEndpoint(endpoint) {
    if (!currentMolecule) {
        showAlert("Please load a molecule first", "warning");
        return;
    }
    
    showLoading("Processing structure...");
    
    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({xyz: currentMolecule})
        });
        
        const result = await response.json();
        
        if (result.success && result.xyz) {
            renderMolecule(result.xyz);
            currentMolecule = result.xyz;
            populateCoordinateTable(result.xyz);
            addLogEntry(`Structure operation completed: ${endpoint}`);
        } else {
            throw new Error(result.error || "Structure operation failed");
        }
    } catch (error) {
        console.error("Structure operation error:", error);
        showAlert("Structure operation failed: " + error.message, "danger");
    } finally {
        hideLoading();
    }
}

function deleteHydrogens() {
    if (!currentMolecule) {
        showAlert("Please load a molecule first", "warning");
        return;
    }
    
    try {
        // Parse XYZ and remove hydrogen atoms
        const lines = currentMolecule.split('\n');
        const atomCount = parseInt(lines[0]);
        const comment = lines[1];
        
        const newAtoms = [];
        for (let i = 2; i < 2 + atomCount; i++) {
            const parts = lines[i].trim().split(/\s+/);
            if (parts[0].toLowerCase() !== 'h') {
                newAtoms.push(lines[i]);
            }
        }
        
        const newXYZ = `${newAtoms.length}\n${comment}\n${newAtoms.join('\n')}`;
        renderMolecule(newXYZ);
        currentMolecule = newXYZ;
        populateCoordinateTable(newXYZ);
        addLogEntry("Removed hydrogen atoms");
        
    } catch (error) {
        console.error("Delete hydrogens error:", error);
        showAlert("Failed to remove hydrogens: " + error.message, "danger");
    }
}

function addHydrogens() {
    // This would typically require RDKit or similar
    showAlert("Add hydrogens functionality requires backend implementation", "info");
}

// ================ COORDINATE EDITING ================
function toggleCoordinateEditor() {
    const checkbox = document.getElementById("manualCoordinates");
    const editor = document.getElementById("coordinateEditor");
    
    if (checkbox?.checked) {
        editor.style.display = "block";
        if (currentMolecule) {
            populateCoordinateTable(currentMolecule);
        }
    } else {
        editor.style.display = "none";
    }
}

function toggleMassColumn() {
    const checkbox = document.getElementById("manualMasses");
    const massColumn = document.getElementById("massColumn");
    
    if (massColumn) {
        massColumn.style.display = checkbox?.checked ? "table-cell" : "none";
    }
    
    // Update table to show/hide mass inputs
    const tableBody = document.getElementById("coordinateTableBody");
    if (tableBody) {
        const rows = tableBody.querySelectorAll("tr");
        rows.forEach(row => {
            const massCell = row.querySelector(".mass-cell");
            if (massCell) {
                massCell.style.display = checkbox?.checked ? "table-cell" : "none";
            }
        });
    }
}

function populateCoordinateTable(xyzContent) {
    const tableBody = document.getElementById("coordinateTableBody");
    if (!tableBody) return;
    
    try {
        const lines = xyzContent.split('\n');
        const atomCount = parseInt(lines[0]);
        
        tableBody.innerHTML = "";
        
        for (let i = 2; i < 2 + atomCount; i++) {
            const parts = lines[i].trim().split(/\s+/);
            if (parts.length >= 4) {
                const row = createCoordinateRow(parts[0], parts[1], parts[2], parts[3], i - 2);
                tableBody.appendChild(row);
            }
        }
    } catch (error) {
        console.error("Error populating coordinate table:", error);
    }
}

function createCoordinateRow(element, x, y, z, index) {
    const row = document.createElement("tr");
    row.innerHTML = `
        <td><strong>${element}</strong></td>
        <td><input type="number" class="form-control form-control-sm coord-input" 
                   value="${parseFloat(x).toFixed(6)}" step="0.000001" data-coord="x" data-index="${index}"></td>
        <td><input type="number" class="form-control form-control-sm coord-input" 
                   value="${parseFloat(y).toFixed(6)}" step="0.000001" data-coord="y" data-index="${index}"></td>
        <td><input type="number" class="form-control form-control-sm coord-input" 
                   value="${parseFloat(z).toFixed(6)}" step="0.000001" data-coord="z" data-index="${index}"></td>
        <td class="mass-cell" style="display: none;">
            <input type="number" class="form-control form-control-sm mass-input" 
                   value="0.0" step="0.001" data-index="${index}">
        </td>
    `;
    return row;
}

function updateCoordinates() {
    if (!currentMolecule) return;
    
    try {
        const lines = currentMolecule.split('\n');
        const atomCount = parseInt(lines[0]);
        const comment = lines[1];
        
        const coordInputs = document.querySelectorAll(".coord-input");
        const newLines = [atomCount.toString(), comment];
        
        for (let i = 0; i < atomCount; i++) {
            const originalParts = lines[i + 2].trim().split(/\s+/);
            const element = originalParts[0];
            
            const xInput = document.querySelector(`[data-coord="x"][data-index="${i}"]`);
            const yInput = document.querySelector(`[data-coord="y"][data-index="${i}"]`);
            const zInput = document.querySelector(`[data-coord="z"][data-index="${i}"]`);
            
            if (xInput && yInput && zInput) {
                const x = parseFloat(xInput.value).toFixed(6);
                const y = parseFloat(yInput.value).toFixed(6);
                const z = parseFloat(zInput.value).toFixed(6);
                newLines.push(`${element}    ${x}    ${y}    ${z}`);
            } else {
                newLines.push(lines[i + 2]);
            }
        }
        
        const newXYZ = newLines.join('\n');
        renderMolecule(newXYZ);
        currentMolecule = newXYZ;
        addLogEntry("Coordinates updated manually");
        
    } catch (error) {
        console.error("Error updating coordinates:", error);
        showAlert("Failed to update coordinates: " + error.message, "danger");
    }
}

// ================ AGENT FUNCTIONS ================
async function postToAgent(endpoint, data) {
    updateAgentStatus("Processing...", "warning");
    
    try {
        const response = await fetch(agentEndpoint + endpoint, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            addAgentLog(`Command executed: ${endpoint}`, "success");
            displayAgentResult(result);
            updateAgentStatus("Connected", "success");
        } else {
            throw new Error(result.error || "Agent command failed");
        }
        
        updateLastActivity();
        
    } catch (error) {
        console.error("Agent error:", error);
        addAgentLog(`Error: ${error.message}`, "error");
        updateAgentStatus("Error", "danger");
        
        // Update connection status if it's a network error
        if (error.message.includes("fetch")) {
            updateConnectionStatus("Disconnected", "danger");
        }
    }
}

function executeAgentCommand() {
    const commandInput = document.getElementById("agentCommand");
    const command = commandInput?.value?.trim();
    
    if (!command) return;
    
    addAgentLog(`$ ${command}`, "command");
    postToAgent("/run_shell", {command: command});
    
    if (commandInput) {
        commandInput.value = "";
    }
}

function displayAgentResult(result) {
    if (result.output) {
        addAgentLog(result.output, "output");
    }
    
    if (result.files) {
        updateDebugFiles(result.files);
    }
}

function addAgentLog(message, type = "info") {
    const terminal = document.getElementById("agentTerminal");
    if (!terminal) return;
    
    const line = document.createElement("div");
    line.className = `terminal-line ${type}`;
    
    const timestamp = new Date().toLocaleTimeString();
    line.innerHTML = `
        <span class="terminal-timestamp">[${timestamp}]</span>
        <span class="terminal-text">${message}</span>
    `;
    
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
}

function updateAgentStatus(status, type) {
    const statusElement = document.getElementById("agentStatus");
    if (statusElement) {
        statusElement.textContent = status;
        statusElement.className = `badge bg-${type}`;
    }
}

function updateConnectionStatus(status, type) {
    const statusElement = document.getElementById("connectionStatus");
    if (statusElement) {
        statusElement.textContent = status;
        statusElement.className = `badge bg-${type}`;
    }
}

function updateLastActivity() {
    const activityElement = document.getElementById("lastActivity");
    if (activityElement) {
        activityElement.textContent = new Date().toLocaleString();
    }
}

// ================ FILE MANAGEMENT ================
async function exportResults(format) {
    if (!currentMolecule && format !== "all") {
        showAlert("No results to export", "warning");
        return;
    }
    
    try {
        switch (format) {
            case "xyz":
                downloadFile(currentMolecule, "molecule.xyz", "text/plain");
                break;
            case "json":
                const jsonData = collectAllResults();
                downloadFile(JSON.stringify(jsonData, null, 2), "results.json", "application/json");
                break;
            case "all":
                await exportAllFiles();
                break;
        }
        
        addLogEntry(`Exported results in ${format} format`);
    } catch (error) {
        console.error("Export error:", error);
        showAlert("Export failed: " + error.message, "danger");
    }
}

function collectAllResults() {
    return {
        timestamp: new Date().toISOString(),
        molecule: currentMolecule,
        parameters: collectCalculationParameters(),
        results: {
            energy: document.getElementById("totalEnergy")?.textContent || "--",
            homo: document.getElementById("homoEnergy")?.textContent || "--",
            lumo: document.getElementById("lumoEnergy")?.textContent || "--",
            gap: document.getElementById("homoLumoGap")?.textContent || "--",
            dipole: document.getElementById("dipoleMoment")?.textContent || "--"
        },
        output: document.getElementById("calculationOutput")?.textContent || "",
        log: document.getElementById("calculationLog")?.textContent || ""
    };
}

function saveToFile() {
    const filename = document.getElementById("filename")?.value || "molecule";
    const format = document.getElementById("fileFormat")?.value || "xyz";
    
    if (!currentMolecule) {
        showAlert("No molecule to save", "warning");
        return;
    }
    
    const extension = format === "xyz" ? ".xyz" : (format === "mol" ? ".mol" : ".sdf");
    downloadFile(currentMolecule, filename + extension, "text/plain");
    addLogEntry(`Saved molecule as ${filename}${extension}`);
}

function copyToClipboard() {
    if (!currentMolecule) {
        showAlert("No molecule to copy", "warning");
        return;
    }
    
    navigator.clipboard.writeText(currentMolecule).then(() => {
        showAlert("Molecule copied to clipboard", "success");
    }).catch(error => {
        console.error("Copy error:", error);
        showAlert("Failed to copy to clipboard", "danger");
    });
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], {type: mimeType});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ================ AUTO-SAVE FUNCTIONALITY ================
async function autoSaveResults(result) {
    if (!isGodModeActive) return;
    
    try {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const moleculeName = "molecule"; // Could be extracted from filename or SMILES
        const folderName = `${moleculeName}_${timestamp}`;
        
        // This would require backend endpoint to save to IAM_Results/
        await fetch("/save_results", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                folder: folderName,
                results: result
            })
        });
        
        addLogEntry(`Results auto-saved to IAM_Results/${folderName}/`);
    } catch (error) {
        console.error("Auto-save error:", error);
    }
}

// ================ UI CONTROL FUNCTIONS ================
function toggleDarkMode() {
    isDarkModeActive = !isDarkModeActive;
    document.body.classList.toggle("dark-mode", isDarkModeActive);
    
    const btn = document.getElementById("toggleDarkMode");
    if (btn) {
        const icon = btn.querySelector("i");
        if (isDarkModeActive) {
            icon.className = "bi bi-sun";
            btn.innerHTML = '<i class="bi bi-sun"></i> Light Mode';
        } else {
            icon.className = "bi bi-moon";
            btn.innerHTML = '<i class="bi bi-moon"></i> Dark Mode';
        }
    }
    
    // Update viewer background
    if (currentViewer) {
        const bg = isDarkModeActive ? "#0f172a" : "white";
        currentViewer.setBackgroundColor(bg);
        currentViewer.render();
    }
}

function toggleGodMode() {
    isGodModeActive = !isGodModeActive;
    
    const banner = document.getElementById("godModeBanner");
    const btn = document.getElementById("toggleGodMode");
    
    if (isGodModeActive) {
        banner.style.display = "block";
        btn?.classList.add("active");
        addLogEntry("God Mode activated - Full system access enabled");
    } else {
        banner.style.display = "none";
        btn?.classList.remove("active");
        addLogEntry("God Mode deactivated");
    }
}

function toggleAdvancedOptions() {
    const checkbox = document.getElementById("showAdvanced");
    const options = document.getElementById("advancedOptions");
    
    if (options) {
        options.style.display = checkbox?.checked ? "block" : "none";
    }
}

function toggleSolventOptions() {
    const checkbox = document.getElementById("solventFlag");
    const options = document.getElementById("solventOptions");
    
    if (options) {
        options.style.display = checkbox?.checked ? "block" : "none";
    }
}

function resetParameters() {
    // Reset all form inputs to defaults
    const inputs = [
        {id: "charge", value: "0"},
        {id: "multiplicity", value: "1"},
        {id: "method", value: "xtb"},
        {id: "calcType", value: "singlepoint"}
    ];
    
    inputs.forEach(({id, value}) => {
        const element = document.getElementById(id);
        if (element) element.value = value;
    });
    
    // Reset checkboxes
    const checkboxes = ["showAdvanced", "uhfFlag", "solventFlag", "manualCoordinates", "manualMasses"];
    checkboxes.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) checkbox.checked = false;
    });
    
    // Hide advanced options
    toggleAdvancedOptions();
    toggleSolventOptions();
    toggleCoordinateEditor();
    toggleMassColumn();
    
    addLogEntry("Parameters reset to defaults");
}

function saveParameters() {
    const params = collectCalculationParameters();
    localStorage.setItem("iam_parameters", JSON.stringify(params));
    showAlert("Parameters saved", "success");
}

function loadDefaultMolecule() {
    // Load a simple test molecule (methane)
    const methane = `5
Methane molecule
C    0.000000    0.000000    0.000000
H    1.089000    0.000000    0.000000
H   -0.363000    1.026810    0.000000
H   -0.363000   -0.513405   -0.889165
H   -0.363000   -0.513405    0.889165`;
    
    currentMolecule = methane;
    renderMolecule(methane);
    populateCoordinateTable(methane);
    
    // Set default SMILES
    const smilesInput = document.getElementById("smilesInput");
    if (smilesInput) {
        smilesInput.value = "C";
    }
}

// ================ UTILITY FUNCTIONS ================
function showLoading(message = "Processing...") {
    const overlay = document.getElementById("loadingOverlay");
    const messageElement = document.getElementById("loadingMessage");
    
    if (overlay) overlay.style.display = "flex";
    if (messageElement) messageElement.textContent = message;
}

function hideLoading() {
    const overlay = document.getElementById("loadingOverlay");
    if (overlay) overlay.style.display = "none";
}

function showAlert(message, type = "info") {
    // Create or update calculation status alert
    updateCalculationStatus(message, type);
    
    // Also log to console and agent log
    console.log(`[${type.toUpperCase()}] ${message}`);
    addLogEntry(message);
}

function updateCalculationStatus(message, type) {
    const statusElement = document.getElementById("calculationStatus");
    if (statusElement) {
        statusElement.textContent = message;
        statusElement.className = `alert alert-${type}`;
        
        // Add icon based on type
        const icons = {
            info: "bi-info-circle",
            success: "bi-check-circle",
            warning: "bi-exclamation-triangle",
            danger: "bi-x-circle"
        };
        
        const icon = icons[type] || icons.info;
        statusElement.innerHTML = `<i class="bi ${icon}"></i> ${message}`;
    }
}

function addLogEntry(message) {
    const logElement = document.getElementById("calculationLog");
    if (logElement) {
        const timestamp = new Date().toLocaleTimeString();
        const newEntry = `[${timestamp}] ${message}\n`;
        logElement.textContent += newEntry;
        logElement.scrollTop = logElement.scrollHeight;
    }
}

function updateDebugInfo(elementId, message, type = "info") {
    const element = document.getElementById(elementId);
    if (element) {
        if (elementId === "xtbStatus") {
            const badges = {
                info: "bg-secondary",
                success: "bg-success", 
                warning: "bg-warning",
                danger: "bg-danger"
            };
            element.innerHTML = `<span class="badge ${badges[type] || badges.info}">${message}</span>`;
        } else {
            element.textContent = message;
        }
    }
}

function updateDebugFiles(files) {
    const filesList = document.getElementById("filesList");
    if (filesList && files.length > 0) {
        filesList.innerHTML = files.map(file => 
            `<li><small class="text-muted">${file}</small></li>`
        ).join("");
    }
}

function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result);
        reader.onerror = reject;
        reader.readAsText(file);
    });
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        addLogEntry(`File selected: ${file.name} (${file.size} bytes)`);
    }
}

async function exportTempFiles() {
    try {
        const response = await fetch("/export_temp_files", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({})
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "iam_temp_files.zip";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            addLogEntry("Temporary files exported");
        } else {
            throw new Error("Failed to export temporary files");
        }
    } catch (error) {
        console.error("Export temp files error:", error);
        showAlert("Failed to export temporary files: " + error.message, "danger");
    }
}

async function exportAllFiles() {
    const zip = new JSZip();
    
    // Add molecule file
    if (currentMolecule) {
        zip.file("molecule.xyz", currentMolecule);
    }
    
    // Add results JSON
    const results = collectAllResults();
    zip.file("results.json", JSON.stringify(results, null, 2));
    
    // Add output and log
    const output = document.getElementById("calculationOutput")?.textContent;
    if (output) {
        zip.file("output.log", output);
    }
    
    const log = document.getElementById("calculationLog")?.textContent;
    if (log) {
        zip.file("calculation.log", log);
    }
    
    // Generate and download zip
    const content = await zip.generateAsync({type: "blob"});
    downloadFile(content, "iam_results.zip", "application/zip");
}

// Export functions for global access
window.IAMViewer = {
    renderMolecule,
    loadFromSmiles,
    loadFromFile,
    runCalculation,
    toggleDarkMode,
    toggleGodMode,
    postToAgent
};
