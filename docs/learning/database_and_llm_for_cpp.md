# 数据库与 LLM 入门：从 C++ 算法视角理解

这份笔记默认你的基础是 C++ 算法代码：变量、数组、结构体、vector、map、函数、复杂度、文件读写能理解；数据库和大模型应用基本没接触过。

先给总类比：

```text
数据库
= 程序外部的持久化数据结构
= 程序重启后还在的 vector/map/table

LLM API
= 一个远程 solve() 函数
= 你把 prompt 当输入发过去，它把回答当输出返回
```

## 1. 为什么需要数据库

如果没有数据库，后端程序里的数据通常只存在内存里。

C++ 类比：

```cpp
vector<Record> records;
records.push_back(new_record);
```

只要程序一退出：

```text
records 没了
```

后端也是一样。

如果用户调用了：

```text
POST /resume/analyze
```

我们在内存里算出结果后，如果不保存，那么下一次程序重启，历史记录就没了。

数据库解决的是：

```text
数据持久化
```

也就是：

```text
程序关了，数据还在。
程序下次启动，还能查回来。
```

## 2. 数据库像什么

你可以把数据库先理解成：

```text
很多张表 table
每张表像 vector<struct>
每一行 row 像一个 struct 实例
每一列 column 像 struct 的字段
```

比如我们项目里有一张表：

```text
analysis_records
```

它大概等价于 C++：

```cpp
struct AnalysisRecord {
    int id;
    string target_role;
    string resume_text;
    string job_description;
    int match_score;
    string matched_keywords;
    string missing_keywords;
    string strengths;
    string suggestions;
    string interview_questions;
    string analysis_mode;
    string created_at;
};

vector<AnalysisRecord> analysis_records;
```

区别是：

```text
vector 在内存里，程序退出就没。
数据库表在磁盘里，程序退出还在。
```

## 3. SQLite 是什么

SQLite 是一种很轻量的数据库。

它的特点：

```text
不需要单独安装数据库服务器
数据存在一个 .db 文件里
Python 自带 sqlite3 可以直接操作
适合 demo、小工具、学习项目
```

我们项目里：

```text
ai_resume_backend/data/analysis.db
```

就是 SQLite 数据库文件。

它有点像：

```text
一个更强的二进制数据文件
```

但它支持 SQL 查询。

## 4. MySQL 和 SQLite 的区别

SQLite：

```text
一个文件就是数据库
适合本地 demo、小项目、移动端、小工具
```

MySQL：

```text
一个单独运行的数据库服务
需要连接 host、port、username、password
适合多人、多服务、生产环境
```

C++ 类比：

```text
SQLite 像你本地读写一个文件
MySQL 像你通过网络访问一个专门管理数据的服务进程
```

实习简历里写 SQLite 可以，但如果岗位要求 MySQL，你可以说：

```text
项目当前使用 SQLite 完成持久化 demo，表结构和 SQL 操作可迁移到 MySQL。
```

这样诚实而且合理。

## 5. SQL 是什么

SQL 是操作关系型数据库的语言。

它不是 Python，也不是 C++。

它专门用来：

```text
建表
插入数据
查询数据
更新数据
删除数据
```

常见操作：

```sql
CREATE TABLE ...
INSERT INTO ...
SELECT ...
UPDATE ...
DELETE ...
```

## 6. 建表是什么

我们项目里建表：

```sql
CREATE TABLE IF NOT EXISTS analysis_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_role TEXT NOT NULL,
    resume_text TEXT NOT NULL,
    job_description TEXT NOT NULL,
    match_score INTEGER NOT NULL,
    matched_keywords TEXT NOT NULL,
    missing_keywords TEXT NOT NULL,
    strengths TEXT NOT NULL,
    suggestions TEXT NOT NULL,
    interview_questions TEXT NOT NULL,
    analysis_mode TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
```

这相当于定义一个结构体：

```cpp
struct AnalysisRecord {
    int id;                  // 主键，自增
    string target_role;
    string resume_text;
    string job_description;
    int match_score;
    string matched_keywords;
    string missing_keywords;
    string strengths;
    string suggestions;
    string interview_questions;
    string analysis_mode;
    string created_at;
};
```

重要字段解释：

```text
id
  每条记录的唯一编号，类似数组下标，但更稳定。

PRIMARY KEY
  主键，表示这列可以唯一标识一行。

AUTOINCREMENT
  自动递增，插入第一条是 1，第二条是 2。

TEXT
  字符串。

INTEGER
  整数。

NOT NULL
  不能为空。

DEFAULT CURRENT_TIMESTAMP
  如果不传创建时间，数据库自动填当前时间。
```

