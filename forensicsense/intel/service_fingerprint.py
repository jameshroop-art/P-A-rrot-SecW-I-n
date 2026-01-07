"""Service fingerprinting and technology detection"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
from urllib.parse import urljoin
from ..utils.logging import get_logger

logger = get_logger('service_fingerprint')


class ServiceFingerprinter:
    """Identify services and technologies running on target"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        
    async def fingerprint_http(self, url: str) -> Dict:
        """
        Fingerprint HTTP service
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary with HTTP fingerprint data
        """
        result = {
            "url": url,
            "status_code": None,
            "headers": {},
            "server": None,
            "powered_by": None,
            "technologies": [],
            "cookies": [],
            "security_headers": {},
            "title": None,
            "redirect_chain": []
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    allow_redirects=True,
                    ssl=False  # For testing environments
                ) as response:
                    result["status_code"] = response.status
                    result["headers"] = dict(response.headers)
                    result["server"] = response.headers.get('Server')
                    result["powered_by"] = response.headers.get('X-Powered-By')
                    
                    # Extract cookies
                    if 'Set-Cookie' in response.headers:
                        result["cookies"] = response.headers.getall('Set-Cookie')
                    
                    # Check security headers
                    security_headers = [
                        'Strict-Transport-Security',
                        'Content-Security-Policy',
                        'X-Frame-Options',
                        'X-Content-Type-Options',
                        'X-XSS-Protection'
                    ]
                    for header in security_headers:
                        if header in response.headers:
                            result["security_headers"][header] = response.headers[header]
                    
                    # Read body for analysis
                    try:
                        body = await response.text()
                        
                        # Extract title
                        import re
                        title_match = re.search(r'<title>(.*?)</title>', body, re.IGNORECASE)
                        if title_match:
                            result["title"] = title_match.group(1).strip()
                        
                        # Detect technologies from HTML
                        result["technologies"] = self._detect_technologies(body, result["headers"])
                        
                    except:
                        pass
                    
        except asyncio.TimeoutError:
            result["error"] = "Connection timeout"
            logger.warning(f"Timeout connecting to {url}")
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error fingerprinting {url}: {e}")
        
        return result
    
    def _detect_technologies(self, body: str, headers: Dict) -> List[Dict]:
        """
        Detect technologies from HTML and headers
        
        Args:
            body: HTML body
            headers: HTTP headers
            
        Returns:
            List of detected technologies
        """
        technologies = []
        
        # Framework detection patterns
        patterns = {
            "WordPress": [r'wp-content', r'wordpress'],
            "Joomla": [r'joomla', r'/components/com_'],
            "Drupal": [r'drupal', r'sites/default'],
            "Laravel": [r'laravel'],
            "Django": [r'csrfmiddlewaretoken', r'__admin'],
            "React": [r'react', r'data-reactroot'],
            "Angular": [r'ng-app', r'angular'],
            "Vue.js": [r'vue', r'data-v-'],
            "jQuery": [r'jquery'],
            "Bootstrap": [r'bootstrap'],
            "PHP": [r'\.php'],
            "ASP.NET": [r'__VIEWSTATE', r'ASP.NET'],
        }
        
        import re
        for tech, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, body, re.IGNORECASE):
                    technologies.append({"name": tech, "confidence": "medium"})
                    break
        
        # Check headers for technology hints
        if 'X-Powered-By' in headers:
            powered_by = headers['X-Powered-By']
            if 'PHP' in powered_by:
                technologies.append({"name": "PHP", "version": powered_by, "confidence": "high"})
            elif 'ASP.NET' in powered_by:
                technologies.append({"name": "ASP.NET", "confidence": "high"})
        
        if 'Server' in headers:
            server = headers['Server']
            if 'Apache' in server:
                technologies.append({"name": "Apache", "version": server, "confidence": "high"})
            elif 'nginx' in server:
                technologies.append({"name": "nginx", "version": server, "confidence": "high"})
            elif 'Microsoft-IIS' in server:
                technologies.append({"name": "IIS", "version": server, "confidence": "high"})
        
        return technologies
    
    async def fingerprint_service(self, host: str, port: int, 
                                  service: Optional[str] = None) -> Dict:
        """
        Fingerprint a service on a specific port
        
        Args:
            host: Target host
            port: Port number
            service: Optional service name hint
            
        Returns:
            Service fingerprint data
        """
        result = {
            "host": host,
            "port": port,
            "service": service,
            "version": None,
            "details": {}
        }
        
        # HTTP/HTTPS services
        if port in [80, 8080, 8000] or service in ['http', 'http-proxy']:
            url = f"http://{host}:{port}"
            result["details"] = await self.fingerprint_http(url)
        elif port in [443, 8443] or service in ['https', 'https-alt']:
            url = f"https://{host}:{port}"
            result["details"] = await self.fingerprint_http(url)
        
        # For other services, we'd need specific fingerprinting logic
        # (SSH, FTP, SMTP, etc.)
        
        return result
    
    async def probe_common_paths(self, base_url: str) -> List[Dict]:
        """
        Probe common paths to discover admin panels, etc.
        
        Args:
            base_url: Base URL to probe
            
        Returns:
            List of discovered paths
        """
        common_paths = [
            '/admin',
            '/administrator',
            '/login',
            '/wp-admin',
            '/phpmyadmin',
            '/dashboard',
            '/admin.php',
            '/manager',
            '/console',
            '/.git',
            '/.env',
            '/robots.txt',
            '/sitemap.xml'
        ]
        
        discovered = []
        
        async with aiohttp.ClientSession() as session:
            for path in common_paths:
                url = urljoin(base_url, path)
                try:
                    async with session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=5),
                        allow_redirects=False,
                        ssl=False
                    ) as response:
                        if response.status < 400:
                            discovered.append({
                                "path": path,
                                "url": url,
                                "status": response.status,
                                "size": response.headers.get('Content-Length', 'unknown')
                            })
                            logger.info(f"Discovered: {url} [{response.status}]")
                except:
                    pass
                
                await asyncio.sleep(0.2)  # Rate limiting
        
        return discovered
