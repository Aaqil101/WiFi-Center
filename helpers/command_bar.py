def processing(self, *, begin: bool = False, end: bool = False) -> None:
    """
    Helper function to control the command bar's enabled state.

    Disables the command bar at the beginning of a function and enables it at the end.
    Useful for preventing user input during long-running operations.

    Parameters:
        begin (bool, optional): If True, disables the command bar. Defaults to False.
        end (bool, optional): If True, enables the command bar and focuses it. Defaults to False.
    """
    if begin:
        # Disable the command bar at the beginning of the function
        self.command_bar.setDisabled(True)

    if end:
        self.command_bar.setDisabled(False)
        self.command_bar.setFocus()
