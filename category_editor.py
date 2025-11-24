"""
Enhanced Category Editor Dialog
محرر الفئات المحسّن مع ميزات متقدمة
"""

import json
import os
from pathlib import Path
from typing import Dict, Set, List, Optional
from collections import Counter

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QGroupBox, QMessageBox, QInputDialog, QFileDialog,
    QMenu, QToolButton, QFrame, QSplitter, QProgressDialog,
    QComboBox, QCheckBox, QTextEdit, QTabWidget, QWidget,
    QApplication, QStyle
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QSize
from PySide6.QtGui import QColor, QBrush, QIcon, QAction, QKeySequence, QShortcut, QPixmap

import qtawesome as qta
import file_organizer


# ═══════════════════════════════════════════════════════════════
#                    COLOR SCHEMES FOR CATEGORIES
# ═══════════════════════════════════════════════════════════════

CATEGORY_COLORS = {
    "Images": "#4CAF50",
    "Videos": "#2196F3",
    "Audio": "#9C27B0",
    "Documents": "#FF9800",
    "Archives": "#795548",
    "Code": "#00BCD4",
    "Executables": "#F44336",
    "Others": "#9E9E9E",
    "default": "#607D8B",
}

DEFAULT_COLORS = [
    "#E91E63", "#673AB7", "#3F51B5", "#009688",
    "#8BC34A", "#CDDC39", "#FFC107", "#FF5722",
]


# ═══════════════════════════════════════════════════════════════
#                    EXTENSION SCANNER THREAD
# ═══════════════════════════════════════════════════════════════

class ExtensionScannerThread(QThread):
    """Thread لفحص الامتدادات في مجلد"""
    progress = Signal(int, int)
    finished_scan = Signal(dict)
    
    def __init__(self, folder_path: Path, recursive: bool = True):
        super().__init__()
        self.folder_path = folder_path
        self.recursive = recursive
        self._cancelled = False
    
    def cancel(self):
        self._cancelled = True
    
    def run(self):
        extensions = Counter()
        try:
            if self.recursive:
                files = list(self.folder_path.rglob("*"))
            else:
                files = list(self.folder_path.glob("*"))
            
            total = len(files)
            for i, f in enumerate(files):
                if self._cancelled:
                    break
                if f.is_file():
                    ext = f.suffix.lower()
                    if ext:
                        extensions[ext] += 1
                if i % 100 == 0:
                    self.progress.emit(i, total)
            
            self.progress.emit(total, total)
            self.finished_scan.emit(dict(extensions))
        except Exception as e:
            self.finished_scan.emit({})


# ═══════════════════════════════════════════════════════════════
#                    HELP DIALOG
# ═══════════════════════════════════════════════════════════════

class HelpDialog(QDialog):
    """نافذة المساعدة الشاملة"""
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.tr_func = translator.t if translator else lambda x, d=None: d or x
        self.setWindowTitle(self.tr_func("help_title", "Category Editor Help"))
        self.setMinimumSize(600, 500)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Quick Start Tab
        quick_start = QTextEdit()
        quick_start.setReadOnly(True)
        quick_start.setHtml(self._get_quick_start_html())
        tabs.addTab(quick_start, qta.icon('fa5s.rocket'), 
                   self.tr_func("quick_start", "Quick Start"))
        
        # Shortcuts Tab
        shortcuts = QTextEdit()
        shortcuts.setReadOnly(True)
        shortcuts.setHtml(self._get_shortcuts_html())
        tabs.addTab(shortcuts, qta.icon('fa5s.keyboard'), 
                   self.tr_func("shortcuts", "Shortcuts"))
        
        # Tips Tab
        tips = QTextEdit()
        tips.setReadOnly(True)
        tips.setHtml(self._get_tips_html())
        tabs.addTab(tips, qta.icon('fa5s.lightbulb'), 
                   self.tr_func("tips", "Tips"))
        
        # Close button
        close_btn = QPushButton(qta.icon('fa5s.times'), 
                               self.tr_func("close", "Close"))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def _get_quick_start_html(self):
        return """
        <h2>🚀 Quick Start Guide</h2>
        <h3>Adding Extensions</h3>
        <ul>
            <li><b>Quick Add:</b> Type extension in the text field and press Enter</li>
            <li><b>Bulk Add:</b> Click "Bulk Add" to add multiple extensions at once</li>
            <li><b>Auto-Detect:</b> Scan a folder to discover new extensions</li>
        </ul>
        
        <h3>Managing Categories</h3>
        <ul>
            <li><b>Add Category:</b> Click the + button or use Ctrl+N</li>
            <li><b>Rename:</b> Double-click on a category name</li>
            <li><b>Delete:</b> Select and press Delete key</li>
            <li><b>Change Color:</b> Right-click on a category</li>
        </ul>
        
        <h3>Moving Extensions</h3>
        <ul>
            <li>Drag & drop extensions between categories</li>
            <li>Or right-click and select "Move to..."</li>
        </ul>
        """
    
    def _get_shortcuts_html(self):
        return """
        <h2>⌨️ Keyboard Shortcuts</h2>
        <table border="1" cellpadding="8" style="border-collapse: collapse;">
            <tr><th>Shortcut</th><th>Action</th></tr>
            <tr><td><b>Ctrl+N</b></td><td>New Category</td></tr>
            <tr><td><b>Ctrl+F</b></td><td>Search</td></tr>
            <tr><td><b>Ctrl+S</b></td><td>Save & Close</td></tr>
            <tr><td><b>Ctrl+E</b></td><td>Export Settings</td></tr>
            <tr><td><b>Ctrl+I</b></td><td>Import Settings</td></tr>
            <tr><td><b>Delete</b></td><td>Delete Selected</td></tr>
            <tr><td><b>Enter</b></td><td>Quick Add Extension</td></tr>
            <tr><td><b>F1</b></td><td>Show Help</td></tr>
            <tr><td><b>Escape</b></td><td>Close Dialog</td></tr>
        </table>
        """
    
    def _get_tips_html(self):
        return """
        <h2>💡 Tips & Tricks</h2>
        <ul>
            <li><b>Use Auto-Detect</b> on your Downloads folder to find all file types you commonly use</li>
            <li><b>Export your settings</b> to share with others or backup</li>
            <li><b>Color code</b> your categories for easier visual identification</li>
            <li><b>Search</b> to quickly find where an extension is categorized</li>
            <li><b>Bulk add</b> extensions from a list (one per line)</li>
        </ul>
        
        <h3>Extension Format</h3>
        <ul>
            <li>Extensions should start with a dot: <code>.txt</code></li>
            <li>If you type without dot, it will be added automatically</li>
            <li>Extensions are case-insensitive: <code>.JPG</code> = <code>.jpg</code></li>
        </ul>
        """


