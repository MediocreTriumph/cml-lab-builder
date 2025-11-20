"""
Lab inspection tools for CML Lab Builder
"""

import sys
from typing import Dict, Any
from fastmcp import FastMCP
from ..client import get_client
from ..utils import check_auth


def register_inspection_tools(mcp: FastMCP):
    """Register lab inspection tools with the MCP server"""
    
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
            error_msg = auth_check.get("error", "Authentication failed")
            return f"Error: {error_msg}"
        
        try:
            # Get complete topology in one call
            response = await get_client().request("GET", f"/api/v0/labs/{lab_id}/topology")
            topology = response.json()
            
            # Extract the components
            lab_info = topology.get("lab", {})
            nodes = topology.get("nodes", [])
            links = topology.get("links", [])
            
            # Create a topology summary
            result = f"Lab Topology: {lab_info.get('title', 'Untitled')}\n"
            result += f"Description: {lab_info.get('description', 'None')}\n"
            result += f"Version: {lab_info.get('version', 'unknown')}\n\n"
            
            # Create node lookup by ID for easier link processing
            node_lookup = {node.get("id"): node for node in nodes}
            
            # Add nodes
            result += f"Nodes ({len(nodes)}):\n"
            for node in nodes:
                result += f"- {node.get('label', 'Unnamed')} (ID: {node.get('id')})\n"
                result += f"  Type: {node.get('node_definition', 'unknown')}\n"
                result += f"  Position: ({node.get('x', 0)}, {node.get('y', 0)})\n"
                
                # Show interfaces
                interfaces = node.get('interfaces', [])
                if interfaces:
                    result += f"  Interfaces ({len(interfaces)}):\n"
                    for intf in interfaces:
                        result += f"    - {intf.get('label', 'unknown')} (type: {intf.get('type', 'unknown')})\n"
            
            # Add links
            result += f"\nLinks ({len(links)}):\n"
            for link in links:
                node_a_id = link.get('node_a')
                node_b_id = link.get('node_b')
                
                # Get node labels
                node_a_label = node_lookup.get(node_a_id, {}).get('label', node_a_id)
                node_b_label = node_lookup.get(node_b_id, {}).get('label', node_b_id)
                
                # Get interface labels by looking up interface IDs
                intf_a_id = link.get('interface_a')
                intf_b_id = link.get('interface_b')
                
                intf_a_label = 'unknown'
                intf_b_label = 'unknown'
                
                # Find interface labels
                if node_a_id in node_lookup:
                    for intf in node_lookup[node_a_id].get('interfaces', []):
                        if intf.get('id') == intf_a_id:
                            intf_a_label = intf.get('label', 'unknown')
                            break
                
                if node_b_id in node_lookup:
                    for intf in node_lookup[node_b_id].get('interfaces', []):
                        if intf.get('id') == intf_b_id:
                            intf_b_label = intf.get('label', 'unknown')
                            break
                
                result += f"- {node_a_label} ({intf_a_label}) ↔ {node_b_label} ({intf_b_label})\n"
            
            return result
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Exception in get_lab_topology: {error_details}", file=sys.stderr)
            return f"Error getting lab topology: {str(e)}"
