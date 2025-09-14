"""
Performance Optimization Module for Molecular Orbitals
IAM Physical Chemistry Educational Tools - Option D: Optimisation Performance

This module provides performance enhancements including:
- Parallel computation capabilities
- GPU acceleration (when available)
- Caching and memoization
- Batch processing
- Memory optimization
"""

import numpy as np
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import functools
import time
import os
import psutil
from typing import Dict, List, Tuple, Optional, Any, Callable
import json
import hashlib
from dataclasses import dataclass
import logging

# Optional GPU acceleration
try:
    import cupy as cp
    GPU_AVAILABLE = True
    print("✅ CuPy GPU acceleration available")
except ImportError:
    GPU_AVAILABLE = False
    print("⚠️ CuPy not available - using CPU only")

# Optional advanced parallelization
try:
    from joblib import Parallel, delayed
    JOBLIB_AVAILABLE = True
    print("✅ Joblib parallel processing available")
except ImportError:
    JOBLIB_AVAILABLE = False
    print("⚠️ Joblib not available - using standard multiprocessing")


@dataclass
class PerformanceMetrics:
    """Performance monitoring data"""
    execution_time: float
    memory_usage: float
    cpu_usage: float
    gpu_usage: Optional[float] = None
    cache_hits: int = 0
    cache_misses: int = 0
    parallel_efficiency: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            'execution_time': self.execution_time,
            'memory_usage': self.memory_usage,
            'cpu_usage': self.cpu_usage,
            'gpu_usage': self.gpu_usage,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'parallel_efficiency': self.parallel_efficiency
        }


class PerformanceMonitor:
    """Monitor system performance during calculations"""
    
    def __init__(self):
        self.start_time = None
        self.start_memory = None
        self.start_cpu = None
        
    def __enter__(self):
        """Start monitoring"""
        self.start_time = time.time()
        self.start_memory = psutil.virtual_memory().used
        self.start_cpu = psutil.cpu_percent()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop monitoring and calculate metrics"""
        self.execution_time = time.time() - self.start_time
        self.memory_usage = psutil.virtual_memory().used - self.start_memory
        self.cpu_usage = psutil.cpu_percent() - self.start_cpu
        
    def get_metrics(self) -> PerformanceMetrics:
        """Get performance metrics"""
        gpu_usage = None
        if GPU_AVAILABLE:
            try:
                gpu_usage = cp.cuda.runtime.memGetInfo()[0]
            except:
                pass
                
        return PerformanceMetrics(
            execution_time=getattr(self, 'execution_time', 0.0),
            memory_usage=getattr(self, 'memory_usage', 0.0),
            cpu_usage=getattr(self, 'cpu_usage', 0.0),
            gpu_usage=gpu_usage
        )


class AdvancedCache:
    """Advanced caching system with LRU and size limits"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 500):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache = {}
        self.access_order = []
        self.memory_usage = 0
        self.hits = 0
        self.misses = 0
        
    def _calculate_size(self, obj) -> int:
        """Estimate object size in bytes"""
        try:
            if isinstance(obj, np.ndarray):
                return obj.nbytes
            else:
                return len(str(obj).encode('utf-8'))
        except:
            return 1024  # Default estimate
            
    def _evict_lru(self):
        """Evict least recently used items"""
        while (len(self.cache) >= self.max_size or 
               self.memory_usage >= self.max_memory_bytes) and self.access_order:
            
            oldest_key = self.access_order.pop(0)
            if oldest_key in self.cache:
                obj_size = self._calculate_size(self.cache[oldest_key])
                del self.cache[oldest_key]
                self.memory_usage -= obj_size
                
    def get(self, key: str):
        """Get item from cache"""
        if key in self.cache:
            # Move to end (most recent)
            self.access_order.remove(key)
            self.access_order.append(key)
            self.hits += 1
            return self.cache[key]
        else:
            self.misses += 1
            return None
            
    def put(self, key: str, value):
        """Put item in cache"""
        obj_size = self._calculate_size(value)
        
        # Evict if necessary
        self._evict_lru()
        
        self.cache[key] = value
        self.memory_usage += obj_size
        
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.access_order.clear()
        self.memory_usage = 0
        
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        hit_rate = self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        return {
            'size': len(self.cache),
            'memory_usage_mb': self.memory_usage / (1024 * 1024),
            'hit_rate': hit_rate,
            'hits': self.hits,
            'misses': self.misses
        }


