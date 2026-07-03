import numpy as np
# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QComboBox
# pyrefly: ignore [missing-import]
from PyQt6.QtCore import Qt, QTimer
# pyrefly: ignore [missing-import]
from PyQt6.QtGui import QColor, QBrush
from src.core.telemetry import SessionRecorder

class TabPlayback(QWidget):
    def __init__(self):
        super().__init__()
        self.session_data = None
        self.snapshots = []
        self.current_index = 0
        self.is_playing = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_step)
        
        # Cores para turmas
        self.class_colors = [
            QColor("#4ea8de"), QColor("#48bfe3"), QColor("#56cfe1"), 
            QColor("#64dfdf"), QColor("#72efdd"), QColor("#80ffdb")
        ]
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Painel superior (Load)
        top_panel = QHBoxLayout()
        self.btn_load = QPushButton("Carregar Sessão (.pickle)")
        self.btn_load.clicked.connect(self.load_session)
        top_panel.addWidget(self.btn_load)
        
        self.lbl_info = QLabel("Nenhuma sessão carregada.")
        top_panel.addWidget(self.lbl_info)
        layout.addLayout(top_panel)
        
        # HUD
        hud_layout = QHBoxLayout()
        self.lbl_phase = QLabel("Fase: -")
        self.lbl_iter = QLabel("Iteração: -")
        self.lbl_temp = QLabel("Temp: -")
        self.lbl_cost = QLabel("Custo Global: -")
        hud_layout.addWidget(self.lbl_phase)
        hud_layout.addWidget(self.lbl_iter)
        hud_layout.addWidget(self.lbl_temp)
        hud_layout.addWidget(self.lbl_cost)
        layout.addLayout(hud_layout)
        
        # Grid
        self.table = QTableWidget(0, 0)
        layout.addWidget(self.table)
        
        # Timeline e Controles
        ctrl_layout = QHBoxLayout()
        self.btn_play = QPushButton("▶ Play")
        self.btn_play.clicked.connect(self.toggle_play)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self.slider_changed)
        
        self.combo_speed = QComboBox()
        self.combo_speed.addItems(["1x", "2x", "5x", "10x"])
        self.combo_speed.currentIndexChanged.connect(self.update_speed)
        
        ctrl_layout.addWidget(self.btn_play)
        ctrl_layout.addWidget(self.slider)
        ctrl_layout.addWidget(self.combo_speed)
        
        layout.addLayout(ctrl_layout)
        self.setLayout(layout)

    def update_speed(self):
        speed_str = self.combo_speed.currentText().replace("x", "")
        interval = int(1000 / int(speed_str))
        if self.is_playing:
            self.timer.setInterval(interval)

    def toggle_play(self):
        if not self.snapshots: return
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.btn_play.setText("⏸ Pause")
            self.update_speed()
            self.timer.start()
        else:
            self.btn_play.setText("▶ Play")
            self.timer.stop()

    def next_step(self):
        if self.current_index < len(self.snapshots) - 1:
            self.slider.setValue(self.current_index + 1)
        else:
            self.toggle_play()

    def slider_changed(self, value):
        self.current_index = value
        self.render_snapshot()

    def load_session(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir Sessão", "", "Pickle Files (*.pickle)")
        if path:
            try:
                self.session_data = SessionRecorder.load_session(path)
                self.snapshots = self.session_data["snapshots"]
                self.setup_grid()
                
                self.slider.setEnabled(True)
                self.slider.setMinimum(0)
                self.slider.setMaximum(len(self.snapshots) - 1)
                self.slider.setValue(0)
                
                self.lbl_info.setText(f"Sessão carregada: {len(self.snapshots)} snapshots.")
                self.render_snapshot()
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Falha ao carregar: {e}")

    def setup_grid(self):
        profs = sorted(self.session_data["prof_id_to_idx"].items(), key=lambda x: x[1])
        prof_names = [p[0] for p in profs]
        
        matrix_shape = self.snapshots[0].matrix_copy.shape
        self.table.setRowCount(matrix_shape[0])
        self.table.setColumnCount(matrix_shape[1])
        
        self.table.setVerticalHeaderLabels(prof_names)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def render_snapshot(self):
        if not self.snapshots: return
        
        snap = self.snapshots[self.current_index]
        self.lbl_phase.setText(f"Fase: {snap.phase}")
        self.lbl_iter.setText(f"Iteração: {snap.iteration}")
        self.lbl_temp.setText(f"Temp: {snap.temperature:.2f}")
        self.lbl_cost.setText(f"Custo Global: {snap.cost}")
        
        mat = snap.matrix_copy
        int_to_cd = self.session_data["int_to_class_disc"]
        
        color_indisp = QBrush(QColor("#333333"))
        color_vago = QBrush(QColor("#ffffff"))
        
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                val = mat[i, j]
                item = QTableWidgetItem()
                
                if val == -1:
                    item.setText("X")
                    item.setBackground(color_indisp)
                    item.setForeground(QBrush(QColor("white")))
                elif val == 0:
                    item.setText("")
                    item.setBackground(color_vago)
                else:
                    cd = int_to_cd.get(val)
                    if cd:
                        turma, disc = cd
                        item.setText(f"{turma}\n{disc}")
                        color_idx = hash(turma) % len(self.class_colors)
                        item.setBackground(QBrush(self.class_colors[color_idx]))
                
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)
