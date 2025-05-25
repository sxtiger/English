from flask import Flask, render_template, request, session
from flask_session import Session
import pandas as pd
import random
import os

# 初始化Flask应用
app = Flask(__name__)
app.secret_key = os.urandom(24).hex()  # 生成随机密钥

# 配置服务器端Session
app.config.update(
    SESSION_TYPE='filesystem',
    SESSION_FILE_DIR='./flask_sessions',
    SESSION_COOKIE_NAME='lang_test',
    PERMANENT_SESSION_LIFETIME=1800  # 30分钟有效期
)
Session(app)

# 全局数据
df = pd.read_excel('English Phrase.xlsx')
phrases = df[['英文短语', '中文翻译']].to_dict('records')
user_sessions = {}

def initialize_test_data():
    """ 生成测试题目和选项 """
    test_data = []
    for phrase in random.sample(phrases, min(50, len(phrases))):
        # 随机决定题目类型（英译中/中译英）
        is_english = random.choice([True, False])
        
        # 生成题目
        if is_english:
            question = phrase['英文短语']
            correct_answer = phrase['中文翻译']
            answer_pool = [p['中文翻译'] for p in phrases if p['中文翻译'] != correct_answer]
        else:
            question = phrase['中文翻译']
            correct_answer = phrase['英文短语']
            answer_pool = [p['英文短语'] for p in phrases if p['英文短语'] != correct_answer]
        
        # 生成选项
        try:
            wrong_answers = random.sample(answer_pool, 3)
        except ValueError:
            wrong_answers = answer_pool * 3
        
        options = [correct_answer] + wrong_answers[:3]
        random.shuffle(options)
        correct_index = options.index(correct_answer) + 1
        
        test_data.append({
            'display': question,
            'options': options,
            'correct_index': correct_index,
            'correct_answer': correct_answer
        })
    return test_data

@app.route('/', methods=['GET', 'POST'])
def index():
    # 获取或创建用户会话
    user_id = session.get('user_id')
    if not user_id or user_id not in user_sessions:
        user_id = os.urandom(16).hex()  # 生成唯一用户ID
        session['user_id'] = user_id
        user_sessions[user_id] = {
            'test_data': initialize_test_data(),
            'current': 0,
            'correct': 0,
            'wrong': 0,
            'wrong_list': []
        }
    
    user_data = user_sessions[user_id]
    
    # 处理答案提交
    if request.method == 'POST':
        process_answer(user_data)
    
    # 显示结果或下一题
    if user_data['current'] >= len(user_data['test_data']):
        return show_result(user_data)
    return show_question(user_data)

def process_answer(user_data):
    """ 处理用户答案 """
    current = user_data['current']
    question = user_data['test_data'][current]
    user_choice = request.form.get('answer', '-1')
    
    if user_choice == str(question['correct_index']):
        user_data['correct'] += 1
    else:
        user_data['wrong'] += 1
        user_data['wrong_list'].append({
            'question': question['display'],
            'correct': question['correct_answer'],
            'selected': question['options'][int(user_choice)-1] if user_choice.isdigit() else '无效选择',
            'options': question['options']  # 确保包含选项列表
        })
    
    user_data['current'] += 1

def show_question(user_data):
    """ 显示题目页面 """
    current = user_data['current']
    question = user_data['test_data'][current]
    return render_template('index.html',
                         question=question['display'],
                         options=question['options'],
                         progress=current+1,
                         total=len(user_data['test_data']))

def show_result(user_data):
    """ 显示结果页面 """
    return render_template('result.html',
                         correct=user_data['correct'],
                         wrong=user_data['wrong'],
                         wrong_list=user_data['wrong_list'],
                         total=len(user_data['test_data']))

if __name__ == '__main__':
    # 创建session存储目录
    if not os.path.exists(app.config['SESSION_FILE_DIR']):
        os.makedirs(app.config['SESSION_FILE_DIR'])
    app.run(host='0.0.0.0', port=50000, debug=True)