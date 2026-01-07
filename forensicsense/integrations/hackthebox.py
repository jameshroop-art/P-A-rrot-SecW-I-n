"""
Hack The Box integration

Provides integration with HTB API for automated exploitation
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
from ..utils.logging import get_logger

logger = get_logger('hackthebox')


class HackTheBoxAPI:
    """Hack The Box API integration"""
    
    def __init__(self, api_token: Optional[str] = None, api_url: str = None):
        self.api_token = api_token
        self.api_url = api_url or "https://labs.hackthebox.com/api/v4"
        self.headers = {}
        
        if api_token:
            self.headers['Authorization'] = f'Bearer {api_token}'
            logger.info("HTB API initialized with token")
        else:
            logger.warning("HTB API token not provided - limited functionality")
    
    async def list_machines(self, active_only: bool = True) -> List[Dict]:
        """
        List HTB machines
        
        Args:
            active_only: Only return active machines
            
        Returns:
            List of machine information
        """
        if not self.api_token:
            logger.error("HTB API token required")
            return []
        
        try:
            url = f"{self.api_url}/machine/list"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        machines = data.get('data', [])
                        
                        if active_only:
                            machines = [m for m in machines if m.get('active')]
                        
                        logger.info(f"Retrieved {len(machines)} HTB machines")
                        return machines
                    else:
                        logger.error(f"HTB API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error listing HTB machines: {e}")
            return []
    
    async def get_machine(self, machine_id: int) -> Optional[Dict]:
        """Get specific machine info"""
        if not self.api_token:
            logger.error("HTB API token required")
            return None
        
        try:
            url = f"{self.api_url}/machine/profile/{machine_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data')
                    else:
                        logger.error(f"HTB API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting HTB machine: {e}")
            return None
    
    async def submit_flag(self, flag: str, difficulty: int = 50) -> Dict:
        """
        Submit flag to HTB
        
        Args:
            flag: Flag value
            difficulty: Difficulty rating (0-100)
            
        Returns:
            Submission result
        """
        if not self.api_token:
            logger.error("HTB API token required")
            return {"success": False, "error": "No API token"}
        
        try:
            url = f"{self.api_url}/machine/own"
            payload = {
                "flag": flag,
                "difficulty": difficulty
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    data = await response.json()
                    
                    if response.status == 200 and data.get('success'):
                        logger.info("Flag submitted successfully!")
                        return {"success": True, "message": data.get('message', '')}
                    else:
                        logger.error(f"Flag submission failed: {data.get('message', '')}")
                        return {"success": False, "error": data.get('message', '')}
                        
        except Exception as e:
            logger.error(f"Error submitting flag: {e}")
            return {"success": False, "error": str(e)}


class HTBIntegration:
    """High-level HTB integration"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.api = HackTheBoxAPI(api_token)
        
    async def profile_htb_machine(self, machine_name: str) -> Dict:
        """
        Profile HTB machine
        
        Args:
            machine_name: Name of HTB machine
            
        Returns:
            Profile data
        """
        logger.info(f"Profiling HTB machine: {machine_name}")
        
        # Get machine list to find ID
        machines = await self.api.list_machines()
        
        machine = None
        for m in machines:
            if m.get('name', '').lower() == machine_name.lower():
                machine = m
                break
        
        if not machine:
            logger.error(f"Machine {machine_name} not found")
            return {"error": "Machine not found"}
        
        # Get detailed machine info
        machine_id = machine.get('id')
        detailed = await self.api.get_machine(machine_id)
        
        # Extract IP for profiling
        ip = machine.get('ip') or detailed.get('ip')
        
        result = {
            "name": machine_name,
            "id": machine_id,
            "ip": ip,
            "os": machine.get('os'),
            "difficulty": machine.get('difficulty'),
            "machine_info": detailed
        }
        
        logger.info(f"HTB machine profiled: {machine_name} @ {ip}")
        
        return result
    
    async def exploit_htb_machine(self, machine_name: str, auto_submit: bool = False) -> Dict:
        """
        Auto-exploit HTB machine
        
        Args:
            machine_name: Name of HTB machine
            auto_submit: Automatically submit flags if found
            
        Returns:
            Exploitation results
        """
        logger.info(f"Starting exploitation of HTB machine: {machine_name}")
        
        # Profile machine first
        profile = await self.profile_htb_machine(machine_name)
        
        if "error" in profile:
            return profile
        
        # Exploitation logic would go here
        # For now, return placeholder
        
        result = {
            "machine": machine_name,
            "status": "ready",
            "message": "HTB exploitation framework ready (full implementation in progress)",
            "profile": profile
        }
        
        return result
