#!/bin/bash
# start_all.sh
# ============
# Script de démarrage automatique pour IAM
# Lance tous les composants : Flask backend, Agent IAM, Interface web
#
# Auteur: IAM Project Team
# Version: 2.0 (Juillet 2025)

echo "🚀 DÉMARRAGE COMPLET IAM"
echo "========================"
echo "Intelligent Agent for Molecules - Version 2.0"
echo ""

# Configuration
IAM_DIR="/home/lppou/IAM"
VENV_PATH="/home/lppou/IAM/chem-env"  # ou venv selon votre config
LOG_DIR="$IAM_DIR/IAM_Logs"

# Couleurs pour output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Répertoire IAM
    if [ ! -d "$IAM_DIR" ]; then
        log_error "Répertoire IAM non trouvé: $IAM_DIR"
        exit 1
    fi
    
    # Activation environnement
    if [ -f "$IAM_DIR/chem-env/bin/activate" ]; then
        log_info "Activation environnement conda: chem-env"
        source ~/miniconda3/etc/profile.d/conda.sh
        conda activate chem-env
    elif [ -f "$VENV_PATH/bin/activate" ]; then
        log_info "Activation environnement virtuel"
        source "$VENV_PATH/bin/activate"
    else
        log_warning "Aucun environnement virtuel détecté"
    fi
    
    # Python et packages
    if ! command -v python &> /dev/null; then
        log_error "Python non trouvé"
        exit 1
    fi
    
    # XTB
    if command -v xtb &> /dev/null; then
        log_success "XTB disponible: $(xtb --version 2>&1 | head -1)"
    else
        log_warning "XTB non trouvé - calculs limités"
    fi
    
    # Créer dossiers logs si inexistants
    mkdir -p "$LOG_DIR"
    
    log_success "Prérequis vérifiés"
}

# Démarrage Flask Backend
start_flask_backend() {
    log_info "Démarrage Flask Backend..."
    
    cd "$IAM_DIR/IAM_GUI"
    
    if [ ! -f "backend.py" ]; then
        log_error "backend.py non trouvé dans IAM_GUI/"
        return 1
    fi
    
    # Arrêter processus existant sur port 5000
    if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null; then
        log_warning "Port 5000 occupé - arrêt processus existant"
        pkill -f "python.*backend.py" || true
        sleep 2
    fi
    
    # Démarrage en arrière-plan
    nohup python backend.py > "$LOG_DIR/flask_backend.log" 2>&1 &
    FLASK_PID=$!
    echo $FLASK_PID > "$LOG_DIR/flask.pid"
    
    # Vérification démarrage
    sleep 3
    if curl -s http://localhost:5000/ > /dev/null; then
        log_success "Flask Backend démarré (PID: $FLASK_PID, Port: 5000)"
        return 0
    else
        log_error "Échec démarrage Flask Backend"
        return 1
    fi
}

# Démarrage Agent IAM
start_iam_agent() {
    log_info "Démarrage IAM Agent..."
    
    cd "$IAM_DIR"
    
    if [ ! -f "IAM_Agent.py" ]; then
        log_error "IAM_Agent.py non trouvé"
        return 1
    fi
    
    # Arrêter agent existant
    pkill -f "python.*IAM_Agent.py" || true
    sleep 1
    
    # Créer dossiers surveillance
    mkdir -p ToAnalyze/{SMILES,MOL,XYZ}
    mkdir -p IAM_Results/{Processed,Failed}
    
    # Démarrage en arrière-plan
    nohup python IAM_Agent.py > "$LOG_DIR/iam_agent.log" 2>&1 &
    AGENT_PID=$!
    echo $AGENT_PID > "$LOG_DIR/agent.pid"
    
    log_success "IAM Agent démarré (PID: $AGENT_PID)"
    return 0
}

# Test composants
test_components() {
    log_info "Test des composants..."
    
    # Test Flask
    if curl -s http://localhost:5000/ | grep -q "IAM"; then
        log_success "✅ Flask Backend fonctionnel"
    else
        log_warning "⚠️ Flask Backend problème de réponse"
    fi
    
    # Test IAM_MoleculeEngine
    cd "$IAM_DIR"
    if python -c "from IAM_MoleculeEngine import IAM_MoleculeEngine; print('✅ IAM_MoleculeEngine OK')" 2>/dev/null; then
        log_success "✅ IAM_MoleculeEngine importable"
    else
        log_warning "⚠️ IAM_MoleculeEngine problème d'import"
    fi
    
    # Test IAM_PerformancePredictor
    if python -c "from IAM_PerformancePredictor import IAM_PerformancePredictor; print('✅ IAM_PerformancePredictor OK')" 2>/dev/null; then
        log_success "✅ IAM_PerformancePredictor importable"
    else
        log_warning "⚠️ IAM_PerformancePredictor problème d'import"
    fi
}

# Ouverture interface web
open_web_interface() {
    log_info "Ouverture interface web..."
    
    # URLs à tester
    URLS=(
        "http://localhost:5000"
        "http://127.0.0.1:5000"
        "http://192.168.1.$(hostname -I | cut -d' ' -f1 | cut -d'.' -f4):5000"
    )
    
    for url in "${URLS[@]}"; do
        echo "🌐 Interface disponible sur: $url"
    done
    
    # Ouverture automatique (si desktop disponible)
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:5000" 2>/dev/null &
        log_success "Interface ouverte automatiquement"
    elif command -v open &> /dev/null; then  # macOS
        open "http://localhost:5000" 2>/dev/null &
        log_success "Interface ouverte automatiquement"
    else
        log_info "Ouvrez manuellement: http://localhost:5000"
    fi
}

