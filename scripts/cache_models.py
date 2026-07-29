import os
import sys
import logging
from pathlib import Path

# Disable concurrent downloads for HF to save RAM
os.environ["HF_HUB_DISABLE_CONCURRENT_DOWNLOADS"] = "1"

# Add the parent directory to sys.path so we can import backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.backends import get_all_model_configs

try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("Warning: huggingface_hub not installed, skipping test run")
    sys.exit(0)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cache_models():
    configs = get_all_model_configs()
    for config in configs:
        logger.info(f"Downloading model {config.model_name} from {config.hf_repo_id}")
        try:
            snapshot_download(
                repo_id=config.hf_repo_id,
                allow_patterns=["*.safetensors", "*.json", "*.txt", "*.pt", "*.model", "*.bin", "*.onnx", "*.tiktoken"],
                ignore_patterns=["*.msgpack", "*.h5", "*.ot"],
                max_workers=1
            )
            logger.info(f"Successfully cached {config.model_name}")
        except Exception as e:
            logger.error(f"Failed to cache {config.model_name}: {e}")

if __name__ == "__main__":
    cache_models()
