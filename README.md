# Nexus Hand AI
A modern, AI-powered hand detection and gesture recognition desktop application built with Python. Designed with a futuristic cyberpunk aesthetic and optimized for high performance and real-time processing.

## 🚀 Features
- **Real-Time Hand Detection**: Ultra-fast 21-point hand landmark tracking using MediaPipe.
- **Gesture Recognition**: Built-in support for Peace, Thumbs Up, Fist, Open Palm, Pointing, and OK gestures.
- **Cyberpunk UI**: Modern PyQt6 interface with neon accents, custom styling, and a glassmorphism feel.
- **Asynchronous Processing**: Thread-safe camera handling ensures the UI remains responsive and fluid.
- **Configurable**: Easily adjust settings through the `configs/settings.json` file.

## 🛠️ Tech Stack
- **Python 3.12+**
- **OpenCV**: Camera capture and image processing.
- **MediaPipe**: State-of-the-art hand tracking.
- **PyQt6**: Professional desktop GUI framework.
- **NumPy**: Matrix operations and data handling.

## 📦 Project Structure
```
Hand-and-Face-Detection/
│
├── configs/
│   └── settings.json        # Application configuration
├── detection/
│   └── hand_tracker.py      # Core AI detection module
├── gestures/
│   └── recognizer.py        # Logic for gesture classification
├── ui/
│   ├── main_window.py       # PyQt6 Main Window and Camera Thread
│   └── styles.py            # Custom Cyberpunk CSS
├── utils/
│   ├── fps_counter.py       # Performance monitoring
│   └── logger.py            # Standardized logging
├── main.py                  # Entry point
└── requirements.txt         # Dependencies
```

## ⚙️ Installation Guide

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd Hand-and-Face-Detection
   ```

2. **Create a virtual environment (Optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install the requirements**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Usage
Run the application using the following command:
```bash
python main.py
```
*Note: Make sure your webcam is connected and accessible.*

## 🔮 Future Enhancements (Roadmap)
- [ ] Multi-user hand interaction mode
- [ ] Virtual mouse control using hand gestures
- [ ] 3D holographic visual overlays
- [ ] Custom plugin system for adding new gesture actions

## 🛡️ License
This project is open-source and available under the MIT License.
