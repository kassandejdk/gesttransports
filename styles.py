
APP_STYLE = """
QWidget {
    font-family: 'Poppins', sans-serif;
    font-size: 13px;
    color: #1a1f2e;
    background-color: #f5f7fa;
}
QScrollArea { border: none; }
QScrollBar:vertical {
    background: #f0f2f5; width: 8px; border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #c8d0da; border-radius: 4px; min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 8px;
    gridline-color: #e8ecf0;
    outline: none;
}
QTableWidget::item { padding: 8px 12px; border: none; color: #1a1f2e; }
QTableWidget::item:selected {
    background-color: #dce8ff;
    color: #1a1f2e;
}
QHeaderView::section {
    background-color: #f0f2f5;
    color: #6e7781;
    font-weight: 600;
    font-size: 11px;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #d0d7de;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QDateTimeEdit, QTimeEdit {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 8px 10px;
    color: #1a1f2e;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QDateEdit:focus, QDateTimeEdit:focus, QTimeEdit:focus {
    border: 1px solid #0969da;
}
QComboBox::drop-down { border: none; padding-right: 8px; }
QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    selection-background-color: #dce8ff;
    color: #1a1f2e;
}
QPushButton {
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}
QLabel { background: transparent; color: #1a1f2e; }
QGroupBox {
    border: 1px solid #d0d7de;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
}
QGroupBox::title {
    color: #6e7781;
    subcontrol-origin: margin;
    left: 10px;
    top: -6px;
    font-size: 11px;
    font-weight: 600;
}
"""

def primary_btn(text, color="#82a2f5", text_color="#0d1117"):
    btn = None
    from PySide6 import QtWidgets, QtGui, QtCore
    btn = QtWidgets.QPushButton(text)
    btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {color};
            color: {text_color};
            border: none;
            border-radius: 6px;
            padding: 8px 18px;
            font-weight: 700;
            font-size: 13px;
        }}
        QPushButton:hover {{ background-color: #9bb5ff; }}
        QPushButton:pressed {{ background-color: #6b8de0; }}
    """)
    return btn

def danger_btn(text):
    from PySide6 import QtWidgets, QtGui, QtCore
    btn = QtWidgets.QPushButton(text)
    btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
    btn.setStyleSheet("""
        QPushButton {
            background-color: #da3633;
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 8px 18px;
            font-weight: 700;
        }
        QPushButton:hover { background-color: #f85149; }
    """)
    return btn

def section_title(text):
    from PySide6 import QtWidgets
    lbl = QtWidgets.QLabel(text)
    lbl.setStyleSheet("font-size: 20px; font-weight: 700; color: #1a1f2e; margin-bottom: 4px;")
    return lbl

def card_widget(parent=None):
    from PySide6 import QtWidgets
    f = QtWidgets.QFrame(parent)
    f.setStyleSheet("""
        QFrame {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 10px;
        }
    """)
    return f

def make_table(headers):
    from PySide6 import QtWidgets, QtCore
    t = QtWidgets.QTableWidget()
    t.setColumnCount(len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.horizontalHeader().setStretchLastSection(True)
    t.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    t.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    t.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    t.verticalHeader().setVisible(False)
    t.setAlternatingRowColors(True)
    t.verticalHeader().setDefaultSectionSize(42)
    return t