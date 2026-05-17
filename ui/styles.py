CYBERPUNK_STYLESHEET = """
QMainWindow {
    background-color: #070303;
}
QLabel {
    color: #FF5555;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 14px;
}
QPushButton {
    background-color: rgba(255, 0, 85, 0.05);
    color: #FF3366;
    border: 2px solid #FF0055;
    border-radius: 6px;
    padding: 8px 16px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #FF0055;
    color: #070303;
    border: 2px solid #FF0055;
}
QPushButton:pressed {
    background-color: #CC0044;
    border: 2px solid #CC0044;
}
QFrame {
    border: 1px solid #FF0055;
    border-radius: 8px;
    background-color: rgba(20, 5, 10, 0.8);
}
QTabWidget::pane {
    border: 1px solid #FF0055;
    background-color: rgba(15, 5, 8, 0.9);
    border-radius: 8px;
}
QTabBar::tab {
    background-color: rgba(10, 3, 5, 0.85);
    color: #996666;
    border: 1px solid #441111;
    border-bottom: none;
    padding: 10px 15px;
    font-family: 'Consolas', monospace;
    font-weight: bold;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QTabBar::tab:selected, QTabBar::tab:hover {
    background-color: rgba(15, 5, 8, 0.9);
    color: #FF3366;
    border-left: 1px solid #FF0055;
    border-right: 1px solid #FF0055;
    border-top: 2px solid #FF0055;
}
QCheckBox {
    color: #E2CCCC;
    font-family: 'Consolas', monospace;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #FF0055;
    border-radius: 3px;
    background-color: rgba(0, 0, 0, 0.5);
}
QCheckBox::indicator:checked {
    background-color: #FF0055;
    image: url(no_image_placeholder);
}
QSlider::groove:horizontal {
    border: 1px solid #441111;
    height: 6px;
    background: #180508;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #FF5500;
    border: 1px solid #FF5500;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: #FF8800;
    border-color: #FF8800;
}
QTextEdit {
    background-color: #030101;
    color: #FF3333;
    border: 1px solid #FF0055;
    font-family: 'Consolas', monospace;
    font-size: 12px;
    border-radius: 6px;
}
QGroupBox {
    border: 1px solid #662222;
    border-radius: 6px;
    margin-top: 15px;
    padding-top: 15px;
    font-family: 'Consolas', monospace;
    font-weight: bold;
    color: #FF5500;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    background-color: #070303;
}
QListWidget {
    background-color: rgba(0,0,0,0.5);
    border: 1px solid #441111;
    border-radius: 6px;
    color: #E2CCCC;
    font-family: 'Consolas', monospace;
}
QListWidget::item {
    padding: 6px;
}
QListWidget::item:selected {
    background-color: rgba(255, 0, 85, 0.2);
    color: #FF3366;
}
"""
