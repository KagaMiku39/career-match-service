# MySQL / SQL 与大模型岗位关键词入门

这份笔记先补两个基础：

1. SQL / MySQL 到底怎么写、怎么执行。
2. JD 里大模型相关词汇是什么意思。

## 1. SQL 是什么

SQL 是 Structured Query Language，结构化查询语言。

你可以把它理解成：

```text
专门操作数据库表的语言
```

它不是 C++，不是 Python，但后端程序经常把 SQL 字符串交给数据库执行。

比如：

```sql
SELECT * FROM users;
```

意思是：

```text
从 users 表中查询所有列、所有行。
```

## 2. MySQL 是什么

MySQL 是一个关系型数据库系统。

SQLite 和 MySQL 都能执行 SQL，但定位不同：

```text
SQLite
  一个 .db 文件就是数据库，适合本地 demo。

MySQL
  一个独立运行的数据库服务，适合真实后端项目。
```

C++ 类比：

```text
SQLite 像本地文件读写。
MySQL 像一个专门管理数据的服务器程序。
```

后端连接 MySQL 通常需要：

```text
host     数据库在哪台机器
port     MySQL 默认 3306
user     用户名
password 密码
database 使用哪个数据库
```

## 3. SQL 靠换行分隔吗

不是。

SQL 一般靠分号 `;` 表示一条语句结束。

这是一条语句：

```sql
SELECT * FROM users;
```

这也是同一条语句，只是换行写：

```sql
SELECT
    *
FROM
    users;
```

换行只是为了好看。

真正结束的是最后的：

```sql
;
```

所以你可以理解成：

```text
SQL 解析器会一直读，直到遇到分号，才认为一条语句结束。
```

## 4. 为什么 SQL 经常写很多行

因为一条查询可能包含很多部分。

例如：

```sql
SELECT id, name, score
FROM users
WHERE score >= 60
ORDER BY score DESC
LIMIT 10;
```

这其实是一条语句。

拆开看：

```text
SELECT id, name, score  要查询哪些列
FROM users              从哪张表查
WHERE score >= 60       只要满足条件的行
ORDER BY score DESC     按 score 从大到小排序
LIMIT 10                最多返回 10 行
;                       语句结束
```

类比 C++：

```cpp
vector<User> ans;
for (auto &u : users) {
    if (u.score >= 60) {
        ans.push_back(u);
    }
}
sort(ans.begin(), ans.end(), cmp_score_desc);
ans.resize(min(10, (int)ans.size()));
```

SQL 是把这些逻辑用声明式语言写出来。

## 5. SQL 是声明式语言

C++ 通常是命令式：

```text
第一步做什么，第二步做什么，第三步做什么。
```

SQL 更偏声明式：

```text
我想要什么结果。
```

比如：

```sql
SELECT * FROM users WHERE age >= 18;
```

你没有告诉数据库“怎么遍历、怎么判断、怎么优化”。

你只是说：

```text
我要 users 表里 age >= 18 的行。
```

数据库自己决定怎么执行。

这就是为什么后面会有“索引优化”“查询优化”这些东西。

## 6. 表、行、列

数据库表可以类比 `vector<struct>`。

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

类比 C++：

```cpp
struct User {
    int id;
    string name;
    int age;
    string created_at;
};

vector<User> users;
```

对应关系：

```text
table 表     -> vector<User> users
row 行       -> 一个 User 实例
column 列    -> User 的字段
primary key -> 唯一标识一行的字段
```

## 7. 常见 SQL 关键词

### CREATE TABLE

建表。

```sql
CREATE TABLE analysis_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    target_role VARCHAR(100) NOT NULL,
    match_score INT NOT NULL
);
```

意思是定义一张表的结构。

### INSERT INTO

插入一行。

```sql
INSERT INTO analysis_records (target_role, match_score)
VALUES ('大模型应用后端开发实习生', 76);
```

类比：

```cpp
analysis_records.push_back(record);
```

### SELECT

查询。

```sql
SELECT id, target_role, match_score
FROM analysis_records;
```

意思是查这三列。

### *

星号表示所有列。

```sql
SELECT * FROM analysis_records;
```

意思是查所有列。

### FROM

从哪张表查。

```sql
FROM analysis_records
```

### WHERE

筛选条件。

```sql
SELECT *
FROM analysis_records
WHERE match_score >= 60;
```

类比：

```cpp
if (record.match_score >= 60)
```

### ORDER BY

排序。

```sql
ORDER BY match_score DESC
```

意思是按匹配分降序排序。

```text
ASC  升序，小到大
DESC 降序，大到小
```

### LIMIT

限制返回数量。

```sql
LIMIT 10
```

最多返回 10 行。

