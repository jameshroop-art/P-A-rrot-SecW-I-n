"""Networking utilities for ForensicSense"""

import socket
import ipaddress
import dns.resolver
from typing import List, Dict, Optional
from urllib.parse import urlparse


def is_valid_ip(ip: str) -> bool:
    """Check if string is a valid IP address"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_valid_domain(domain: str) -> bool:
    """Check if string is a valid domain name"""
    # Basic validation
    if not domain or len(domain) > 253:
        return False
    
    # Check for valid characters
    import re
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
    return bool(re.match(pattern, domain))


def resolve_target(target: str) -> Dict:
    """
    Resolve a target (domain or IP) to get comprehensive DNS information
    
    Args:
        target: Domain name or IP address
        
    Returns:
        Dictionary with resolution results
    """
    result = {
        "target": target,
        "is_ip": is_valid_ip(target),
        "is_domain": is_valid_domain(target),
        "a_records": [],
        "aaaa_records": [],
        "mx_records": [],
        "txt_records": [],
        "ns_records": [],
        "cname_records": []
    }
    
    if result["is_ip"]:
        # Reverse DNS lookup
        try:
            hostname = socket.gethostbyaddr(target)[0]
            result["hostname"] = hostname
        except (socket.herror, socket.gaierror):
            result["hostname"] = None
    
    elif result["is_domain"]:
        # Forward DNS lookup
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        
        # A records
        try:
            answers = resolver.resolve(target, 'A')
            result["a_records"] = [str(rdata) for rdata in answers]
        except Exception:
            pass
        
        # AAAA records
        try:
            answers = resolver.resolve(target, 'AAAA')
            result["aaaa_records"] = [str(rdata) for rdata in answers]
        except Exception:
            pass
        
        # MX records
        try:
            answers = resolver.resolve(target, 'MX')
            result["mx_records"] = [{"priority": rdata.preference, "server": str(rdata.exchange)} 
                                   for rdata in answers]
        except Exception:
            pass
        
        # TXT records
        try:
            answers = resolver.resolve(target, 'TXT')
            result["txt_records"] = [str(rdata) for rdata in answers]
        except Exception:
            pass
        
        # NS records
        try:
            answers = resolver.resolve(target, 'NS')
            result["ns_records"] = [str(rdata) for rdata in answers]
        except Exception:
            pass
        
        # CNAME records
        try:
            answers = resolver.resolve(target, 'CNAME')
            result["cname_records"] = [str(rdata) for rdata in answers]
        except Exception:
            pass
    
    return result


def parse_target_url(url: str) -> Dict:
    """
    Parse a URL to extract components
    
    Args:
        url: URL string
        
    Returns:
        Dictionary with URL components
    """
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    parsed = urlparse(url)
    
    return {
        "original": url,
        "scheme": parsed.scheme,
        "netloc": parsed.netloc,
        "hostname": parsed.hostname,
        "port": parsed.port or (443 if parsed.scheme == 'https' else 80),
        "path": parsed.path,
        "params": parsed.params,
        "query": parsed.query,
        "fragment": parsed.fragment
    }


def is_safe_environment(target: str, safe_list: List[str]) -> bool:
    """
    Check if target is in a safe testing environment
    
    Args:
        target: Target domain/IP
        safe_list: List of safe environment patterns
        
    Returns:
        True if target matches safe environment
    """
    target_lower = target.lower()
    
    for safe_pattern in safe_list:
        safe_pattern = safe_pattern.lower()
        
        # Exact match
        if target_lower == safe_pattern:
            return True
        
        # Domain suffix match
        if target_lower.endswith(safe_pattern):
            return True
        
        # Wildcard pattern match
        if '*' in safe_pattern:
            import re
            pattern = safe_pattern.replace('.', r'\.').replace('*', '.*')
            if re.match(f'^{pattern}$', target_lower):
                return True
    
    return False


def get_local_ip() -> Optional[str]:
    """Get the local machine's IP address"""
    try:
        # Create a socket to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None
