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

def get_hex_and_font_color(seed_text: str) -> tuple[str, str]:
    """
    Returns (bg_hex, font_hex) with smart contrast.
    Font is WHITE for dark backgrounds (luminance < 0.35), BLACK for light ones.
    Uses WCAG 2.1 relative luminance formula.
    """
    bg_hex = generate_stable_color(seed_text)
    r = int(bg_hex[1:3], 16) / 255.0
    g = int(bg_hex[3:5], 16) / 255.0
    b = int(bg_hex[5:7], 16) / 255.0

    # sRGB linearization
    def linearize(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    L = 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)
    font_color = "#ffffff" if L < 0.35 else "#000000"
    return bg_hex, font_color
