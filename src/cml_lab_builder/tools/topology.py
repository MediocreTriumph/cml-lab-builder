"""
Topology building tools for CML Lab Builder
"""

import sys
from typing import Dict, Any, Optional, Union
from fastmcp import FastMCP
from ..client import get_client
from ..utils import check_auth, handle_api_error


def register_topology_tools(mcp: FastMCP):
    """Register topology building tools with the MCP server"""
    
    @mcp.tool()
    async def add_node(
        lab_id: str, 
        label: str, 
        node_definition: str, 
        x: int = 0, 
        y: int = 0,
        populate_interfaces: bool = True,
        ram: Optional[int] = None,
        cpu_limit: Optional[int] = None,
        parameters: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Add a node to the specified lab
        
        Args:
            lab_id: ID of the lab
            label: Label for the new node
            node_definition: Type of node (e.g., 'iosv', 'csr1000v')
            x: X coordinate for node placement
            y: Y coordinate for node placement
            populate_interfaces: Whether to automatically create interfaces
            ram: RAM allocation for the node (optional)
            cpu_limit: CPU limit for the node (optional)
            parameters: Node-specific parameters (optional)
        
        Returns:
            Dictionary with node ID and confirmation message
        """
        auth_check = check_auth()
        if auth_check:
            return auth_check
        
        try:
            # Construct the node data payload
            node_data = {
                "label": label,
                "node_definition": node_definition,
                "x": x,
                "y": y,
                "parameters": parameters or {},
                "tags": [],
                "hide_links": False
            }
            
            # Add optional parameters if provided
            if ram is not None:
                node_data["ram"] = ram
            
            if cpu_limit is not None:
                node_data["cpu_limit"] = cpu_limit
            
            # Add populate_interfaces as a query parameter
            endpoint = f"/api/v0/labs/{lab_id}/nodes"
            if populate_interfaces:
                endpoint += "?populate_interfaces=true"
            
            # Make the API request
            headers = {"Content-Type": "application/json"}
            response = await get_client().request(
                "POST",
                endpoint,
                json=node_data,
                headers=headers
            )
            
            # Process the response
            result = response.json()
            node_id = result.get("id")
            
            if not node_id:
                return {"error": "Failed to create node, no node ID returned", "response": result}
            
            return {
                "node_id": node_id,
                "message": f"Added node '{label}' with ID: {node_id}",
                "status": "success",
                "details": result
            }
        except Exception as e:
            return handle_api_error("add_node", e)

    async def _find_available_interface(lab_id: str, node_id: str) -> Union[str, Dict[str, str]]:
        """
        Find an available physical interface on a node
        CRITICAL: Physical interfaces start at index 1 (loopback is index 0)
        
        Args:
            lab_id: ID of the lab
            node_id: ID of the node
            
        Returns:
            Interface ID or error dictionary
        """
        auth_check = check_auth()
        if auth_check:
            return auth_check
        
        try:
            # Get interfaces for the node with operational=true to get details
            interfaces_response = await get_client().request(
                "GET", 
                f"/api/v0/labs/{lab_id}/nodes/{node_id}/interfaces?operational=true"
            )
            interfaces = interfaces_response.json()
            
            # Ensure we have an array of interfaces
            if isinstance(interfaces, str):
                interfaces = interfaces.split()
            elif isinstance(interfaces, dict):
                interfaces = list(interfaces.keys())
            
            # Make sure we have interfaces to work with
            if not interfaces:
                return {"error": f"No interfaces found for node {node_id}"}
            
            # Find first available physical interface (skip index 0 which is loopback)
            for interface_id in interfaces:
                # Get detailed info for this interface
                interface_detail = await get_client().request(
                    "GET", 
                    f"/api/v0/labs/{lab_id}/interfaces/{interface_id}?operational=true"
                )
                interface_data = interface_detail.json()
                
                # CRITICAL FIX: Skip loopback interfaces (index 0), start with physical (index 1+)
                slot = interface_data.get("slot", -1)
                if slot == 0:
                    print(f"Skipping loopback interface at slot 0: {interface_id}", file=sys.stderr)
                    continue
                
                # Check if physical and not connected
                if (interface_data.get("type") == "physical" and 
                    interface_data.get("is_connected") == False):
                    print(f"Found available interface at slot {slot}: {interface_id}", file=sys.stderr)
                    return interface_id
            
            return {"error": f"No available physical interface found for node {node_id}"}
        except Exception as e:
            return handle_api_error("find_available_interface", e)

    async def _create_link_helper(lab_id: str, interface_id_a: str, interface_id_b: str) -> Dict[str, Any]:
        """
        Helper function to create a link between two interfaces
        
        Args:
            lab_id: ID of the lab
            interface_id_a: ID of the first interface
            interface_id_b: ID of the second interface
        
        Returns:
            Dictionary with link ID and confirmation message
        """
        try:
            print(f"Creating link between interfaces {interface_id_a} and {interface_id_b}", file=sys.stderr)
            
            # Use standard format with src_int and dst_int
            link_data = {
                "src_int": interface_id_a,
                "dst_int": interface_id_b
            }
            
            headers = {"Content-Type": "application/json"}
            response = await get_client().request(
                "POST", 
                f"/api/v0/labs/{lab_id}/links",
                json=link_data,
                headers=headers
            )
            
            result = response.json()
            print(f"Link creation response: {result}", file=sys.stderr)
            
            # Extract the link ID from the response
            link_id = result.get("id")
            if not link_id:
                return {"error": "Failed to create link, no link ID returned", "response": result}
            
            return {
                "link_id": link_id,
                "message": f"Created link between interfaces {interface_id_a} and {interface_id_b}",
                "status": "success",
                "details": result
            }
        except Exception as e:
            return handle_api_error("create_link", e)

    @mcp.tool()
    async def link_nodes(lab_id: str, node_id_a: str, node_id_b: str) -> Dict[str, Any]:
        """
        Create a link between two nodes by automatically selecting appropriate interfaces
        
        Args:
            lab_id: ID of the lab
            node_id_a: ID of the first node
            node_id_b: ID of the second node
        
        Returns:
            Dictionary with link ID and confirmation message
        """
        auth_check = check_auth()
        if auth_check:
            return auth_check
        
        try:
            # Find available interfaces on both nodes
            interface_a = await _find_available_interface(lab_id, node_id_a)
            if isinstance(interface_a, dict) and "error" in interface_a:
                return interface_a
            
            interface_b = await _find_available_interface(lab_id, node_id_b)
            if isinstance(interface_b, dict) and "error" in interface_b:
                return interface_b
            
            # Create the link using these interfaces
            return await _create_link_helper(lab_id, interface_a, interface_b)
        except Exception as e:
            return handle_api_error("link_nodes", e)

    @mcp.tool()
    async def create_link_v3(lab_id: str, interface_id_a: str, interface_id_b: str) -> Dict[str, Any]:
        """
        Create a link between two interfaces in a lab (alternative format)
        
        Args:
            lab_id: ID of the lab
            interface_id_a: ID of the first interface
            interface_id_b: ID of the second interface
        
        Returns:
            Dictionary with link ID and confirmation message
        """
        auth_check = check_auth()
        if auth_check:
            return auth_check
        
        return await _create_link_helper(lab_id, interface_id_a, interface_id_b)
