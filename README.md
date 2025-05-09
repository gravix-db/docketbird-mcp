# DocketBird MCP Server

This MCP server provides access to DocketBird's court case data and document management functionality.

## Requirements

- Python 3.11
- uv package manager

## Setup

1. Install uv if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Unix/MacOS
# OR
.venv\Scripts\activate     # On Windows
```

3. Install dependencies:

```bash
uv pip install .
```

4. Set up your environment variables:

```bash
export DOCKETBIRD_API_KEY=your_api_key_here  # On Unix/MacOS
# OR
set DOCKETBIRD_API_KEY=your_api_key_here     # On Windows
```

## Running the Server

Run the server using:

```bash
uv run docketbird_mcp.py --transport stdio  # For stdio transport
uv run docketbird_mcp.py --transport sse    # For SSE transport
```

## Available Tools

The server provides the following tools:

1. `get_case_details`: Get comprehensive details about a case including all documents
2. `download_document_by_id`: Download a specific document by its DocketBird ID
3. `list_cases`: Get a list of cases belonging to an account
4. `list_courts_and_types`: Get a comprehensive list of all available courts and case types

## Configuration Files

Make sure these files are in the same directory as the script:

- `courts.json`: Contains information about all available courts
- `case_types.json`: Contains information about different types of cases

## MCP Server Configuration

The MCP server configuration can be added to one of these locations depending on your MCP client:

- Cursor: `~/.cursor/mcp.json`
- Claude in mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

* How to open Claude Desktop config file from app
  - Launch Claude Desktop application
  - Navigate to the application menu and select Settings
  - Select Developer from the left navigation panel
  - Click the Edit Config button
  - Your system will automatically open the configuration file in your default text editor

1. Install uv if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Add the following configuration to the appropriate file:

_For macOS:_

```json
{
  "mcpServers": {
    "docketbird-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "PATH_TO_THE_SERVER/docketbird-mcp",
        "python",
        "docketbird_mcp.py"
      ],
      "env": {
        "DOCKETBIRD_API_KEY": "YOUR_KEY"
      }
    }
  }
}
```

_For Windows:_

```json
{
  "mcpServers": {
    "docketbird-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "PATH_TO_SERVER\\docketbird-mcp",
        "python",
        "docketbird_mcp.py"
      ],
      "env": {
        "DOCKETBIRD_API_KEY": "YOUR_KEY"
      }
    }
  }
}
```

Be sure to replace:

- PATH_TO_THE_SERVER with the actual path to where you cloned the DocketBird MCP repository (for macOS)
- PATH_TO_SERVER with the actual path to where you cloned the DocketBird MCP repository (for Windows)
- YOUR_KEY with your actual DocketBird API key

## Deployment

The DocketBird MCP server can be deployed to a cloud server using Docker and GitHub Actions. The deployment process is defined in the `.github/workflows/deploy.yml` file.

### Docker Deployment

The server is containerized using Docker. You can build and run the Docker image locally with the desired transport type:

```bash
# Build for ARM architecture (M1/M2 Mac)
docker buildx build --platform linux/arm64 -t docketbird-mcp-arm:latest --load .

# Build for AMD architecture (standard servers)
docker buildx build --platform linux/amd64 -t docketbird-mcp:latest --load .

# Run locally with stdio transport
docker run -d \
  --name docketbird-mcp-stdio \
  --restart=always \
  -e DOCKETBIRD_API_KEY="your_api_key_here" \
  -e TRANSPORT_TYPE="stdio" \
  docketbird-mcp-arm:latest /app/start.sh

# Run locally with SSE transport
docker run -d \
  --name docketbird-mcp-sse \
  --restart=always \
  -e DOCKETBIRD_API_KEY="your_api_key_here" \
  -e TRANSPORT_TYPE="sse" \
  docketbird-mcp-arm:latest /app/start.sh
```

### Validating Deployment

To validate that your deployment is working correctly:

1. Check that the container is running:

```bash
docker ps | grep docketbird-mcp
```

2. Verify the container logs:

```bash
docker logs docketbird-mcp
```

The logs should show:

```
Starting DocketBird MCP server...
API Key set: your_...
Running python docketbird_mcp.py
```

3. Test the connection from your MCP client using the configuration from this README.

If the container isn't running, you can troubleshoot by checking:

- Docker image exists: `docker images | grep docketbird`
- Container logs for errors: `docker logs docketbird-mcp`
- Server logs: Check if there are any permission or network issues

## DocketBird Agent Prototype

A prototype agent has been created to interact with the deployed DocketBird MCP server. This agent provides a user-friendly interface for querying case information and document details.

### Features

- Interactive command-line interface
- Natural language querying for case information
- Connects to the deployed DocketBird MCP server

### Setup and Running

1. Ensure you have the OpenAI API key set as an environment variable:

```bash
export OPENAI_API_KEY=your_openai_api_key_here  # On Unix/MacOS
# OR
set OPENAI_API_KEY=your_openai_api_key_here     # On Windows
```

2. Navigate to the project directory and run the agent:

```bash
cd agents
python db_agent_prototype.py
```

3. The agent will display a welcome banner and prompt you for your first query.

4. Example queries:
   - "Please retrieve details for txnd-3:2007-cv-01697"
   - "What documents are available in this case?"
   - "When was the last filing in this case?"

### Requirements

The agent requires:

- OpenAI API key (for GPT-4.1 model)
- Internet connection to access the deployed MCP server
- Python dependencies: pydantic_ai, termcolor, python-dotenv

Note: This is a prototype that uses the already deployed DocketBird MCP server at http://165.227.221.151:8040/sse.
