# 📝 ملف README.md الكامل

```markdown
# 📂 Sortify - Advanced File Organizer

A powerful and user-friendly desktop application built with Python and PySide6 to intelligently sort your files into clean, organized folders.

Tired of cluttered "Downloads" or "Desktop" folders? Sortify automates the cleaning process with a rich set of features, a multi-language interface, and robust safety mechanisms like Undo and Dry-run mode.

![Sortify Screenshot](https://raw.githubusercontent.com/abdulrahman20242/Sortify/main/Capture.PNG)

---

## ✨ What's New in v2.5

- 🎨 **Enhanced Category Editor** - Completely redesigned with advanced features
- 🔍 **Auto-Detect Extensions** - Scan any folder to discover new file types
- 📋 **Bulk Add Extensions** - Add multiple extensions at once
- 🔎 **Search & Filter** - Quickly find categories and extensions
- 🎯 **Skip Uncategorized Files** - New option to skip files not in any category
- 📥 **Import/Export Settings** - Backup and share your category configurations
- 🌈 **Color-Coded Categories** - Visual identification for each category
- ⌨️ **Keyboard Shortcuts** - Faster workflow with hotkeys
- 🌐 **Default English Language** - App now starts in English by default

---

## 🚀 Features

### Core Functionality

| Feature | Description |
|---------|-------------|
| **By Type** | Groups files into folders like `Images`, `Videos`, `Documents` |
| **By Date (Month)** | Sorts files into `Year/Month` folders (e.g., `2024/10-October`) |
| **By Date (Day)** | Sorts files into `Year/Month/Day` folders (e.g., `2024/10/16`) |
| **By Size** | Categorizes files as `Small`, `Medium`, or `Large` |
| **By First Letter** | Groups files into alphabetical folders (`A`, `B`, `C`...) |
| **By Name** | Creates a folder for each file using its name |

- **Flexible Actions:** Choose to **Move** original files or create a **Copy**
- **Smart Conflict Resolution:** Automatically `Rename`, `Overwrite`, or `Skip` duplicate files
- **Recursive Processing:** Option to include all files from subdirectories
- **Skip Uncategorized:** Option to skip files with unknown extensions instead of moving to "Others"

### 🎨 Enhanced Category Editor (NEW!)

The completely redesigned Category Editor includes:

| Feature | Description | Shortcut |
|---------|-------------|----------|
| **Auto-Detect** | Scan folders to discover new extensions | - |
| **Quick Add** | Add extensions by pressing Enter | `Enter` |
| **Bulk Add** | Add multiple extensions at once | - |
| **Move Extensions** | Transfer extensions between categories | Right-click |
| **Import/Export** | Backup and restore settings | `Ctrl+I` / `Ctrl+E` |
| **Search & Filter** | Find categories and extensions quickly | `Ctrl+F` |
| **Color Coding** | Visual identification for categories | Right-click |
| **Reset to Defaults** | Restore original categories | - |
| **Help Dialog** | Comprehensive usage guide | `F1` |

### User Experience & Interface

- **Modern GUI:** Clean and responsive interface built with PySide6
- **Real-time Progress:** Progress bar and live log for long operations
- **Detailed Results Table:** Color-coded status for each file (Success, Skipped, Failed)
- **Multi-language Support:** Switch between **English** and **Arabic** instantly
- **Themes:** Switch between **Light** and **Dark** modes
- **Drag & Drop:** Drop folders directly into the path input field

### Safety & Customization

| Feature | Description |
|---------|-------------|
| ↩️ **Undo** | Revert the entire last operation with one click |
| 🛡️ **Dry-run** | Preview what will happen without touching files |
| 💾 **Profiles** | Save and load favorite settings for quick reuse |
| 🚫 **Skip Unknown** | Skip uncategorized files instead of moving to Others |

---

## 🛠️ Installation

**Prerequisites:** Python 3.9+

### Quick Install

```bash
# Clone the repository
git clone https://github.com/abdulrahman20242/Sortify.git
cd Sortify

# Create virtual environment (Recommended)
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

```
PySide6>=6.5.0
QtAwesome>=1.2.0
pyqtdarktheme>=2.1.0
```

