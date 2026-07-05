import hashlib

def generate_stable_color(seed_text: str) -> str:
    """Gera uma cor HEX pastel baseada no hash estável de uma string (ex: Nome da Turma + Nome Disciplina)"""
    h = hashlib.md5(seed_text.encode('utf-8')).hexdigest()
    
    # Pega os 3 primeiros bytes
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    
    # Suaviza para tons pasteis
    r = (r + 255) // 2
    g = (g + 255) // 2
    b = (b + 255) // 2
    
    return f"#{r:02x}{g:02x}{b:02x}"

def get_hex_and_font_color(seed_text: str):
    bg_hex = generate_stable_color(seed_text)
    return bg_hex, "#000000"
