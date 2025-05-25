from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
import pandas as pd
import random
import os
import md2excel

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# 配置
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

def get_question_count(max_count):
    try:
        count = int(request.form.get('question_count', 50))
        return min(max(1, count), max_count)
    except:
        return min(50, max_count)

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        total = md2excel.markdown_to_excel(
            app.config['MD_FILE'], 
            app.config['EXCEL_FILE']
        )
    except Exception as e:
        return render_template('error.html', message=f"文件转换失败: {str(e)}")

    if request.method == 'POST':
        session['question_count'] = get_question_count(total)
        return redirect(url_for('start_test'))
    
    return render_template('index.html', 
                         total=total,
                         default=min(50, total))

@app.route('/test', methods=['GET', 'POST'])
def start_test():
    # 用户会话管理
    user_id = session.get('user_id')
    if not user_id or user_id not in user_sessions:
        user_id = os.urandom(16).hex()
        session['user_id'] = user_id
        
        try:
            df = pd.read_excel(app.config['EXCEL_FILE'])
            phrases = df.to_dict('records')
            test_data = random.sample(
                phrases, 
                min(session['question_count'], len(phrases))
                )
        except Exception as e:
            return render_template('error.html', message=f"数据加载失败: {str(e)}")

        user_sessions[user_id] = {
            'test_data': test_data,
            'current': 0,
            'correct': 0,
            'wrong': 0,
            'wrong_list': []
        }
    
    user_data = user_sessions[user_id]

    # 处理答案
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

    # 显示结果
    if user_data['current'] >= len(user_data['test_data']):
        return render_template('result.html',
                            correct=user_data['correct'],
                            wrong=user_data['wrong'],
                            wrong_list=user_data['wrong_list'],
                            total=len(user_data['test_data']))
    
    # 生成新题目
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

    options = [correct] + random.sample(pool, 3)[:3]
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

if __name__ == '__main__':
    if not os.path.exists(app.config['SESSION_FILE_DIR']):
        os.makedirs(app.config['SESSION_FILE_DIR'])
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=True)