# ═══════════════════════════════════════════════════════════════
#                    BULK ADD DIALOG
# ═══════════════════════════════════════════════════════════════

class BulkAddDialog(QDialog):
    """نافذة إضافة امتدادات متعددة"""
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.tr_func = translator.t if translator else lambda x, d=None: d or x
        self.setWindowTitle(self.tr_func("bulk_add_title", "Bulk Add Extensions"))
        self.setMinimumSize(400, 300)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Instructions
        info_label = QLabel(self.tr_func("bulk_add_info", 
            "Enter extensions (one per line or comma-separated):"))
        layout.addWidget(info_label)
        
        # Text area
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(".txt, .doc, .pdf\n.mp3\n.mp4")
        layout.addWidget(self.text_edit)
        
        # Preview
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("color: gray;")
        layout.addWidget(self.preview_label)
        
        self.text_edit.textChanged.connect(self._update_preview)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton(qta.icon('fa5s.times'), 
                                self.tr_func("cancel", "Cancel"))
        cancel_btn.clicked.connect(self.reject)
        
        add_btn = QPushButton(qta.icon('fa5s.plus'), 
                             self.tr_func("add_all", "Add All"))
        add_btn.clicked.connect(self.accept)
        add_btn.setDefault(True)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)
    
    def _update_preview(self):
        extensions = self.get_extensions()
        count = len(extensions)
        self.preview_label.setText(f"{count} extensions found")
    
    def get_extensions(self) -> List[str]:
        """استخراج الامتدادات من النص"""
        text = self.text_edit.toPlainText()
        text = text.replace(',', '\n').replace(';', '\n')
        extensions = []
        for line in text.split('\n'):
            ext = line.strip().lower()
            if ext:
                if not ext.startswith('.'):
                    ext = '.' + ext
                if ext not in extensions:
                    extensions.append(ext)
        return extensions


# ═══════════════════════════════════════════════════════════════
#                    AUTO-DETECT DIALOG
# ═══════════════════════════════════════════════════════════════

