import os
from pathlib import Path


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


def get_and_apply_styles(*, script_file: str, file: str, set_content: callable) -> None:
    """
    Given a script file path, a style file name, and a setter function for the style content,
    applies the style to the given setter function.

    Args:
        script_file: The path to the script file that is applying the style.
        file: The name of the style file to apply.
        set_content: A callable that takes the style content as a string and applies it.

    Returns:
        The path to the style file that was applied.
    """
    style_path: Path = Path(script_file).parent / "styles" / file

    with open(str(style_path), "r") as file:
        set_content(file.read())


if __name__ == "__main__":
    print("Downloads directory:", get_downloads_directory())
