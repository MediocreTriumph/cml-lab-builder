"""
CML Lab Builder MCP Server

A lean MCP server for building and managing Cisco Modeling Labs topologies.
Focused on the 8 core tools needed for lab creation and topology building.
"""

import os
from dotenv import load_dotenv
from fastmcp import FastMCP

from .tools import (
    register_auth_tools,
    register_lab_lifecycle_tools,
    register_topology_tools,
    register_inspection_tools
)

# Load environment variables
load_dotenv()

# Create the FastMCP server
mcp = FastMCP("cml-lab-builder")

# Register all tool groups
register_auth_tools(mcp)
register_lab_lifecycle_tools(mcp)
register_topology_tools(mcp)
register_inspection_tools(mcp)


def main():
    """Main entry point for the MCP server"""
    # Get configuration from environment
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))
    
    # Run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
