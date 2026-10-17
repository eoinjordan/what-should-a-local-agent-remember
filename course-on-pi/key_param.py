"""Connection and keys for the course code, Pi edition.

The course's key_param.py holds an Atlas URI, an OpenAI key and a Voyage key.
On the RUBIK Pi the URI points at the local replica set, and the two API keys are
optional: without them the code uses a local embedding model and a scripted LLM so
every MongoDB part of the course still runs. Set the environment variables to use
the real services exactly as the course does.
"""
import os

mongodb_uri = os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017/?replicaSet=rs0")

openai_api_key = os.environ.get("OPENAI_API_KEY", "")      # course default LLM: gpt-4o
openai_base_url = os.environ.get("LLM_BASE_URL", "")       # any OpenAI-compatible server, e.g. llama-server --jinja
voyage_api_key = os.environ.get("VOYAGE_API_KEY", "")      # course default embeddings: voyage-3-lite (512 dims)
