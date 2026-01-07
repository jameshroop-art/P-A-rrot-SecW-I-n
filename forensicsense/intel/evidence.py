"""Evidence collection and sealing for chain of custody"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from ..utils.crypto import EvidenceSealer
from ..utils.logging import get_logger

logger = get_logger('evidence')


class Evidence:
    """Evidence record with chain of custody"""
    
    def __init__(self, evidence_id: str, evidence_type: str, data: Any, 
                 collector: str, case_id: Optional[str] = None):
        self.evidence_id = evidence_id
        self.evidence_type = evidence_type
        self.data = data
        self.collector = collector
        self.case_id = case_id
        self.collected_at = datetime.utcnow().isoformat()
        self.chain = []
        
    def add_to_chain(self, action: str, actor: str, notes: str = ""):
        """Add entry to chain of custody"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "actor": actor,
            "notes": notes
        }
        self.chain.append(entry)
        logger.info(f"Chain of custody: {action} by {actor} for evidence {self.evidence_id}")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type,
            "data": self.data,
            "collector": self.collector,
            "case_id": self.case_id,
            "collected_at": self.collected_at,
            "chain_of_custody": self.chain
        }
    
    def seal(self) -> Dict:
        """Seal evidence cryptographically"""
        sealer = EvidenceSealer()
        evidence_dict = self.to_dict()
        
        metadata = {
            "collector": self.collector,
            "case_id": self.case_id,
            "evidence_type": self.evidence_type
        }
        
        sealed = sealer.seal_evidence(evidence_dict, metadata)
        logger.info(f"Evidence {self.evidence_id} sealed with hash {sealed['seal']['hash']}")
        
        return sealed


class EvidenceCollector:
    """Collect and manage evidence"""
    
    def __init__(self, collector_name: str, case_id: Optional[str] = None,
                 evidence_dir: Path = None):
        self.collector_name = collector_name
        self.case_id = case_id
        self.evidence_dir = evidence_dir or Path("evidence")
        self.evidence_dir.mkdir(exist_ok=True, parents=True)
        self.sealer = EvidenceSealer()
        self.evidence_items = []
        
    def collect(self, evidence_type: str, data: Any, 
                evidence_id: Optional[str] = None) -> Evidence:
        """
        Collect evidence
        
        Args:
            evidence_type: Type of evidence (e.g., 'network_scan', 'osint', 'vuln_scan')
            data: The evidence data
            evidence_id: Optional custom evidence ID
            
        Returns:
            Evidence object
        """
        if evidence_id is None:
            evidence_id = f"{evidence_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        evidence = Evidence(
            evidence_id=evidence_id,
            evidence_type=evidence_type,
            data=data,
            collector=self.collector_name,
            case_id=self.case_id
        )
        
        evidence.add_to_chain("collected", self.collector_name)
        self.evidence_items.append(evidence)
        
        logger.info(f"Collected evidence: {evidence_id} ({evidence_type})")
        
        return evidence
    
    def seal_and_save(self, evidence: Evidence) -> Path:
        """
        Seal evidence and save to file
        
        Args:
            evidence: Evidence object to seal
            
        Returns:
            Path to sealed evidence file
        """
        sealed = evidence.seal()
        
        filename = f"{evidence.evidence_id}.sealed"
        filepath = self.evidence_dir / filename
        
        self.sealer.save_sealed_evidence(sealed, filepath)
        evidence.add_to_chain("sealed_and_saved", self.collector_name, 
                             notes=f"Saved to {filepath}")
        
        logger.info(f"Evidence saved to {filepath}")
        
        return filepath
    
    def save_all(self) -> Dict[str, Path]:
        """
        Seal and save all collected evidence
        
        Returns:
            Dictionary mapping evidence IDs to file paths
        """
        saved = {}
        
        for evidence in self.evidence_items:
            filepath = self.seal_and_save(evidence)
            saved[evidence.evidence_id] = filepath
        
        logger.info(f"Saved {len(saved)} evidence items")
        
        return saved
    
    def load_evidence(self, filepath: Path) -> Dict:
        """
        Load and verify sealed evidence
        
        Args:
            filepath: Path to sealed evidence file
            
        Returns:
            Evidence data if valid
        """
        sealed = self.sealer.load_sealed_evidence(filepath)
        logger.info(f"Loaded and verified evidence from {filepath}")
        
        return sealed["evidence"]
