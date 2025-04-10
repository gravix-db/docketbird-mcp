FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml /app/
COPY requirements.txt /app/

# Install uv package manager and other tools
RUN pip install --no-cache-dir uv && \
    pip install --no-cache-dir termcolor

# Install dependencies using the --system flag with uv
RUN uv pip install --system .

# Copy the rest of the application
COPY . /app/

# Expose port for potential HTTP/API access (if needed in the future)
EXPOSE 8000

# Create a startup script with debug information
RUN echo '#!/bin/bash\necho "Starting DocketBird MCP server..."\necho "API Key set: ${DOCKETBIRD_API_KEY:0:5}..."\necho "Transport type: ${TRANSPORT_TYPE}"\npython -c "import os; print(f\"Environment variables: {dict(os.environ)}\")" | grep -v DOCKETBIRD_API_KEY\necho "Running python docketbird_mcp.py with transport ${TRANSPORT_TYPE}"\npython docketbird_mcp.py --transport ${TRANSPORT_TYPE}' > /app/start.sh && \
    chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"] 