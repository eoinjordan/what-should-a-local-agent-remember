"""Embeddings for the course code, Pi edition.

Course default: VoyageAI voyage-3-lite, 512 dimensions, needs an API key.
Pi default:     fastembed BAAI/bge-small-en-v1.5, 384 dimensions, runs locally on the
                Pi's CPU through onnxruntime (about 130 MB of model files, well under
                the RAM that a torch-based model would need next to the Pi's other jobs).

Both are exposed through one function so main.py reads exactly like the course.
"""
import key_param

if key_param.voyage_api_key:
    import voyageai
    MODEL_NAME, DIMENSIONS = "voyage-3-lite", 512
    _client = voyageai.Client(api_key=key_param.voyage_api_key)

    def embed(text: str, input_type: str = "query"):
        return _client.embed(text, model=MODEL_NAME, input_type=input_type).embeddings[0]
else:
    from fastembed import TextEmbedding
    MODEL_NAME, DIMENSIONS = "BAAI/bge-small-en-v1.5", 384
    _model = TextEmbedding(model_name=MODEL_NAME)

    def embed(text: str, input_type: str = "query"):
        return next(iter(_model.embed([text]))).tolist()