### UPDATE

更新已有数据。

```sql
UPDATE analysis_records
SET match_score = 80
WHERE id = 1;
```

注意：没有 `WHERE` 会更新整张表，很危险。

### DELETE

删除数据。

```sql
DELETE FROM analysis_records
WHERE id = 1;
```

注意：没有 `WHERE` 会删除整张表数据，很危险。

## 8. MySQL 常见数据类型

### INT

整数。

```sql
age INT
```

### BIGINT

更大的整数。

常用于很大的 id、计数。

### VARCHAR(n)

可变长度字符串。

```sql
name VARCHAR(100)
```

最多 100 个字符。

### TEXT

长文本。

简历文本、文章内容可以用它。

### DATETIME

日期时间。

```sql
created_at DATETIME
```

### BOOLEAN

布尔值。

MySQL 里通常内部类似 `TINYINT(1)`。

## 9. 主键是什么

主键 Primary Key 是一行数据的唯一标识。

比如：

```sql
id INT PRIMARY KEY AUTO_INCREMENT
```

意思是：

```text
id 是主键。
每插入一行，id 自动加一。
```

类比：

```cpp
record.id = ++global_id;
```

为什么需要主键？

因为你要稳定地找到某一行：

```sql
SELECT * FROM analysis_records WHERE id = 1;
```

## 10. NOT NULL 是什么

```sql
name VARCHAR(100) NOT NULL
```

意思是：

```text
这一列不能是空值 NULL。
```

NULL 不是空字符串。

```text
空字符串 ""：有值，只是长度为 0。
NULL：没有值，不知道值是什么。
```

## 11. DEFAULT 是什么

```sql
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

意思是：

```text
如果插入时不传 created_at，数据库自动填当前时间。
```

## 12. 索引是什么

索引 index 是为了加快查询。

你可以类比算法里的预处理。

没有索引：

```cpp
for (auto &row : table) {
    if (row.id == target) return row;
}
```

可能 O(n)。

有索引：

```text
数据库维护一份额外的数据结构，比如 B+ 树。
可以更快定位目标行。
```

类似你为了快速查询，额外建：

```cpp
unordered_map<int, int> id_to_pos;
```

但是索引不是越多越好。

因为：

```text
查询变快
插入/更新会变慢
占用更多空间
```

## 13. 事务是什么

事务 transaction 是一组操作，要么全部成功，要么全部失败。

经典例子：转账。

```text
A 扣 100
B 加 100
```

这两个操作必须一起成功。

不能出现：

```text
A 扣了钱
B 没收到钱
```

SQL 里：

```sql
START TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

COMMIT;
```

如果中间失败：

```sql
ROLLBACK;
```

先知道概念即可。

## 14. JD 里的数据库优化是什么意思

JD 里说：

```text
熟悉数据库设计和优化，有数据库调优经验
```

对实习生来说，你先理解这些就够：

```text
表结构设计合理
给常查字段建索引
避免 SELECT *
用 LIMIT 控制返回数量
避免一次查太多数据
理解事务保证一致性
```

你的项目目前能说：

```text
我设计了 analysis_records 表保存分析记录，使用 id 作为主键，通过 LIMIT 控制历史查询数量。
```

## 15. 大模型岗位关键词

JD 里关于大模型的词很多，我们逐个拆。

### 大模型应用

不是训练一个大模型。

多数公司说“大模型应用开发”，意思是：

```text
调用现成大模型 API
把它接入业务系统
做 prompt、接口、数据库、工作流、权限、日志、稳定性
```

所以你不用一开始就会训练 LLaMA。

你要会：

```text
把模型能力包装成后端 API。
```

### Prompt 工程

Prompt 就是给模型的输入指令。

Prompt 工程就是设计更稳定、更可控的输入。

比如：

差的 prompt：

```text
帮我看看简历。
```

好的 prompt：

```text
你是技术简历顾问。请根据岗位 JD 分析简历匹配度。
必须只返回 JSON，字段包括 match_score、matched_keywords、missing_keywords、suggestions。
```

核心目标：

```text
让模型输出稳定、可解析、符合业务需要。
```

### 大模型 API 集成

就是在后端里调用模型接口。

流程：

```text
接收用户请求
构造 prompt
调用 LLM API
解析模型返回
保存结果
返回给用户
```

你项目里 `analyze_resume_with_llm()` 就是这个骨架。

### GPT / GLM / LLaMA

这些是不同模型或模型家族。

```text
GPT
  OpenAI 的模型系列。

GLM
  智谱 AI 的模型系列。

LLaMA
  Meta 开源模型系列。
