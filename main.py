import sys
import json
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def load_config():
    try:
        with open("configs/settings.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def main():
    app = QApplication(sys.argv)
    
    # We apply our custom stylesheet inside the MainWindow
    # qdarkstyle can be used as a base, but our custom CSS is enough for the Cyberpunk feel
    
    config = load_config()
    
    window = MainWindow(config)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
