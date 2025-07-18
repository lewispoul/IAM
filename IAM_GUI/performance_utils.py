# Performance optimizations for IAM Backend
from functools import lru_cache, wraps
from typing import Dict, Any
import time
import hashlib
import json
import gzip
import io

# Simple in-memory cache for frequent operations
CACHE = {}
CACHE_STATS = {"hits": 0, "misses": 0, "total_size": 0}

def cache_result(expiry_seconds=300):
    """Decorator to cache function results with expiration"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            current_time = time.time()
            
            # Check if cached result exists and is still valid
            if cache_key in CACHE:
                cached_data, cached_time = CACHE[cache_key]
                if current_time - cached_time < expiry_seconds:
                    CACHE_STATS["hits"] += 1
                    return cached_data
                else:
                    # Remove expired entry
                    del CACHE[cache_key]
            
            # Call function and cache result
            CACHE_STATS["misses"] += 1
            result = func(*args, **kwargs)
            CACHE[cache_key] = (result, current_time)
            
            # Update cache stats
            CACHE_STATS["total_size"] = len(CACHE)
            
            return result
        return wrapper
    return decorator

def compress_response(data: Dict[str, Any]) -> bytes:
    """Compress large JSON responses using gzip"""
    json_str = json.dumps(data, separators=(',', ':'))
    return gzip.compress(json_str.encode('utf-8'))

def decompress_response(compressed_data: bytes) -> Dict[str, Any]:
    """Decompress gzip compressed JSON responses"""
    json_str = gzip.decompress(compressed_data).decode('utf-8')
    return json.loads(json_str)

@lru_cache(maxsize=100)
def get_molecular_formula_cached(atoms_str: str) -> str:
    """Cached molecular formula calculation"""
    atoms = json.loads(atoms_str)
    atom_counts = {}
    for atom in atoms:
        atom_counts[atom] = atom_counts.get(atom, 0) + 1
    
    formula = ""
    for element in sorted(atom_counts.keys(), key=lambda x: (x != 'C', x != 'H', x != 'N', x != 'O', x)):
        count = atom_counts[element]
        if count == 1:
            formula += element
        else:
            formula += f"{element}{count}"
    
    return formula

def validate_xyz_format_optimized(xyz_content: str) -> bool:
    """Optimized XYZ format validation"""
    lines = xyz_content.strip().split('\n', 3)  # Only split first 3 lines
    if len(lines) < 3:
        return False
    
    try:
        atom_count = int(lines[0].strip())
        return atom_count > 0 and len(lines) >= 3
    except (ValueError, IndexError):
        return False

def get_file_hash(content: str) -> str:
    """Generate hash for file content deduplication"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

# Performance monitoring
PERFORMANCE_METRICS = {
    "requests_total": 0,
    "requests_success": 0,
    "requests_error": 0,
    "average_response_time": 0.0,
    "total_response_time": 0.0,
    "cache_stats": CACHE_STATS,
    "memory_usage": 0,
    "active_calculations": 0
}

def track_performance(func):
    """Decorator to track performance metrics"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        PERFORMANCE_METRICS["requests_total"] += 1
        
        try:
            result = func(*args, **kwargs)
            PERFORMANCE_METRICS["requests_success"] += 1
            return result
        except Exception as e:
            PERFORMANCE_METRICS["requests_error"] += 1
            raise e
        finally:
            end_time = time.time()
            response_time = end_time - start_time
            PERFORMANCE_METRICS["total_response_time"] += response_time
            PERFORMANCE_METRICS["average_response_time"] = (
                PERFORMANCE_METRICS["total_response_time"] / PERFORMANCE_METRICS["requests_total"]
            )
    
    return wrapper

# Batch processing utilities
def batch_process_molecules(molecules_data, batch_size=5):
    """Process multiple molecules in batches for better performance"""
    results = []
    
    for i in range(0, len(molecules_data), batch_size):
        batch = molecules_data[i:i + batch_size]
        batch_results = []
        
        for mol_data in batch:
            try:
                # Process individual molecule
                result = process_single_molecule(mol_data)
                batch_results.append(result)
            except Exception as e:
                batch_results.append({
                    "success": False, 
                    "error": str(e),
                    "molecule_id": mol_data.get("id", "unknown")
                })
        
        results.extend(batch_results)
    
    return results

def process_single_molecule(mol_data):
    """Process a single molecule with caching and optimization"""
    # Implementation would depend on specific processing needs
    return {"success": True, "processed": True}

# Memory management utilities
def cleanup_cache():
    """Clean up expired cache entries"""
    current_time = time.time()
    expired_keys = []
    
    for key, (data, cached_time) in CACHE.items():
        if current_time - cached_time > 600:  # 10 minutes
            expired_keys.append(key)
    
    for key in expired_keys:
        del CACHE[key]
    
    CACHE_STATS["total_size"] = len(CACHE)

def get_cache_stats():
    """Get current cache statistics"""
    return {
        "hits": CACHE_STATS["hits"],
        "misses": CACHE_STATS["misses"],
        "hit_rate": CACHE_STATS["hits"] / max(1, CACHE_STATS["hits"] + CACHE_STATS["misses"]),
        "total_entries": CACHE_STATS["total_size"]
    }

# Database connection optimization (if using databases)
class ConnectionPool:
    """Simple connection pool for database connections"""
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.connections = []
        self.active_connections = 0
    
    def get_connection(self):
        """Get a connection from the pool"""
        if self.connections:
            return self.connections.pop()
        elif self.active_connections < self.max_connections:
            # Create new connection
            self.active_connections += 1
            return self.create_connection()
        else:
            raise Exception("Connection pool exhausted")
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        if len(self.connections) < self.max_connections:
            self.connections.append(conn)
        else:
            conn.close()
            self.active_connections -= 1
    
    def create_connection(self):
        """Create a new database connection"""
        # Implementation would depend on database type
        pass

# Static file optimization
def get_static_file_etag(file_path: str) -> str:
    """Generate ETag for static files"""
    try:
        import os
        stat = os.stat(file_path)
        return f'"{stat.st_mtime}-{stat.st_size}"'
    except:
        return '"0-0"'

# Response optimization utilities
def optimize_json_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize JSON response by removing unnecessary data"""
    optimized = {}
    
    for key, value in data.items():
        if value is None:
            continue  # Skip None values
        elif isinstance(value, list) and len(value) == 0:
            continue  # Skip empty lists
        elif isinstance(value, dict) and len(value) == 0:
            continue  # Skip empty dicts
        elif isinstance(value, str) and value.strip() == "":
            continue  # Skip empty strings
        else:
            optimized[key] = value
    
    return optimized

# Error handling optimization
def create_error_response(error_msg: str, details: str = None, error_code: int = 500) -> Dict[str, Any]:
    """Create standardized error responses"""
    response = {
        "success": False,
        "error": error_msg,
        "timestamp": time.time()
    }
    
    if details:
        response["details"] = details
    
    return response