class AutoDetectDialog(QDialog):
    """نافذة الاكتشاف التلقائي للامتدادات"""
    
    def __init__(self, parent=None, translator=None, current_extensions: Set[str] = None):
        super().__init__(parent)
        self.tr_func = translator.t if translator else lambda x, d=None: d or x
        self.current_extensions = current_extensions or set()
        self.detected_extensions = {}
        self.scanner_thread = None
        
        self.setWindowTitle(self.tr_func("auto_detect_title", "Auto-Detect Extensions"))
        self.setMinimumSize(600, 500)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Folder selection
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel(self.tr_func("folder", "Folder:")))
        
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText(self.tr_func("select_folder", "Select a folder to scan..."))
        folder_layout.addWidget(self.folder_edit)
        
        browse_btn = QPushButton(qta.icon('fa5s.folder-open'), "")
        browse_btn.clicked.connect(self._browse_folder)
        folder_layout.addWidget(browse_btn)
        
        layout.addLayout(folder_layout)
        
        # Options
        options_layout = QHBoxLayout()
        self.recursive_check = QCheckBox(self.tr_func("include_subfolders", "Include subfolders"))
        self.recursive_check.setChecked(True)
        options_layout.addWidget(self.recursive_check)
        
        self.new_only_check = QCheckBox(self.tr_func("show_new_only", "Show new extensions only"))
        self.new_only_check.setChecked(True)
        self.new_only_check.stateChanged.connect(self._update_list)
        options_layout.addWidget(self.new_only_check)
        
        options_layout.addStretch()
        
        self.scan_btn = QPushButton(qta.icon('fa5s.search'), 
                                   self.tr_func("scan", "Scan"))
        self.scan_btn.clicked.connect(self._start_scan)
        options_layout.addWidget(self.scan_btn)
        
        layout.addLayout(options_layout)
        
        # Progress
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: blue;")
        layout.addWidget(self.progress_label)
        
        # Results
        results_group = QGroupBox(self.tr_func("detected_extensions", "Detected Extensions"))
        results_layout = QVBoxLayout(results_group)
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel(self.tr_func("filter", "Filter:")))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText(self.tr_func("type_to_filter", "Type to filter..."))
        self.filter_edit.textChanged.connect(self._update_list)
        filter_layout.addWidget(self.filter_edit)
        results_layout.addLayout(filter_layout)
        
        self.results_list = QListWidget()
        self.results_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        results_layout.addWidget(self.results_list)
        
        # Stats
        self.stats_label = QLabel("")
        results_layout.addWidget(self.stats_label)
        
        layout.addWidget(results_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        select_all_btn = QPushButton(self.tr_func("select_all", "Select All"))
        select_all_btn.clicked.connect(lambda: self._select_all(True))
        btn_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton(self.tr_func("deselect_all", "Deselect All"))
        deselect_all_btn.clicked.connect(lambda: self._select_all(False))
        btn_layout.addWidget(deselect_all_btn)
        
        btn_layout.addStretch()
        
        cancel_btn = QPushButton(qta.icon('fa5s.times'), 
                                self.tr_func("cancel", "Cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        add_btn = QPushButton(qta.icon('fa5s.plus'), 
                             self.tr_func("add_selected", "Add Selected"))
        add_btn.clicked.connect(self.accept)
        btn_layout.addWidget(add_btn)
        
        layout.addLayout(btn_layout)
    
    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, 
            self.tr_func("select_folder", "Select Folder")
        )
        if folder:
            self.folder_edit.setText(folder)
    
    def _start_scan(self):
        folder = self.folder_edit.text().strip()
        if not folder or not Path(folder).is_dir():
            QMessageBox.warning(
                self, 
                self.tr_func("error", "Error"),
                self.tr_func("invalid_folder", "Please select a valid folder")
            )
            return
        
        self.scan_btn.setEnabled(False)
        self.progress_label.setText(self.tr_func("scanning", "Scanning..."))
        self.results_list.clear()
        
        self.scanner_thread = ExtensionScannerThread(
            Path(folder), 
            self.recursive_check.isChecked()
        )
        self.scanner_thread.progress.connect(self._on_progress)
        self.scanner_thread.finished_scan.connect(self._on_scan_finished)
        self.scanner_thread.start()
    
    def _on_progress(self, current, total):
        self.progress_label.setText(f"Scanned {current} of {total} files...")
    
    def _on_scan_finished(self, extensions: dict):
        self.scan_btn.setEnabled(True)
        self.detected_extensions = extensions
        self._update_list()
        self.progress_label.setText(self.tr_func("scan_complete", "Scan complete!"))
    
    def _update_list(self):
        self.results_list.clear()
        filter_text = self.filter_edit.text().lower()
        show_new_only = self.new_only_check.isChecked()
        
        total_count = 0
        new_count = 0
        
        for ext, count in sorted(self.detected_extensions.items(), 
                                  key=lambda x: -x[1]):
            is_new = ext not in self.current_extensions
            
            if show_new_only and not is_new:
                continue
            
            if filter_text and filter_text not in ext:
                continue
            
            item = QListWidgetItem(f"{ext} ({count} files)")
            item.setData(Qt.ItemDataRole.UserRole, ext)
            
            if is_new:
                item.setForeground(QBrush(QColor("#4CAF50")))
                new_count += 1
            else:
                item.setForeground(QBrush(QColor("#9E9E9E")))
            
            self.results_list.addItem(item)
            total_count += 1
        
        self.stats_label.setText(f"Total: {total_count} | New: {new_count}")
    
    def _select_all(self, select: bool):
        for i in range(self.results_list.count()):
            self.results_list.item(i).setSelected(select)
    
    def get_selected_extensions(self) -> List[str]:
        """الحصول على الامتدادات المحددة"""
        extensions = []
        for item in self.results_list.selectedItems():
            ext = item.data(Qt.ItemDataRole.UserRole)
            if ext:
                extensions.append(ext)
        return extensions
    
    def closeEvent(self, event):
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.cancel()
            self.scanner_thread.wait()
        super().closeEvent(event)


# ═══════════════════════════════════════════════════════════════
#                    ENHANCED CATEGORY EDITOR
# ═══════════════════════════════════════════════════════════════

class EnhancedCategoryEditorDialog(QDialog):
    """محرر الفئات المحسّن"""
    
    categories_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tr = parent.tr if parent and hasattr(parent, 'tr') else None
        self.categories_data: Dict[str, List[str]] = {}
        self.category_colors: Dict[str, str] = {}
        self._load_data()
        
        self.setWindowTitle(self._t("manage_categories", "Manage Categories"))
        self.setMinimumSize(900, 600)
        
        self._setup_shortcuts()
        self._setup_ui()
        self._populate_categories()
    
    def _t(self, key: str, default: str = None) -> str:
        """ترجمة النص"""
        if self.tr:
            return self.tr.t(key, default)
        return default or key
    
    def _load_data(self):
        """تحميل البيانات"""
        categories = file_organizer.load_categories()
        self.categories_data = {k: list(v) for k, v in categories.items()}
        
        # تحميل الألوان
        colors_file = Path("category_colors.json")
        if colors_file.exists():
            try:
                with open(colors_file, 'r', encoding='utf-8') as f:
                    self.category_colors = json.load(f)
            except:
                pass
        
        # تعيين ألوان افتراضية
        for cat in self.categories_data:
            if cat not in self.category_colors:
                self.category_colors[cat] = CATEGORY_COLORS.get(
                    cat, 
                    CATEGORY_COLORS["default"]
                )
    
    def _save_colors(self):
        """حفظ الألوان"""
        try:
            with open("category_colors.json", 'w', encoding='utf-8') as f:
                json.dump(self.category_colors, f, indent=2)
        except:
            pass
    
    def _setup_shortcuts(self):
        """إعداد اختصارات لوحة المفاتيح"""
        QShortcut(QKeySequence("Ctrl+N"), self, self._add_category)
        QShortcut(QKeySequence("Ctrl+F"), self, self._focus_search)
        QShortcut(QKeySequence("Ctrl+S"), self, self._save_and_close)
        QShortcut(QKeySequence("Ctrl+E"), self, self._export_settings)
        QShortcut(QKeySequence("Ctrl+I"), self, self._import_settings)
        QShortcut(QKeySequence("F1"), self, self._show_help)
        QShortcut(QKeySequence("Delete"), self, self._delete_selected)
    
    def _setup_ui(self):
        """إعداد واجهة المستخدم"""
        main_layout = QVBoxLayout(self)
        
        # ═══════════════ TOOLBAR ═══════════════
        toolbar = self._create_toolbar()
        main_layout.addLayout(toolbar)
        
        # ═══════════════ SEARCH BAR ═══════════════
        search_layout = self._create_search_bar()
        main_layout.addLayout(search_layout)
        
        # ═══════════════ MAIN CONTENT ═══════════════
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel - Categories
        left_panel = self._create_categories_panel()
        splitter.addWidget(left_panel)
        
        # Right Panel - Extensions
        right_panel = self._create_extensions_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([300, 500])
        main_layout.addWidget(splitter)
        
        # ═══════════════ STATISTICS BAR ═══════════════
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #f5f5f5;
                border-radius: 4px;
                color: #666;
            }
        """)
        main_layout.addWidget(self.stats_label)
        
        # ═══════════════ BOTTOM BUTTONS ═══════════════
        bottom_layout = self._create_bottom_buttons()
        main_layout.addLayout(bottom_layout)
        
        self._update_statistics()
    
    def _create_toolbar(self) -> QHBoxLayout:
        """إنشاء شريط الأدوات"""
        toolbar = QHBoxLayout()
        
        # Auto-Detect Button
        auto_detect_btn = QPushButton(qta.icon('fa5s.magic'), 
                                     self._t("auto_detect", "Auto-Detect"))
        auto_detect_btn.setToolTip(self._t("auto_detect_tip", 
            "Scan a folder to discover new file extensions"))
        auto_detect_btn.clicked.connect(self._auto_detect)
        toolbar.addWidget(auto_detect_btn)
        
        # Bulk Add Button
        bulk_add_btn = QPushButton(qta.icon('fa5s.list'), 
                                  self._t("bulk_add", "Bulk Add"))
        bulk_add_btn.setToolTip(self._t("bulk_add_tip", 
            "Add multiple extensions at once"))
        bulk_add_btn.clicked.connect(self._bulk_add)
        toolbar.addWidget(bulk_add_btn)
        
        toolbar.addStretch()
        
        # Import/Export
        import_btn = QPushButton(qta.icon('fa5s.file-import'), 
                                self._t("import", "Import"))
        import_btn.clicked.connect(self._import_settings)
        toolbar.addWidget(import_btn)
        
        export_btn = QPushButton(qta.icon('fa5s.file-export'), 
                                self._t("export", "Export"))
        export_btn.clicked.connect(self._export_settings)
        toolbar.addWidget(export_btn)
        
        toolbar.addWidget(self._create_separator())
        
        # Reset Button
        reset_btn = QPushButton(qta.icon('fa5s.undo-alt'), 
                               self._t("reset_defaults", "Reset"))
        reset_btn.setToolTip(self._t("reset_defaults_tip", 
            "Reset to default categories"))
        reset_btn.clicked.connect(self._reset_to_defaults)
        toolbar.addWidget(reset_btn)
        
        # Help Button
        help_btn = QPushButton(qta.icon('fa5s.question-circle'), "")
        help_btn.setToolTip(self._t("help", "Help (F1)"))
        help_btn.clicked.connect(self._show_help)
        toolbar.addWidget(help_btn)
        
        return toolbar
    
    def _create_separator(self) -> QFrame:
        """إنشاء فاصل"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("color: #ccc;")
        return separator
    
    def _create_search_bar(self) -> QHBoxLayout:
        """إنشاء شريط البحث"""
        layout = QHBoxLayout()
        
        # إنشاء label مع أيقونة بشكل صحيح
        search_icon_label = QLabel()
        search_icon_label.setPixmap(qta.icon('fa5s.search').pixmap(QSize(16, 16)))
        layout.addWidget(search_icon_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(
            self._t("search_placeholder", "Search categories and extensions... (Ctrl+F)")
        )
        self.search_edit.textChanged.connect(self._on_search)
        self.search_edit.setClearButtonEnabled(True)
        layout.addWidget(self.search_edit)
        
        return layout
    
    def _create_categories_panel(self) -> QGroupBox:
        """إنشاء لوحة الفئات"""
        group = QGroupBox(self._t("categories", "Categories"))
        layout = QVBoxLayout(group)
        
        # Category list
        self.cat_list = QListWidget()
        self.cat_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.cat_list.customContextMenuRequested.connect(self._show_category_context_menu)
        self.cat_list.itemSelectionChanged.connect(self._on_category_selected)
        self.cat_list.itemDoubleClicked.connect(self._rename_category)
        layout.addWidget(self.cat_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton(qta.icon('fa5s.plus'), "")
        add_btn.setToolTip(self._t("add_category", "Add Category (Ctrl+N)"))
        add_btn.clicked.connect(self._add_category)
        btn_layout.addWidget(add_btn)
        
        rename_btn = QPushButton(qta.icon('fa5s.edit'), "")
        rename_btn.setToolTip(self._t("rename_category", "Rename Category"))
        rename_btn.clicked.connect(self._rename_category)
        btn_layout.addWidget(rename_btn)
        
        delete_btn = QPushButton(qta.icon('fa5s.trash'), "")
        delete_btn.setToolTip(self._t("delete_category", "Delete Category"))
        delete_btn.clicked.connect(self._delete_category)
        btn_layout.addWidget(delete_btn)
        
        color_btn = QPushButton(qta.icon('fa5s.palette'), "")
        color_btn.setToolTip(self._t("change_color", "Change Color"))
        color_btn.clicked.connect(self._change_category_color)
        btn_layout.addWidget(color_btn)
        
        layout.addLayout(btn_layout)
        
        return group
    
    def _create_extensions_panel(self) -> QGroupBox:
        """إنشاء لوحة الامتدادات"""
        group = QGroupBox(self._t("extensions", "Extensions"))
        layout = QVBoxLayout(group)
        
        # Quick add
        quick_add_layout = QHBoxLayout()
        
        self.ext_input = QLineEdit()
        self.ext_input.setPlaceholderText(
            self._t("quick_add_placeholder", "Type extension and press Enter...")
        )
        self.ext_input.returnPressed.connect(self._quick_add_extension)
        quick_add_layout.addWidget(self.ext_input)
        
        quick_add_btn = QPushButton(qta.icon('fa5s.plus'), "")
        quick_add_btn.setToolTip(self._t("add_extension", "Add Extension"))
        quick_add_btn.clicked.connect(self._quick_add_extension)
        quick_add_layout.addWidget(quick_add_btn)
        
        layout.addLayout(quick_add_layout)
        
        # Extension list
        self.ext_list = QListWidget()
        self.ext_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.ext_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ext_list.customContextMenuRequested.connect(self._show_extension_context_menu)
        self.ext_list.setDragEnabled(True)
        layout.addWidget(self.ext_list)
        
        # Extension count
        self.ext_count_label = QLabel("")
        self.ext_count_label.setStyleSheet("color: gray;")
        layout.addWidget(self.ext_count_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        delete_ext_btn = QPushButton(qta.icon('fa5s.trash'), 
                                    self._t("remove", "Remove"))
        delete_ext_btn.clicked.connect(self._delete_extensions)
        btn_layout.addWidget(delete_ext_btn)
        
        move_btn = QPushButton(qta.icon('fa5s.exchange-alt'), 
                              self._t("move_to", "Move to..."))
        move_btn.clicked.connect(self._move_extensions)
        btn_layout.addWidget(move_btn)
        
        layout.addLayout(btn_layout)
        
        return group
    
    def _create_bottom_buttons(self) -> QHBoxLayout:
        """إنشاء أزرار الأسفل"""
        layout = QHBoxLayout()
        
        cancel_btn = QPushButton(qta.icon('fa5s.times'), 
                                self._t("cancel", "Cancel"))
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        layout.addStretch()
        
        save_btn = QPushButton(qta.icon('fa5s.save'), 
                              self._t("save_and_close", "Save & Close"))
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_and_close)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(save_btn)
        
        return layout
    
    # ═══════════════════════════════════════════════════════════════
    #                    CATEGORY OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def _populate_categories(self):
        """ملء قائمة الفئات"""
        self.cat_list.clear()
        
        for cat in sorted(self.categories_data.keys()):
            item = QListWidgetItem(cat)
            color = self.category_colors.get(cat, CATEGORY_COLORS["default"])
            item.setForeground(QBrush(QColor(color)))
            item.setData(Qt.ItemDataRole.UserRole, cat)
            
            # Icon based on category
            icon = self._get_category_icon(cat)
            if icon:
                item.setIcon(icon)
            
            self.cat_list.addItem(item)
    
    def _get_category_icon(self, category: str) -> QIcon:
        """الحصول على أيقونة الفئة"""
        icons = {
            "Images": "fa5s.image",
            "Videos": "fa5s.video",
            "Audio": "fa5s.music",
            "Documents": "fa5s.file-alt",
            "Archives": "fa5s.file-archive",
            "Code": "fa5s.code",
            "Executables": "fa5s.cog",
            "Others": "fa5s.question",
        }
        icon_name = icons.get(category, "fa5s.folder")
        color = self.category_colors.get(category, CATEGORY_COLORS["default"])
        return qta.icon(icon_name, color=color)
    
    def _on_category_selected(self):
        """عند اختيار فئة"""
        self._update_extensions_list()
    
    def _update_extensions_list(self):
        """تحديث قائمة الامتدادات"""
        self.ext_list.clear()
        
        selected = self.cat_list.selectedItems()
        if not selected:
            self.ext_count_label.setText("")
            return
        
        cat = selected[0].data(Qt.ItemDataRole.UserRole)
        extensions = self.categories_data.get(cat, [])
        
        search_text = self.search_edit.text().lower()
        
        for ext in sorted(extensions):
            if search_text and search_text not in ext.lower():
                continue
            
            item = QListWidgetItem(ext)
            item.setData(Qt.ItemDataRole.UserRole, ext)
            self.ext_list.addItem(item)
        
        count = self.ext_list.count()
        total = len(extensions)
        
        if search_text:
            self.ext_count_label.setText(f"Showing {count} of {total}")
        else:
            self.ext_count_label.setText(f"{count} extensions")
    
    def _add_category(self):
        """إضافة فئة جديدة"""
        name, ok = QInputDialog.getText(
            self,
            self._t("add_category", "Add Category"),
            self._t("category_name", "Category name:")
        )
        
        if ok and name:
            name = name.strip()
            if name in self.categories_data:
                QMessageBox.warning(
                    self,
                    self._t("error", "Error"),
                    self._t("category_exists", "Category already exists!")
                )
                return
            
            self.categories_data[name] = []
            
            # تعيين لون عشوائي
            used_colors = set(self.category_colors.values())
            available_colors = [c for c in DEFAULT_COLORS if c not in used_colors]
            if available_colors:
                self.category_colors[name] = available_colors[0]
            else:
                self.category_colors[name] = DEFAULT_COLORS[
                    len(self.categories_data) % len(DEFAULT_COLORS)
                ]
            
            self._populate_categories()
            self._update_statistics()
            
            # تحديد الفئة الجديدة
            for i in range(self.cat_list.count()):
                if self.cat_list.item(i).data(Qt.ItemDataRole.UserRole) == name:
                    self.cat_list.setCurrentRow(i)
                    break
    
    def _rename_category(self, item=None):
        """إعادة تسمية فئة"""
        selected = self.cat_list.selectedItems()
        if not selected:
            return
        
        old_name = selected[0].data(Qt.ItemDataRole.UserRole)
        
        new_name, ok = QInputDialog.getText(
            self,
            self._t("rename_category", "Rename Category"),
            self._t("new_name", "New name:"),
            text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            new_name = new_name.strip()
            if new_name in self.categories_data:
                QMessageBox.warning(
                    self,
                    self._t("error", "Error"),
                    self._t("category_exists", "Category already exists!")
                )
                return
            
            # نقل البيانات
            self.categories_data[new_name] = self.categories_data.pop(old_name)
            if old_name in self.category_colors:
                self.category_colors[new_name] = self.category_colors.pop(old_name)
            
            self._populate_categories()
    
    def _delete_category(self):
        """حذف فئة"""
        selected = self.cat_list.selectedItems()
        if not selected:
            return
        
        cat = selected[0].data(Qt.ItemDataRole.UserRole)
        ext_count = len(self.categories_data.get(cat, []))
        
        reply = QMessageBox.question(
            self,
            self._t("confirm_delete", "Confirm Delete"),
            f"Delete category '{cat}' with {ext_count} extensions?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.categories_data[cat]
            if cat in self.category_colors:
                del self.category_colors[cat]
            
            self._populate_categories()
            self.ext_list.clear()
            self._update_statistics()
    
    def _change_category_color(self):
        """تغيير لون الفئة"""
        selected = self.cat_list.selectedItems()
        if not selected:
            return
        
        cat = selected[0].data(Qt.ItemDataRole.UserRole)
        
        # عرض قائمة الألوان
        colors = list(CATEGORY_COLORS.values()) + DEFAULT_COLORS
        
        menu = QMenu(self)
        for color in colors:
            action = menu.addAction("")
            action.setData(color)
            
            # إنشاء أيقونة ملونة
            pixmap = qta.icon('fa5s.circle', color=color).pixmap(16, 16)
            action.setIcon(QIcon(pixmap))
        
        action = menu.exec(self.mapToGlobal(self.cat_list.pos()))
        if action:
            self.category_colors[cat] = action.data()
            self._populate_categories()
    
    def _show_category_context_menu(self, pos):
        """قائمة السياق للفئات"""
        item = self.cat_list.itemAt(pos)
        if not item:
            return
        
        menu = QMenu(self)
        
        rename_action = menu.addAction(
            qta.icon('fa5s.edit'), 
            self._t("rename", "Rename")
        )
        
        color_menu = menu.addMenu(
            qta.icon('fa5s.palette'), 
            self._t("change_color", "Change Color")
        )
        for color in list(CATEGORY_COLORS.values()) + DEFAULT_COLORS:
            action = color_menu.addAction("")
            action.setData(("color", color))
            pixmap = qta.icon('fa5s.circle', color=color).pixmap(16, 16)
            action.setIcon(QIcon(pixmap))
        
        menu.addSeparator()
        
        delete_action = menu.addAction(
            qta.icon('fa5s.trash'), 
            self._t("delete", "Delete")
        )
        
        action = menu.exec(self.cat_list.mapToGlobal(pos))
        
        if action == rename_action:
            self._rename_category()
        elif action == delete_action:
            self._delete_category()
        elif action and action.data() and action.data()[0] == "color":
            cat = item.data(Qt.ItemDataRole.UserRole)
            self.category_colors[cat] = action.data()[1]
            self._populate_categories()
    
    # ═══════════════════════════════════════════════════════════════
    #                    EXTENSION OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def _quick_add_extension(self):
        """إضافة امتداد سريع"""
        selected = self.cat_list.selectedItems()
        if not selected:
            QMessageBox.warning(
                self,
                self._t("error", "Error"),
                self._t("select_category_first", "Please select a category first!")
            )
            return
        
        ext = self.ext_input.text().strip().lower()
        if not ext:
            return
        
        if not ext.startswith('.'):
            ext = '.' + ext
        
        cat = selected[0].data(Qt.ItemDataRole.UserRole)
        
        if ext in self.categories_data[cat]:
            QMessageBox.warning(
                self,
                self._t("error", "Error"),
                f"Extension {ext} already exists in this category!"
            )
            return
        
        # التحقق من وجود الامتداد في فئة أخرى
        for other_cat, exts in self.categories_data.items():
            if other_cat != cat and ext in exts:
                reply = QMessageBox.question(
                    self,
                    self._t("extension_exists_other", "Extension Exists"),
                    f"Extension {ext} exists in '{other_cat}'. Move it to '{cat}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.categories_data[other_cat].remove(ext)
                else:
                    return
                break
        
        self.categories_data[cat].append(ext)
        self._update_extensions_list()
        self._update_statistics()
        self.ext_input.clear()
    
    def _delete_extensions(self):
        """حذف الامتدادات المحددة"""
        selected_cat = self.cat_list.selectedItems()
        selected_ext = self.ext_list.selectedItems()
        
        if not selected_cat or not selected_ext:
            return
        
        cat = selected_cat[0].data(Qt.ItemDataRole.UserRole)
        
        for item in selected_ext:
            ext = item.data(Qt.ItemDataRole.UserRole)
            if ext in self.categories_data[cat]:
                self.categories_data[cat].remove(ext)
        
        self._update_extensions_list()
        self._update_statistics()
    
    def _move_extensions(self):
        """نقل الامتدادات إلى فئة أخرى"""
        selected_cat = self.cat_list.selectedItems()
        selected_ext = self.ext_list.selectedItems()
        
        if not selected_cat or not selected_ext:
            return
        
        current_cat = selected_cat[0].data(Qt.ItemDataRole.UserRole)
        
        # قائمة الفئات المتاحة
        available_cats = [c for c in self.categories_data.keys() if c != current_cat]
        
        if not available_cats:
            QMessageBox.warning(
                self,
                self._t("error", "Error"),
                self._t("no_other_categories", "No other categories available!")
            )
            return
        
        target_cat, ok = QInputDialog.getItem(
            self,
            self._t("move_to", "Move to"),
            self._t("select_target_category", "Select target category:"),
            available_cats,
            0,
            False
        )
        
        if ok and target_cat:
            for item in selected_ext:
                ext = item.data(Qt.ItemDataRole.UserRole)
                if ext in self.categories_data[current_cat]:
                    self.categories_data[current_cat].remove(ext)
                if ext not in self.categories_data[target_cat]:
                    self.categories_data[target_cat].append(ext)
            
            self._update_extensions_list()
            self._update_statistics()
    
    def _show_extension_context_menu(self, pos):
        """قائمة السياق للامتدادات"""
        item = self.ext_list.itemAt(pos)
        if not item:
            return
        
        selected_cat = self.cat_list.selectedItems()
        if not selected_cat:
            return
        
        current_cat = selected_cat[0].data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        
        # Move to submenu
        move_menu = menu.addMenu(
            qta.icon('fa5s.exchange-alt'),
            self._t("move_to", "Move to...")
        )
        
        for cat in sorted(self.categories_data.keys()):
            if cat != current_cat:
                action = move_menu.addAction(cat)
                action.setData(("move", cat))
                action.setIcon(self._get_category_icon(cat))
        
        menu.addSeparator()
        
        delete_action = menu.addAction(
            qta.icon('fa5s.trash'),
            self._t("remove", "Remove")
        )
        
        action = menu.exec(self.ext_list.mapToGlobal(pos))
        
        if action == delete_action:
            self._delete_extensions()
        elif action and action.data() and action.data()[0] == "move":
            target_cat = action.data()[1]
            selected_ext = self.ext_list.selectedItems()
            
            for item in selected_ext:
                ext = item.data(Qt.ItemDataRole.UserRole)
                if ext in self.categories_data[current_cat]:
                    self.categories_data[current_cat].remove(ext)
                if ext not in self.categories_data[target_cat]:
                    self.categories_data[target_cat].append(ext)
            
            self._update_extensions_list()
            self._update_statistics()
    
    def _delete_selected(self):
        """حذف العنصر المحدد (فئة أو امتداد)"""
        if self.ext_list.hasFocus() and self.ext_list.selectedItems():
            self._delete_extensions()
        elif self.cat_list.hasFocus() and self.cat_list.selectedItems():
            self._delete_category()
    
    # ═══════════════════════════════════════════════════════════════
    #                    ADVANCED FEATURES
    # ═══════════════════════════════════════════════════════════════
    
    def _auto_detect(self):
        """اكتشاف تلقائي للامتدادات"""
        # جمع كل الامتدادات الحالية
        all_extensions = set()
        for exts in self.categories_data.values():
            all_extensions.update(exts)
        
        dialog = AutoDetectDialog(self, self.tr, all_extensions)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_extensions = dialog.get_selected_extensions()
            
            if new_extensions:
                # إضافة إلى فئة Others أو فئة محددة
                selected_cat = self.cat_list.selectedItems()
                
                if selected_cat:
                    target_cat = selected_cat[0].data(Qt.ItemDataRole.UserRole)
                else:
                    # السؤال عن الفئة المستهدفة
                    cats = list(self.categories_data.keys())
                    target_cat, ok = QInputDialog.getItem(
                        self,
                        self._t("select_category", "Select Category"),
                        self._t("add_extensions_to", "Add extensions to:"),
                        cats,
                        cats.index("Others") if "Others" in cats else 0,
                        False
                    )
                    if not ok:
                        return
                
                added = 0
                for ext in new_extensions:
                    if ext not in self.categories_data[target_cat]:
                        self.categories_data[target_cat].append(ext)
                        added += 1
                
                self._update_extensions_list()
                self._update_statistics()
                
                QMessageBox.information(
                    self,
                    self._t("success", "Success"),
                    f"Added {added} extensions to {target_cat}"
                )
    
    def _bulk_add(self):
        """إضافة متعددة"""
        selected_cat = self.cat_list.selectedItems()
        if not selected_cat:
            QMessageBox.warning(
                self,
                self._t("error", "Error"),
                self._t("select_category_first", "Please select a category first!")
            )
            return
        
        dialog = BulkAddDialog(self, self.tr)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            extensions = dialog.get_extensions()
            cat = selected_cat[0].data(Qt.ItemDataRole.UserRole)
            
            added = 0
            for ext in extensions:
                if ext not in self.categories_data[cat]:
                    self.categories_data[cat].append(ext)
                    added += 1
            
            self._update_extensions_list()
            self._update_statistics()
            
            if added > 0:
                QMessageBox.information(
                    self,
                    self._t("success", "Success"),
                    f"Added {added} extensions"
                )
    
    def _import_settings(self):
        """استيراد الإعدادات"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self._t("import_settings", "Import Settings"),
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if "categories" in data:
                    self.categories_data = {k: list(v) for k, v in data["categories"].items()}
                if "colors" in data:
                    self.category_colors = data["colors"]
                
                self._populate_categories()
                self._update_statistics()
                
                QMessageBox.information(
                    self,
                    self._t("success", "Success"),
                    self._t("settings_imported", "Settings imported successfully!")
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self._t("error", "Error"),
                    f"Failed to import: {e}"
                )
    
    def _export_settings(self):
        """تصدير الإعدادات"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self._t("export_settings", "Export Settings"),
            "categories_backup.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                data = {
                    "categories": self.categories_data,
                    "colors": self.category_colors
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(
                    self,
                    self._t("success", "Success"),
                    self._t("settings_exported", "Settings exported successfully!")
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self._t("error", "Error"),
                    f"Failed to export: {e}"
                )
    
    def _reset_to_defaults(self):
        """إعادة للإعدادات الافتراضية"""
        reply = QMessageBox.question(
            self,
            self._t("confirm_reset", "Confirm Reset"),
            self._t("confirm_reset_msg", 
                   "This will reset all categories to defaults. Continue?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.categories_data = {
                k: list(v) for k, v in file_organizer.DEFAULT_CATEGORIES.items()
            }
            self.category_colors = CATEGORY_COLORS.copy()
            
            self._populate_categories()
            self.ext_list.clear()
            self._update_statistics()
    
    def _on_search(self, text: str):
        """عند البحث"""
        text = text.lower()
        
        # تصفية الفئات
        for i in range(self.cat_list.count()):
            item = self.cat_list.item(i)
            cat = item.data(Qt.ItemDataRole.UserRole)
            
            # البحث في اسم الفئة والامتدادات
            cat_match = text in cat.lower()
            ext_match = any(text in ext for ext in self.categories_data.get(cat, []))
            
            item.setHidden(not (cat_match or ext_match or not text))
        
        # تحديث قائمة الامتدادات
        self._update_extensions_list()
    
    def _focus_search(self):
        """التركيز على البحث"""
        self.search_edit.setFocus()
        self.search_edit.selectAll()
    
    def _show_help(self):
        """عرض المساعدة"""
        dialog = HelpDialog(self, self.tr)
        dialog.exec()
    
    def _update_statistics(self):
        """تحديث الإحصائيات"""
        total_categories = len(self.categories_data)
        total_extensions = sum(len(exts) for exts in self.categories_data.values())
        
        self.stats_label.setText(
            f"📊 {total_categories} categories | {total_extensions} extensions"
        )
    
    def _save_and_close(self):
        """حفظ وإغلاق"""
        try:
            # حفظ الفئات
            with open(file_organizer.CATEGORIES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.categories_data, f, indent=2, sort_keys=True)
            
            # حفظ الألوان
            self._save_colors()
            
            self.categories_changed.emit()
            
            QMessageBox.information(
                self,
                self._t("success", "Success"),
                self._t("categories_saved", "Categories saved successfully!")
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self._t("error", "Error"),
                f"Failed to save: {e}"
            )


# ═══════════════════════════════════════════════════════════════
#                    STANDALONE TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    dialog = EnhancedCategoryEditorDialog()
    dialog.show()
    
    sys.exit(app.exec())
