# Build-in Modules
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict


def get_and_apply_styles(
    *,
    script_file: str,
    set_content_funcs: Dict[str, Callable],
    clear: bool = False,
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
        # Clear the lru_cache for the stylesheet loader
        _load_stylesheet.cache_clear()

    for file, set_content in set_content_funcs.items():
        styles_path: Path = Path(script_file).parent / "styles" / file

        # Load stylesheet (cached if already loaded before)
        stylesheet: str = _load_stylesheet(styles_path)

        # Append styles to respective function
        combined_styles[file] += stylesheet + "\n"

    # Apply styles to the appropriate widgets
    for file, styles in combined_styles.items():
        set_content_funcs[file](styles)


@lru_cache(maxsize=None)
def _load_stylesheet(file_path: Path) -> str:
    """
    Helper function to load a stylesheet from disk.

    Args:
        file_path (Path): Path to the stylesheet file

    Returns:
        str: Content of the stylesheet or empty string if file not found
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Stylesheet {file_path.name} not found.")
        return ""  # Return empty string to prevent errors
