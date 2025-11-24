from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    # Stwórz niebieskie tło
    img = Image.new('RGB', (size, size), color='#0d6efd')
    draw = ImageDraw.Draw(img)
    
    # Narysuj prostą ikonę - białą literę K
    try:
        font_size = int(size * 0.6)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Narysuj tekst "K" na środku
    text = "K"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    position = ((size - text_width) // 2, (size - text_height) // 2 - bbox[1])
    draw.text(position, text, fill='white', font=font)
    
    # Zapisz
    img.save(filename, 'PNG')
    print(f"Utworzono: {filename}")

# Utwórz katalog static jeśli nie istnieje
os.makedirs('static', exist_ok=True)

# Stwórz ikony
create_icon(192, 'static/icon-192.png')
create_icon(512, 'static/icon-512.png')

print("Ikony PWA zostały utworzone!")
