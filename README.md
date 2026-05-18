# Nexus Motion & Neural Gaze Core (Hand & Face Detection AI)

A state-of-the-art, high-performance cognitive AI desktop application that tracks hand gestures, face wireframes, and eye pupil gaze telemetry in real-time. Designed with a breathtaking cyberpunk aesthetic, custom glassmorphism styling, and premium interactive heads-up displays (HUD).

![Holographic HUD Preview](configs/cyber_hud_preview.png) *(Placeholder for live visual rendering)*

---

## ⚡ Next-Gen Features

### 1. 👁️ Neural Face & Pupil Gaze Tracking
- **Interactive Cyber Face Mesh**: Renders a high-tech glowing wireframe over the user's face, tracking the eyebrows, mouth, eyes, and facial contour.
- **Pupil Iris Lock-On**: Dynamic concentric target lock-on crosshairs follow the pupils' movements in real-time.
- **Blink Telemetry Detection**: Asynchronous left and right blink analysis logs activity to the console feed dynamically.
- **EMA Landmark Smoothing**: Sophisticated Exponential Moving Average filtering eliminates sensor jitter for high-precision locks.

### 2. 🔮 3D Holographic Hand HUD
- **3D Spinning Holograms**: Renders a perspective-projected 3D rotating wireframe cube hovering gracefully above the palm center.
- **Palm Telemetry Circles**: Glowing inner and outer segmented rings rotate in opposite directions based on real-time physics.
- **Target Reticle Ticks**: Floating lock-on crosshairs trace the tip of the index pointer.
- **Cyber Data Telemetry Cards**: Holographic connector lines draw a floating card displaying the active hand, detected gesture, 2D coordinates, and lock state.

### 3. 🎨 Aesthetic Customizer & Palettes
- **Hot-Swappable Cyber Themes**: Instant color palette switches between three premium presets:
  - 🔴 **Red Alert**: Neon Crimson & Scarlet Red theme for tactical cyber-ops.
  - 🟢 **Matrix Green**: Lime Green & Matrix Digital rain aesthetic.
  - 🔵 **Synthwave**: Cyber Cyan & Synth Magenta for a futuristic retro-neon vibe.
- **HUD Mode Selection**: Toggle the Hand HUD between the advanced **3D Hologram** and classic **Standard Brackets**.

### 4. 🎛️ Premium Glassmorphism UI
- Fully styled PyQt6 interface incorporating a dark, custom-drawn cyberpunk design.
- Neon button animations, sleek scrollbars, styled checkboxes, glowing horizontal sliders, and high-contrast monospace indicators.

---

## 🛠️ Tech Stack
- **Python 3.12+**
- **OpenCV**: High-performance camera capture and image processing.
- **MediaPipe**: Dual-core Hand Landmarker and Face Mesh vision processors.
- **PyQt6**: Professional GPU-accelerated desktop GUI.
- **NumPy**: Fast matrix operations for 3D projections and physics.

---

## 📂 Project Structure

```
Hand-and-Face-Detection/
│
├── configs/
│   ├── settings.json         # Core settings and configuration
│   └── hand_landmarker.task  # Pre-trained hand task model
│
├── detection/
│   ├── hand_tracker.py       # Hand tracking core
│   └── face_tracker.py       # NEW: Face Mesh & Pupil Gaze tracking core
│
├── effects/
│   └── effects_engine.py     # UPGRADED: 3D Holograms, Face Overlays & Themes
│
├── gestures/
│   └── recognizer.py         # Static and dynamic gesture classifications
│
├── plugins/
│   ├── base_plugin.py        # Abstract plugin structure
│   ├── manager.py            # Hot-swappable plugin loader
│   ├── media_control.py      # Play/Pause gesture integration
│   ├── volume_control.py     # Wave-based volume modifier
│   ├── screenshot.py         # Snap-triggered screen capture
│   └── web_browser.py        # Web launcher trigger
│
├── ui/
│   ├── main_window.py        # UPGRADED: Interactive HUD, Stats Dashboard
│   └── styles.py             # UPGRADED: Cyberpunk QSS stylesheet
│
├── utils/
│   ├── overlays.py           # 3D projections & hologram geometry
│   ├── fps_counter.py        # Telemetry FPS calculator
│   └── logger.py             # High-reliability system logger
│
├── main.py                   # App bootloader entry point
└── requirements.txt          # Python packages list
```

---

## 🚀 Installation & Booting

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd Hand-and-Face-Detection
   ```

2. **Initialize Virtual Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Boot the System**:
   ```bash
   python main.py
   ```

---

## 🕹️ Controls & Navigation

### 🖱️ Virtual Air Mouse
- **Move Cursor**: Point your index finger and glide.
- **Left Click & Drag**: Pinch the tips of your index and middle fingers together.
- **Release Click**: Extend or curl any other finger.

### 🔌 Custom Plug-in Gesture Actions
- 🔴 **Thumbs Up / Down**: Volume control plugin modifies windows master volume.
- 🟢 **OK Gesture**: Media control toggles Play/Pause.
- 🔵 **Fist Close**: Screenshot plugin saves a high-res capture to the `/screenshots` folder.
- 🟡 **Open Palm**: Web browser launcher automatically opens the repository.
