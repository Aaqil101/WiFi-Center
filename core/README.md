# 🌐 WiFi Scanner with 🚀 Cython Optimization

This project is a **WiFi network scanner** with a sleek **PyQt6 GUI** and **system tray integration**, supercharged with **Cython** for lightning-fast performance. 🏎️

---

## ✨ Features

- 🔍 **Background WiFi Scanning**: Always stay updated with available networks.
- 🖥️ **System Tray Integration**: Access the app conveniently from your system tray.
- ⚡ **Cython Optimization**: Enjoy blazing-fast performance.
- 🔄 **Graceful Fallback**: Automatically switches to Python if Cython is unavailable.
- 🎨 **Windows 10/11 Style**: Seamlessly blends with your OS theme.

---

## 🛠️ Installation

### 📋 Prerequisites

- 🐍 **Python 3.6+**
- 🛠️ **C Compiler** ([Visual C++ for Windows](https://visualstudio.microsoft.com/visual-cpp-build-tools/), GCC for Linux/Mac)

### 🚀 Step 1: Install Dependencies

```bash
pip install PyQt6 pywifi numpy cython
```

### ⚙️ Step 2: Compile Cython Module

```bash
python setup.py build_ext --inplace
```

This will compile the `wifi_scanner_cy.pyx` file into a native extension module. 🧩

---

## 🎮 Usage

Run the WiFi scanner script and take control:

```bash
python wifi_scanner.py
```

### 🖱️ System Tray Options

- **Double-click** the tray icon to open the console.
- **Right-click** the tray icon for menu options:
  - 🖥️ **Show Console**: Open the monitoring window.
  - 📂 **View WiFi Data**: Open the JSON file with network data.
  - ❌ **Exit**: Close the application.

---

## 🚀 Performance Benefits

The Cython implementation provides several performance boosts:

1. ⚡ **Faster Signal Processing**: Optimized with C-level operations.
2. 🧠 **Reduced Memory Overhead**: Efficient data structures.
3. 🔄 **Optimized Sorting**: Faster network sorting.
4. 🛠️ **Type-Specific Operations**: Leveraging C types for better performance.

---

## 🗂️ Project Structure

- `wifi_scanner.py`: Main Python application.
- `wifi_scanner_cy.pyx`: Cython implementation of performance-critical code.
- `setup.py`: Compilation script for the Cython module.

---

## 🛠️ Troubleshooting

If you encounter issues with the Cython module, the app will automatically fall back to the pure Python implementation. 🛡️

### Common Issues

- ❌ **Missing C Compiler**: Ensure you have a C compiler installed.
- ⚠️ **Compilation Errors**: Check that you have the correct version of Cython installed.
- 📂 **Import Errors**: Verify that the compilation succeeded by checking for `.so` or `.pyd` files.

---

Enjoy seamless WiFi scanning with style and speed! 🌟