---

## 🖥️ Usage

### Running the Application

**Terminal (all platforms):**
```bash
python file_organizer_gui.py
```

**Windows (easy method):**
Double-click **`Sortify.bat`**

### Basic Workflow

1. **Select Source & Destination**
   - Use "Browse" buttons or drag-and-drop
   - Leave destination empty to create `Organized_Files` inside source

2. **Choose Options**
   - Organization mode (Type, Date, Size, etc.)
   - Action (Move or Copy)
   - Conflict policy (Rename, Skip, Overwrite)
   - ☑️ Check "Skip uncategorized files" to ignore unknown extensions

3. **Run & Monitor**
   - Click "Run" to start
   - Watch progress bar and live logs
   - View color-coded results table

4. **Undo if Needed**
   - Click "Undo" to revert all changes

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+R` | Run organizer |
| `Ctrl+Q` | Exit application |
| `Ctrl+N` | New category (in editor) |
| `Ctrl+F` | Search (in editor) |
| `Ctrl+S` | Save & Close (in editor) |
| `Ctrl+E` | Export settings |
| `Ctrl+I` | Import settings |
| `F1` | Help |
| `Delete` | Delete selected item |

---

## ⚙️ Customization

### Using the Category Editor (Recommended)

Access via `Edit → Manage Categories` or toolbar button.

**Features:**
- ➕ Add/Remove categories and extensions
- 🔍 Auto-detect extensions from any folder
- 📋 Bulk add multiple extensions
- ↔️ Move extensions between categories
- 🎨 Change category colors
- 📥 Import/Export configurations
- 🔄 Reset to defaults

### Manual Configuration

Edit **`categories.json`** directly:

```json
{
  "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
  "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
  "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx"],
  "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
  "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
  "Code": [".py", ".js", ".html", ".css", ".json"],
  "Others": []
}
```

### Category Colors

Colors are stored in **`category_colors.json`**:

```json
{
  "Images": "#4CAF50",
  "Videos": "#2196F3",
  "Audio": "#9C27B0",
  "Documents": "#FF9800",
  "Archives": "#795548",
  "Code": "#00BCD4",
  "Others": "#9E9E9E"
}
```

---

## 🧪 Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-cov
```

### Run Tests

```bash
# Run all tests
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

### Test Coverage

The test suite includes **69 tests** covering:
- ✅ All organization modes
- ✅ Conflict policies
- ✅ Undo functionality
- ✅ Edge cases
- ✅ Error handling

---

## 📁 Project Structure

```
Sortify/
├── file_organizer.py        # Core backend logic
├── file_organizer_gui.py    # Main PySide6 GUI
├── category_editor.py       # Enhanced category editor dialog
├── test_organizer.py        # Pytest test suite (69 tests)
├── translations.json        # Multi-language strings (EN/AR)
├── categories.json          # File type categories (auto-generated)
├── category_colors.json     # Category colors (auto-generated)
├── settings.json            # User settings (auto-generated)
├── profiles.json            # Saved profiles (auto-generated)
├── undo.log                 # Undo operation log (auto-generated)
├── requirements.txt         # Main dependencies
├── requirements-dev.txt     # Development dependencies
├── Sortify.bat              # Windows launcher
└── README.md                # This file
```

---

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| App doesn't start | Ensure Python 3.9+ and all dependencies installed |
| Theme not working | Install `pyqtdarktheme`: `pip install pyqtdarktheme` |
| Icons not showing | Install `QtAwesome`: `pip install qtawesome` |
| Permission error | Run as administrator or check folder permissions |

### Reset Application

Delete these files to reset:
- `settings.json` - Reset all settings
- `categories.json` - Reset categories to defaults
- `profiles.json` - Remove saved profiles

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Abdulrahman** - [GitHub Profile](https://github.com/abdulrahman20242)

---

## 🙏 Acknowledgments

- [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python
- [QtAwesome](https://github.com/spyder-ide/qtawesome) - Iconic fonts for PyQt/PySide
- [pyqtdarktheme](https://github.com/5yutan5/PyQtDarkTheme) - Dark theme support

---

<p align="center">
  Made with ❤️ for organizing chaos into order
</p>
```
