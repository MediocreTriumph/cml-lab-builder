"""
Authentication tools for CML Lab Builder
"""

import sys
from fastmcp import FastMCP
from ..client import CMLAuth, set_client


def register_auth_tools(mcp: FastMCP):
    """Register authentication tools with the MCP server"""
    
    @mcp.tool()
    async def initialize_client(base_url: str, username: str, password: str, verify_ssl: bool = True) -> str:
        """
        Initialize the CML client with authentication credentials
        
        Args:
            base_url: Base URL of the CML server (e.g., https://cml-server)
            username: Username for CML authentication
            password: Password for CML authentication
            verify_ssl: Whether to verify SSL certificates (set to False for self-signed certificates)
        
        Returns:
            A success message if authentication is successful
        """
        # Fix URL if it doesn't have a scheme
        if not base_url.startswith(('http://', 'https://')):
            base_url = f"https://{base_url}"
        
        print(f"Initializing CML client with base_url: {base_url}", file=sys.stderr)
        cml_auth = CMLAuth(base_url, username, password, verify_ssl)
        
        try:
            token = await cml_auth.authenticate()
            print(f"Token received: {token[:10]}...", file=sys.stderr)
            set_client(cml_auth)
            ssl_status = "enabled" if verify_ssl else "disabled (accepting self-signed certificates)"
            return f"Successfully authenticated with CML at {base_url} (SSL verification: {ssl_status})"
        except Exception as e:
            print(f"Error connecting to CML: {str(e)}", file=sys.stderr)
            return f"Error connecting to CML: {str(e)}"
