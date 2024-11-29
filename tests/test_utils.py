import os


def check_path_exists(file):
    """Check if the repository path exists."""
    if not os.path.exists(file):
        raise FileNotFoundError(f"Repository path '{file}' does not exist.")
