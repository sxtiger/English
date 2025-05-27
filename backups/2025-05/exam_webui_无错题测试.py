from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
import pandas as pd
import random
import os
import md2excel

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# 应用配置
app.config.update(
    SESSION_TYPE='filesystem',
    SESSION_FILE_DIR='./flask_sessions',
    SESSION_COOKIE_NAME='lang_test',
    PERMANENT_SESSION_LIFETIME=1800,
    MD_FILE='English Phrase.md',
    EXCEL_FILE='English Phrase.xlsx',
    PORT=50000
)
Session(app)

user_sessions = {}

def generate_options(correct, pool):
    """ 生成包含3个错误答案的选项列表 """
    unique_pool = list({v: None for v in pool})  # 去重
    
    # 生成错误答案
    wrong_answers = []
    try:
        wrong_answers = random.sample(unique_pool, 3)
    except ValueError:
        while len(wrong_answers) < 3:
            need = 3 - len(wrong_answers)
            if len(unique_pool) == 0:
                wrong_answers += ["选项不足"] * need
            else:
                wrong_answers += random.choices(unique_pool, k=need)
    
    # 最终处理
    options = [correct] + wrong_answers[:3]
    return list({v: None for v in options})[:4]  # 确保唯一性

def get_question_count(max_count):
    try:
        count = int(request.form.get('question_count', 50))
        return min(max(1, count), max_count)
    except:
        return min(50, max_count)

@app.route('/')
def index():
    try:
        total = md2excel.markdown_to_excel(
            app.config['MD_FILE'],
            app.config['EXCEL_FILE']
        )
    except Exception as e:
        return render_template('error.html', message=f"文件转换失败: {str(e)}")
    
    session.clear()
    return render_template('index.html',
                         total=total,
                         default=min(50, total))

@app.route('/start', methods=['POST'])
def start_test():
    try:
        df = pd.read_excel(app.config['EXCEL_FILE'])
        total = len(df)
        question_count = get_question_count(total)
        
        if question_count < 1:
            raise ValueError("测试题数量不能小于1")
            
        phrases = df.to_dict('records')
        if question_count >= total:
            test_data = phrases
        else:
            test_data = random.sample(phrases, question_count)
        
        if len(test_data) < 1:
            raise ValueError("没有可用的测试数据")
        
        session['question_count'] = question_count
        session['user_id'] = os.urandom(16).hex()
        
        user_sessions[session['user_id']] = {
            'test_data': test_data,
            'current': 0,
            'correct': 0,
            'wrong': 0,
            'wrong_list': []
        }
        return redirect(url_for('show_question'))
    
    except Exception as e:
        return render_template('error.html', message=f"初始化失败: {str(e)}")

@app.route('/test', methods=['GET', 'POST'])
def show_question():
    user_id = session.get('user_id')
    if not user_id or user_id not in user_sessions:
        return redirect(url_for('index'))
    
    user_data = user_sessions[user_id]
    
    if request.method == 'POST':
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
                'options': question['options']
            })
        user_data['current'] += 1
    
    if user_data['current'] >= len(user_data['test_data']):
        return redirect(url_for('show_result'))
    
    current = user_data['current']
    item = user_data['test_data'][current]
    is_english = random.choice([True, False])
    
    if is_english:
        question = item['英文短语']
        correct = item['中文翻译']
        pool = [p['中文翻译'] for p in user_data['test_data'] if p['中文翻译'] != correct]
    else:
        question = item['中文翻译']
        correct = item['英文短语']
        pool = [p['英文短语'] for p in user_data['test_data'] if p['英文短语'] != correct]
    
    options = generate_options(correct, pool)
    random.shuffle(options)
    
    item.update({
        'display': question,
        'options': options,
        'correct_index': options.index(correct) + 1,
        'correct_answer': correct
    })
    
    return render_template('test.html',
                         question=question,
                         options=options,
                         progress=current+1,
                         total=len(user_data['test_data']))

@app.route('/result')
def show_result():
    user_id = session.get('user_id')
    if not user_id or user_id not in user_sessions:
        return redirect(url_for('index'))
    
    user_data = user_sessions[user_id]
    return render_template('result.html',
                         correct=user_data['correct'],
                         wrong=user_data['wrong'],
                         wrong_list=user_data['wrong_list'],
                         total=len(user_data['test_data']))

@app.route('/reset')
def reset_test():
    user_id = session.get('user_id')
    if user_id and user_id in user_sessions:
        del user_sessions[user_id]
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(app.config['SESSION_FILE_DIR']):
        os.makedirs(app.config['SESSION_FILE_DIR'])
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=True)