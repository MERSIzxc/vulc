from PIL import Image, ImageDraw, ImageFont

def create_icon(size):
    # Создаем изображение с градиентом
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)

    # Рисуем фон градиентом (упрощенный)
    for i in range(size):
        color = (102 + int(i * 16 / size), 126 + int(i * 108 / size), 234 - int(i * 90 / size))
        draw.rectangle([0, i, size, i+1], fill=color)

    # Рисуем букву V
    try:
        font_size = int(size * 0.6)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text = "V"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size - text_width) // 2
    y = (size - text_height) // 2 - bbox[1]

    draw.text((x, y), text, fill='white', font=font)

    return img

# Создаем иконки разных размеров
for size in [16, 48, 128]:
    icon = create_icon(size)
    icon.save(f'C:/Users/Компьютер/Desktop/vulcan_tracker/chrome_extension/icon{size}.png')
    print(f'Created icon{size}.png')

print('All icons created!')
