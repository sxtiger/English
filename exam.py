import pandas as pd
import random

def generate_test(excel_file, num_questions=50):
    df = pd.read_excel(excel_file)
    phrases = df[['英文短语', '中文翻译']].to_dict('records')
    
    test_data = random.sample(phrases, min(num_questions, len(phrases)))
    
    correct = 0
    wrong = 0
    wrong_list = []
    
    for i, item in enumerate(test_data, 1):
        is_english_question = random.choice([True, False])
        
        if is_english_question:
            question = item['英文短语']
            correct_answer = item['中文翻译']
            answer_pool = [row['中文翻译'] for row in phrases if row['中文翻译'] != correct_answer]
        else:
            question = item['中文翻译']
            correct_answer = item['英文短语']
            answer_pool = [row['英文短语'] for row in phrases if row['英文短语'] != correct_answer]
        
        try:
            wrong_answers = random.sample(answer_pool, 3)
        except ValueError:
            wrong_answers = answer_pool * 3
        
        options = [correct_answer] + wrong_answers[:3]
        random.shuffle(options)
        correct_index = options.index(correct_answer) + 1
        
        # 修改后的显示部分
        print(f"\n题目 {i}/{len(test_data)}")
        print(f"问：{question}")
        for idx, opt in enumerate(options, 1):
            print(f"{idx}. {opt}")
        
        while True:
            try:
                user_choice = int(input("请输入答案编号（1-4）："))
                if 1 <= user_choice <= 4:
                    break
            except:
                pass
            print("请输入有效的数字（1-4）")
        
        if user_choice == correct_index:
            correct += 1
        else:
            wrong += 1
            wrong_list.append({
                '题目': question,
                '正确答案': correct_answer,
                '你的选择': options[user_choice-1],
                '选项': options
            })
    
    # 修改后的结果展示
    print("\n\n=== 测试完成！ ===")
    print(f"正确：{correct}题")
    print(f"错误：{wrong}题")
    
    if wrong > 0:
        print("\n=== 错题解析 ===")
        for error in wrong_list:
            print(f"\n题目：{error['题目']}")
            print(f"正确答案：{error['正确答案']}")
            print(f"你的选择：{error['你的选择']}")
            print("所有选项：")
            for idx, opt in enumerate(error['选项'], 1):
                print(f"{idx}. {opt}")

# 使用示例
generate_test('English Phrase.xlsx')