import os
from collections import defaultdict
from pathlib import Path
from typing import Callable, Dict


def get_downloads_directory() -> str:
    """
    Determine the path to the current user's Downloads directory.
    Uses pathlib as the primary method with environment variables as fallback.

    Returns:
        str: The absolute path to the Downloads directory
    """
    downloads_path = None

    # Primary method: Using pathlib
    try:
        downloads_path = str(Path.home() / "Downloads")
        if os.path.exists(downloads_path):
            return downloads_path
    except Exception as e:
        print(f"Pathlib method failed: {e}")

    # Fallback method: Using environment variables
    try:
        # Try Windows environment variable first
        user_profile: str | None = os.environ.get("USERPROFILE")
        if user_profile:
            downloads_path = os.path.join(user_profile, "Downloads")
            if os.path.exists(downloads_path):
                return downloads_path

        # Try Unix/MacOS environment variable
        home_dir: str | None = os.environ.get("HOME")
        if home_dir:
            downloads_path: str = os.path.join(home_dir, "Downloads")
            if os.path.exists(downloads_path):
                return downloads_path
    except Exception as e:
        print(f"Environment variable method failed: {e}")

    # If we reach here, both methods failed
    raise FileNotFoundError("Could not locate Downloads directory using any method")


_stylesheet_cache: dict = {}  # Global dictionary to store stylesheets


def get_and_apply_styles(
    *, script_file: str, set_content_funcs: Dict[str, Callable], clear: bool = False
) -> None:
    """
    Applies stylesheets to the respective widgets using the provided functions.

    Loads stylesheets from the "styles" directory relative to the provided script file
    and applies them to the widgets using the provided functions.

    Args:
        script_file (str): The path to the script file
        set_content_funcs (Dict[str, Callable]): A dictionary of functions to apply the stylesheets
            where the key is the name of the stylesheet and the value is the function to apply it
        clear (bool, optional): If True, clears the cache before applying styles, Defaults to False.

    Example:
    >>> get_and_apply_styles(
            script_file=__file__,
            set_content_funcs={
                "style1.css": self.widget1.setStyleSheet,
                "style2.css": self.widget2.setStyleSheet,
            }
        )

    Returns:
        None
    """
    # Dictionary to store merged styles for each function
    combined_styles = defaultdict(str)

    if clear:
        _stylesheet_cache.clear()  # Clear the cache

    for file, set_content in set_content_funcs.items():
        styles_path: Path = Path(script_file).parent / "styles" / file

        # Load from cache if available
        if styles_path not in _stylesheet_cache:
            _stylesheet_cache[styles_path] = _load_stylesheet(styles_path)

        # Append styles to respective function
        combined_styles[file] += _stylesheet_cache[styles_path] + "\n"

    # Apply styles to the appropriate widgets
    for file, styles in combined_styles.items():
        set_content_funcs[file](styles)


def _load_stylesheet(file_path: Path) -> str:
    """Helper function to load a stylesheet from disk."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"⚠ Warning: Stylesheet {file_path.name} not found.")
        return ""  # Return empty string to prevent errors


if __name__ == "__main__":
    print("Downloads directory:", get_downloads_directory())
