# CML Lab Builder

A lean MCP server for building and managing Cisco Modeling Labs (CML) topologies. This focused server provides 8 core tools for lab creation, topology building, and basic management.

## Features

- **Focused Functionality**: Only 8 essential tools for optimal performance
- **Clean Architecture**: Modular design with separated concerns
- **Easy Setup**: Simple uv-based installation
- **Fast Integration**: Works seamlessly with Claude Desktop

## Tools Included

### Authentication
1. **initialize_client** - Authenticate with CML server

### Lab Lifecycle
2. **create_lab** - Create new labs
3. **start_lab** - Start a lab
4. **stop_lab** - Stop a lab

### Topology Building
5. **add_node** - Add nodes to lab
6. **link_nodes** - Auto-link nodes using first available interfaces
7. **create_link_v3** - Create links with specific interface IDs

### Inspection
8. **get_lab_topology** - Get topology summary

## Installation

### Prerequisites
- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Access to a Cisco Modeling Labs server

### Quick Start

1. **Navigate to the repository:**
```bash
cd c:\users\jscon\documents\python_projects\cml-lab-builder
```

2. **Install with uv:**
```bash
uv pip install -e .
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your CML server details
```

### Claude Desktop Configuration

Add this to your Claude Desktop configuration file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cml-lab-builder": {
      "command": "uv",
      "args": [
        "--directory",
        "c:\\users\\jscon\\documents\\python_projects\\cml-lab-builder",
        "run",
        "cml-lab-builder"
      ]
    }
  }
}
```

After adding the configuration, restart Claude Desktop.

## Usage Examples

### Example 1: Basic Lab Creation
```
Create a new lab called 'OSPF Test Lab'
```

### Example 2: Add Routers
```
Add two IOSv routers named R1 and R2 to the lab
```

### Example 3: Connect Nodes
```
Connect R1 to R2
```

### Example 4: View Topology
```
Show me the topology of the lab
```

### Example 5: Start the Lab
```
Start the lab
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
CML_URL=https://your-cml-server
CML_USERNAME=your-username
CML_PASSWORD=your-password
```

## Key Implementation Notes

### Interface Selection
The `link_nodes` tool automatically selects available physical interfaces, properly skipping loopback interfaces (index 0) and starting with physical interfaces at index 1.

### Error Handling
All tools use consistent error handling and return structured error messages when operations fail.

### Authentication
The client maintains a single authenticated session. Use `initialize_client` once per session.

## Common Node Definitions

- `iosv` - Cisco IOSv (Layer 3 switch/router)
- `csr1000v` - Cisco CSR1000v router
- `iosvl2` - Cisco IOSvL2 (Layer 2 switch)
- `nxosv9000` - Cisco NX-OSv 9000
- `alpine` - Alpine Linux (lightweight)
- `ubuntu` - Ubuntu Linux

## Troubleshooting

### Authentication Fails
- Verify CML server URL is correct
- Check username/password
- If using self-signed certificates, set `verify_ssl=False` in `initialize_client`

### Cannot Create Links
- Ensure nodes have available physical interfaces
- Check that nodes are in the correct state (stopped for config changes)
- Verify interface IDs are correct when using `create_link_v3`

### Lab Won't Start
- Check CML server has sufficient resources
- Verify node definitions are available on your CML server
- Review CML server logs for detailed errors

## License

MIT License

## Related Projects

- **claude-cml-toolkit** - Full-featured MCP server with additional tools
