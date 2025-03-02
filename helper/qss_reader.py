import re


class QSSReader:
    """
    A class for reading specific lines, blocks, or properties from a QSS file.
    """

    def read_line(self, file_path: str, line_number: int) -> str:
        """
        Reads a specific line from a QSS file.

        Parameters:
        file_path (str): The path to the QSS file.
        line_number (int): The line number to read.

        Returns:
        str: The content of the specified line, or None if the line doesn't exist.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            lines: list[str] = file.readlines()
            return (
                lines[line_number - 1].strip()
                if 0 < line_number <= len(lines)
                else "Empty"
            )

    def find_block(self, file_path: str, selector: str) -> str:
        """
        Finds and returns a block of styles associated with a specific selector.

        Parameters:
        file_path (str): The path to the QSS file.
        selector (str): The selector whose styles need to be extracted.

        Returns:
        str: The block of styles for the given selector, or None if not found.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            inside_block = False
            block_lines = []

            for line in file:
                stripped: str = line.strip()
                if stripped.split(" ")[0] == selector:
                    inside_block = True
                if inside_block:
                    block_lines.append(stripped)
                if inside_block and "}" in stripped:
                    break

            return "\n".join(block_lines) if block_lines else "Empty"

    def find_property(self, file_path: str, selector: str, property_name: str) -> str:
        """
        Extracts the value of a specific property from a selector's style block.

        Parameters:
        file_path (str): The path to the QSS file.
        selector (str): The selector whose property value needs to be extracted.
        property_name (str): The property name to search for.

        Returns:
        str: The value of the specified property, or None if not found.
        """

        block: str = self.find_block(file_path, selector)
        if block:
            match: re.Match[str] | None = re.search(
                rf"{property_name}\s*:\s*([^;]+);", block
            )
            return match.group(1).strip() if match else "Empty"
        return "Empty"


# Example usage
if __name__ == "__main__":
    qss_reader = QSSReader()
    file_path = "style.qss"

    print(qss_reader.read_line(file_path, 3))  # Example: Read line 3
    print(qss_reader.find_block(file_path, "QLabel"))  # Find QLabel styles
    print(
        qss_reader.find_property(file_path, "QLabel", "color")
    )  # Extract QLabel color
