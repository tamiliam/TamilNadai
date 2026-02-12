"""Upload Tamil Grammar Benchmark to Hugging Face Hub.

Prerequisites:
  pip install huggingface_hub

Usage:
  python upload_to_hf.py <hf_username>

This will create or update the dataset at:
  https://huggingface.co/datasets/<hf_username>/tamil-grammar-benchmark
"""

import os
import sys

DATASET_NAME = "tamil-grammar-benchmark"
DATASET_DIR = os.path.dirname(os.path.abspath(__file__))

FILES_TO_UPLOAD = [
    "README.md",
    "sentences.csv",
    "sentences.jsonl",
    "rules.csv",
]


def main():
    if len(sys.argv) < 2:
        print("Usage: python upload_to_hf.py <hf_username>")
        print("Example: python upload_to_hf.py myusername")
        sys.exit(1)

    username = sys.argv[1]
    repo_id = f"{username}/{DATASET_NAME}"

    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("Installing huggingface_hub...")
        os.system(f"{sys.executable} -m pip install huggingface_hub")
        from huggingface_hub import HfApi

    api = HfApi()

    # Check if logged in
    try:
        user_info = api.whoami()
        print(f"Logged in as: {user_info['name']}")
    except Exception:
        print("Not logged in. Please run: huggingface-cli login")
        print("You'll need a Hugging Face access token from: https://huggingface.co/settings/tokens")
        sys.exit(1)

    # Create the dataset repo (no-op if it already exists)
    print(f"\nCreating dataset repo: {repo_id}")
    api.create_repo(
        repo_id=repo_id,
        repo_type="dataset",
        exist_ok=True,
    )

    # Upload files
    for filename in FILES_TO_UPLOAD:
        filepath = os.path.join(DATASET_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  Skipping {filename} (not found)")
            continue
        print(f"  Uploading {filename}...")
        api.upload_file(
            path_or_fileobj=filepath,
            path_in_repo=filename,
            repo_id=repo_id,
            repo_type="dataset",
        )

    print(f"\nDone! Dataset available at:")
    print(f"  https://huggingface.co/datasets/{repo_id}")


if __name__ == "__main__":
    main()
