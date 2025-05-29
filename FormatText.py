import re
import os

def split_phrases(text):
    """
    将混合的短语文本分割成单独的英文短语和中文翻译对
    改进逻辑：英文短语只包含英文字母、空格和英文标点
    中文翻译以中文字符开始，不包含英文字母
    """
    # 预处理：移除多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    phrases = []
    
    # 当前处理位置
    start = 0
    length = len(text)
    
    while start < length:
        # 查找下一个中文字符位置（中文翻译开始）
        cn_start = -1
        for i in range(start, length):
            if '\u4e00' <= text[i] <= '\u9fff':  # 中文字符范围
                cn_start = i
                break
        
        if cn_start == -1:
            # 没有找到中文字符，剩余部分作为英文短语
            if start < length:
                phrases.append((text[start:], ""))
            break
        
        # 英文短语是从start到cn_start之间的文本（去除尾部空格）
        en_phrase = text[start:cn_start].rstrip()
        
        # 查找英文短语结束位置（下一个英文短语开始）
        next_en_start = -1
        for i in range(cn_start + 1, length):
            # 英文字母或常见英文标点
            if ('a' <= text[i] <= 'z') or ('A' <= text[i] <= 'Z') or text[i] in '([':
                # 确保前面没有中文字符（即不是中文中的标点）
                if i == 0 or not ('\u4e00' <= text[i-1] <= '\u9fff'):
                    next_en_start = i
                    break
        
        if next_en_start == -1:
            # 没有下一个英文短语，剩余部分作为中文翻译
            cn_trans = text[cn_start:]
            phrases.append((en_phrase, cn_trans))
            break
        
        # 中文翻译是从cn_start到next_en_start之间的文本
        cn_trans = text[cn_start:next_en_start].rstrip()
        phrases.append((en_phrase, cn_trans))
        
        # 移动到下一个短语
        start = next_en_start
    
    return phrases

def main():
    with open('text.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    output_lines = []
    current_day = None
    current_block = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 检测天数行（如【73】）
        day_match = re.match(r'^【(\d+)】$', line)
        if day_match:
            # 处理上一个区块
            if current_day is not None and current_block:
                block_text = ' '.join(current_block)
                phrases = split_phrases(block_text)
                output_lines.append(f"## Day{current_day}({len(phrases)})")
                for en, cn in phrases:
                    output_lines.append(f"- {en} : {cn}")
            
            # 开始新区块
            current_day = day_match.group(1)
            current_block = []
        else:
            current_block.append(line)
    
    # 处理最后一个区块
    if current_day is not None and current_block:
        block_text = ' '.join(current_block)
        phrases = split_phrases(block_text)
        output_lines.append(f"## Day{current_day}({len(phrases)})")
        for en, cn in phrases:
            output_lines.append(f"- {en} : {cn}")
    
    # 写入输出文件
    with open('FormatText.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print("格式化完成！输出文件: FormatText.txt")

if __name__ == "__main__":
    main()