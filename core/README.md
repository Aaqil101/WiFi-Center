# WiFi Scanner with Cython Optimization

This project is a WiFi network scanner with a PyQt6 GUI and system tray integration, optimized using Cython for improved performance.

## Features

- Background WiFi network scanning
- System tray integration
- Performance-optimized scanning with Cython
- Graceful fallback to Python implementation if Cython is unavailable
- Windows 10/11 style integration

## Installation

### Prerequisites

- Python 3.6+
- C compiler ([Visual C++ for Windows](https://visualstudio.microsoft.com/visual-cpp-build-tools/), GCC for Linux/Mac)

### Step 1: Install Dependencies

```bash
pip install PyQt6 pywifi numpy cython
```

### Step 2: Compile Cython Module

```bash
python setup.py build_ext --inplace
```

This will compile the `wifi_scanner_cy.pyx` file into a native extension module.

## Usage

Simply run the WiFi scanner script:

```bash
python wifi_scanner.py
```

The application will start in the system tray. You can:

- Double-click the tray icon to open the console
- Right-click the tray icon for menu options:
  - **Show Console**: Open the monitoring window
  - **View WiFi Data**: Open the JSON file with network data
  - **Exit**: Close the application

## Performance Benefits

The Cython implementation provides several performance improvements:

1. **Faster Signal Processing**: The signal strength calculation is optimized with C-level operations
2. **Reduced Memory Overhead**: More efficient data structures
3. **Optimized Sorting**: Network sorting is more efficient
4. **Type-Specific Operations**: Using C types for better performance

## Project Structure

- `wifi_scanner.py`: Main Python application
- `wifi_scanner_cy.pyx`: Cython implementation of performance-critical code
- `setup.py`: Compilation script for Cython module

## Troubleshooting

If you encounter errors related to the Cython module, the application will automatically fall back to the pure Python implementation.

Common issues:

- **Missing C compiler**: Make sure you have a C compiler installed
- **Compilation errors**: Check that you have the correct version of Cython installed
- **Import errors**: Verify that the compilation succeeded by checking for `.so` or `.pyd` files
