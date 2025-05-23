import pandas as pd

def markdown_to_excel(md_file, excel_file):
    # 初始化变量
    current_book = ""
    current_day = ""
    data = []

    # 读取Markdown文件
    with open(md_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # 解析书本名称
            if line.startswith('# '):
                current_book = line[2:].strip()
                current_day = ""  # 遇到新书时重置学习日
            # 解析学习日
            elif line.startswith('## '):
                current_day = line[3:].strip()
            # 解析短语条目
            elif line.startswith('- '):
                if not current_book or not current_day:
                    continue
                
                # 分割中英文
                entry = line[2:].split(':', 1)
                if len(entry) != 2:
                    continue
                
                english = entry[0].strip()
                chinese = entry[1].strip()
                
                data.append({
                    "英文短语": english,
                    "中文翻译": chinese,
                    "学习日": current_day,
                    "书本名称": current_book
                })

    # 创建DataFrame并保存Excel
    df = pd.DataFrame(data)
    df = df[['英文短语', '中文翻译', '学习日', '书本名称']]  # 调整列顺序
    df.to_excel(excel_file, index=False, engine='openpyxl')

# 使用示例
markdown_to_excel('English Phrase.md', 'English Phrase.xlsx')