def memoize_with_cache(cache: AdvancedCache):
    """Decorator for caching function results"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key_data = f"{func.__name__}_{str(args)}_{str(sorted(kwargs.items()))}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
                
            # Calculate and cache result
            result = func(*args, **kwargs)
            cache.put(cache_key, result)
            return result
            
        return wrapper
    return decorator


class ParallelProcessor:
    """Advanced parallel processing for orbital calculations"""
    
    def __init__(self, use_gpu: bool = True, n_workers: Optional[int] = None):
        self.use_gpu = use_gpu and GPU_AVAILABLE
        self.n_workers = n_workers or min(mp.cpu_count(), 8)
        self.cache = AdvancedCache()
        
    def parallel_orbital_calculation(self, coordinates: List[Tuple], 
                                   orbital_indices: List[int],
                                   method: str = "xtb") -> List[Dict]:
        """Calculate multiple orbitals in parallel"""
        
        if self.use_gpu:
            return self._gpu_parallel_calculation(coordinates, orbital_indices, method)
        else:
            return self._cpu_parallel_calculation(coordinates, orbital_indices, method)
            
    def _cpu_parallel_calculation(self, coordinates: List[Tuple], 
                                 orbital_indices: List[int],
                                 method: str) -> List[Dict]:
        """CPU-based parallel calculation"""
        
        def calculate_single_orbital(orbital_index: int) -> Dict:
            """Calculate single orbital"""
            # Mock calculation for demonstration
            # In real implementation, this would call actual quantum chemistry code
            energy = -0.5 * (orbital_index + 1) + np.random.normal(0, 0.1)
            coefficients = np.random.randn(len(coordinates))
            
            return {
                'orbital_index': orbital_index,
                'energy': energy,
                'coefficients': coefficients.tolist(),
                'density_data': self._calculate_orbital_density(coordinates, coefficients)
            }
        
        if JOBLIB_AVAILABLE:
            # Use joblib for advanced parallelization
            results = Parallel(n_jobs=self.n_workers)(
                delayed(calculate_single_orbital)(idx) for idx in orbital_indices
            )
        else:
            # Use standard multiprocessing
            with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
                results = list(executor.map(calculate_single_orbital, orbital_indices))
                
        return results
        
    def _gpu_parallel_calculation(self, coordinates: List[Tuple], 
                                 orbital_indices: List[int],
                                 method: str) -> List[Dict]:
        """GPU-accelerated parallel calculation"""
        
        if not self.use_gpu:
            return self._cpu_parallel_calculation(coordinates, orbital_indices, method)
            
        try:
            # Convert coordinates to GPU arrays
            coords_gpu = cp.array(coordinates)
            
            results = []
            for orbital_index in orbital_indices:
                # Mock GPU calculation
                energy = -0.5 * (orbital_index + 1) + cp.random.normal(0, 0.1).get()
                coefficients_gpu = cp.random.randn(len(coordinates))
                
                # Calculate density on GPU
                density_gpu = self._gpu_calculate_orbital_density(coords_gpu, coefficients_gpu)
                
                results.append({
                    'orbital_index': orbital_index,
                    'energy': float(energy),
                    'coefficients': coefficients_gpu.get().tolist(),
                    'density_data': density_gpu.get().tolist()
                })
                
            return results
            
        except Exception as e:
            print(f"GPU calculation failed: {e}, falling back to CPU")
            return self._cpu_parallel_calculation(coordinates, orbital_indices, method)
            
    def _calculate_orbital_density(self, coordinates: List[Tuple], 
                                  coefficients: np.ndarray) -> List[float]:
        """Calculate orbital density (CPU)"""
        # Mock density calculation
        density = np.abs(coefficients) ** 2
        return density.tolist()
        
    def _gpu_calculate_orbital_density(self, coordinates_gpu, coefficients_gpu):
        """Calculate orbital density (GPU)"""
        # Mock GPU density calculation
        density_gpu = cp.abs(coefficients_gpu) ** 2
        return density_gpu
        
    def batch_process_molecules(self, molecules_data: List[Dict],
                               batch_size: int = 4) -> List[Dict]:
        """Process multiple molecules in batches"""
        
        results = []
        
        for i in range(0, len(molecules_data), batch_size):
            batch = molecules_data[i:i + batch_size]
            
            # Process batch in parallel
            with ThreadPoolExecutor(max_workers=min(len(batch), self.n_workers)) as executor:
                batch_results = list(executor.map(self._process_single_molecule, batch))
                
            results.extend(batch_results)
            
        return results
        
    def _process_single_molecule(self, molecule_data: Dict) -> Dict:
        """Process a single molecule"""
        # Mock processing
        return {
            'molecule_id': molecule_data.get('id', 'unknown'),
            'processing_time': np.random.uniform(0.1, 2.0),
            'orbitals_calculated': np.random.randint(5, 20),
            'success': True
        }


class OptimizedOrbitalAnalyzer:
    """Performance-optimized molecular orbital analyzer"""
    
    def __init__(self, enable_gpu: bool = True, cache_size_mb: int = 500):
        self.processor = ParallelProcessor(use_gpu=enable_gpu)
        self.cache = AdvancedCache(max_memory_mb=cache_size_mb)
        self.performance_log = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    @memoize_with_cache
    def optimized_orbital_calculation(self, xyz_content: str, method: str = "xtb",
                                    charge: int = 0, multiplicity: int = 1,
                                    use_parallel: bool = True) -> Dict:
        """Optimized orbital calculation with caching and parallelization"""
        
        with PerformanceMonitor() as monitor:
            # Parse coordinates
            coordinates = self._parse_xyz_coordinates(xyz_content)
            
            # Determine orbital indices to calculate
            n_electrons = self._estimate_electrons(coordinates, charge)
            orbital_indices = list(range(max(1, n_electrons // 2 - 3), 
                                       n_electrons // 2 + 4))
            
            if use_parallel and len(orbital_indices) > 1:
                # Parallel calculation
                orbital_results = self.processor.parallel_orbital_calculation(
                    coordinates, orbital_indices, method
                )
            else:
                # Sequential calculation
                orbital_results = [
                    self._calculate_single_orbital(coordinates, idx, method)
                    for idx in orbital_indices
                ]
            
            # Compile results
            results = {
                'success': True,
                'coordinates': coordinates,
                'orbitals': orbital_results,
                'method': method,
                'n_orbitals': len(orbital_results),
                'parallel_used': use_parallel and len(orbital_indices) > 1
            }
            
        # Log performance
        metrics = monitor.get_metrics()
        metrics.cache_hits = self.cache.hits
        metrics.cache_misses = self.cache.misses
        
        self.performance_log.append({
            'timestamp': time.time(),
            'metrics': metrics.to_dict(),
            'calculation_size': len(orbital_indices)
        })
        
        self.logger.info(f"Orbital calculation completed in {metrics.execution_time:.2f}s")
        
        return results
        
    def _parse_xyz_coordinates(self, xyz_content: str) -> List[Tuple]:
        """Parse XYZ coordinates"""
        lines = xyz_content.strip().split('\n')
        coordinates = []
        
        for line in lines[2:]:  # Skip first two lines
            parts = line.split()
            if len(parts) >= 4:
                element = parts[0]
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                coordinates.append((element, x, y, z))
                
        return coordinates
        
    def _estimate_electrons(self, coordinates: List[Tuple], charge: int) -> int:
        """Estimate number of electrons"""
        atomic_numbers = {'H': 1, 'C': 6, 'N': 7, 'O': 8, 'F': 9, 'P': 15, 'S': 16}
        total_electrons = sum(atomic_numbers.get(coord[0], 6) for coord in coordinates)
        return total_electrons - charge
        
    def _calculate_single_orbital(self, coordinates: List[Tuple], 
                                 orbital_index: int, method: str) -> Dict:
        """Calculate single orbital (mock implementation)"""
        # Mock calculation
        energy = -0.5 * (orbital_index + 1) + np.random.normal(0, 0.1)
        coefficients = np.random.randn(len(coordinates))
        
        return {
            'orbital_index': orbital_index,
            'energy': energy,
            'coefficients': coefficients.tolist(),
            'occupation': 2.0 if orbital_index <= len(coordinates) else 0.0
        }
        
    def benchmark_performance(self, test_molecules: List[str], 
                            methods: List[str] = None) -> Dict:
        """Benchmark performance across different configurations"""
        
        if methods is None:
            methods = ['xtb']
            
        benchmark_results = {
            'timestamp': time.time(),
            'system_info': self._get_system_info(),
            'results': []
        }
        
        for method in methods:
            for use_parallel in [False, True]:
                for molecule in test_molecules:
                    
                    start_time = time.time()
                    
                    try:
                        result = self.optimized_orbital_calculation(
                            molecule, method, use_parallel=use_parallel
                        )
                        success = True
                        error = None
                    except Exception as e:
                        success = False
                        error = str(e)
                        result = None
                        
                    execution_time = time.time() - start_time
                    
                    benchmark_results['results'].append({
                        'method': method,
                        'parallel': use_parallel,
                        'molecule_size': len(molecule.split('\n')) - 2,
                        'execution_time': execution_time,
                        'success': success,
                        'error': error,
                        'n_orbitals': len(result['orbitals']) if result else 0
                    })
                    
        return benchmark_results
        
    def _get_system_info(self) -> Dict:
        """Get system information for benchmarking"""
        return {
            'cpu_count': mp.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'gpu_available': GPU_AVAILABLE,
            'joblib_available': JOBLIB_AVAILABLE,
            'cache_size_mb': self.cache.max_memory_bytes / (1024**2)
        }
        
    def get_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        
        if not self.performance_log:
            return {'error': 'No performance data available'}
            
        # Calculate statistics
        execution_times = [entry['metrics']['execution_time'] for entry in self.performance_log]
        memory_usage = [entry['metrics']['memory_usage'] for entry in self.performance_log]
        
        cache_stats = self.cache.get_stats()
        
        return {
            'summary': {
                'total_calculations': len(self.performance_log),
                'avg_execution_time': np.mean(execution_times),
                'min_execution_time': np.min(execution_times),
                'max_execution_time': np.max(execution_times),
                'avg_memory_usage_mb': np.mean(memory_usage) / (1024**2),
                'cache_hit_rate': cache_stats['hit_rate']
            },
            'cache_statistics': cache_stats,
            'system_info': self._get_system_info(),
            'recent_calculations': self.performance_log[-10:],  # Last 10
            'recommendations': self._generate_performance_recommendations()
        }
        
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        cache_stats = self.cache.get_stats()
        
        if cache_stats['hit_rate'] < 0.3:
            recommendations.append("Augmentez la taille du cache pour améliorer les performances")
            
        if not GPU_AVAILABLE:
            recommendations.append("Installez CuPy pour l'accélération GPU")
            
        if not JOBLIB_AVAILABLE:
            recommendations.append("Installez joblib pour un parallélisme avancé")
            
        if psutil.virtual_memory().percent > 80:
            recommendations.append("Mémoire système faible - réduisez la taille des calculs")
            
        avg_time = np.mean([entry['metrics']['execution_time'] for entry in self.performance_log])
        if avg_time > 30:
            recommendations.append("Temps de calcul élevé - considérez des méthodes plus rapides")
            
        return recommendations
        
    def clear_cache(self):
        """Clear calculation cache"""
        self.cache.clear()
        self.logger.info("Cache cleared")
        
    def optimize_for_memory(self):
        """Optimize settings for low-memory systems"""
        self.cache = AdvancedCache(max_memory_mb=100)  # Reduce cache size
        self.processor.n_workers = min(2, mp.cpu_count())  # Reduce workers
        self.logger.info("Optimized for low-memory operation")
        
    def optimize_for_speed(self):
        """Optimize settings for maximum speed"""
        self.cache = AdvancedCache(max_memory_mb=1000)  # Increase cache
        self.processor.n_workers = mp.cpu_count()  # Use all cores
        self.processor.use_gpu = True  # Enable GPU if available
        self.logger.info("Optimized for maximum speed")


# Utility functions for performance testing
def generate_test_molecules(sizes: List[int]) -> List[str]:
    """Generate test molecules of different sizes"""
    molecules = []
    
    for size in sizes:
        lines = [str(size), f"Test molecule with {size} atoms"]
        
        for i in range(size):
            element = 'C' if i % 4 != 0 else 'H'
            x = np.random.uniform(-3, 3)
            y = np.random.uniform(-3, 3) 
            z = np.random.uniform(-3, 3)
            lines.append(f"{element}    {x:.6f}    {y:.6f}    {z:.6f}")
            
        molecules.append('\n'.join(lines))
        
    return molecules


def run_performance_benchmark():
    """Run comprehensive performance benchmark"""
    
    print("🚀 Démarrage du benchmark de performance...")
    
    # Initialize optimizer
    optimizer = OptimizedOrbitalAnalyzer(enable_gpu=GPU_AVAILABLE)
    
    # Generate test molecules
    test_molecules = generate_test_molecules([5, 10, 15, 20])
    
    # Run benchmark
    results = optimizer.benchmark_performance(test_molecules)
    
    # Print results
    print("\n📊 Résultats du benchmark:")
    print(f"Système: {results['system_info']['cpu_count']} CPUs, "
          f"{results['system_info']['memory_total_gb']:.1f} GB RAM")
    print(f"GPU disponible: {results['system_info']['gpu_available']}")
    
    for result in results['results']:
        print(f"  {result['method']} ({'parallèle' if result['parallel'] else 'séquentiel'}): "
              f"{result['execution_time']:.2f}s pour {result['molecule_size']} atomes")
              
    # Performance report
    performance_report = optimizer.get_performance_report()
    print(f"\n⚡ Rapport de performance:")
    print(f"  Temps moyen: {performance_report['summary']['avg_execution_time']:.2f}s")
    print(f"  Taux de cache: {performance_report['summary']['cache_hit_rate']:.1%}")
    
    if performance_report['recommendations']:
        print(f"\n💡 Recommandations:")
        for rec in performance_report['recommendations']:
            print(f"  - {rec}")


if __name__ == "__main__":
    run_performance_benchmark()
