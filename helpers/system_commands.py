# In-Build Modules
import ctypes
import os


def shutdown() -> None:
    """Shut down the computer after receiving user confirmation."""
    os.system("shutdown /s /t 0")


def reboot() -> None:
    """Reboot the computer after receiving user confirmation."""
    os.system("shutdown /r /t 0")


def hibernate() -> None:
    """Attempts to hibernate the PC. If hibernation is unavailable, it falls back to sleep."""
    try:
        result: int = os.system("shutdown /h")
        if result == 0:
            return  # Successfully hibernated, exit function
    except Exception:
        pass  # Hibernation is not available, proceed to sleep

    # If hibernation fails, try sleep
    try:
        ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
    except Exception:
        pass  # If both fail, do nothing


def sleep() -> None:
    """Attempts to put the PC to sleep. If sleep is unavailable, it falls back to hibernation."""
    try:
        ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
        return  # Successfully slept, exit function
    except Exception:
        pass  # Sleep is not available, proceed to hibernate

    # If sleeping fails, try hibernation
    os.system("shutdown /h")


def lock_or_logout() -> None:
    """Attempts to lock the workstation; if unavailable, logs out the user."""
    try:
        if ctypes.windll.user32.LockWorkStation():
            return  # Successfully locked, exit function
    except AttributeError:
        pass  # LockWorkStation is not available, proceed to logout

    # If locking fails, sign out the user
    os.system("shutdown /l")