## 7. 插入数据是什么

我们项目里每次分析后会保存：

```sql
INSERT INTO analysis_records (...)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
```

C++ 类比：

```cpp
analysis_records.push_back(record);
```

区别是：

```text
push_back 存到内存 vector
INSERT 存到数据库文件
```

这里的 `?` 是占位符。

为什么不用字符串拼接？

不要这样：

```python
sql = "INSERT INTO table VALUES (" + user_input + ")"
```

因为用户输入可能包含恶意 SQL，导致 SQL 注入。

用 `?`：

```python
conn.execute("INSERT INTO table VALUES (?)", (user_input,))
```

数据库会把它当普通数据处理，更安全。

## 8. 查询数据是什么

查询历史：

```sql
SELECT id, target_role, match_score, matched_keywords, missing_keywords, created_at
FROM analysis_records
ORDER BY id DESC
LIMIT ?
```

意思是：

```text
从 analysis_records 表里取部分字段
按 id 从大到小排序
最多取 limit 条
```

C++ 类比：

```cpp
vector<AnalysisRecord> ans;
for (int i = records.size() - 1; i >= 0 && ans.size() < limit; --i) {
    ans.push_back(records[i]);
}
```

查询单条：

```sql
SELECT *
FROM analysis_records
WHERE id = ?
```

意思是：

```text
查 id 等于某个值的那一行。
```

C++ 类比：

```cpp
for (auto &record : records) {
    if (record.id == id) return record;
}
```

## 9. 为什么 list 要存成 JSON 字符串

SQLite 的列类型比较简单。

我们的响应里有：

```python
matched_keywords: list[str]
suggestions: list[str]
```

数据库里不直接存 Python 的 list。

所以我们做：

```python
json.dumps(response.matched_keywords, ensure_ascii=False)
```

把 list 转成 JSON 字符串：

```json
["python", "fastapi", "prompt"]
```

存进数据库时是 TEXT。

取出来时：

```python
json.loads(row["matched_keywords"])
```

再转回 Python list。

C++ 类比：

```text
vector<string>
  -> 序列化成字符串
  -> 写入文件/数据库
  -> 读出来
  -> 反序列化成 vector<string>
```

## 10. 我们项目的数据库代码怎么走

文件：

```text
app/storage.py
```

主要函数：

```text
init_db()
  创建数据库表

save_analysis(request, response)
  保存一次分析结果

list_analysis_records(limit)
  查询历史列表

get_analysis_record(record_id)
  查询某条记录详情
```

启动时：

```python
init_db()
```

每次分析：

```python
response = analyze_resume(request)
response.record_id = save_analysis(request, response)
return response
```

所以现在调用一次：

```text
POST /resume/analyze
```

不仅会返回分析结果，还会写入 SQLite。

## 11. 数据库在后端项目里的位置

完整链路：

```text
客户端
  POST /resume/analyze
    |
FastAPI main.py
    |
Pydantic schemas.py
    |
service.py 分析
    |
storage.py 写 SQLite
    |
返回 JSON
```

你可以记：

```text
service.py 管计算
storage.py 管存取
```

## 12. LLM 是什么

LLM 是 Large Language Model，大语言模型。

比如 GPT、GLM、Qwen、LLaMA。

你可以先把它理解成：

```text
一个很强但不稳定的文本处理函数
```

C++ 类比：

```cpp
string answer = llm_solve(prompt);
```

区别是：

```text
这个函数不在你本地代码里
它在远程服务器上
你通过 HTTP API 调用它
它返回自然语言或 JSON 文本
```

## 13. LLM API 是什么

LLM API 就是大模型服务暴露出来的网络接口。

你向它发 HTTP 请求：

```text
POST https://api.xxx.com/v1/chat/completions
```

请求体里放：

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "你是严谨的简历顾问"},
    {"role": "user", "content": "请分析这份简历..."}
  ],
  "temperature": 0.2
}
```

它返回：

```json
{
  "choices": [
    {
      "message": {
        "content": "模型回答..."
      }
    }
  ]
}
```

这就是：

```text
你把 prompt 发给远程模型
模型把回答返回给你
```

## 14. messages 是什么

LLM 对话通常不是只发一个字符串，而是发一个消息数组。

```json
[
  {"role": "system", "content": "你是严谨的中文技术简历顾问，只返回 JSON。"},
  {"role": "user", "content": "请分析这份简历..."}
]
```

常见 role：

```text
system
  给模型设定规则和身份。

user
  用户提出的问题。

assistant
  模型之前的回答，做多轮对话时会用。
