# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QRadioButton, QButtonGroup, QMessageBox, QProgressDialog
# pyrefly: ignore [missing-import]
from PyQt6.QtCore import Qt, QTimer
from src.models.state_manager import StateManager
from src.utils.persistence import WorkspacePersistence

class TabExecution(QWidget):
    def __init__(self, state_manager: StateManager, ui_main):
        super().__init__()
        self.state_manager = state_manager
        self.ui_main = ui_main
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        lbl_title = QLabel("Hub de Execução (Otimização)")
        lbl_title.setProperty("class", "title-h1")
        layout.addWidget(lbl_title)
        
        lbl_desc = QLabel("Escolha a fonte de dados para rodar a metaheurística. O motor rodará em Multi-Start paralelo e gravará um log de auditoria permanente.")
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)
        
        # Source Selection
        self.bg_source = QButtonGroup(self)
        
        self.rb_current = QRadioButton("Memória Atual da Interface (O que você editou)")
        self.rb_current.setChecked(True)
        self.bg_source.addButton(self.rb_current, 0)
        
        self.rb_loose = QRadioButton("Benchmark Sintético: Loose (Baixa Densidade)")
        self.bg_source.addButton(self.rb_loose, 1)
        
        self.rb_std = QRadioButton("Benchmark Sintético: Standard (Densidade Média)")
        self.bg_source.addButton(self.rb_std, 2)
        
        self.rb_const = QRadioButton("Benchmark Sintético: Constrained (Alta Densidade)")
        self.bg_source.addButton(self.rb_const, 3)
        
        layout.addWidget(self.rb_current)
        layout.addWidget(self.rb_loose)
        layout.addWidget(self.rb_std)
        layout.addWidget(self.rb_const)
        
        self.btn_run = QPushButton("🚀 Iniciar Otimização")
        self.btn_run.setMinimumHeight(60)
        self.btn_run.setProperty("class", "primary")
        self.btn_run.clicked.connect(self.prepare_and_run)
        
        layout.addStretch()
        layout.addWidget(self.btn_run)
        self.setLayout(layout)

    def prepare_and_run(self):
        source_id = self.bg_source.checkedId()
        
        if source_id == 0:
            if not self.state_manager.state.professores:
                QMessageBox.warning(self, "Erro", "Não há dados preenchidos na memória. Cadastre professores ou importe um Workspace.")
                return
            self.execute_engine(self.state_manager.state)
        else:
            # É um Benchmark Sintético, precisa gerar
            tier_map = {1: "loose", 2: "standard", 3: "constrained"}
            tier = tier_map[source_id]
            
            # Mostrar loading spinner bloqueante para geração
            self.progress_gen = QProgressDialog(f"Gerando Matriz Sintética de Teste ({tier})...", None, 0, 0, self)
            self.progress_gen.setWindowTitle("Aguarde")
            self.progress_gen.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress_gen.setCancelButton(None)
            self.progress_gen.show()
            
            # Usar QTimer para dar tempo da UI renderizar o progress dialog antes de travar processando
            QTimer.singleShot(100, lambda: self.generate_and_run(tier))

    def generate_and_run(self, tier):
        from src.utils.synthetic_factory import SyntheticDataFactory
        from src.models.stp_state import STPState
        
        try:
            raw_dict = SyntheticDataFactory.generate(tier)
            # Validação pydantic
            bench_state = STPState(**raw_dict)
            self.progress_gen.close()
            self.execute_engine(bench_state)
        except Exception as e:
            self.progress_gen.close()
            QMessageBox.critical(self, "Erro no Gerador", f"Falha ao gerar dados sintéticos:\n{e}")

    def execute_engine(self, pydantic_state):
        from src.core.state import TimetableState
        from src.core.telemetry import SessionRecorder
        from src.views.workers import EngineWorker
        
        t_state = TimetableState(pydantic_state)
        t_state.session_recorder = SessionRecorder(t_state)
        
        self.progress_opt = QProgressDialog("Otimizando grade... Isso pode levar de 5 a 30 segundos dependendo da densidade.", "Cancelar", 0, 0, self)
        self.progress_opt.setWindowTitle("Processando Metaheurística")
        self.progress_opt.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_opt.setCancelButton(None)
        self.progress_opt.show()
        
        self.btn_run.setEnabled(False)
        
        self.worker = EngineWorker(t_state, multi_start_runs=4)
        self.worker.finished_signal.connect(self.on_heuristic_finished)
        self.worker.error_signal.connect(self.on_heuristic_error)
        self.worker.start()
        
    def on_heuristic_finished(self, final_state):
        self.progress_opt.close()
        self.btn_run.setEnabled(True)
        
        # Salva auditoria universal no disco
        try:
            data_to_save = {
                "snapshots": final_state.session_recorder.snapshots,
                "prof_id_to_idx": final_state.prof_id_to_idx,
                "int_to_class_disc": final_state.int_to_class_disc,
                "stp_state_dict": final_state.stp_state.model_dump()
            }
            filepath = WorkspacePersistence.save_telemetry(data_to_save, prefix="run")
            QMessageBox.information(self, "Sucesso", f"Otimização concluída!\nLog de auditoria salvo em:\n{filepath}")
        except Exception as e:
            QMessageBox.warning(self, "Aviso", f"Otimização concluída, mas falhou ao salvar auditoria:\n{e}")
            
        # Repassa para o Playback (Nova Arquitetura Top-Level)
        self.ui_main.playback_widget.load_session(final_state)
        self.ui_main.open_playback_tab()
        
    def on_heuristic_error(self, err_msg):
        self.progress_opt.close()
        self.btn_run.setEnabled(True)
        QMessageBox.critical(self, "Erro na Otimização", f"Ocorreu um erro:\n{err_msg}")
