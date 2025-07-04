# About English Study
something about study English

# Update
## 2025-05-28: （临时）开放外网端口
- 端口冲突，修改为50001
- 临时为学习需要，开放外网端口
- 配置了SSL证书
- 用https://127.0.0.1:50001访问（外网：https://域名:50001)
## 2025-05-27: 增加错题记录
- 修改exam_webui.py、index.htm文件
- 对答错的题目记录到excel文件中
- 在测试时可选择正常测试、或错误测试
## 2025-05-26: 修复测试题小于4个时的错误
- 修改exam_webui.py
- 增加error.html模板
-  目前核心文件架构：  
	```
	├── exam_webui.py  #网页测试文件  
	├── md2excel.py    #takedown文件内容转换为Excel文件  
	├── templates/     #网页模板  
	│   ├── index.html  
	│   ├── test.html  
	│   ├── error.html  
	│   └── result.html  
	├── requirements.txt  #依赖  
	├── English Phrase.md  #makedown文件  
	└── English Phrase.xlsx  #Excel文件  

## 2025-05-25: exam_webui.py、templates、requirements.txt
- exam_webui.py修改：
	- 增加功能：在测试前先将English Phrase.md转换一次成English Phrase.xlsx，以保持数据最新；
	- 增加功能：测试时先读取数据总条数，然后让测试者输入想测试的随机题目数量，默认为50题；
- templates目录：
	- 从原index.html、result.html2个文件改为3个文件：index.html、test.html、reault.html
	- 原index.html=test.html
- requirements.txt:
	- 需要的依赖，`pip install -r requirements.txt`
- 目前核心文件架构：  
	```
	├── exam_webui.py  #网页测试文件  
	├── md2excel.py    #takedown文件内容转换为Excel文件  
	├── templates/     #网页模板  
	│   ├── index.html  
	│   ├── test.html  
	│   └── result.html  
	├── requirements.txt  #依赖  
	├── English Phrase.md  #makedown文件  
	└── English Phrase.xlsx  #Excel文件  
	```
## 2025-05-25: 更改webui.py、增加维护maintenance.sh
- 由于sessions大小限制导致出错，更改了主程序代码，网页端口号更改为50000，即`http://127.0.0.1:50000`
- webUI.py更名为exam_webui.py，以利功能扩展
- maintenance.sh
	- 运行exam_webui.py会增加flask_sessions目录下文件，运行后删除过期的临时文件
	- 备份主xlsx文件
	- 记录维护日志
## 2025-05-24: webui.py
- 功能：增加网页版测试（其他与exam.py相同）
-  安装依赖：`pip install flask pandas openpyxl`
- `templates`目录:存放网页模板
- 运行应用：`python app.py`
- 打开浏览器访问：`http://127.0.0.1:5000`
## 2025-05-23: exam.py
- 功能：调用English Phrase.xlsx内容，自动生成50题测试选择题（中英文双向），测试结束后显示正确与错误题数，并列出错误答题
## 2025-05-23: md2excel.py
- 功能：将makedown文件English Phrase.md内容转换为Excel表格English Phrase.xlsx，方便学习使用
- 需要安装依赖库：`pip install pandas openpyxl`
## 2025-05-22: 基本makedown文件
- English phrase.md
