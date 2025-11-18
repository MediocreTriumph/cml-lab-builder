"""
Lab lifecycle management tools for CML Lab Builder
"""

import sys
from typing import Dict
from fastmcp import FastMCP
from ..client import get_client
from ..utils import check_auth, handle_api_error


def register_lab_lifecycle_tools(mcp: FastMCP):
    """Register lab lifecycle tools with the MCP server"""
    
    @mcp.tool()
    async def create_lab(title: str, description: str = "") -> Dict[str, str]:
        """
        Create a new lab in CML
        
        Args:
            title: Title of the new lab
            description: Optional description for the lab
        
        Returns:
            Dictionary containing lab ID and confirmation message
        """
        auth_check = check_auth()
        if auth_check:
            return auth_check
        
        try:
            print(f"Creating lab with title: {title}", file=sys.stderr)
            
            response = await get_client().request(
                "POST", 
                "/api/v0/labs",
                json={"title": title, "description": description}
            )
            
            lab_data = response.json()
            print(f"Lab creation response: {lab_data}", file=sys.stderr)
            
            lab_id = lab_data.get("id")
            
            if not lab_id:
                return {"error": "Failed to create lab, no lab ID returned"}
            
            return {
                "lab_id": lab_id,
                "message": f"Created lab '{title}' with ID: {lab_id}",
                "status": "success"
            }
        except Exception as e:
            return handle_api_error("create_lab", e)

    @mcp.tool()
    async def start_lab(lab_id: str) -> str:
        """
        Start the specified lab
        
        Args:
            lab_id: ID of the lab to start
        
        Returns:
            Confirmation message
        """
        auth_check = check_auth()
        if auth_check:
            return auth_check["error"]
        
        try:
            response = await get_client().request("PUT", f"/api/v0/labs/{lab_id}/start")
            return f"Lab {lab_id} started successfully"
        except Exception as e:
            return f"Error starting lab: {str(e)}"

    @mcp.tool()
    async def stop_lab(lab_id: str) -> str:
        """
        Stop the specified lab
        
        Args:
            lab_id: ID of the lab to stop
        
        Returns:
            Confirmation message
        """
        auth_check = check_auth()
        if auth_check:
            return auth_check["error"]
        
        try:
            response = await get_client().request("PUT", f"/api/v0/labs/{lab_id}/stop")
            return f"Lab {lab_id} stopped successfully"
        except Exception as e:
            return f"Error stopping lab: {str(e)}"
