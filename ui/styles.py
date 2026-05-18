CYBERPUNK_STYLESHEET = """
QMainWindow {
    background-color: #030203;
}
QLabel {
    color: #FF2B6D;
    font-family: 'Consolas', 'Segoe UI', monospace;
    font-size: 14px;
    font-weight: 500;
}
QPushButton {
    background-color: rgba(255, 0, 85, 0.04);
    color: #FF2B6D;
    border: 1px solid #FF0055;
    border-radius: 4px;
    padding: 8px 16px;
    font-family: 'Consolas', monospace;
    font-size: 13px;
    font-weight: bold;
    text-transform: uppercase;
}
QPushButton:hover {
    background-color: rgba(255, 0, 85, 0.2);
    color: #FFFFFF;
    border: 1px solid #FF3377;
    box-shadow: 0 0 10px #FF0055;
}
QPushButton:pressed {
    background-color: rgba(255, 0, 85, 0.4);
    border: 1px solid #FF0055;
}
QFrame {
    border: 1px solid #331122;
    border-radius: 6px;
    background-color: rgba(12, 4, 8, 0.95);
}
QTabWidget::pane {
    border: 1px solid #441122;
    background-color: rgba(8, 2, 5, 0.96);
    border-radius: 6px;
}
QTabBar::tab {
    background-color: rgba(5, 2, 4, 0.9);
    color: #885566;
    border: 1px solid #220A14;
    border-bottom: none;
    padding: 8px 16px;
    font-family: 'Consolas', monospace;
    font-weight: bold;
    font-size: 12px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected, QTabBar::tab:hover {
    background-color: rgba(12, 4, 8, 0.95);
    color: #FF2B6D;
    border-left: 1px solid #FF0055;
    border-right: 1px solid #FF0055;
    border-top: 2px solid #FF0055;
}
QCheckBox {
    color: #DDAABB;
    font-family: 'Consolas', monospace;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #FF0055;
    border-radius: 2px;
    background-color: rgba(0, 0, 0, 0.7);
}
QCheckBox::indicator:checked {
    background-color: #FF0055;
    image: url(no_image_placeholder);
}
QCheckBox::indicator:hover {
    border-color: #FF5599;
}
QSlider::groove:horizontal {
    border: 1px solid #331122;
    height: 4px;
    background: #11050A;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #FF0055;
    border: 1px solid #FF3377;
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #FF5599;
    border-color: #FFFFFF;
}
QTextEdit {
    background-color: #050204;
    color: #FF3366;
    border: 1px solid #331122;
    font-family: 'Consolas', monospace;
    font-size: 12px;
    border-radius: 4px;
}
QGroupBox {
    border: 1px solid #3d1424;
    border-radius: 6px;
    margin-top: 15px;
    padding-top: 15px;
    font-family: 'Consolas', monospace;
    font-weight: bold;
    color: #FF2B6D;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    background-color: #030203;
}
QListWidget {
    background-color: rgba(0, 0, 0, 0.6);
    border: 1px solid #331122;
    border-radius: 4px;
    color: #DDAABB;
    font-family: 'Consolas', monospace;
}
QListWidget::item {
    padding: 5px;
}
QListWidget::item:selected {
    background-color: rgba(255, 0, 85, 0.15);
    color: #FFFFFF;
    border-left: 2px solid #FF0055;
}
QComboBox {
    background-color: #120409;
    border: 1px solid #FF0055;
    border-radius: 4px;
    padding: 4px 10px;
    color: #FF2B6D;
    font-family: 'Consolas', monospace;
    font-size: 12px;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
    border-left: 1px solid #FF0055;
}
QComboBox QAbstractItemView {
    background-color: #120409;
    border: 1px solid #FF0055;
    selection-background-color: rgba(255, 0, 85, 0.2);
    selection-color: #FFFFFF;
    color: #FF2B6D;
    font-family: 'Consolas', monospace;
}
QScrollBar:vertical {
    border: none;
    background: #080205;
    width: 8px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #331122;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #FF0055;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
"""
