class AppStyles:
    """Centralized stylesheet for the application."""
    
    MAIN_STYLE = """
        QMainWindow, QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        QLabel {
            color: #e0e0e0;
        }
        QTabWidget::pane {
            border: 1px solid #444444;
            background-color: #1e1e1e;
            border-radius: 4px;
        }
        QTabBar::tab {
            background-color: #2d2d2d;
            color: #aaaaaa;
            padding: 8px 16px;
            margin-right: 2px;
            border: 1px solid #444444;
            border-bottom: None;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: 1px solid #444444;
            border-bottom: 1px solid #1e1e1e;
            font-weight: bold;
        }
        QTabBar::tab:hover:!selected {
            background-color: #3a3a3a;
        }
        QPushButton {
            background-color: #007acc;
            color: white;
            border: None;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0098ff;
        }
        QPushButton:pressed {
            background-color: #005c99;
        }
        QPushButton:disabled {
            background-color: #3a3a3a;
            color: #777777;
        }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            padding: 6px;
            border: 1px solid #444444;
            border-radius: 4px;
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border: 1px solid #007acc;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #444444;
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 15px;
            color: #e0e0e0;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: #e0e0e0;
        }
        QTableWidget, QTableView {
            border: 1px solid #444444;
            border-radius: 4px;
            background-color: #1e1e1e;
            alternate-background-color: #252525;
            color: #e0e0e0;
            gridline-color: #444444;
        }
        QHeaderView::section {
            background-color: #2d2d2d;
            padding: 4px;
            border: 1px solid #444444;
            font-weight: bold;
            color: #e0e0e0;
        }
        QScrollBar:vertical {
            background: #1e1e1e;
            width: 14px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #444444;
            min-height: 20px;
            border-radius: 7px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            background: #1e1e1e;
            height: 14px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:horizontal {
            background: #444444;
            min-width: 20px;
            border-radius: 7px;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
    """
    
    ERROR_TEXT = "color: #ff5555;"
    SUCCESS_TEXT = "color: #50fa7b;"
    WARNING_TEXT = "color: #f1fa8c;"
