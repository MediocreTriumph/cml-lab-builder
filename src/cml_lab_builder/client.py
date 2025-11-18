"""
CML API Client

Handles authentication and HTTP requests to the Cisco Modeling Labs API.
"""

import sys
import httpx
from typing import Optional


class CMLAuth:
    """Authentication and request handling for Cisco Modeling Labs"""
    
    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool = True):
        """
        Initialize the CML authentication client
        
        Args:
            base_url: Base URL of the CML server
            username: Username for CML authentication
            password: Password for CML authentication
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = None
        self.verify_ssl = verify_ssl
        self.client = httpx.AsyncClient(base_url=base_url, verify=verify_ssl)
        
        # Suppress SSL warnings if verify_ssl is False
        if not verify_ssl:
            try:
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            except ImportError:
                print("urllib3 not available, SSL warning suppression disabled", file=sys.stderr)
    
    async def authenticate(self) -> str:
        """
        Authenticate with CML and get a token
        
        Returns:
            Authentication token
        
        Raises:
            httpx.HTTPStatusError: If authentication fails
        """
        print(f"Authenticating with CML at {self.base_url}", file=sys.stderr)
        response = await self.client.post(
            "/api/v0/authenticate",
            json={"username": self.username, "password": self.password}
        )
        response.raise_for_status()
        self.token = response.text.strip('"')
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})
        
        # Verify the token works
        try:
            auth_check = await self.client.get("/api/v0/authok")
            auth_check.raise_for_status()
            print(f"Authentication successful, token verified", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Token verification failed: {str(e)}", file=sys.stderr)
            
        return self.token
    
    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """
        Make an authenticated request to CML API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint to call
            **kwargs: Additional arguments to pass to httpx
        
        Returns:
            HTTP response
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        if not self.token:
            await self.authenticate()
        
        print(f"Making {method} request to {endpoint}", file=sys.stderr)
        
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        
        kwargs["headers"]["Authorization"] = f"Bearer {self.token}"
        
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            
            # If unauthorized, re-authenticate once
            if response.status_code == 401:
                print(f"Got 401 response, re-authenticating...", file=sys.stderr)
                await self.authenticate()
                kwargs["headers"]["Authorization"] = f"Bearer {self.token}"
                response = await self.client.request(method, endpoint, **kwargs)
            
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Request error: {str(e)}", file=sys.stderr)
            raise


# Global state for CML client
_cml_client: Optional[CMLAuth] = None


def get_client() -> Optional[CMLAuth]:
    """Get the current CML client instance"""
    return _cml_client


def set_client(client: CMLAuth) -> None:
    """Set the CML client instance"""
    global _cml_client
    _cml_client = client