# Affichage status
show_status() {
    echo ""
    echo "📊 STATUS IAM"
    echo "=============="
    
    # Flask
    if curl -s http://localhost:5000/ > /dev/null; then
        echo "✅ Flask Backend: ACTIF (http://localhost:5000)"
    else
        echo "❌ Flask Backend: INACTIF"
    fi
    
    # Agent
    if pgrep -f "IAM_Agent.py" > /dev/null; then
        echo "✅ IAM Agent: ACTIF"
    else
        echo "❌ IAM Agent: INACTIF"
    fi
    
    # Dossiers
    echo "📁 Dossiers:"
    echo "   Surveillance: $IAM_DIR/ToAnalyze"
    echo "   Résultats: $IAM_DIR/IAM_Results"
    echo "   Logs: $LOG_DIR"
    
    # Statistiques
    if [ -d "$IAM_DIR/IAM_Results" ]; then
        result_count=$(find "$IAM_DIR/IAM_Results" -name "*.json" | wc -l)
        echo "   Résultats sauvés: $result_count fichiers"
    fi
}

# Création fichier test
create_test_files() {
    log_info "Création fichiers de test..."
    
    # SMILES test
    cat > "$IAM_DIR/ToAnalyze/SMILES/ethanol_test.smi" << EOF
CCO ethanol
EOF
    
    # MOL test (eau)
    cat > "$IAM_DIR/ToAnalyze/MOL/water_test.mol" << EOF

  Marvin  01010101

  3  2  0  0  0  0            999 V2000
    0.0000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    0.7571    0.5861    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7571    0.5861    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  1  3  1  0  0  0  0
M  END
EOF
    
    log_success "Fichiers de test créés"
}

# Gestion arrêt
cleanup() {
    echo ""
    log_info "Arrêt des services IAM..."
    
    # Arrêt Flask
    if [ -f "$LOG_DIR/flask.pid" ]; then
        FLASK_PID=$(cat "$LOG_DIR/flask.pid")
        kill $FLASK_PID 2>/dev/null || true
        rm -f "$LOG_DIR/flask.pid"
        log_info "Flask Backend arrêté"
    fi
    
    # Arrêt Agent
    if [ -f "$LOG_DIR/agent.pid" ]; then
        AGENT_PID=$(cat "$LOG_DIR/agent.pid")
        kill $AGENT_PID 2>/dev/null || true
        rm -f "$LOG_DIR/agent.pid"
        log_info "IAM Agent arrêté"
    fi
    
    # Nettoyage processus restants
    pkill -f "python.*backend.py" 2>/dev/null || true
    pkill -f "python.*IAM_Agent.py" 2>/dev/null || true
    
    log_success "Arrêt complet IAM"
    exit 0
}

# Gestion signal interruption
trap cleanup SIGINT SIGTERM

# SCRIPT PRINCIPAL
main() {
    # Changement répertoire IAM
    cd "$IAM_DIR" || exit 1
    
    # Vérifications
    check_prerequisites
    
    echo ""
    echo "🔧 DÉMARRAGE DES SERVICES"
    echo "========================"
    
    # Démarrage Flask Backend
    if start_flask_backend; then
        sleep 2
    else
        log_error "Impossible de démarrer Flask Backend"
        exit 1
    fi
    
    # Démarrage Agent IAM
    start_iam_agent
    sleep 2
    
    # Tests
    test_components
    
    # Création fichiers test
    create_test_files
    
    echo ""
    echo "🌐 INTERFACE WEB"
    echo "==============="
    open_web_interface
    
    # Status
    show_status
    
    echo ""
    echo "🎉 IAM DÉMARRÉ AVEC SUCCÈS!"
    echo "=========================="
    echo ""
    echo "💡 Utilisation:"
    echo "   • Ouvrir http://localhost:5000 pour l'interface web"
    echo "   • Déposer fichiers dans ToAnalyze/ pour traitement automatique"
    echo "   • Consulter logs dans IAM_Logs/"
    echo "   • Ctrl+C pour arrêter tous les services"
    echo ""
    
    # Boucle maintenance
    while true; do
        sleep 30
        
        # Vérification services
        if ! curl -s http://localhost:5000/ > /dev/null; then
            log_warning "Flask Backend non répondant - redémarrage..."
            start_flask_backend
        fi
        
        if ! pgrep -f "IAM_Agent.py" > /dev/null; then
            log_warning "IAM Agent arrêté - redémarrage..."
            start_iam_agent
        fi
    done
}

# Gestion arguments
case "${1:-start}" in
    "start")
        main
        ;;
    "stop")
        cleanup
        ;;
    "status")
        show_status
        ;;
    "restart")
        cleanup
        sleep 2
        main
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        echo ""
        echo "Commands:"
        echo "  start   - Démarre tous les services IAM (défaut)"
        echo "  stop    - Arrête tous les services IAM"
        echo "  status  - Affiche le statut des services"
        echo "  restart - Redémarre tous les services"
        exit 1
        ;;
esac
