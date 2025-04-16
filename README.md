# WiFi-Center

An application that allows users to connect to and disconnect from Wi-Fi using only the keyboard.

[![License: MIT](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)
[![Core README](https://img.shields.io/badge/Core-README-blue)](https://github.com/Aaqil101/WiFi-Center/tree/master/core#readme)
[![Python](https://img.shields.io/badge/Python-3.13%2B-yellow)](https://www.python.org/)
[![GitHub stars](https://img.shields.io/github/stars/Aaqil101/WiFi-Center.svg)](https://github.com/Aaqil101/WiFi-Center/stargazers)

---

## ✨ Features

* **Network Scanner:** Scans and displays available Wi-Fi networks in real-time.
* **Connection Manager:** Connects to secured and unsecured Wi-Fi networks using commands.
* **Command Bar:** Executes commands for various actions (connect, disconnect, refresh, system power, etc.).
* **Command Autocompletion:** Suggests commands as you type (use `Tab` to complete).
* **Help Guide:** Provides access to detailed documentation within the app.

---

## 🚀 Installation (from Source)

**System Requirements:**

* **Operating System:** Windows 10 or newer
* **Python:** Version 3.9 or higher (added to PATH)
* **Dependencies:** PyQt6, Cython, NumPy (see `requirements.txt`)
* **C/C++ Compiler:** Required for building Cython extensions (e.g., [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/))

**Steps:**

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/Aaqil101/WiFi-Center.git
    ```

2. **Navigate to Project Directory:**

    ```bash
    cd WiFi-Center
    ```

3. **(Recommended) Create & Activate Virtual Environment:**

    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

4. **Install Requirements:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Build Cython Extensions:**

    ```bash
    cd .\core\
    python setup.py build_ext --inplace
    cd ..
    ```

    *(Note: The `cd ..` command is added to return to the root directory after building)*

6. **Run the Application:**

    ```bash
    python master.py
    ```

---

## 💻 Basic Usage

Use the command bar at the bottom of the application window to enter commands:

* **Connect to a network:**

    ```bash
    connect <SSID>
    ```

    *(Replace `<SSID>` with the **actual network name**. You'll be prompted for a password if required.)*

* **Disconnect from the current network:**

    ```bash
    disconnect
    ```

* **Refresh the network list:**

    ```bash
    refresh
    ```

* **Get help:**

    ```bash
    --help
    ```

* **Chain commands:** Use `&&` to run multiple commands sequentially.

    ```bash
    refresh && connect "MyWiFiNetwork"
    ```

* **Exit the application:**

    ```bash
    quit
    ```
