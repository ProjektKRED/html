import re
import os

def process_table_logic(content, filename_no_ext, h1_title):
    # ПРЕДОБРАБОТКА
    content = content.replace('\xa0', ' ')
    content = content.replace('\\|', '|')
    content = re.sub(r'<[Bb][Rr]\s*/?>', '\n', content)
    content = re.sub(r'\n\s*\n', '\n', content) 

    # 1. Функция таблиц
    def parse_to_aligned_table(match):
        table_block = match.group(0)
        rows = [r.strip() for r in table_block.strip().split('\n') if r.strip()]
        table_data = []
        for row in rows:
            if re.match(r'^\s*\|?[\s\-\:\|]+\|?\s*$', row): continue
            cells = [c.strip().replace('**', '') for c in row.split('|')]
            if cells and cells[0] == '': cells.pop(0)
            if cells and cells[-1] == '': cells.pop()
            if cells: table_data.append(cells)
        if not table_data: return ""
        num_columns = max(len(row) for row in table_data)
        col_widths = [0] * num_columns
        icons = ['✅', '❌', '⚠️', '❓', '⚡', '✨']
        for row in table_data:
            for i, cell in enumerate(row):
                if i < num_columns:
                    v_len = len(cell)
                    for icon in icons: v_len += cell.count(icon)
                    if v_len > col_widths[i]: col_widths[i] = v_len
        aligned = []
        for row in table_data:
            line = ""
            for i, cell in enumerate(row):
                v_len = len(cell)
                for icon in icons: v_len += cell.count(icon)
                line += cell + (" " * (col_widths[i] - v_len + 4))
            aligned.append(line.rstrip())
        return f"<pre>{'\\n'.join(aligned)}</pre>".replace('\\n', '\n')

    content = re.sub(r'((?:^.*\|.*(?:\n|$))+)', parse_to_aligned_table, content, flags=re.MULTILINE)
    content = re.sub(r'\[a=(.*?)\](.*?)\[/a\]', r'<a href="\1" class="custom-link">\2</a>', content)

    # ПОИСК ИЗОБРАЖЕНИЯ
    img_tag = ""
    img_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.JPG', '.PNG']
    for ext in img_extensions:
        img_path = os.path.join('image', filename_no_ext + ext)
        if os.path.exists(img_path):
            img_tag = f'<img src="../image/{filename_no_ext}{ext}" class="post-image" alt="Post Image">'
            break

    # HTML Оболочка
    html_start = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{h1_title}</title>
    <style>
        body {{ font-family: -apple-system, system-ui, sans-serif; line-height: 1.5; color: #333; max-width: 800px; margin: 40px auto; padding: 20px; }}
        h1 {{ font-size: 1.8em; font-weight: bold; margin: 0 0 10px 0; border-bottom: 2px solid #eee; padding-bottom: 5px; }}
        .copy-panel {{ margin-bottom: 20px; }}
        .btn-copy {{ background: #007bff; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 15px; }}
        .btn-copy.success {{ background: #28a745; }}
        .post-image {{ max-width: 100%; height: auto; border-radius: 10px; margin-bottom: 25px; display: block; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        p {{ margin: 5px 0; }}
        .cta {{ background: #f0f7ff; border-left: 5px solid #007bff; padding: 12px; margin: 10px 0; font-weight: bold; display: block; }}
        blockquote {{ background: #f9f9f9; border-left: 4px solid #00b894; margin: 15px 0; padding: 10px 20px; font-style: italic; border-radius: 0 8px 8px 0; }}
        pre {{ background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 8px; font-family: "Consolas", monospace; font-size: 13px; line-height: 1.4; white-space: pre; overflow-x: auto; margin: 15px 0; }}
        ul, ol {{ margin: 10px 0 15px 30px; }}
        li {{ margin-bottom: 4px; }}
        strong {{ font-weight: 600; }}
    </style>
</head>
<body>"""

    copy_script = """
    <script>
    function copyText() {{
        const el = document.getElementById("content-to-copy");
        const range = document.createRange();
        range.selectNode(el);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
        document.execCommand("copy");
        window.getSelection().removeAllRanges();
        const btn = document.querySelector('.btn-copy');
        btn.textContent = '✅ Текст скопирован!';
        btn.classList.add('success');
        setTimeout(() => {{ btn.textContent = '📋 Копировать для Tenchat'; btn.classList.remove('success'); }}, 2000);
    }}
    </script>"""

    lines = [l for l in content.split('\n') if l.strip() or '<pre>' in l or '</pre>' in l]
    body_content = ["<div id='content-to-copy'>"]
    current_list_type = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('H1 —') or re.match(r'^#\s', stripped): continue
        
        if '<pre>' in line or '</pre>' in line:
            if current_list_type: body_content.append(f"</{current_list_type}>"); current_list_type = None
            body_content.append(line)
            continue
        
        is_list = stripped.startswith('* ') or stripped.startswith('- ') or re.match(r'^\d+[\.\)]\s', stripped)
        if is_list:
            new_type = 'ul' if (stripped.startswith('* ') or stripped.startswith('- ')) else 'ol'
            if current_list_type != new_type:
                if current_list_type: body_content.append(f"</{current_list_type}>")
                body_content.append(f"<{new_type}>")
                current_list_type = new_type
            txt = re.sub(r'^(\*|-|\d+[\.\)])\s+', '', stripped)
            txt = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', txt)
            body_content.append(f"<li>{txt}</li>")
        else:
            if current_list_type: body_content.append(f"</{current_list_type}>"); current_list_type = None
            if re.match(r'^#{2,}\s', stripped): body_content.append(f"<p><strong>{re.sub(r'^#+\s*', '', stripped)}</strong></p>")
            elif stripped.startswith('>'): body_content.append(f"<blockquote>{stripped.lstrip('>').strip().replace('*', '')}</blockquote>")
            elif '⚡' in stripped: body_content.append(f'<span class="cta">{stripped}</span>')
            else: body_content.append(f"<p>{re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', stripped)}</p>")

    if current_list_type: body_content.append(f"</{current_list_type}>")
    body_content.append("</div>")
    
    return html_start + f"<h1>{h1_title}</h1>" + \
           "<div class='copy-panel'><button class='btn-copy' onclick='copyText()'>📋 Копировать для Tenchat</button></div>" + \
           img_tag + "\n".join(body_content) + copy_script + "</body></html>"

def natural_sort_key(s):
    """ Вспомогательная функция для сортировки файлов (1, 2, 10 вместо 1, 10, 2) """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def run_batch_processing():
    for d in ['input', 'output', 'image']:
        if not os.path.exists(d): os.makedirs(d)

    # Читаем заголовки из h1.txt
    h1_titles = []
    if os.path.exists('h1.txt'):
        with open('h1.txt', 'r', encoding='utf-8') as f:
            h1_titles = [line.strip() for line in f.readlines() if line.strip()]

    # Получаем список файлов и сортируем их ЧЕЛОВЕЧЕСКИМ способом
    files = [f for f in os.listdir('input') if f.endswith('.txt')]
    files.sort(key=natural_sort_key)
    
    if len(h1_titles) < len(files):
        print(f"⚠️ Внимание: в h1.txt заголовков меньше ({len(h1_titles)}), чем файлов ({len(files)})!")

    for index, filename in enumerate(files):
        name_no_ext = os.path.splitext(filename)[0]
        # Берем заголовок по индексу. Теперь индексы совпадают.
        current_h1 = h1_titles[index] if index < len(h1_titles) else f"Заголовок не найден (файл {index+1})"
        
        try:
            try:
                with open(os.path.join('input', filename), 'r', encoding='utf-8') as f:
                    text = f.read()
            except:
                with open(os.path.join('input', filename), 'r', encoding='cp1251') as f:
                    text = f.read()
            
            html_result = process_table_logic(text, name_no_ext, current_h1)
            with open(os.path.join('output', name_no_ext + '.html'), 'w', encoding='utf-8') as f:
                f.write(html_result)
            print(f"✅ Готово: {filename} -> заголовок: {current_h1}")
        except Exception as e:
            print(f"❌ Ошибка в {filename}: {e}")

if __name__ == "__main__":
    run_batch_processing()