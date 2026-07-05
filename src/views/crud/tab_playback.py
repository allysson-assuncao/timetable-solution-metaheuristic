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
        
        # Painel superior (Load / Export)
        top_panel = QHBoxLayout()
        self.btn_load = QPushButton("Carregar Sessão (.pickle)")
        self.btn_load.clicked.connect(self.load_from_file)
        top_panel.addWidget(self.btn_load)
        
        self.btn_export = QPushButton("📊 Exportar Excel (XLSX)")
        self.btn_export.clicked.connect(self.export_excel)
        self.btn_export.setEnabled(False)
        self.btn_export.setStyleSheet("background-color: #2b9348; color: white; font-weight: bold;")
        top_panel.addWidget(self.btn_export)
        
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
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Timeline e Controles
        ctrl_layout = QHBoxLayout()
        self.btn_play = QPushButton("▶ Play")
        self.btn_play.clicked.connect(self.toggle_play)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self.slider_changed)
        
        self.lbl_speed = QLabel("Velocidade (1x):")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(1)
        self.speed_slider.valueChanged.connect(self.update_speed)
        
        ctrl_layout.addWidget(self.btn_play)
        ctrl_layout.addWidget(self.slider)
        ctrl_layout.addWidget(self.lbl_speed)
        ctrl_layout.addWidget(self.speed_slider)
        
        layout.addLayout(ctrl_layout)
        self.setLayout(layout)

    def update_speed(self):
        speed_mult = self.speed_slider.value()
        self.lbl_speed.setText(f"Velocidade ({speed_mult}x):")
        
        interval = max(10, int(1000 / speed_mult))
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

    def load_from_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir Sessão", "", "Pickle Files (*.pickle)")
        if path:
            try:
                data = SessionRecorder.load_session(path)
                
                # Tenta reconstruir o raw_state para habilitar exportação Excel
                if "stp_state_dict" in data:
                    from src.models.stp_state import STPState
                    from src.core.state import TimetableState
                    pyd_state = STPState(**data["stp_state_dict"])
                    t_state = TimetableState(pyd_state)
                    
                    # Como recriamos, a matriz final estará vazia (é recriada zerada).
                    # Mas o exporter usa t_state.matrix. Vamos injetar a matriz do último snapshot nela.
                    t_state.matrix = data["snapshots"][-1].matrix_copy
                    self.raw_state = t_state
                    self.btn_export.setEnabled(True)
                else:
                    self.raw_state = None
                    self.btn_export.setEnabled(False)
                    
                self.setup_from_data(data)
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Falha ao carregar: {e}")

    def load_session(self, state):
        # Recebe o TimetableState recém rodado do QThread
        self.raw_state = state
        self.btn_export.setEnabled(True)
        
        data = {
            "snapshots": state.session_recorder.snapshots,
            "prof_id_to_idx": state.prof_id_to_idx,
            "int_to_class_disc": state.int_to_class_disc
        }
        self.setup_from_data(data)
        
    def export_excel(self):
        if not hasattr(self, 'raw_state') or not self.raw_state:
            QMessageBox.warning(self, "Erro", "Nenhum estado válido para exportar.")
            return
            
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Excel", "Horario_Escolar_Otimizado.xlsx", "Excel Files (*.xlsx)")
        if path:
            try:
                from src.utils.exporter import ExportManager
                exporter = ExportManager(self.raw_state)
                exporter.export_to_excel(path)
                QMessageBox.information(self, "Sucesso", f"Excel exportado com sucesso em:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro na exportação: {e}")

    def setup_from_data(self, data):
        self.session_data = data
        self.snapshots = data["snapshots"]
        
        self.setup_grid()
        
        self.slider.setEnabled(True)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.snapshots) - 1)
        self.slider.setValue(0)
        self.current_index = 0
        
        self.lbl_info.setText(f"Sessão carregada: {len(self.snapshots)} snapshots.")
        self.render_snapshot()

    def setup_grid(self):
        profs = sorted(self.session_data["prof_id_to_idx"].items(), key=lambda x: x[1])
        prof_names = [p[0] for p in profs]
        
        matrix_shape = self.snapshots[0].matrix_copy.shape
        self.table.setRowCount(matrix_shape[0])
        self.table.setColumnCount(matrix_shape[1])
        
        self.table.setVerticalHeaderLabels(prof_names)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

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
                    item.setToolTip("Indisponibilidade / Fora da carga horária")
                elif val == 0:
                    item.setText("")
                    item.setBackground(color_vago)
                    item.setToolTip("Período Livre")
                else:
                    cd = int_to_cd.get(val)
                    if cd:
                        turma, disc = cd
                        item.setText(f"{turma}\n{disc}")
                        item.setToolTip(f"Turma: {turma}\nDisciplina: {disc}")
                        color_idx = hash(turma) % len(self.class_colors)
                        item.setBackground(QBrush(self.class_colors[color_idx]))
                
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)
