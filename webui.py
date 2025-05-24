# 文件结构：
# ├── app.py
# ├── templates/
# │   └── index.html
# └── output.xlsx

# app.py
from flask import Flask, render_template, request, session
import pandas as pd
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 设置一个安全的密钥

# 加载数据
df = pd.read_excel('English Phrase.xlsx')
phrases = df[['英文短语', '中文翻译']].to_dict('records')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # 初始化测试
        session.clear()
        session['test_data'] = random.sample(phrases, min(50, len(phrases)))
        session['current_question'] = 0
        session['correct'] = 0
        session['wrong'] = 0
        session['wrong_list'] = []
        return render_template('index.html', 
                             question=get_current_question(),
                             total=len(session['test_data']))

    elif request.method == 'POST':
        # 处理答案
        user_choice = request.form.get('answer')
        current = session['current_question']
        question_data = session['test_data'][current]
        correct_index = session.get(f'correct_index_{current}')

        # 验证答案
        if user_choice == str(correct_index):
            session['correct'] += 1
        else:
            session['wrong'] += 1
            session['wrong_list'].append({
                'question': session.get(f'question_{current}'),
                'correct_answer': question_data['correct_answer'],
                'user_choice': question_data['options'][int(user_choice)-1],
                'options': question_data['options']
            })

        # 进入下一题
        session['current_question'] += 1
        if session['current_question'] >= len(session['test_data']):
            return show_result()
        
        return render_template('index.html',
                             question=get_current_question(),
                             total=len(session['test_data']))

def get_current_question():
    current = session['current_question']
    item = session['test_data'][current]
    
    # 生成题目
    is_english = random.choice([True, False])
    if is_english:
        question = item['英文短语']
        correct_answer = item['中文翻译']
        answer_pool = [p['中文翻译'] for p in phrases if p['中文翻译'] != correct_answer]
    else:
        question = item['中文翻译']
        correct_answer = item['英文短语']
        answer_pool = [p['英文短语'] for p in phrases if p['英文短语'] != correct_answer]
    
    # 生成选项
    try:
        wrong_answers = random.sample(answer_pool, 3)
    except ValueError:
        wrong_answers = answer_pool * 3
    
    options = [correct_answer] + wrong_answers[:3]
    random.shuffle(options)
    correct_index = options.index(correct_answer) + 1
    
    # 保存状态
    session[f'question_{current}'] = question
    session[f'correct_index_{current}'] = correct_index
    session['test_data'][current].update({
        'options': options,
        'correct_answer': correct_answer
    })
    
    return {
        'text': question,
        'options': options,
        'number': current + 1,
        'total': len(session['test_data'])
    }

def show_result():
    return render_template('result.html',
                         correct=session['correct'],
                         wrong=session['wrong'],
                         wrong_list=session['wrong_list'])

if __name__ == '__main__':
    app.run(debug=True)