```

C++ 类比：

```cpp
struct Message {
    string role;
    string content;
};

vector<Message> messages;
```

## 15. Prompt 是什么

Prompt 就是你给模型的输入指令。

普通 prompt：

```text
帮我分析简历。
```

工程化 prompt：

```text
请分析这份简历和目标岗位的匹配度，必须只返回 JSON。
JSON 格式如下：
{
  "match_score": 0 到 100 的整数,
  "matched_keywords": [],
  "missing_keywords": [],
  "strengths": [],
  "suggestions": [],
  "interview_questions": []
}
```

为什么要这么写？

因为后端程序不喜欢自然语言散文，它需要稳定结构。

你希望模型返回：

```json
{
  "match_score": 75,
  "suggestions": ["补充 FastAPI 项目"]
}
```

而不是：

```text
我觉得你还不错，不过可以继续努力……
```

## 16. 结构化输出是什么

结构化输出就是让模型按固定格式返回。

本项目希望模型返回：

```json
{
  "match_score": 0,
  "matched_keywords": [],
  "missing_keywords": [],
  "strengths": [],
  "suggestions": [],
  "interview_questions": []
}
```

然后后端可以：

```python
parsed = json.loads(content)
```

把它变成 Python dict。

C++ 类比：

```text
模型返回一段文本
-> JSON parser 解析
-> 得到类似 struct 的数据
```

## 17. temperature 是什么

`temperature` 可以理解成“随机程度”。

```text
temperature 低
  回答更稳定，更保守，更适合后端结构化输出。

temperature 高
  回答更发散，更有创造性，但格式更容易飘。
```

做简历分析、JSON 输出这种任务，通常设置低一点：

```json
"temperature": 0.2
```

## 18. API Key 是什么

API Key 是访问大模型服务的凭证。

类似：

```text
密码 / token / 身份令牌
```

请求头里：

```text
Authorization: Bearer 你的_API_KEY
```

意思是：

```text
我有凭证，请允许我调用模型。
```

不要把 API Key 写死在代码里。

为什么？

```text
代码可能上传 GitHub
别人拿到 key 就能花你的钱
```

所以我们用环境变量：

```powershell
$env:LLM_API_KEY="你的 API Key"
```

代码里读取：

```python
os.getenv("LLM_API_KEY")
```

## 19. 环境变量是什么

环境变量是操作系统给程序的一组配置。

你可以理解成：

```text
程序启动时能读取到的全局 key-value 配置
```

比如：

```text
LLM_API_KEY=xxx
LLM_MODEL=gpt-4o-mini
```

为什么不用写进代码？

因为：

```text
不同机器、不同环境、不同账号配置不同。
密钥不应该进代码仓库。
```

## 20. 我们项目里的 LLM 调用骨架

在 `service.py`：

```python
if request.use_llm and os.getenv("LLM_API_KEY"):
    llm_response = analyze_resume_with_llm(request)
    if llm_response is not None:
        return llm_response
```

意思是：

```text
如果用户要求用 LLM，并且环境里配置了 API Key
  就尝试调用大模型
如果成功
  返回 LLM 结果
否则
  继续走本地规则分析
```

这样设计的好处：

```text
没有 API Key 时项目也能演示。
有 API Key 时可以展示真实大模型调用。
模型调用失败时不会让整个接口崩掉。
```

这叫：

```text
fallback / 降级
```

## 21. 为什么要 fallback

LLM 调用可能失败：

```text
网络失败
API key 错误
额度用完
模型返回不是 JSON
请求超时
```

如果没有 fallback，用户一调用接口就报 500。

有 fallback：

```text
LLM 调不通 -> 规则模式继续返回结果
```

这就是工程稳定性的一个小体现。

## 22. LLM 和普通函数的区别

普通函数：

```cpp
int add(int a, int b) {
    return a + b;
}
```

特点：

```text
确定性强
输入一样，输出一样
速度快
不会突然输出奇怪格式
```

LLM：

```text
输入 prompt
输出文本
可能不稳定
可能不按格式
可能慢
可能失败
可能收费
```

所以后端接 LLM 时，要多考虑：

```text
超时
重试
格式校验
错误处理
成本
缓存
日志
安全
```

## 23. RAG 是什么

RAG 是 Retrieval-Augmented Generation，检索增强生成。

先不用被英文吓到。

它解决的问题是：

```text
模型不一定知道你的私有资料。
模型上下文长度有限。
模型可能胡说。
```

RAG 的流程：

```text
用户问题
  -> 先从资料库里检索相关片段
  -> 把片段和问题一起发给 LLM
  -> LLM 基于片段回答