```

岗位里提它们，通常意思是：

```text
你了解不同模型的 API 调用方式和应用场景。
```

实习生先会 OpenAI 兼容 API 就很好，因为很多平台都兼容这个格式。

### OpenAI 兼容 API

很多模型服务模仿 OpenAI 的接口格式。

也就是说，不管底层是 GPT、Qwen、GLM，调用格式可能都长这样：

```json
{
  "model": "xxx",
  "messages": [
    {"role": "system", "content": "你是助手"},
    {"role": "user", "content": "你好"}
  ]
}
```

好处是：

```text
代码改 base_url、api_key、model 就能切换模型供应商。
```

### 结构化输出

让模型返回固定格式，比如 JSON。

后端最怕模型返回一大段散文。

所以我们要求：

```text
只返回 JSON，不要 Markdown。
```

这样后端才能：

```python
json.loads(content)
```

把模型输出解析成程序可用的数据。

### RAG

RAG 是检索增强生成。

流程：

```text
用户问题
-> 先查资料库
-> 找到相关片段
-> 把片段和问题一起发给模型
-> 模型基于资料回答
```

为什么需要 RAG？

```text
模型不知道你的私有资料。
模型可能胡说。
上下文长度有限。
```

简历项目里的 RAG 例子：

```text
把你的项目说明、简历、岗位 JD 当资料库。
用户问“我的 Unity 项目怎么写进后端简历？”
系统先检索相关项目片段，再让模型回答。
```

### Embedding

Embedding 是把文本变成向量。

```text
"FastAPI 后端开发"
-> [0.12, -0.03, 0.88, ...]
```

语义相近的文本，向量距离更近。

RAG 常用 embedding 做检索。

### 向量数据库

存 embedding 向量并快速查询相似文本的数据库。

比如：

```text
Milvus
FAISS
Chroma
pgvector
```

你现在先知道用途即可：

```text
向量数据库服务于 RAG 的检索步骤。
```

### Agent

Agent 是让模型不只是回答，而是能选择工具、调用工具、根据结果继续推理。

比如：

```text
模型判断需要查数据库
-> 调用数据库工具
-> 看结果
-> 再回答用户
```

实习生阶段先了解，不必急着深入。

### Function Calling / Tool Calling

让模型输出“我要调用哪个函数、参数是什么”。

例如：

```json
{
  "name": "search_resume_records",
  "arguments": {
    "keyword": "FastAPI"
  }
}
```

后端程序真正执行这个函数，再把结果给模型。

### 微调 Fine-tuning

用数据继续训练模型，让模型更适合某类任务。

大模型应用后端实习一般不一定要求你会微调。

你先重点学：

```text
Prompt
LLM API
结构化输出
RAG
后端集成
```

## 16. 你现在该怎么学 SQL

按这个顺序：

1. 建表：`CREATE TABLE`
2. 插入：`INSERT INTO`
3. 查询：`SELECT FROM WHERE`
4. 排序分页：`ORDER BY LIMIT`
5. 更新删除：`UPDATE DELETE`
6. 主键、索引、事务

练习表可以用：

```sql
CREATE TABLE analysis_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    target_role VARCHAR(100) NOT NULL,
    resume_text TEXT NOT NULL,
    job_description TEXT NOT NULL,
    match_score INT NOT NULL,
    analysis_mode VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

插入：

```sql
INSERT INTO analysis_records
    (target_role, resume_text, job_description, match_score, analysis_mode)
VALUES
    ('大模型应用后端开发实习生', '我的简历', '岗位 JD', 76, 'rule');
```

查询：

```sql
SELECT id, target_role, match_score, created_at
FROM analysis_records
ORDER BY id DESC
LIMIT 10;
```

按条件查询：

```sql
SELECT *
FROM analysis_records
WHERE match_score >= 60;
```

更新：

```sql
UPDATE analysis_records
SET match_score = 80
WHERE id = 1;
```

删除：

```sql
DELETE FROM analysis_records
WHERE id = 1;
```

## 17. 面试时你可以怎么说

SQL / 数据库：

```text
我理解关系型数据库可以类比为持久化的表结构，项目中使用 SQLite 保存分析记录，表中用自增 id 作为主键，保存简历文本、岗位 JD、匹配分、分析模式和创建时间等字段。查询历史记录时使用 ORDER BY 和 LIMIT 控制返回顺序与数量。后续如果迁移到 MySQL，表结构和基本 SQL 思路是一致的。
```

大模型：

```text
我理解大模型应用开发重点不是训练模型，而是把模型 API 稳定接入业务系统。项目里我设计了 OpenAI 兼容 API 的调用骨架，通过 Prompt 要求模型返回固定 JSON 字段，并在调用失败或未配置 API key 时回退到本地规则分析，保证接口可演示和可用。
```

