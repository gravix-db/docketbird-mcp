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
uv pip install -r requirements.txt
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
uv run docketbird_mcp.py
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

  1. Install uv if you haven't already:
```bash
pip3.11 install requests mcp
```

Add the following configuration to the appropriate file:

```json
{
  "mcpServers": {
    "docketbird-mcp": {
            "command": "python3.11",
            "args": ["PATH_TO_PROJECT/docketbird_mcp.py"],
            "env": {
                "DOCKETBIRD_API_KEY": "YOUR_KEY"
    }
  }
}
```

Replace `/path/to/docketbird-mcp/docketbird_mcp.py` with the absolute path to your `docketbird_mcp.py` file.

