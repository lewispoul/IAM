#!/usr/bin/env python3
"""
IAM_Agent.py
============
Agent autonome IAM pour surveillance et traitement automatique:
- Surveille dossier ToAnalyze/
- Lance calculs XTB automatiquement
- Gère prédictions VoD
- Sauvegarde dans IAM_Results/ et IAM_Knowledge/

Auteur: IAM Project Team
Version: 2.0 (Juillet 2025)
"""

import os
import time
import json
import shutil
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Modules IAM
from IAM_MoleculeEngine import IAM_MoleculeEngine
from IAM_PerformancePredictor import IAM_PerformancePredictor

# RDKit pour parsing molécules
try:
    from rdkit import Chem
    RDKIT_AVAILABLE = True
except ImportError:
    print("⚠️ RDKit non disponible - fonctionnalités limitées")
    RDKIT_AVAILABLE = False


class IAM_FileHandler(FileSystemEventHandler):
    """
    Handler pour événements fichiers (watchdog)
    """
    
    def __init__(self, agent):
        self.agent = agent
    
    def on_created(self, event):
        if not event.is_directory:
            self.agent.queue_file_for_processing(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            self.agent.queue_file_for_processing(event.src_path)


class IAM_Agent:
    """
    Agent autonome IAM pour traitement automatique de molécules
    """
    
    def __init__(self, 
                 watch_directory: str = "ToAnalyze",
                 results_directory: str = "IAM_Results",
                 knowledge_directory: str = "IAM_Knowledge",
                 log_level: str = "INFO"):
        """
        Initialise l'agent IAM
        
        Args:
            watch_directory: Dossier à surveiller
            results_directory: Dossier résultats
            knowledge_directory: Base de connaissances
            log_level: Niveau de logging
        """
        
        # Dossiers
        self.watch_dir = Path(watch_directory)
        self.results_dir = Path(results_directory)
        self.knowledge_dir = Path(knowledge_directory)
        
        # Création dossiers si inexistants
        self.watch_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        self.knowledge_dir.mkdir(exist_ok=True)
        
        # Sous-dossiers spécialisés
        (self.watch_dir / "SMILES").mkdir(exist_ok=True)
        (self.watch_dir / "MOL").mkdir(exist_ok=True)
        (self.watch_dir / "XYZ").mkdir(exist_ok=True)
        (self.results_dir / "Processed").mkdir(exist_ok=True)
        (self.results_dir / "Failed").mkdir(exist_ok=True)
        
        # Modules IAM
        self.molecule_engine = IAM_MoleculeEngine(
            results_dir=str(self.results_dir),
            knowledge_dir=str(self.knowledge_dir)
        )
        self.performance_predictor = IAM_PerformancePredictor(
            knowledge_dir=str(self.knowledge_dir)
        )
        
        # Logging
        self._setup_logging(log_level)
        
        # Queue de traitement
        self.processing_queue = []
        self.processing_lock = threading.Lock()
        
        # État agent
        self.is_running = False
        self.processed_files = set()
        
        # Statistiques
        self.stats = {
            'files_processed': 0,
            'files_failed': 0,
            'start_time': None,
            'last_activity': None
        }
        
        self.logger.info("🤖 Agent IAM initialisé")
        self.logger.info(f"   Surveillance: {self.watch_dir}")
        self.logger.info(f"   Résultats: {self.results_dir}")
    
    def _setup_logging(self, level: str):
        """Configure logging pour l'agent"""
        log_dir = Path("IAM_Logs")
        log_dir.mkdir(exist_ok=True)
        
        # Format log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Logger principal
        self.logger = logging.getLogger('IAM_Agent')
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Handler fichier
        file_handler = logging.FileHandler(log_dir / 'iam_agent.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def queue_file_for_processing(self, file_path: str):
        """
        Ajoute fichier à la queue de traitement
        """
        file_path = Path(file_path)
        
        # Vérifications
        if not file_path.exists():
            return
        
        if str(file_path) in self.processed_files:
            return
        
        # Extensions supportées
        supported_extensions = {'.smi', '.smiles', '.mol', '.sdf', '.xyz'}
        if file_path.suffix.lower() not in supported_extensions:
            return
        
        # Éviter fichiers temporaires
        if file_path.name.startswith('.') or file_path.name.startswith('~'):
            return
        
        with self.processing_lock:
            if str(file_path) not in [str(p) for p in self.processing_queue]:
                self.processing_queue.append(file_path)
                self.logger.info(f"📥 Fichier en queue: {file_path.name}")
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Traite un fichier individuel
        
        Args:
            file_path: Chemin fichier à traiter
            
        Returns:
            Résultats du traitement
        """
        self.logger.info(f"🔄 Traitement: {file_path.name}")
        
        results = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'processing_time': datetime.now().isoformat(),
            'success': False,
            'steps': []
        }
        
        try:
            # 1. Lecture fichier
            content = file_path.read_text().strip()
            if not content:
                raise ValueError("Fichier vide")
            
            results['steps'].append("✅ Lecture fichier")
            
            # 2. Détection format et parsing
            file_format = self._detect_file_format(file_path, content)
            results['format'] = file_format
            results['steps'].append(f"✅ Format détecté: {file_format}")
            
            # 3. Conversion vers structure unifiée
            mol_data = self._parse_molecule_content(content, file_format)
            results.update(mol_data)
            results['steps'].append("✅ Parsing molécule")
            
            # 4. Calculs XTB
            if 'smiles' in mol_data or 'mol_object' in mol_data:
                xtb_results = self._run_xtb_calculation(mol_data, file_path.stem)
                results.update(xtb_results)
                
                if xtb_results.get('success'):
                    results['steps'].append("✅ Calcul XTB réussi")
                else:
                    results['steps'].append("⚠️ Calcul XTB échoué")
            
            # 5. Prédictions performances
            performance_results = self._predict_performance(mol_data)
            results.update(performance_results)
            results['steps'].append("✅ Prédictions performances")
            
            # 6. Sauvegarde
            self._save_processing_results(results)
            results['steps'].append("✅ Résultats sauvegardés")
            
            # 7. Archivage fichier source
            self._archive_processed_file(file_path)
            results['steps'].append("✅ Fichier archivé")
            
            results['success'] = True
            self.stats['files_processed'] += 1
            
        except Exception as e:
            self.logger.error(f"❌ Erreur traitement {file_path.name}: {e}")
            results['error'] = str(e)
            results['steps'].append(f"❌ Erreur: {e}")
            
            # Déplacer vers dossier Failed
            self._move_failed_file(file_path)
            self.stats['files_failed'] += 1
        
        # Marquer comme traité
        self.processed_files.add(str(file_path))
        self.stats['last_activity'] = datetime.now().isoformat()
        
        return results
    
    def _detect_file_format(self, file_path: Path, content: str) -> str:
        """Détecte le format du fichier"""
        extension = file_path.suffix.lower()
        
        if extension in ['.smi', '.smiles']:
            return 'smiles'
        elif extension in ['.mol', '.sdf']:
            return 'mol'
        elif extension == '.xyz':
            return 'xyz'
        
        # Détection par contenu
        if content.startswith(('V2000', 'V3000')) or 'M  END' in content:
            return 'mol'
        elif content.split('\n')[0].strip().isdigit():
            return 'xyz'
        else:
            return 'smiles'  # Par défaut
    
    def _parse_molecule_content(self, content: str, file_format: str) -> Dict[str, Any]:
        """Parse le contenu selon le format"""
        mol_data = {'format': file_format}
        
        if file_format == 'smiles':
            # SMILES: première ligne non-vide
            smiles = content.split('\n')[0].strip()
            mol_data['smiles'] = smiles
            
            # Conversion RDKit si disponible
            if RDKIT_AVAILABLE:
                try:
                    mol = Chem.MolFromSmiles(smiles)
                    if mol:
                        mol_data['mol_object'] = mol
                        mol_data['molecular_formula'] = Chem.rdMolDescriptors.CalcMolFormula(mol)
                        mol_data['molar_mass'] = Chem.rdMolDescriptors.CalcExactMolWt(mol)
                except Exception as e:
                    mol_data['rdkit_error'] = str(e)
        
        elif file_format == 'mol':
            mol_data['mol_content'] = content
            
            # Conversion RDKit si disponible
            if RDKIT_AVAILABLE:
                try:
                    mol = Chem.MolFromMolBlock(content)
                    if mol:
                        mol_data['mol_object'] = mol
                        mol_data['smiles'] = Chem.MolToSmiles(mol)
                        mol_data['molecular_formula'] = Chem.rdMolDescriptors.CalcMolFormula(mol)
                        mol_data['molar_mass'] = Chem.rdMolDescriptors.CalcExactMolWt(mol)
                except Exception as e:
                    mol_data['rdkit_error'] = str(e)
        
        elif file_format == 'xyz':
            mol_data['xyz_content'] = content
            
            # Extraction formule depuis XYZ (approximative)
            lines = content.split('\n')
            if len(lines) >= 3:
                try:
                    atom_count = int(lines[0].strip())
                    elements = []
                    for i in range(2, min(2 + atom_count, len(lines))):
                        parts = lines[i].strip().split()
                        if parts:
                            elements.append(parts[0])
                    
                    # Compter éléments
                    from collections import Counter
                    element_counts = Counter(elements)
                    formula = ''.join(f"{elem}{count if count > 1 else ''}" 
                                    for elem, count in sorted(element_counts.items()))
                    mol_data['molecular_formula'] = formula
                    
                except Exception as e:
                    mol_data['xyz_parse_error'] = str(e)
        
        return mol_data
    
    def _run_xtb_calculation(self, mol_data: Dict[str, Any], job_name: str) -> Dict[str, Any]:
        """Lance calcul XTB"""
        try:
            if 'smiles' in mol_data:
                # Pipeline complet SMILES → XTB
                return self.molecule_engine.full_pipeline(
                    mol_data['smiles'], job_name, 'smiles'
                )
            
            elif 'xyz_content' in mol_data:
                # Calcul XTB direct sur XYZ
                return self.molecule_engine.run_xtb_calculation(
                    mol_data['xyz_content'], job_name
                )
            
            elif 'mol_object' in mol_data:
                # Conversion mol → XYZ puis XTB
                xyz_content = self.molecule_engine.mol_to_xyz(mol_data['mol_object'])
                return self.molecule_engine.run_xtb_calculation(xyz_content, job_name)
            
            else:
                return {'success': False, 'error': 'Format non supporté pour XTB'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _predict_performance(self, mol_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prédictions performances énergétiques"""
        try:
            if 'molecular_formula' in mol_data:
                # Prédictions basées sur formule
                formula = mol_data['molecular_formula']
                return self.performance_predictor.full_prediction(formula)
            else:
                return {'performance_prediction': 'formule_manquante'}
        
        except Exception as e:
            return {'performance_error': str(e)}
    
    def _save_processing_results(self, results: Dict[str, Any]):
        """Sauvegarde résultats traitement"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{results['file_name']}_{timestamp}_results.json"
        
        results_file = self.results_dir / filename
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.logger.info(f"💾 Résultats sauvés: {filename}")
    
    def _archive_processed_file(self, file_path: Path):
        """Archive fichier traité"""
        archive_dir = self.results_dir / "Processed"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        new_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        archive_path = archive_dir / new_name
        
        shutil.move(str(file_path), str(archive_path))
        self.logger.info(f"📦 Archivé: {new_name}")
    
    def _move_failed_file(self, file_path: Path):
        """Déplace fichier échoué"""
        failed_dir = self.results_dir / "Failed"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        new_name = f"{file_path.stem}_{timestamp}_FAILED{file_path.suffix}"
        failed_path = failed_dir / new_name
        
        try:
            shutil.move(str(file_path), str(failed_path))
            self.logger.warning(f"⚠️ Échec archivé: {new_name}")
        except Exception as e:
            self.logger.error(f"Erreur archivage échec: {e}")
    
    def process_queue(self):
        """Traite la queue de fichiers"""
        while self.is_running:
            try:
                with self.processing_lock:
                    if self.processing_queue:
                        file_to_process = self.processing_queue.pop(0)
                    else:
                        file_to_process = None
                
                if file_to_process:
                    self.process_file(file_to_process)
                else:
                    time.sleep(1)  # Attente si queue vide
                    
            except Exception as e:
                self.logger.error(f"Erreur traitement queue: {e}")
                time.sleep(5)
    
    def start_monitoring(self):
        """Démarre surveillance automatique"""
        self.logger.info("🚀 Démarrage surveillance IAM Agent")
        
        # Statistiques
        self.stats['start_time'] = datetime.now().isoformat()
        self.is_running = True
        
        # Thread traitement queue
        processing_thread = threading.Thread(target=self.process_queue, daemon=True)
        processing_thread.start()
        
        # Watchdog pour surveillance dossier
        event_handler = IAM_FileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.watch_dir), recursive=True)
        observer.start()
        
        # Scan initial des fichiers existants
        self.scan_existing_files()
        
        try:
            self.logger.info(f"👁️ Surveillance active: {self.watch_dir}")
            while self.is_running:
                time.sleep(10)
                self.log_status()
        
        except KeyboardInterrupt:
            self.logger.info("🛑 Arrêt demandé par utilisateur")
        
        finally:
            observer.stop()
            observer.join()
            self.is_running = False
            self.logger.info("✅ Surveillance arrêtée")
    
    def scan_existing_files(self):
        """Scan initial des fichiers existants"""
        self.logger.info("🔍 Scan initial des fichiers...")
        
        for file_path in self.watch_dir.rglob('*'):
            if file_path.is_file():
                self.queue_file_for_processing(str(file_path))
        
        self.logger.info(f"📥 {len(self.processing_queue)} fichiers en queue")
    
    def log_status(self):
        """Log du statut périodique"""
        queue_size = len(self.processing_queue)
        processed = self.stats['files_processed']
        failed = self.stats['files_failed']
        
        if queue_size > 0 or processed > 0 or failed > 0:
            self.logger.info(
                f"📊 Status: Queue={queue_size}, Traités={processed}, Échecs={failed}"
            )
    
    def stop(self):
        """Arrête l'agent"""
        self.is_running = False
        self.logger.info("🛑 Arrêt agent demandé")


# Test et exécution directe
if __name__ == "__main__":
    print("🤖 IAM Agent - Mode autonome")
    print("=" * 40)
    
    # Créer agent
    agent = IAM_Agent()
    
    # Créer fichier test si dossier vide
    test_file = agent.watch_dir / "SMILES" / "test_ethanol.smi"
    if not test_file.exists():
        test_file.write_text("CCO ethanol")
        print(f"📄 Fichier test créé: {test_file}")
    
    # Démarrer surveillance
    try:
        agent.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt agent...")
        agent.stop()
