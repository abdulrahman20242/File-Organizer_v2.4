# 📂 Sortify - Advanced File Organizer

A powerful and user-friendly desktop application built with Python and PySide6 to intelligently sort your files into clean, organized folders.

Tired of cluttered "Downloads" or "Desktop" folders? Sortify automates the cleaning process with a rich set of features, a multi-language interface, and robust safety mechanisms like Undo and Dry-run mode.

![Sortify Screenshot](https://raw.githubusercontent.com/abdulrahman20242/File-Organizer_v2.3/main/Capture.PNG)

---

## ✨ What's New in v2.5

*   **🎨 Enhanced Category Editor:** Completely redesigned with Auto-Detect, Bulk Add, Search, Import/Export, and Color Coding features.
*   **🎯 Skip Uncategorized Files:** New option to skip files with extensions not in any category instead of moving them to "Others".
*   **⌨️ Keyboard Shortcuts:** Added shortcuts for faster workflow in the Category Editor.
*   **🌐 Default English:** Application now starts in English by default.
*   **🐛 Bug Fixes:** Various improvements and bug fixes.

---

## 🚀 Features

### Core Functionality
*   **Multiple Organization Modes:**
    *   **By Type:** Groups files into folders like `Images`, `Videos`, `Documents`.
    *   **By Name:** Creates a folder for each file, named after the file itself.
    *   **By Date (Month):** Sorts files into `Year/Month` folders (e.g., `2024/10-October`).
    *   **By Date (Day):** Sorts files into `Year/Month/Day` folders (e.g., `2024/10/16`).
    *   **By Size:** Categorizes files as `Small`, `Medium`, or `Large`.
    *   **By First Letter:** Groups files into alphabetical folders (`A`, `B`, `C`...).
*   **Flexible Actions:** Choose to **Move** original files or create a **Copy**.
*   **Smart Conflict Resolution:** Automatically `Rename`, `Overwrite`, or `Skip` files if they already exist in the destination.
*   **Recursive Processing:** Option to include all files from subdirectories.
*   **Skip Uncategorized:** Option to skip files with unknown extensions instead of moving to "Others".

### User Experience & Interface
*   **✨ Enhanced Category Editor:** A powerful interface to manage categories with these features:
    *   **Auto-Detect:** Scan any folder to discover new file extensions automatically.
    *   **Quick Add:** Add extensions instantly by typing and pressing Enter.
    *   **Bulk Add:** Add multiple extensions at once (comma or line separated).
    *   **Move Extensions:** Transfer extensions between categories easily.
    *   **Import/Export:** Backup and restore your category configurations.
    *   **Search & Filter:** Quickly find categories and extensions.
    *   **Color Coding:** Visual identification for each category.
    *   **Keyboard Shortcuts:** `Ctrl+N`, `Ctrl+F`, `Ctrl+S`, `Ctrl+E`, `Ctrl+I`, `F1`, `Delete`.
*   **Modern GUI:** Clean and responsive interface built with PySide6.
*   **Real-time Progress:** A progress bar and live log ensure the app never freezes during long operations.
*   **Detailed Results Table:** See the status of each file (Success, Skipped, Failed) in a clear, color-coded table.
*   **Multi-language Support:** Switch between **English** and **Arabic** on the fly.
*   **Themes:** Instantly switch between **Light** and **Dark** modes.
*   **Drag & Drop:** Easily drop your source folder into the path input field.

### Safety & Customization
*   **↩️ Undo Last Operation:** A critical safety feature! Revert the entire last organization process with a single click.
*   **🛡️ Dry-run Mode:** A simulation mode that shows you what will happen **without touching your files**, allowing you to preview the result safely.
*   **💾 Profiles:** Save and load your favorite settings (e.g., "Sort Downloads" vs. "Backup Photos") for quick reuse.
*   **🚫 Skip Unknown Files:** Choose to skip files that don't match any category instead of moving them to "Others".
*   **Easy Windows Launch:** Includes a `Sortify.bat` script for double-click execution.

---

## 🛠️ Installation

**Prerequisites:** Python 3.9+

1.  Clone the repository and navigate into the project directory:
    ```bash
    git clone https://github.com/abdulrahman20242/File-Organizer_v2.4.git
    cd File-Organizer_v2.4
    ```

2.  **Create and activate a virtual environment (Recommended):**
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  Install the required libraries using pip:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🖥️ Usage

You can run the application in two ways:

1.  **From the terminal (all platforms):**
    (Make sure your virtual environment is active)
    ```bash
    python file_organizer_gui.py
    ```

2.  **On Windows (easy method):**
    Simply double-click the **`Sortify.bat`** file. This script automatically launches the application.

**How it works:**
1.  **Select Source & Destination:** Use the "Browse" buttons or drag-and-drop a folder. If the destination is empty, an `Organized_Files` folder will be created inside the source.
2.  **Choose Your Options:** Select the organization mode, action (move/copy), and conflict policy.
3.  **Optional:** Check "Skip uncategorized files" to ignore files with unknown extensions.
4.  **Run:** Click the "Run" button to start.
5.  **Monitor:** Watch the progress bar and view live logs or the color-coded results table.
6.  **Undo (if needed):** If you're not happy, just click "Undo".

---

## ⚙️ Customization

### Using the Category Editor (Recommended)

The easiest way to customize file categories is through the built-in **Category Editor**. You can access it from the `Edit -> Manage Categories` menu or the toolbar.

**New Features in the Enhanced Editor:**
*   **Auto-Detect:** Click "Auto-Detect" to scan a folder and discover all file extensions in it.
*   **Bulk Add:** Click "Bulk Add" to add multiple extensions at once.
*   **Import/Export:** Save your category setup to a JSON file or load one from another computer.
*   **Search:** Use `Ctrl+F` to quickly find any category or extension.
*   **Colors:** Right-click on a category to change its color for visual identification.

### Manual Configuration

For advanced users, you can also manually edit the **`categories.json`** file. For example, to add `.eps` files to the "Images" category:
```json
{
  "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heic", ".eps"],
  "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
  "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx"],
  "Others": []
}
```

You can also customize category colors in **`category_colors.json`**:
```json
{
  "Images": "#4CAF50",
  "Videos": "#2196F3",
  "Documents": "#FF9800",
  "Others": "#9E9E9E"
}
```

---

## 🧪 Running Tests

This project includes a comprehensive test suite with **69 tests** to ensure the core logic is working correctly.

1.  Install the development dependencies:
    ```bash
    pip install -r requirements-dev.txt
    ```

2.  Run pytest from the project's root directory:
    ```bash
    # Run all tests with verbose output
    pytest test_organizer.py -v
    
    # Quick summary
    pytest test_organizer.py -q
    
    # With coverage report
    pytest test_organizer.py --cov=file_organizer --cov-report=html
    
    # Run specific test class
    pytest test_organizer.py::TestOrganizeByType -v
    
    # Run specific test
    pytest test_organizer.py::TestUndo::test_undo_move_operation -v
    ```

---

## 📒 Project Structure

*   `file_organizer_gui.py`: The main file for the PySide6 graphical user interface.
*   `file_organizer.py`: Contains all the backend logic for file operations (sorting, undo, etc.).
*   `category_editor.py`: The enhanced category editor dialog with advanced features.
*   `test_organizer.py`: The `pytest` test suite for the backend logic (69 tests).
*   `Sortify.bat`: A convenience script for launching the GUI on Windows.
*   `translations.json`: Stores text strings for multi-language support (English & Arabic).
*   `categories.json`: Default and user-customizable file type categories.
*   `category_colors.json`: Stores the color coding for each category.
*   `settings.json`: Stores user settings (created automatically).
*   `profiles.json`: Stores saved profiles (created automatically).
*   `requirements.txt`: Main dependencies required to run the application.
*   `requirements-dev.txt`: Extra dependencies for development and testing.

---

## 🔧 Troubleshooting

*   **App doesn't start:** Make sure Python 3.9+ is installed and all dependencies are installed via `pip install -r requirements.txt`.
*   **Theme not working:** Install pyqtdarktheme: `pip install pyqtdarktheme`.
*   **Icons not showing:** Install QtAwesome: `pip install qtawesome`.
*   **Reset to defaults:** Delete `settings.json`, `categories.json`, and `profiles.json` to reset all settings.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the repository
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Abdulrahman** - [GitHub Profile](https://github.com/abdulrahman20242)

---

## 🙏 Acknowledgments

*   [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python
*   [QtAwesome](https://github.com/spyder-ide/qtawesome) - Iconic fonts for PyQt/PySide
*   [pyqtdarktheme](https://github.com/5yutan5/PyQtDarkTheme) - Dark theme support
```

---


