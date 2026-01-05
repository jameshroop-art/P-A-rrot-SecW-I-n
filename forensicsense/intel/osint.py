"""OSINT (Open Source Intelligence) collection"""

import asyncio
import aiohttp
from typing import Dict, List, Optional
from ..utils.logging import get_logger

logger = get_logger('osint')


class OSINTCollector:
    """Collect open source intelligence about targets"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        
    async def collect_whois(self, domain: str) -> Dict:
        """
        Collect WHOIS information
        
        Args:
            domain: Domain name
            
        Returns:
            WHOIS data
        """
        result = {
            "domain": domain,
            "registrar": None,
            "creation_date": None,
            "expiration_date": None,
            "name_servers": [],
            "status": [],
            "raw": None
        }
        
        try:
            import whois
            w = whois.whois(domain)
            
            result["registrar"] = w.registrar
            result["creation_date"] = str(w.creation_date) if w.creation_date else None
            result["expiration_date"] = str(w.expiration_date) if w.expiration_date else None
            result["name_servers"] = w.name_servers if w.name_servers else []
            result["status"] = w.status if w.status else []
            result["raw"] = str(w)
            
            logger.info(f"Collected WHOIS data for {domain}")
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error collecting WHOIS for {domain}: {e}")
        
        return result
    
    async def collect_subdomains_passive(self, domain: str) -> List[str]:
        """
        Passive subdomain enumeration using public sources
        
        Args:
            domain: Domain name
            
        Returns:
            List of discovered subdomains
        """
        subdomains = set()
        
        # crt.sh (Certificate Transparency logs)
        try:
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    if response.status == 200:
                        data = await response.json()
                        for entry in data:
                            name = entry.get('name_value', '')
                            if name and domain in name:
                                # Clean up wildcards
                                name = name.replace('*.', '')
                                if name:
                                    subdomains.add(name.strip())
            
            logger.info(f"Found {len(subdomains)} subdomains for {domain} via crt.sh")
            
        except Exception as e:
            logger.error(f"Error collecting subdomains: {e}")
        
        return sorted(list(subdomains))
    
    async def check_haveibeenpwned(self, email: str, api_key: Optional[str] = None) -> Dict:
        """
        Check if email appears in data breaches
        
        Args:
            email: Email address to check
            api_key: HIBP API key (required for non-rate-limited access)
            
        Returns:
            Breach information
        """
        result = {
            "email": email,
            "breaches": [],
            "total_breaches": 0
        }
        
        if not api_key:
            logger.warning("HIBP API key not provided - skipping breach check")
            return result
        
        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {
                "hibp-api-key": api_key,
                "User-Agent": "ForensicSense"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        breaches = await response.json()
                        result["breaches"] = [b.get("Name") for b in breaches]
                        result["total_breaches"] = len(breaches)
                        logger.info(f"Found {len(breaches)} breaches for {email}")
                    elif response.status == 404:
                        logger.info(f"No breaches found for {email}")
                    else:
                        result["error"] = f"HTTP {response.status}"
                        
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error checking HIBP for {email}: {e}")
        
        return result
    
    async def collect_wayback_urls(self, domain: str) -> List[str]:
        """
        Collect historical URLs from Wayback Machine
        
        Args:
            domain: Domain name
            
        Returns:
            List of historical URLs
        """
        urls = []
        
        try:
            url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=original&collapse=urlkey"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    if response.status == 200:
                        data = await response.json()
                        # First row is headers
                        urls = [row[0] for row in data[1:] if row]
                        logger.info(f"Found {len(urls)} historical URLs for {domain}")
                        
        except Exception as e:
            logger.error(f"Error collecting Wayback URLs: {e}")
        
        return urls[:100]  # Limit to first 100
    
    async def collect_osint(self, target: str) -> Dict:
        """
        Comprehensive OSINT collection
        
        Args:
            target: Domain or organization name
            
        Returns:
            Comprehensive OSINT data
        """
        logger.info(f"Collecting OSINT for {target}")
        
        # Run collection tasks in parallel
        whois_task = self.collect_whois(target)
        subdomains_task = self.collect_subdomains_passive(target)
        wayback_task = self.collect_wayback_urls(target)
        
        whois_data, subdomains, wayback_urls = await asyncio.gather(
            whois_task, subdomains_task, wayback_task,
            return_exceptions=True
        )
        
        result = {
            "target": target,
            "whois": whois_data if not isinstance(whois_data, Exception) else {"error": str(whois_data)},
            "subdomains": subdomains if not isinstance(subdomains, Exception) else [],
            "historical_urls": wayback_urls if not isinstance(wayback_urls, Exception) else [],
            "subdomain_count": len(subdomains) if not isinstance(subdomains, Exception) else 0,
        }
        
        logger.info(f"OSINT collection complete for {target}")
        
        return result
