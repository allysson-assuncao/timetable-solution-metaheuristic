import pandas as pd
import numpy as np
from src.core.state import TimetableState

class ExportManager:
    def __init__(self, state: TimetableState):
        self.state = state
        self.int_to_class_disc = state.int_to_class_disc
        
    def export_to_excel(self, filepath: str = "Horario_Escolar_Otimizado.xlsx"):
        matrix = self.state.matrix
        M, P = matrix.shape
        
        # Recuperar IDs legíveis (Professores)
        prof_ids = [p.id_professor for p in self.state.stp_state.professores]
        prof_names = {p.id_professor: p.nome for p in self.state.stp_state.professores}
        
        # O state garante que a linha 'i' é exatamente o professor no índice 'i' da lista
        row_labels = [prof_names.get(p_id, p_id) for p_id in prof_ids]
        
        # Montar rótulos das colunas
        dias_letivos = self.state.stp_state.parametros_execucao.dias_letivos
        periodos_por_dia = self.state.stp_state.parametros_execucao.periodos_por_dia
        dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        
        col_labels = []
        for d in range(dias_letivos):
            dia = dias_semana[d % 7]
            for p in range(periodos_por_dia):
                col_labels.append(f"{dia} - P{p+1}")
                
        # Garantir que bate com P
        col_labels = col_labels[:P]
        
        # Construir array de dados traduzido
        export_data = []
        for i in range(M):
            row_data = []
            for j in range(P):
                val = matrix[i, j]
                if val == -1:
                    row_data.append("INDISPONÍVEL")
                elif val == 0:
                    row_data.append("Livre")
                else:
                    class_id, disc_id = self.int_to_class_disc.get(val, ("Desconhecido", "Desconhecido"))
                    # Tentar achar o nome legível da turma
                    turma_name = next((t.nome for t in self.state.stp_state.turmas if t.id_turma == class_id), class_id)
                    disc_name = next((d.nome for d in self.state.stp_state.disciplinas if d.id_disciplina == disc_id), disc_id)
                    row_data.append(f"{turma_name}\n({disc_name})")
            export_data.append(row_data)
            
        # Converter para DataFrame
        df = pd.DataFrame(export_data, index=row_labels, columns=col_labels)
        
        # Exportar para Excel com formatação básica
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Horário Completo")
            
            workbook = writer.book
            worksheet = writer.sheets["Horário Completo"]
            
            # Ajustar largura das colunas e quebra de linha
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter # Nome da coluna (A, B, C...)
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                        
                        # Ativar quebra de texto (wrap text)
                        cell.alignment = cell.alignment.copy(wrapText=True)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 25) # Limitar largura máxima
                worksheet.column_dimensions[column].width = adjusted_width
                
        print(f"Planilha exportada com sucesso em: {filepath}")
        return filepath
