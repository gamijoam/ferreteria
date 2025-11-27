"""
Modern Theme Stylesheet for Ferretería ERP
Elegant, professional design with consistent colors and spacing
"""

MODERN_THEME = """
/* ===== GLOBAL STYLES ===== */
QWidget {
    background-color: #f5f5f5;
    color: #333;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11pt;
}

QMainWindow {
    background-color: #ffffff;
}

/* ===== BUTTONS ===== */
QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 12px 24px;
    font-weight: 500;
    font-size: 11pt;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QPushButton:disabled {
    background-color: #BDBDBD;
    color: #757575;
}

/* Primary Button (Green) */
QPushButton[class="primary"] {
    background-color: #4CAF50;
}

QPushButton[class="primary"]:hover {
    background-color: #388E3C;
}

/* Danger Button (Red) */
QPushButton[class="danger"] {
    background-color: #F44336;
}

QPushButton[class="danger"]:hover {
    background-color: #D32F2F;
}

/* Warning Button (Orange) */
QPushButton[class="warning"] {
    background-color: #FF9800;
}

QPushButton[class="warning"]:hover {
    background-color: #F57C00;
}

/* ===== INPUT FIELDS ===== */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: white;
    border: 2px solid #E0E0E0;
    border-radius: 6px;
    padding: 10px;
    font-size: 11pt;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #2196F3;
}

/* ===== COMBO BOX ===== */
QComboBox {
    background-color: white;
    border: 2px solid #E0E0E0;
    border-radius: 6px;
    padding: 10px;
    min-width: 150px;
}

QComboBox:hover {
    border-color: #2196F3;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: url(none);
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #666;
    margin-right: 10px;
}

/* ===== TABLES ===== */
QTableWidget {
    background-color: white;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    gridline-color: #F0F0F0;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #F0F0F0;
}

QTableWidget::item:selected {
    background-color: #E3F2FD;
    color: #1976D2;
}

QHeaderView::section {
    background-color: #2196F3;
    color: white;
    padding: 12px;
    border: none;
    font-weight: bold;
    font-size: 11pt;
}

QHeaderView::section:hover {
    background-color: #1976D2;
}

/* ===== GROUP BOX ===== */
QGroupBox {
    background-color: white;
    border: 2px solid #E0E0E0;
    border-radius: 8px;
    margin-top: 16px;
    padding: 20px;
    font-weight: bold;
    font-size: 12pt;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    background-color: white;
    color: #2196F3;
}

/* ===== LABELS ===== */
QLabel {
    color: #333;
    font-size: 11pt;
}

QLabel[class="title"] {
    font-size: 24pt;
    font-weight: bold;
    color: #1976D2;
    padding: 10px;
}

QLabel[class="subtitle"] {
    font-size: 14pt;
    font-weight: 500;
    color: #666;
}

QLabel[class="metric-value"] {
    font-size: 32pt;
    font-weight: bold;
    color: #2196F3;
}

/* ===== TABS ===== */
QTabWidget::pane {
    border: 2px solid #E0E0E0;
    border-radius: 8px;
    background-color: white;
    padding: 10px;
}

QTabBar::tab {
    background-color: #F5F5F5;
    color: #666;
    padding: 12px 24px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: white;
    color: #2196F3;
    border-bottom: 3px solid #2196F3;
}

QTabBar::tab:hover {
    background-color: #E3F2FD;
}

/* ===== CHECKBOXES ===== */
QCheckBox {
    spacing: 8px;
    font-size: 11pt;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #BDBDBD;
    border-radius: 4px;
    background-color: white;
}

QCheckBox::indicator:checked {
    background-color: #2196F3;
    border-color: #2196F3;
    image: url(none);
}

/* ===== DATE EDIT ===== */
QDateEdit {
    background-color: white;
    border: 2px solid #E0E0E0;
    border-radius: 6px;
    padding: 10px;
}

QDateEdit:focus {
    border-color: #2196F3;
}

QDateEdit::drop-down {
    border: none;
    width: 30px;
}

/* ===== SCROLLBAR ===== */
QScrollBar:vertical {
    background-color: #F5F5F5;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #BDBDBD;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #9E9E9E;
}

QScrollBar:horizontal {
    background-color: #F5F5F5;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #BDBDBD;
    border-radius: 6px;
    min-width: 30px;
}

/* ===== MENU BAR ===== */
QMenuBar {
    background-color: #1976D2;
    color: white;
    padding: 5px;
}

QMenuBar::item {
    padding: 8px 16px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #1565C0;
}

/* ===== STATUS BAR ===== */
QStatusBar {
    background-color: #F5F5F5;
    color: #666;
    border-top: 1px solid #E0E0E0;
}

/* ===== FRAMES ===== */
QFrame {
    background-color: white;
    border-radius: 8px;
}

/* ===== DIALOG ===== */
QDialog {
    background-color: white;
}
"""

# Color Palette
COLORS = {
    "primary": "#2196F3",
    "primary_dark": "#1976D2",
    "primary_light": "#E3F2FD",
    "success": "#4CAF50",
    "success_dark": "#388E3C",
    "danger": "#F44336",
    "danger_dark": "#D32F2F",
    "warning": "#FF9800",
    "warning_dark": "#F57C00",
    "info": "#00BCD4",
    "background": "#F5F5F5",
    "surface": "#FFFFFF",
    "text": "#333333",
    "text_secondary": "#666666",
    "border": "#E0E0E0",
}
