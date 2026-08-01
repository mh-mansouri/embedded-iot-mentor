# Build from the repository root, not from this folder:
#   docker build -f chatgpt-app/mcp-server/Dockerfile -t embedded-iot-mentor-mcp .
#
# The server reads the reference files and runs the helper scripts out of
# embedded-iot-mentor/, so the image has to carry the skill folder too. That is
# the whole point of the connector — the docs it serves are the skill's own.
FROM python:3.12-slim

# The MCP registry refuses to list an image that does not claim the server name
# it is published under. This label is what proves the two belong together, and
# it has to be baked into the image rather than added at publish time.
LABEL io.modelcontextprotocol.server.name="io.github.mh-mansouri/embedded-iot-mentor"

WORKDIR /app

# Requirements first: the layer only rebuilds when the dependency changes,
# not on every edit to the mentor.
COPY chatgpt-app/mcp-server/requirements.txt chatgpt-app/mcp-server/
RUN pip install --no-cache-dir -r chatgpt-app/mcp-server/requirements.txt

COPY chatgpt-app/ chatgpt-app/
COPY embedded-iot-mentor/ embedded-iot-mentor/

# 0.0.0.0 because the default loopback bind serves nothing outside the
# container. Hosts that assign a port override PORT.
ENV HOST=0.0.0.0 \
    PORT=8000 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "chatgpt-app/mcp-server/server.py"]
