from .mcp_server import MCPServer

def run_server():
    # Configure and start the MCP server
    server = MCPServer()
    server.run()

if __name__ == "__main__":
    run_server()
