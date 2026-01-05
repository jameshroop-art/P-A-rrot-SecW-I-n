"""Network scanning capabilities (passive and respectful)"""

import asyncio
import socket
from typing import List, Dict, Optional
from ..utils.logging import get_logger

logger = get_logger('network_scanner')


class NetworkScanner:
    """
    Passive network scanner with rate limiting
    """
    
    def __init__(self, timeout: int = 5, rate_limit: bool = True, 
                 max_concurrent: int = 10):
        self.timeout = timeout
        self.rate_limit = rate_limit
        self.max_concurrent = max_concurrent
        
    async def scan_port(self, host: str, port: int) -> Dict:
        """
        Scan a single port
        
        Args:
            host: Target host
            port: Port number
            
        Returns:
            Dictionary with scan results
        """
        result = {
            "port": port,
            "state": "closed",
            "service": self._get_service_name(port),
            "banner": None
        }
        
        try:
            # Attempt connection
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=self.timeout
            )
            
            result["state"] = "open"
            
            # Try to grab banner
            try:
                banner_data = await asyncio.wait_for(
                    reader.read(1024),
                    timeout=2
                )
                if banner_data:
                    result["banner"] = banner_data.decode('utf-8', errors='ignore').strip()
            except:
                pass
            
            writer.close()
            await writer.wait_closed()
            
        except asyncio.TimeoutError:
            result["state"] = "filtered"
        except ConnectionRefusedError:
            result["state"] = "closed"
        except Exception as e:
            result["state"] = "error"
            result["error"] = str(e)
        
        return result
    
    async def scan_ports(self, host: str, ports: List[int]) -> List[Dict]:
        """
        Scan multiple ports with concurrency control
        
        Args:
            host: Target host
            ports: List of port numbers
            
        Returns:
            List of scan results
        """
        logger.info(f"Scanning {len(ports)} ports on {host}")
        
        results = []
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def scan_with_semaphore(port):
            async with semaphore:
                if self.rate_limit:
                    await asyncio.sleep(0.1)  # Rate limiting delay
                return await self.scan_port(host, port)
        
        tasks = [scan_with_semaphore(port) for port in ports]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, dict)]
        
        # Filter to open ports
        open_ports = [r for r in valid_results if r["state"] == "open"]
        logger.info(f"Found {len(open_ports)} open ports on {host}")
        
        return valid_results
    
    async def quick_scan(self, host: str) -> List[Dict]:
        """
        Quick scan of common ports
        
        Args:
            host: Target host
            
        Returns:
            List of open ports
        """
        common_ports = [
            21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 
            993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 8080, 8443
        ]
        
        return await self.scan_ports(host, common_ports)
    
    async def full_scan(self, host: str) -> List[Dict]:
        """
        Full scan of all ports (slow, use with caution)
        
        Args:
            host: Target host
            
        Returns:
            List of open ports
        """
        all_ports = list(range(1, 1025))  # Well-known ports only
        return await self.scan_ports(host, all_ports)
    
    def _get_service_name(self, port: int) -> Optional[str]:
        """Get service name for a port"""
        try:
            return socket.getservbyport(port)
        except:
            # Common services not in getservbyport
            common_services = {
                8080: 'http-proxy',
                8443: 'https-alt',
                3306: 'mysql',
                5432: 'postgresql',
                1433: 'mssql',
                3389: 'rdp',
                5900: 'vnc'
            }
            return common_services.get(port, 'unknown')
    
    async def scan_target(self, host: str, scan_type: str = 'quick') -> Dict:
        """
        Main scanning function
        
        Args:
            host: Target host
            scan_type: 'quick' or 'full'
            
        Returns:
            Comprehensive scan results
        """
        logger.info(f"Starting {scan_type} scan on {host}")
        
        if scan_type == 'full':
            ports = await self.full_scan(host)
        else:
            ports = await self.quick_scan(host)
        
        result = {
            "host": host,
            "scan_type": scan_type,
            "total_ports_scanned": len([p for p in ports if p["state"] != "error"]),
            "open_ports": [p for p in ports if p["state"] == "open"],
            "filtered_ports": [p for p in ports if p["state"] == "filtered"],
            "all_results": ports
        }
        
        logger.info(f"Scan complete: {len(result['open_ports'])} open ports found")
        
        return result
