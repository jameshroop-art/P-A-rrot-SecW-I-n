"""Main target profiling engine - orchestrates intelligence gathering"""

import asyncio
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from ..utils.logging import get_logger
from ..utils.networking import resolve_target, parse_target_url
from .network_scanner import NetworkScanner
from .service_fingerprint import ServiceFingerprinter
from .osint import OSINTCollector
from .vulnerability_db import VulnerabilityDatabase
from .evidence import EvidenceCollector

logger = get_logger('profiler')


@dataclass
class TargetProfile:
    """Complete target profile"""
    target: str
    profile_depth: str
    started_at: str
    completed_at: Optional[str] = None
    
    # DNS Resolution
    dns_info: Dict = field(default_factory=dict)
    
    # Network Scanning
    network_scan: Dict = field(default_factory=dict)
    
    # Service Fingerprinting
    services: List[Dict] = field(default_factory=list)
    http_fingerprint: Dict = field(default_factory=dict)
    discovered_paths: List[Dict] = field(default_factory=list)
    
    # OSINT
    osint: Dict = field(default_factory=dict)
    
    # Vulnerabilities
    vulnerabilities: List[Dict] = field(default_factory=list)
    risk_assessment: Dict = field(default_factory=dict)
    
    # Evidence
    evidence_sealed: bool = False
    evidence_files: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class TargetProfiler:
    """
    Main target profiling engine
    
    Performs comprehensive reconnaissance without exploitation
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.scanner = NetworkScanner(
            timeout=self.config.get('timeout', 5),
            rate_limit=self.config.get('rate_limiting', True),
            max_concurrent=self.config.get('max_concurrent_scans', 10)
        )
        self.fingerprinter = ServiceFingerprinter(timeout=self.config.get('timeout', 10))
        self.osint = OSINTCollector(timeout=self.config.get('timeout', 30))
        self.vuln_db = VulnerabilityDatabase(timeout=self.config.get('timeout', 30))
        
    async def profile_target(
        self,
        target: str,
        depth: str = 'standard',
        collect_evidence: bool = True
    ) -> TargetProfile:
        """
        Complete reconnaissance of target
        
        Args:
            target: Domain name, IP address, or URL
            depth: Profiling depth - 'basic', 'standard', 'full', 'deep'
            collect_evidence: Whether to seal and collect evidence
            
        Returns:
            TargetProfile with comprehensive intelligence
        """
        logger.info(f"Starting target profiling: {target} (depth: {depth})")
        
        started_at = datetime.utcnow().isoformat()
        
        # Initialize profile
        profile = TargetProfile(
            target=target,
            profile_depth=depth,
            started_at=started_at
        )
        
        # Evidence collector
        if collect_evidence:
            evidence_collector = EvidenceCollector(
                collector_name="TargetProfiler",
                case_id=f"profile_{target}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            )
        
        # Parse target
        try:
            if target.startswith('http://') or target.startswith('https://'):
                url_info = parse_target_url(target)
                target_host = url_info['hostname']
            else:
                target_host = target
                url_info = None
        except Exception as e:
            logger.error(f"Error parsing target: {e}")
            target_host = target
            url_info = None
        
        # Step 1: DNS Resolution (all depths)
        logger.info("Step 1: DNS Resolution")
        try:
            profile.dns_info = resolve_target(target_host)
            if collect_evidence:
                evidence_collector.collect('dns_resolution', profile.dns_info)
        except Exception as e:
            logger.error(f"DNS resolution error: {e}")
            profile.dns_info = {"error": str(e)}
        
        # Step 2: Network Scanning
        if depth in ['standard', 'full', 'deep']:
            logger.info("Step 2: Network Scanning")
            try:
                # Use first A record if available
                scan_target = target_host
                if profile.dns_info.get('a_records'):
                    scan_target = profile.dns_info['a_records'][0]
                
                scan_type = 'full' if depth == 'deep' else 'quick'
                profile.network_scan = await self.scanner.scan_target(scan_target, scan_type)
                
                if collect_evidence:
                    evidence_collector.collect('network_scan', profile.network_scan)
                    
            except Exception as e:
                logger.error(f"Network scanning error: {e}")
                profile.network_scan = {"error": str(e)}
        
        # Step 3: Service Fingerprinting
        if depth in ['full', 'deep']:
            logger.info("Step 3: Service Fingerprinting")
            try:
                open_ports = profile.network_scan.get('open_ports', [])
                
                # Fingerprint each open service
                for port_info in open_ports[:10]:  # Limit to first 10 for performance
                    service_fp = await self.fingerprinter.fingerprint_service(
                        target_host,
                        port_info['port'],
                        port_info.get('service')
                    )
                    profile.services.append(service_fp)
                
                # HTTP fingerprinting
                if any(p['port'] in [80, 443, 8080, 8443] for p in open_ports):
                    base_url = f"https://{target_host}" if any(p['port'] == 443 for p in open_ports) else f"http://{target_host}"
                    profile.http_fingerprint = await self.fingerprinter.fingerprint_http(base_url)
                    
                    # Discover paths
                    if depth == 'deep':
                        profile.discovered_paths = await self.fingerprinter.probe_common_paths(base_url)
                
                if collect_evidence:
                    evidence_collector.collect('service_fingerprinting', {
                        'services': profile.services,
                        'http_fingerprint': profile.http_fingerprint,
                        'discovered_paths': profile.discovered_paths
                    })
                    
            except Exception as e:
                logger.error(f"Service fingerprinting error: {e}")
        
        # Step 4: OSINT Collection
        if depth in ['full', 'deep']:
            logger.info("Step 4: OSINT Collection")
            try:
                profile.osint = await self.osint.collect_osint(target_host)
                
                if collect_evidence:
                    evidence_collector.collect('osint', profile.osint)
                    
            except Exception as e:
                logger.error(f"OSINT collection error: {e}")
                profile.osint = {"error": str(e)}
        
        # Step 5: Vulnerability Assessment
        logger.info("Step 5: Vulnerability Assessment")
        try:
            # Extract technologies
            technologies = profile.http_fingerprint.get('technologies', [])
            
            # Match vulnerabilities
            profile.vulnerabilities = self.vuln_db.match_vulnerabilities(technologies)
            
            # Calculate risk score
            profile.risk_assessment = self.vuln_db.assess_risk_score(profile.to_dict())
            
            if collect_evidence:
                evidence_collector.collect('vulnerability_assessment', {
                    'vulnerabilities': profile.vulnerabilities,
                    'risk_assessment': profile.risk_assessment
                })
                
        except Exception as e:
            logger.error(f"Vulnerability assessment error: {e}")
            profile.risk_assessment = {"error": str(e)}
        
        # Finalize profile
        profile.completed_at = datetime.utcnow().isoformat()
        
        # Seal evidence
        if collect_evidence:
            logger.info("Sealing evidence")
            evidence_files = evidence_collector.save_all()
            profile.evidence_sealed = True
            profile.evidence_files = [str(f) for f in evidence_files.values()]
        
        logger.info(f"Target profiling complete: {target}")
        logger.info(f"Risk Level: {profile.risk_assessment.get('level', 'UNKNOWN')}")
        logger.info(f"Risk Score: {profile.risk_assessment.get('score', 0)}/100")
        
        return profile
    
    async def quick_profile(self, target: str) -> TargetProfile:
        """Quick profile with basic depth"""
        return await self.profile_target(target, depth='basic', collect_evidence=False)
    
    async def full_profile(self, target: str) -> TargetProfile:
        """Full profile with evidence collection"""
        return await self.profile_target(target, depth='full', collect_evidence=True)
    
    async def deep_profile(self, target: str) -> TargetProfile:
        """Deep profile with extensive scanning"""
        return await self.profile_target(target, depth='deep', collect_evidence=True)
