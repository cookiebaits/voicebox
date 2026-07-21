import os
import sys

def download_models():
    # Set cache dir to what huggingface uses in the container
    os.environ["HF_HUB_CACHE"] = "/home/voicebox/.cache/huggingface"
    os.makedirs(os.environ["HF_HUB_CACHE"], exist_ok=True)

    from huggingface_hub import snapshot_download

    # We download the models needed for offline deployment based on WHISPER_HF_REPOS and chatterbox/tada logic

    models = [
        "openai/whisper-large-v3-turbo",
        "ResembleAI/chatterbox-turbo",
        "HumeAI/tada-1b",
    ]

    for repo in models:
        print(f"Downloading {repo}...")
        try:
            snapshot_download(
                repo_id=repo,
                token=None,
                allow_patterns=["*.safetensors", "*.json", "*.txt", "*.pt", "*.model", "*.bin", "*.pth", "*.npz", "*.yaml", "*.md"],
            )
        except Exception as e:
            print(f"Failed to download {repo}: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    download_models()
