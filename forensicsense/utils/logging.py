"""Logging utilities for ForensicSense"""

import logging
import os
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(level=logging.INFO, log_file=None):
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger('forensicsense')
    root_logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    if log_file is None:
        log_file = log_dir / f"forensicsense_{datetime.now().strftime('%Y%m%d')}.log"
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name):
    """Get a logger instance"""
    return logging.getLogger(f'forensicsense.{name}')


class AuditLogger:
    """Immutable audit logger with blockchain-style integrity"""
    
    def __init__(self, audit_file="audit_logs/audit.log"):
        self.audit_file = Path(audit_file)
        self.audit_file.parent.mkdir(exist_ok=True, parents=True)
        self.logger = get_logger('audit')
        self._previous_hash = "0" * 64  # Genesis hash
        
    def log_action(self, user, target, action, result, auth_token=None):
        """Log an auditable action with blockchain-style chaining"""
        import hashlib
        import json
        
        timestamp = datetime.utcnow().isoformat()
        
        entry = {
            "timestamp": timestamp,
            "user": user,
            "target": target,
            "action": action,
            "result": result,
            "auth_token": auth_token,
            "previous_hash": self._previous_hash
        }
        
        # Calculate hash of this entry
        entry_str = json.dumps(entry, sort_keys=True)
        current_hash = hashlib.sha256(entry_str.encode()).hexdigest()
        entry["hash"] = current_hash
        
        # Write to audit log (append-only)
        with open(self.audit_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Update previous hash for next entry
        self._previous_hash = current_hash
        
        self.logger.info(f"AUDIT: {action} on {target} by {user} - {result}")
        
        return current_hash
    
    def verify_integrity(self):
        """Verify the integrity of the audit log"""
        import hashlib
        import json
        
        if not self.audit_file.exists():
            return True, "No audit log found"
        
        previous_hash = "0" * 64
        line_num = 0
        
        with open(self.audit_file, 'r') as f:
            for line in f:
                line_num += 1
                try:
                    entry = json.loads(line.strip())
                    
                    # Verify previous hash chain
                    if entry.get("previous_hash") != previous_hash:
                        return False, f"Hash chain broken at line {line_num}"
                    
                    # Recalculate hash
                    stored_hash = entry.pop("hash")
                    entry_str = json.dumps(entry, sort_keys=True)
                    calculated_hash = hashlib.sha256(entry_str.encode()).hexdigest()
                    
                    if calculated_hash != stored_hash:
                        return False, f"Hash mismatch at line {line_num}"
                    
                    previous_hash = stored_hash
                    
                except json.JSONDecodeError:
                    return False, f"Invalid JSON at line {line_num}"
        
        return True, f"Audit log verified: {line_num} entries"
