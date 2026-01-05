"""Cryptography utilities for evidence sealing"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class EvidenceSealer:
    """Cryptographically seal evidence for chain of custody"""
    
    def __init__(self, hash_algorithm='sha256'):
        self.hash_algorithm = hash_algorithm
        
    def seal_evidence(self, data: Any, metadata: Dict = None) -> Dict:
        """
        Seal evidence with cryptographic hash
        
        Args:
            data: The evidence data to seal
            metadata: Optional metadata (collector, case_id, etc.)
            
        Returns:
            Sealed evidence package with hash
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Prepare evidence package
        evidence = {
            "timestamp": timestamp,
            "data": data,
            "metadata": metadata or {},
            "sealer_version": "1.0"
        }
        
        # Calculate hash
        evidence_str = json.dumps(evidence, sort_keys=True)
        evidence_hash = self._calculate_hash(evidence_str.encode())
        
        # Create sealed package
        sealed = {
            "evidence": evidence,
            "seal": {
                "algorithm": self.hash_algorithm,
                "hash": evidence_hash,
                "sealed_at": timestamp
            }
        }
        
        return sealed
    
    def verify_seal(self, sealed_evidence: Dict) -> bool:
        """
        Verify the integrity of sealed evidence
        
        Args:
            sealed_evidence: Sealed evidence package
            
        Returns:
            True if seal is valid, False otherwise
        """
        try:
            evidence = sealed_evidence["evidence"]
            seal = sealed_evidence["seal"]
            
            # Recalculate hash
            evidence_str = json.dumps(evidence, sort_keys=True)
            calculated_hash = self._calculate_hash(evidence_str.encode())
            
            # Compare with stored hash
            return calculated_hash == seal["hash"]
            
        except (KeyError, TypeError):
            return False
    
    def _calculate_hash(self, data: bytes) -> str:
        """Calculate hash of data"""
        h = hashlib.new(self.hash_algorithm)
        h.update(data)
        return h.hexdigest()
    
    def save_sealed_evidence(self, sealed_evidence: Dict, filepath: Path):
        """Save sealed evidence to file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(sealed_evidence, f, indent=2)
    
    def load_sealed_evidence(self, filepath: Path) -> Dict:
        """Load and verify sealed evidence from file"""
        with open(filepath, 'r') as f:
            sealed = json.load(f)
        
        if not self.verify_seal(sealed):
            raise ValueError("Evidence seal verification failed - data may be tampered")
        
        return sealed


def hash_file(filepath: Path, algorithm='sha256') -> str:
    """Calculate hash of a file"""
    h = hashlib.new(algorithm)
    
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    
    return h.hexdigest()


def hash_string(data: str, algorithm='sha256') -> str:
    """Calculate hash of a string"""
    h = hashlib.new(algorithm)
    h.update(data.encode())
    return h.hexdigest()
