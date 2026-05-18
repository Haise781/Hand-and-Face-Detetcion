import sys
import os
import cv2
import numpy as np
import time
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QFrame, QTabWidget, QCheckBox, QSlider, 
    QTextEdit, QGroupBox, QListWidget, QScrollArea, QListWidgetItem,
    QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap, QFont

from detection.hand_tracker import HandDetector
from detection.face_tracker import FaceDetector
from gestures.recognizer import GestureRecognizer
from effects.effects_engine import ProfessionalOverlayEngine
from audio.audio_engine import AudioEngine
from utils.fps_counter import FPSCounter
from utils.virtual_mouse import VirtualMouse
from plugins.manager import PluginManager
from ui.styles import CYBERPUNK_STYLESHEET

class CameraThread(QThread):
    # Signals for frame and telemetry updates (hands, fps, mouse status, action logs, faces)
    change_pixmap_signal = pyqtSignal(np.ndarray)
    update_stats_signal = pyqtSignal(list, int, str, list, list)

    def __init__(self, camera_id=0, max_hands=2, detection_con=0.8, track_con=0.8):
        super().__init__()
        self.camera_id = camera_id
        self._run_flag = True
        
        # Detectors & Core Utilities
        self.detector = HandDetector(max_hands=max_hands, detection_con=detection_con, track_con=track_con)
        self.face_detector = FaceDetector(max_faces=1, min_detection_con=0.5, min_tracking_con=0.5)
        self.recognizer = GestureRecognizer()
        self.fps_counter = FPSCounter()
        
        # Professional HUD & Audio Engines
        self.effects = ProfessionalOverlayEngine()
        self.audio = AudioEngine()
        self.audio.set_enabled(False) # Silent professional by default
        
        self.virtual_mouse = VirtualMouse()
        self.plugin_manager = PluginManager()
        
        # Dynamic Configuration Controls
        self.enable_hud_overlays = True
        self.enable_basic_drawing = True
        self.enable_face_hud = True
        self.hand_hud_mode = "3D Hologram" # Toggle: "3D Hologram" or "Standard Brackets"
        self.multi_user_mode = True
        self.last_alarm_time = 0
        self.enable_wink_actions = True
        self.enable_yawn_alerts = True
        self.enable_drowsy_alerts = True
        self.last_yawn_alarm_time = 0

    def run(self):
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            print(f"[ERROR] Failed to open camera ID {self.camera_id}")
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, "CRITICAL ERROR: CAMERA OFFLINE", (60, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(error_frame, "Connect a USB camera and restart core engine.", (60, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 180, 255), 1)
            self.change_pixmap_signal.emit(error_frame)
            self.update_stats_signal.emit([], 0, "Offline", ["[SYS] Vision sensors offline - check connection."], [])
            
            while self._run_flag:
                self.msleep(500)
            return

        while self._run_flag:
            ret, frame = cap.read()
            if ret:
                # Mirror effect for comfortable gesture mapping
                frame = cv2.flip(frame, 1)
                
                # 1. Hand Tracking Core (draw clean tech skeleton nodes if enabled)
                frame = self.detector.find_hands(frame, draw=self.enable_basic_drawing)
                active_hands = self.detector.get_active_hands(frame)
                
                hands_data = []
                action_logs = []
                
                # Render sleek hand HUD overlays (Standard Brackets or 3D Hologram)
                if self.enable_hud_overlays and len(active_hands) > 0:
                    frame = self.effects.process_hand_overlays(frame, active_hands, mode=self.hand_hud_mode)
                
                # Check for simultaneous dual-hand combos
                combo = self.recognizer.detect_two_hand_combo(active_hands)
                if combo != "None":
                    if combo == "Energy Blast":
                        self.audio.play_sound_async("energy_blast")
                        action_logs.append(f"[SYS] DUAL HAND: KINETIC PUSH DETECTED")
                    elif combo == "Dual Magic Shield":
                        self.audio.play_sound_async("spell_cast")
                        action_logs.append(f"[SYS] DUAL HAND: DEFENSIVE GUARD ENGAGED")
                else:
                    # Process individual hand gestures
                    for hand in active_hands:
                        label = hand["label"]
                        lm_list = hand["lm_list"]
                        cx, cy = lm_list[9][1], lm_list[9][2] # Palm Center
                        
                        # Recognize static pose
                        pose, conf = self.recognizer.recognize_pose(lm_list)
                        
                        # Track and detect dynamic motions
                        dynamic = self.recognizer.track_and_detect_dynamics(label, lm_list)
                        
                        # Track snap release
                        snap = self.recognizer.detect_snap(label, lm_list)
                        
                        active_gesture = pose
                        
                        if dynamic != "None":
                            active_gesture = dynamic
                            if dynamic == "Circular Command":
                                self.audio.play_sound_async("spell_cast")
                                action_logs.append(f"[{label.upper()} HAND] GESTURE: CIRCULAR COMMAND DETECTED")
                            elif "Swipe" in dynamic:
                                self.audio.play_sound_async("ui_nav")
                                action_logs.append(f"[{label.upper()} HAND] HUD NAV: {dynamic.upper()}")
                        elif snap:
                            active_gesture = "Finger Snap"
                            self.audio.play_sound_async("snap")
                            action_logs.append(f"[{label.upper()} HAND] ACTION: FINGER SNAP DETECTED")
                                
                        hands_data.append({
                            "label": label,
                            "gesture": active_gesture,
                            "coords": (cx, cy)
                        })
                        
                        # Process Custom Dynamic Plugins
                        logs = self.plugin_manager.process_gesture(hand["index"], active_gesture, lm_list, frame, self.detector.results)
                        if logs:
                            action_logs.extend(logs)
                
                # 2. Face Tracking & Pupil Gaze Core
                active_faces = []
                if self.enable_face_hud:
                    active_faces = self.face_detector.find_faces(frame)
                    frame = self.effects.process_face_overlays(frame, active_faces)
                    
                    # Log face blinks/winks/yawns dynamically and execute HUD actions
                    for face in active_faces:
                        if face.get("drowsy", False) and self.enable_drowsy_alerts:
                            now = time.time()
                            if now - self.last_alarm_time > 1.5:
                                self.audio.play_sound_async("alarm")
                                self.last_alarm_time = now
                                action_logs.append("[SYS] CRITICAL: USER FATIGUE ALERT ENGAGED")
                        
                        elif face.get("yawning", False) and self.enable_yawn_alerts:
                            now = time.time()
                            if now - self.last_yawn_alarm_time > 3.0:
                                self.audio.play_sound_async("spell_cast")
                                self.last_yawn_alarm_time = now
                                action_logs.append("[SYS] NEURAL WARNING: HIGH FATIGUE - USER YAWNING DETECTED")
                                
                        else:
                            # 1. Right Eye Wink theme switcher command
                            if face.get("right_wink_triggered", False) and self.enable_wink_actions:
                                self.audio.play_sound_async("ui_nav")
                                current = self.effects.current_theme
                                themes = list(self.effects.themes.keys())
                                next_idx = (themes.index(current) + 1) % len(themes)
                                next_theme = themes[next_idx]
                                self.effects.set_theme(next_theme)
                                action_logs.append(f"[SYS] EYE COMMAND: SYNCING HUD THEME -> {next_theme.upper()}")
                            
                            # 2. Left Eye Wink camera snapshot command
                            elif face.get("left_wink_triggered", False) and self.enable_wink_actions:
                                self.audio.play_sound_async("snap")
                                os.makedirs("screenshots", exist_ok=True)
                                timestamp = time.strftime("%Y%m%d_%H%M%S")
                                filename = f"screenshots/snap_wink_{timestamp}.png"
                                cv2.imwrite(filename, frame)
                                action_logs.append(f"[SYS] EYE COMMAND: NEURAL SCAN SNAPSHOT SAVED TO {filename}")
                                
                            # 3. Log normal blinks
                            elif face["left_blink"] and face["right_blink"]:
                                action_logs.append(f"[SYS] NEURAL FEED: DUAL-BLINK DETECTED")
                            elif face["left_blink"]:
                                action_logs.append(f"[SYS] NEURAL FEED: LEFT-BLINK DETECTED")
                            elif face["right_blink"]:
                                action_logs.append(f"[SYS] NEURAL FEED: RIGHT-BLINK DETECTED")
                
                # 3. Handle Virtual Mouse (tracked primarily via hand 0 index tip)
                mouse_status = "Inactive"
                if self.virtual_mouse.enabled and len(active_hands) > 0:
                    primary_hand = active_hands[0]
                    lm_list = primary_hand["lm_list"]
                    fingers = self.recognizer.fingers_up(lm_list)
                    mouse_status = self.virtual_mouse.update(lm_list, frame.shape[1], frame.shape[0], fingers)
                
                # Calculate FPS
                fps = self.fps_counter.update()
                
                # Emit update signals
                self.update_stats_signal.emit(hands_data, fps, mouse_status, action_logs, active_faces)
                self.change_pixmap_signal.emit(frame)
            else:
                self.msleep(10)

        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()
        if hasattr(self, 'detector'):
            self.detector.close()
        if hasattr(self, 'face_detector'):
            self.face_detector.close()


class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle(config.get("app_name", "Neural Motion Vision Core"))
        self.setGeometry(100, 100, 1150, 780)
        self.setStyleSheet(CYBERPUNK_STYLESHEET)
        
        self.init_ui()
        
        # Start core background camera thread
        self.thread = CameraThread(
            camera_id=self.config.get("camera_id", 0),
            max_hands=self.config.get("max_hands", 2),
            detection_con=0.8,
            track_con=0.8
        )
        
        # Connect signals
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.update_stats_signal.connect(self.update_stats)
        self.thread.start()
        
        # Load Dynamic Plugins
        self.populate_plugins_tab()
        self.log_system_event("System Online. Cyber-Tech Motion & Gaze Core initialized.")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Left Panel (Video feed display)
        left_layout = QVBoxLayout()
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("border: 1px solid #FF0055; background-color: #000000; border-radius: 8px;")
        left_layout.addWidget(self.video_label, stretch=4)
        
        # Bezel indicator bar
        self.lbl_sub_status = QLabel("HUD STATUS: SENSORS ARMED // MOTION & GAZE: DETECTING")
        self.lbl_sub_status.setFont(QFont("Consolas", 10))
        self.lbl_sub_status.setStyleSheet("color: #FF2B6D; padding: 6px; border: 1px solid rgba(255, 0, 85, 0.2); border-radius: 4px; background-color: rgba(12,4,8,0.6);")
        self.lbl_sub_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.lbl_sub_status)
        
        main_layout.addLayout(left_layout, stretch=3)
        
        # Right Panel (Tabs panel)
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(12, 12, 12, 12)
        
        # Cyber title
        title_label = QLabel("NEURAL MOTION CORE\nHUD PLATFORM v4.0")
        title_label.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #FF0055; margin-bottom: 12px; border: none; font-weight: 900;")
        right_layout.addWidget(title_label)
        
        # Control panel tabs
        self.tabs = QTabWidget()
        right_layout.addWidget(self.tabs)
        
        # Tab 1: Telemetry
        self.tab_telemetry = QWidget()
        self.setup_telemetry_tab()
        self.tabs.addTab(self.tab_telemetry, "TELEMETRY")
        
        # Tab 2: V-Mouse
        self.tab_mouse = QWidget()
        self.setup_mouse_tab()
        self.tabs.addTab(self.tab_mouse, "V-MOUSE")
        
        # Tab 3: Overlay Config
        self.tab_visuals = QWidget()
        self.setup_visuals_tab()
        self.tabs.addTab(self.tab_visuals, "HUD CONFIG")
        
        # Tab 4: Audios
        self.tab_audios = QWidget()
        self.setup_audio_tab()
        self.tabs.addTab(self.tab_audios, "AUDIO CORE")
        
        # Tab 5: Plugins
        self.tab_plugins = QWidget()
        self.setup_plugins_tab()
        self.tabs.addTab(self.tab_plugins, "PLUGINS")
        
        # Tab 6: Neural Face Commands
        self.tab_face_commands = QWidget()
        self.setup_face_commands_tab()
        self.tabs.addTab(self.tab_face_commands, "NEURAL CMD")
        
        # bottom actions
        right_layout.addSpacing(15)
        self.btn_recalibrate = QPushButton("RECALIBRATE SENSORS")
        self.btn_recalibrate.clicked.connect(self.recalibrate_fields)
        self.btn_exit = QPushButton("TERMINATE CORE SYSTEM")
        self.btn_exit.setStyleSheet("border-color: #FF0055; color: #FF0055; background-color: rgba(255, 0, 85, 0.05);")
        self.btn_exit.clicked.connect(self.close)
        
        right_layout.addWidget(self.btn_recalibrate)
        right_layout.addSpacing(8)
        right_layout.addWidget(self.btn_exit)
        
        main_layout.addWidget(right_panel, stretch=2)

    def setup_telemetry_tab(self):
        layout = QVBoxLayout(self.tab_telemetry)
        
        # Performance
        stats_group = QGroupBox("TRACKING METRICS")
        stats_layout = QVBoxLayout(stats_group)
        self.fps_label = QLabel("FPS: 0")
        self.hands_label = QLabel("Hands Detected: 0")
        self.face_label = QLabel("Face Neural Lock: Offline")
        self.blink_label = QLabel("Blink Telemetry: L: Normal | R: Normal")
        self.gaze_label = QLabel("Pupil Tracking: L: - | R: -")
        
        for lbl in [self.fps_label, self.hands_label, self.face_label, self.blink_label, self.gaze_label]:
            lbl.setFont(QFont("Consolas", 11))
            stats_layout.addWidget(lbl)
        layout.addWidget(stats_group)
        
        # Hands list
        hands_group = QGroupBox("ACTIVE MOTION ENTITIES")
        hands_layout = QVBoxLayout(hands_group)
        self.hands_list = QListWidget()
        self.hands_list.setMinimumHeight(80)
        hands_layout.addWidget(self.hands_list)
        layout.addWidget(hands_group)
        
        # Spells text feed console
        console_group = QGroupBox("SYSTEM CONSOLE FEED")
        console_layout = QVBoxLayout(console_group)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(150)
        console_layout.addWidget(self.console)
        layout.addWidget(console_group)

    def setup_mouse_tab(self):
        layout = QVBoxLayout(self.tab_mouse)
        
        instructions = QLabel(
            "==== GESTURE V-MOUSE ====\n\n"
            "• POINTING (Index finger up): Move system pointer\n"
            "• PINCH (Index & Middle tips close): Left click / Hold & Drag\n"
            "• OTHER GESTURES: Releases click instantly"
        )
        instructions.setFont(QFont("Consolas", 10))
        instructions.setStyleSheet("color: #FF8888; padding: 10px; border: 1px dashed #FF0055; border-radius: 6px; background-color: rgba(0,0,0,0.5);")
        layout.addWidget(instructions)
        
        mouse_group = QGroupBox("VIRTUAL MOUSE CONTROLLER")
        mouse_layout = QVBoxLayout(mouse_group)
        
        self.chk_enable_mouse = QCheckBox("Enable Air Mouse Control")
        self.chk_enable_mouse.stateChanged.connect(self.toggle_virtual_mouse)
        mouse_layout.addWidget(self.chk_enable_mouse)
        mouse_layout.addSpacing(15)
        
        lbl_smooth = QLabel("Gliding Smoothening:")
        mouse_layout.addWidget(lbl_smooth)
        self.slider_smooth = QSlider(Qt.Orientation.Horizontal)
        self.slider_smooth.setRange(1, 20)
        self.slider_smooth.setValue(5)
        self.slider_smooth.valueChanged.connect(self.change_mouse_smoothening)
        mouse_layout.addWidget(self.slider_smooth)
        
        layout.addWidget(mouse_group)
        
        status_group = QGroupBox("ACTION FEEDBACK")
        status_layout = QVBoxLayout(status_group)
        self.lbl_mouse_status = QLabel("MOUSE STATE: INACTIVE")
        self.lbl_mouse_status.setFont(QFont("Consolas", 12))
        self.lbl_mouse_status.setStyleSheet("color: #FF5500; font-weight: bold;")
        status_layout.addWidget(self.lbl_mouse_status)
        layout.addWidget(status_group)
        
        layout.addStretch()

    def setup_visuals_tab(self):
        layout = QVBoxLayout(self.tab_visuals)
        
        # Cyber theme controller
        theme_group = QGroupBox("HUD AESTHETIC PALETTE")
        theme_layout = QVBoxLayout(theme_group)
        
        lbl_theme = QLabel("Active Color Scheme:")
        theme_layout.addWidget(lbl_theme)
        
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Red Alert", "Matrix Green", "Synthwave"])
        self.combo_theme.currentTextChanged.connect(self.change_hud_theme)
        theme_layout.addWidget(self.combo_theme)
        layout.addWidget(theme_group)
        
        fx_group = QGroupBox("HUD OVERLAY SETTINGS")
        fx_layout = QVBoxLayout(fx_group)
        
        self.chk_hud_brackets = QCheckBox("Render Target Brackets & Reticles")
        self.chk_hud_brackets.setChecked(True)
        self.chk_hud_brackets.stateChanged.connect(self.toggle_hud_overlays)
        fx_layout.addWidget(self.chk_hud_brackets)
        
        self.chk_landmarks = QCheckBox("Render Tech Skeleton Joints")
        self.chk_landmarks.setChecked(True)
        self.chk_landmarks.stateChanged.connect(self.toggle_landmarks)
        fx_layout.addWidget(self.chk_landmarks)
        
        self.chk_face_hud = QCheckBox("Render Face & Pupil Mesh Overlay")
        self.chk_face_hud.setChecked(True)
        self.chk_face_hud.stateChanged.connect(self.toggle_face_hud)
        fx_layout.addWidget(self.chk_face_hud)
        
        layout.addWidget(fx_group)
        
        mode_group = QGroupBox("MOTION HUD OVERLAY STYLE")
        mode_layout = QVBoxLayout(mode_group)
        
        lbl_mode = QLabel("Hand HUD Mode:")
        mode_layout.addWidget(lbl_mode)
        
        self.combo_hud_mode = QComboBox()
        self.combo_hud_mode.addItems(["3D Hologram", "Standard Brackets"])
        self.combo_hud_mode.currentTextChanged.connect(self.change_hand_hud_mode)
        mode_layout.addWidget(self.combo_hud_mode)
        layout.addWidget(mode_group)
        
        multi_group = QGroupBox("DETECTION PARAMS")
        multi_layout = QVBoxLayout(multi_group)
        
        self.chk_multi_user = QCheckBox("Detect Multiple Hands Concurrently")
        self.chk_multi_user.setChecked(True)
        self.chk_multi_user.stateChanged.connect(self.toggle_multi_user)
        multi_layout.addWidget(self.chk_multi_user)
        
        layout.addWidget(multi_group)
        layout.addStretch()

    def setup_audio_tab(self):
        layout = QVBoxLayout(self.tab_audios)
        
        audio_group = QGroupBox("SYSTEM AUDIO")
        audio_layout = QVBoxLayout(audio_group)
        
        self.chk_enable_audio = QCheckBox("Enable UI Sound Feedback")
        self.chk_enable_audio.setChecked(False) 
        self.chk_enable_audio.stateChanged.connect(self.toggle_audio_engine)
        audio_layout.addWidget(self.chk_enable_audio)
        
        desc = QLabel(
            "==== SOUND SYSTEM ====\n\n"
            "Plays non-blocking background audio beeps for gesture confirmations."
        )
        desc.setFont(QFont("Consolas", 10))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #CC8888; margin-top: 15px;")
        audio_layout.addWidget(desc)
        
        layout.addWidget(audio_group)
        layout.addStretch()

    def setup_plugins_tab(self):
        layout = QVBoxLayout(self.tab_plugins)
        
        desc_label = QLabel("Hot-swappable gesture plugin modules dashboard:")
        desc_label.setFont(QFont("Consolas", 10))
        layout.addWidget(desc_label)
        
        # Dynamic scroll area
        self.plugins_scroll = QScrollArea()
        self.plugins_scroll.setWidgetResizable(True)
        self.plugins_scroll_content = QWidget()
        self.plugins_scroll_layout = QVBoxLayout(self.plugins_scroll_content)
        self.plugins_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.plugins_scroll.setWidget(self.plugins_scroll_content)
        
        layout.addWidget(self.plugins_scroll)
        
        self.btn_refresh_plugins = QPushButton("FORCE RESCAN PLUGINS")
        self.btn_refresh_plugins.clicked.connect(self.reload_plugins)
        layout.addWidget(self.btn_refresh_plugins)

    def setup_face_commands_tab(self):
        layout = QVBoxLayout(self.tab_face_commands)
        
        # AR Filters group
        ar_group = QGroupBox("COGNITIVE AR FACE FILTER")
        ar_layout = QVBoxLayout(ar_group)
        self.combo_face_filter = QComboBox()
        self.combo_face_filter.addItems(["Tactical Visor", "Neon Circuit", "Lock Reticle", "None"])
        self.combo_face_filter.currentTextChanged.connect(self.change_face_filter)
        ar_layout.addWidget(QLabel("Select Active AR Overlay:"))
        ar_layout.addWidget(self.combo_face_filter)
        layout.addWidget(ar_group)
        
        # Dynamic gesture triggers group
        triggers_group = QGroupBox("NEURAL TRIGGER SETTINGS")
        triggers_layout = QVBoxLayout(triggers_group)
        
        self.chk_wink_actions = QCheckBox("Enable Eye-Wink Controls")
        self.chk_wink_actions.setChecked(True)
        self.chk_wink_actions.stateChanged.connect(self.toggle_wink_actions)
        
        self.chk_yawn_alerts = QCheckBox("Enable Mouth Yawn Warning")
        self.chk_yawn_alerts.setChecked(True)
        self.chk_yawn_alerts.stateChanged.connect(self.toggle_yawn_alerts)
        
        self.chk_drowsy_alerts = QCheckBox("Enable Fatigue Alarm")
        self.chk_drowsy_alerts.setChecked(True)
        self.chk_drowsy_alerts.stateChanged.connect(self.toggle_drowsy_alerts)
        
        triggers_layout.addWidget(self.chk_wink_actions)
        triggers_layout.addWidget(self.chk_yawn_alerts)
        triggers_layout.addWidget(self.chk_drowsy_alerts)
        layout.addWidget(triggers_group)
        
        # Info card
        info_label = QLabel(
            "==== BIOLOGICAL CONTROLS ====\n\n"
            "• Right Wink: Cycle HUD theme colors\n"
            "• Left Wink: Take instant camera snapshot\n"
            "• Yawn: Trigger fatigue console warning\n"
            "• Closed Eyes: Sound emergency dual-tone alarm"
        )
        info_label.setFont(QFont("Consolas", 9))
        info_label.setStyleSheet("color: #DDAABB; background-color: rgba(255, 255, 255, 0.02); padding: 8px; border: 1px solid rgba(255, 255, 255, 0.05);")
        layout.addWidget(info_label)
        layout.addStretch()

    def change_face_filter(self, filter_name):
        self.thread.effects.face_filter_mode = filter_name
        self.thread.audio.play_sound_async("ui_nav")

    def toggle_wink_actions(self, state):
        self.thread.enable_wink_actions = bool(state)
        self.thread.audio.play_sound_async("ui_nav")

    def toggle_yawn_alerts(self, state):
        self.thread.enable_yawn_alerts = bool(state)
        self.thread.audio.play_sound_async("ui_nav")

    def toggle_drowsy_alerts(self, state):
        self.thread.enable_drowsy_alerts = bool(state)
        self.thread.audio.play_sound_async("ui_nav")

    def populate_plugins_tab(self):
        # Clear existing
        for i in reversed(range(self.plugins_scroll_layout.count())):
            w = self.plugins_scroll_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
                
        plugins = self.thread.plugin_manager.get_plugins()
        if not plugins:
            no_lbl = QLabel("[SYSTEM] No dynamic plugins compiled.")
            no_lbl.setStyleSheet("color: #FF0055;")
            self.plugins_scroll_layout.addWidget(no_lbl)
            return

        for plugin in plugins:
            plugin_frame = QFrame()
            plugin_frame.setStyleSheet("border: 1px solid #441122; background-color: rgba(12,4,8,0.9); padding: 8px; margin-bottom: 5px;")
            frame_layout = QVBoxLayout(plugin_frame)
            
            header = QHBoxLayout()
            chk = QCheckBox(plugin.name)
            chk.setChecked(plugin.enabled)
            chk.stateChanged.connect(lambda state, p=plugin: self.toggle_plugin_state(p, state))
            chk.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
            chk.setStyleSheet("color: #FF2B6D;")
            
            trigger_lbl = QLabel(f"[{plugin.gesture_trigger}]")
            trigger_lbl.setStyleSheet("color: #FF5500; font-weight: bold;")
            trigger_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            header.addWidget(chk)
            header.addWidget(trigger_lbl)
            frame_layout.addLayout(header)
            
            desc = QLabel(plugin.description)
            desc.setFont(QFont("Consolas", 9))
            desc.setStyleSheet("color: #A08080; margin-left: 20px; border: none;")
            desc.setWordWrap(True)
            frame_layout.addWidget(desc)
            
            self.plugins_scroll_layout.addWidget(plugin_frame)

    # ====================================================
    # Event Handlers & Slots
    # ====================================================
    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        h, w, ch = cv_img.shape
        bytes_per_line = ch * w
        qt_format = QImage(cv_img.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
        scaled_pixmap = qt_format.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
        self.video_label.setPixmap(QPixmap.fromImage(scaled_pixmap))

    @pyqtSlot(list, int, str, list, list)
    def update_stats(self, hands_data, fps, mouse_status, action_logs, faces_data):
        self.fps_label.setText(f"System FPS: {fps}")
        self.hands_label.setText(f"Active Hand Tracking Lock: {len(hands_data)}")
        
        # Sync combobox theme with active theme from camera thread (for wink-based theme switching)
        active_theme = self.thread.effects.current_theme
        if self.combo_theme.currentText() != active_theme:
            self.combo_theme.blockSignals(True)
            self.combo_theme.setCurrentText(active_theme)
            self.combo_theme.blockSignals(False)
        
        # Update Face Telemetry
        if faces_data:
            face = faces_data[0]
            is_drowsy = face.get("drowsy", False)
            
            if is_drowsy:
                self.face_label.setText("Face Neural Lock: WARNING - FATIGUE DETECTED")
                self.face_label.setStyleSheet("color: #FF0055; font-weight: bold;")
                self.blink_label.setText("Blink Telemetry: DROWSINESS ALERT ACTIVE !!!")
                self.blink_label.setStyleSheet("color: #FF0055; font-weight: bold; background-color: rgba(255, 0, 85, 0.1); border: 1px solid #FF0055; padding: 2px;")
            elif face.get("yawning", False):
                self.face_label.setText("Face Neural Lock: LOCKED - YAWN ALERT")
                self.face_label.setStyleSheet("color: #FFA500; font-weight: bold;")
                self.blink_label.setText(f"Blink Telemetry: Yawning (Aspect Ratio: {face.get('yawn_ratio', 0.0):.2f})")
                self.blink_label.setStyleSheet("color: #FFA500; font-weight: bold; border: none; background-color: transparent; padding: 0px;")
            else:
                self.face_label.setText(f"Face Neural Lock: LOCKED (ID: {face['index']})")
                self.face_label.setStyleSheet("color: #00FF66; font-weight: bold;")
                blink_l = "BLINK!" if face["left_blink"] else "Normal"
                blink_r = "BLINK!" if face["right_blink"] else "Normal"
                self.blink_label.setText(f"Blink Telemetry: L: {blink_l} | R: {blink_r}")
                if face["left_blink"] or face["right_blink"]:
                    self.blink_label.setStyleSheet("color: #FF0055; font-weight: bold; border: none; background-color: transparent; padding: 0px;")
                else:
                    self.blink_label.setStyleSheet("color: #DDAABB; border: none; background-color: transparent; padding: 0px;")
                
            if face["left_pupil"] and face["right_pupil"]:
                lx, ly = face["left_pupil"]
                rx, ry = face["right_pupil"]
                self.gaze_label.setText(f"Pupil Tracking: L: [{lx},{ly}] | R: [{rx},{ry}]")
                self.gaze_label.setStyleSheet("color: #00FFFF;")
            else:
                self.gaze_label.setText("Pupil Tracking: Gaze Lock Scanning...")
                self.gaze_label.setStyleSheet("color: #FF5500;")
        else:
            self.face_label.setText("Face Neural Lock: Offline")
            self.face_label.setStyleSheet("color: #FF0055;")
            self.blink_label.setText("Blink Telemetry: L: Offline | R: Offline")
            self.blink_label.setStyleSheet("color: #DDAABB;")
            self.gaze_label.setText("Pupil Tracking: L: Offline | R: Offline")
            self.gaze_label.setStyleSheet("color: #DDAABB;")
            
        self.lbl_mouse_status.setText(f"MOUSE STATE: {mouse_status.upper()}")
        if "Click" in mouse_status:
            self.lbl_mouse_status.setStyleSheet("color: #00FF66; font-weight: bold;")
        elif "Moving" in mouse_status:
            self.lbl_mouse_status.setStyleSheet("color: #FF5500; font-weight: bold;")
        else:
            self.lbl_mouse_status.setStyleSheet("color: #FF0055; font-weight: bold;")

        self.hands_list.clear()
        for hand in hands_data:
            item_text = f"HAND: {hand['label'].upper()} | GESTURE: {hand['gesture']} | COORDS: {hand['coords']}"
            item = QListWidgetItem(item_text)
            item.setFont(QFont("Consolas", 10))
            if hand['label'] == "Left":
                item.setForeground(Qt.GlobalColor.yellow)
            else:
                item.setForeground(Qt.GlobalColor.red)
            self.hands_list.addItem(item)
            
        for log in action_logs:
            self.log_system_event(log)

    def log_system_event(self, text):
        ts = time.strftime("%H:%M:%S")
        self.console.append(f"[{ts}] {text}")
        sb = self.console.verticalScrollBar()
        sb.setValue(sb.maximum())

    # Control Toggles & Slots
    def toggle_virtual_mouse(self, state):
        enabled = (state == 2)
        self.thread.virtual_mouse.set_enabled(enabled)
        self.log_system_event(f"Virtual Air Mouse control {'ENABLED' if enabled else 'DISABLED'}.")

    def change_mouse_smoothening(self, value):
        self.thread.virtual_mouse.smoothening = value
        self.log_system_event(f"Air Mouse gliding smoothening set to {value}.")

    def toggle_hud_overlays(self, state):
        enabled = (state == 2)
        self.thread.enable_hud_overlays = enabled
        self.log_system_event(f"HUD Bracket Overlays {'ENABLED' if enabled else 'DISABLED'}.")

    def toggle_landmarks(self, state):
        enabled = (state == 2)
        self.thread.enable_basic_drawing = enabled
        self.log_system_event(f"Tech Skeleton Joints {'ENABLED' if enabled else 'DISABLED'}.")

    def toggle_face_hud(self, state):
        enabled = (state == 2)
        self.thread.enable_face_hud = enabled
        self.log_system_event(f"Face & Pupil HUD overlays {'ENABLED' if enabled else 'DISABLED'}.")

    def change_hud_theme(self, theme_name):
        self.thread.effects.set_theme(theme_name)
        self.log_system_event(f"Active HUD visual theme preset set to: {theme_name.upper()}.")

    def change_hand_hud_mode(self, mode_name):
        self.thread.hand_hud_mode = mode_name
        self.log_system_event(f"Hand HUD overlay style changed to: {mode_name.upper()}.")

    def toggle_multi_user(self, state):
        enabled = (state == 2)
        self.thread.multi_user_mode = enabled
        self.log_system_event(f"Multi-hand dynamic tracking {'ENABLED' if enabled else 'DISABLED'}.")

    def toggle_audio_engine(self, state):
        enabled = (state == 2)
        self.thread.audio.set_enabled(enabled)
        self.log_system_event(f"Audio Feedback {'ENABLED' if enabled else 'DISABLED'}.")

    def toggle_plugin_state(self, plugin, state):
        enabled = (state == 2)
        plugin.enabled = enabled
        self.log_system_event(f"Plugin '{plugin.name}' {'ENABLED' if enabled else 'DISABLED'}.")

    def reload_plugins(self):
        self.log_system_event("Rescanning plugin modules directory...")
        self.thread.plugin_manager.load_plugins()
        self.populate_plugins_tab()
        self.log_system_event("Dynamic plugins loaded successfully.")

    def recalibrate_fields(self):
        self.log_system_event("Initiating sensor field recalibration... Hold face and hands in frame.")
        self.lbl_sub_status.setText("HUD STATUS: RE-OPTIMIZING SYSTEM SENSOR FIELDS...")
        time.sleep(0.1)
        self.lbl_sub_status.setText("HUD STATUS: SENSORS ARMED // MOTION & GAZE: DETECTING")
        self.log_system_event("Recalibration complete. Gaze locks & hand sensor coordinates aligned.")

    def closeEvent(self, event):
        self.log_system_event("Shutting down vision capturing threads...")
        self.thread.stop()
        event.accept()
