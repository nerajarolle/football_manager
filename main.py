import os

from app import main
# Render injects a dynamic $PORT variable, defaulting to 8001 locally
env_port = int(os.environ.get("PORT", 8001))
main(port=env_port, reload=False)
