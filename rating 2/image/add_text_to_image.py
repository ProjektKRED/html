from PIL import Image, ImageDraw, ImageFont
import os
import random

def add_text_to_image(text_file_path, output_dir):
    # Получаем список доступных фонов
    background_images = ["background_image1.jpg", "background_image2.jpg", "background_image3.jpg", "background_image4.jpg", "background_image5.jpg"]

    # Открываем файл с текстами
    with open(text_file_path, 'r', encoding='utf-8') as file:
        h1 = file.readlines()

    # Настроим начальную позицию для текста
    line_height = 100  # Высота между строками текста (сделаем отступы меньше)
    max_width = 800  # Максимальная ширина текста с отступом
    max_height = 600  # Максимальная высота текста с отступом

    # Убедитесь, что папка для вывода существует
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Функция для экранирования символов в тексте, чтобы они подходили для имени файла
    def sanitize_filename(text):
        return text.replace(":", "_").replace("/", "_").replace("\\", "_")  # Заменяем двоеточие и слэши

    # Функция для уменьшения шрифта на 1% до тех пор, пока текст не поместится
    def adjust_font_size(font, text, draw, max_width, max_height):
        current_font = font
        while True:
            lines = wrap_text(text, current_font, max_width)
            total_height = len(lines) * line_height

            if total_height <= max_height:
                text_width = max([draw.textbbox((0, 0), line, font=current_font)[2] - draw.textbbox((0, 0), line, font=current_font)[0] for line in lines])
                if text_width <= max_width:
                    break
            new_size = int(current_font.size * 0.99)
            if new_size < 10:
                break
            current_font = ImageFont.truetype("DejaVuSans-Bold.ttf", new_size)
        return current_font

    # Функция для разбивки текста на строки с переносом
    def wrap_text(text, font, max_width):
        lines = []
        words = text.split(' ')
        current_line = ""
        
        for word in words:
            test_line = current_line + (word if current_line == "" else " " + word)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
            
            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        return lines

    # Проходим по строкам из файла и добавляем их на изображение
    for idx, text in enumerate(h1):
        text = text.strip()  # Убираем лишние пробелы и переводы строк
        sanitized_text = sanitize_filename(text)  # Экранируем символы для имени файла
        # Случайный выбор фона для каждой строки
        selected_background = random.choice(background_images)
        img = Image.open(selected_background)  # Загружаем выбранный фон
        draw = ImageDraw.Draw(img)  # Переинициализируем объект draw

        # Делаем копию изображения для каждого текста
        img_copy = img.copy()
        draw_copy = ImageDraw.Draw(img_copy)

        # Применяем функцию для уменьшения шрифта
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 100)
        font = adjust_font_size(font, text, draw_copy, max_width, max_height)

        # Разбиваем текст на строки с учетом максимальной ширины
        wrapped_text = wrap_text(text, font, max_width)

        # Центрируем текст на изображении по обеим осям
        total_text_height = len(wrapped_text) * line_height
        position = ((img_copy.width - max_width) // 2, (img_copy.height - total_text_height) // 2)

        # Добавляем текст с обводкой
        shadow_offset = 5
        for line in wrapped_text:
            bbox = draw_copy.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            line_position = ((img_copy.width - text_width) // 2, position[1])

            # Обводка текста
            for offset in [(shadow_offset, shadow_offset), (-shadow_offset, shadow_offset), 
                           (shadow_offset, -shadow_offset), (-shadow_offset, -shadow_offset)]:
                draw_copy.text((line_position[0] + offset[0], line_position[1] + offset[1]), line, font=font, fill="black")
            
            # Основной текст
            draw_copy.text(line_position, line, font=font, fill="white")  # Белый текст
            position = (position[0], position[1] + line_height)  # Смещаем позицию для следующей строки

        # Генерируем имя файла
        result_filename = f"result{idx + 1}.jpg"
        output_path = os.path.join(output_dir, result_filename)

        # Сохраняем новое изображение как .jpg
        img_copy.convert('RGB').save(output_path, "JPEG")
        print(f"Изображение сохранено как {output_path}")

# Пример использования
text_file_path = "h1.txt"         # Путь к файлу с текстами
output_dir = "output"                # Папка для сохранения результата

add_text_to_image(text_file_path, output_dir)