```

C++ 类比：

```cpp
vector<string> docs = load_docs();
vector<string> related = retrieve_top_k(docs, question);
string prompt = build_prompt(related, question);
string answer = call_llm(prompt);
```

对于简历项目：

```text
用户问：我这个 Unity 项目怎么写进后端简历？
系统先检索你的简历、项目说明、岗位 JD
再让模型基于这些资料回答
```

这就是 RAG。

## 24. 向量数据库是什么

RAG 常用“向量检索”。

大概过程：

```text
文本 -> embedding 模型 -> 一串数字 vector<float>
```

比如：

```text
"FastAPI 后端开发"
-> [0.12, -0.03, 0.88, ...]
```

语义相近的文本，向量距离更近。

C++ 类比：

```cpp
vector<double> embedding;
double similarity = cosine(a, b);
```

向量数据库就是专门存这些向量并快速查最近邻的数据库。

你现在暂时不用实现完整向量数据库，但要知道：

```text
RAG = 文档切分 + 向量化 + 检索 + 拼 prompt + 调 LLM
```

## 25. 缓存 Redis 是什么

Redis 是内存数据库，常用来做缓存。

如果同一个 JD 被分析很多次，每次都调大模型很贵、很慢。

可以：

```text
key = hash(resume_text + job_description)
value = 分析结果 JSON
```

第一次：

```text
缓存没有 -> 调 LLM -> 存 Redis -> 返回
```

第二次：

```text
缓存命中 -> 直接返回
```

C++ 类比：

```cpp
unordered_map<string, Result> cache;
```

区别是 Redis 是独立服务，多个后端进程都能访问。

## 26. 当前项目和岗位 JD 的对应关系

岗位要求：

```text
提示词工程
大模型 API 集成
后端 API
数据处理
数据库对接
Python
可靠性
```

当前项目对应：

```text
FastAPI 接口
  -> 后端 API

Pydantic schema
  -> 结构化请求/响应

SQLite
  -> 数据库持久化

build_llm_prompt()
  -> Prompt 工程

analyze_resume_with_llm()
  -> LLM API 集成骨架

fallback 到 rule
  -> 可靠性/降级
```

## 27. 面试时怎么说数据库

你可以说：

```text
这个项目里我用 SQLite 做了分析记录持久化，设计了 analysis_records 表，用 id 作为自增主键，保存简历文本、岗位 JD、匹配分、关键词、建议和面试题等字段。接口调用 /resume/analyze 后会先生成分析结果，再写入数据库并返回 record_id；同时提供 /analyses 和 /analyses/{record_id} 查询历史记录。
```

如果被问为什么用 SQLite：

```text
因为项目当前是本地 demo，SQLite 不需要额外数据库服务，适合快速验证表结构和持久化流程；如果部署到生产环境，可以把存储层替换为 MySQL/PostgreSQL，接口层和业务层改动较小。
```

## 28. 面试时怎么说 LLM

你可以说：

```text
我把大模型调用设计成可选模式：请求里 use_llm=true 且环境变量配置了 LLM_API_KEY 时，会调用 OpenAI 兼容 Chat Completions API；Prompt 要求模型只返回固定 JSON 字段，后端再解析成响应模型。如果模型调用失败、超时或返回格式不合法，则自动回退到本地规则分析，保证接口可用。
```

这句话很有后端味道，因为它提到了：

```text
配置
结构化输出
解析
异常处理
降级
可用性
```

## 29. 你现在最低要掌握的知识点

数据库最低掌握：

```text
表 table
行 row
列 column
主键 primary key
建表 CREATE TABLE
插入 INSERT
查询 SELECT
SQLite 是本地文件数据库
```

LLM 最低掌握：

```text
LLM API 是远程文本处理服务
Prompt 是给模型的输入指令
messages 是对话数组
API Key 是调用凭证
结构化输出是让模型返回 JSON
fallback 是调用失败时降级
RAG 是先检索资料再让模型回答
```

## 30. 下一步可以怎么增强项目

优先级从高到低：

1. 写 README 截图和接口示例。
2. 增加 `.env.example`，说明环境变量。
3. 增加 Dockerfile，让项目一条命令启动。
4. 加 Redis 缓存，缓存重复分析结果。
5. 加 PDF 解析，把简历 PDF 转文本。
6. 加简单 RAG，把简历文本切段后按关键词检索再问模型。

当前投简历阶段，最划算的是：

```text
README + 接口截图 + 简历项目 bullet
```

因为这最容易让面试官相信你真的跑过项目。

