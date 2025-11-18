"""
Lab inspection tools for CML Lab Builder
"""

import sys
from typing import Dict, Any, Union
from fastmcp import FastMCP
from ..client import get_client
from ..utils import check_auth


def register_inspection_tools(mcp: FastMCP):
    """Register lab inspection tools with the MCP server"""
    
    async def _get_lab_details(lab_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific lab (internal helper)
        
        Args:
            lab_id: ID of the lab to get details for
        
        Returns:
            Dictionary containing lab details
        """
        try:
            response = await get_client().request("GET", f"/api/v0/labs/{lab_id}")
            return response.json()
        except Exception as e:
            return {"error": f"Error getting lab details: {str(e)}"}
    
    async def _get_lab_nodes(lab_id: str) -> Union[Dict[str, Any], str]:
        """
        Get all nodes in a specific lab (internal helper)
        
        Args:
            lab_id: ID of the lab
        
        Returns:
            Dictionary of nodes in the lab or error message
        """
        try:
            response = await get_client().request("GET", f"/api/v0/labs/{lab_id}/nodes")
            nodes = response.json()
            
            # If the response is a list, convert it to a dictionary
            if isinstance(nodes, list):
                print(f"Converting nodes list to dictionary", file=sys.stderr)
                result = {}
                for node in nodes:
                    node_id = node.get("id")
                    if node_id:
                        result[node_id] = node
                return result
            
            return nodes
        except Exception as e:
            return {"error": f"Error getting lab nodes: {str(e)}"}
    
    async def _get_lab_links(lab_id: str) -> Union[Dict[str, Any], str]:
        """
        Get all links in a specific lab (internal helper)
        
        Args:
            lab_id: ID of the lab
        
        Returns:
            Dictionary of links in the lab or error message
        """
        try:
            response = await get_client().request("GET", f"/api/v0/labs/{lab_id}/links")
            links = response.json()
            
            # If the response is a list, convert it to a dictionary
            if isinstance(links, list):
                print(f"Converting links list to dictionary", file=sys.stderr)
                result = {}
                for link in links:
                    link_id = link.get("id")
                    if link_id:
                        result[link_id] = link
                return result
            
            return links
        except Exception as e:
            return {"error": f"Error getting lab links: {str(e)}"}
    
    @mcp.tool()
    async def get_lab_topology(lab_id: str) -> str:
        """
        Get a detailed summary of the lab topology
        
        Args:
            lab_id: ID of the lab
        
        Returns:
            Formatted summary of the lab topology
        """
        auth_check = check_auth()
        if auth_check:
            return {"error": auth_check.get("error", "Authentication failed")}
        
        try:
            # Get lab details
            lab_details = await _get_lab_details(lab_id)
            if isinstance(lab_details, dict) and "error" in lab_details:
                return lab_details["error"]
            
            # Get nodes
            nodes = await _get_lab_nodes(lab_id)
            if isinstance(nodes, dict) and "error" in nodes:
                return nodes["error"]
            
            # Get links
            links = await _get_lab_links(lab_id)
            if isinstance(links, dict) and "error" in links:
                return links["error"]
            
            # Create a topology summary
            result = f"Lab Topology: {lab_details.get('title', 'Untitled')}\n"
            result += f"State: {lab_details.get('state', 'unknown')}\n"
            result += f"Description: {lab_details.get('description', 'None')}\n\n"
            
            # Add nodes
            result += "Nodes:\n"
            for node_id, node in nodes.items():
                result += f"- {node.get('label', 'Unnamed')} (ID: {node_id})\n"
                result += f"  Type: {node.get('node_definition', 'unknown')}\n"
                result += f"  State: {node.get('state', 'unknown')}\n"
            
            # Add links
            result += "\nLinks:\n"
            for link_id, link in links.items():
                src_node_id = link.get('src_node')
                dst_node_id = link.get('dst_node')
                
                if src_node_id in nodes and dst_node_id in nodes:
                    src_node = nodes[src_node_id].get('label', src_node_id)
                    dst_node = nodes[dst_node_id].get('label', dst_node_id)
                    result += (f"- Link {link_id}: {src_node} ({link.get('src_int', 'unknown')}) → "
                               f"{dst_node} ({link.get('dst_int', 'unknown')})\n")
                else:
                    result += f"- Link {link_id}: {src_node_id}:{link.get('src_int')} → {dst_node_id}:{link.get('dst_int')}\n"
            
            return result
        except Exception as e:
            return f"Error getting lab topology: {str(e)}"
