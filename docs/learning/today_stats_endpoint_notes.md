# Today: Add /stats Endpoint

## 1. 今天做了什么

给 CareerMatch Service 增加了一个只读统计接口：

```text
GET /stats
```

它返回当前数据库里四类数据的数量：

```json
{
  analysis_count: 6,
  knowledge_chunk_count: 1,
  prompt_template_count: 2,
  workflow_run_count: 2
}
```

## 2. 为什么要做

这个接口不是核心业务分析，而是后台管理/调试接口。

真实后端系统不能只是“收到请求然后返回结果”，还需要知道系统当前状态，例如保存了多少分析记录、多少知识片段、多少 Prompt 模板、多少工作流运行记录。

用算法训练类比：

```text
/stats 就像刷题统计面板：今天做了几题、每个专题有多少题、哪些内容已经积累。
```

## 3. 改了哪些文件

### app/schemas.py

新增 `StatsResponse`：

```python
class StatsResponse(BaseModel):
    analysis_count: int
    knowledge_chunk_count: int
    prompt_template_count: int
    workflow_run_count: int
```

它像 C++ 里的返回结构体：

```cpp
struct StatsResponse {
    int analysis_count;
    int knowledge_chunk_count;
    int prompt_template_count;
    int workflow_run_count;
};
```

### app/storage.py

新增 `count_table_rows()` 和 `get_stats()`。

`count_table_rows()` 负责执行：

```sql
SELECT COUNT(*) AS count FROM table_name;
```

类比 C++：

```cpp
return table.size();
```

`get_stats()` 负责把四张表的 count 组装成一个 `StatsResponse`。

### app/main.py

新增路由：

```python
@app.get(/stats, response_model=StatsResponse)
def stats() -> StatsResponse:
    return get_stats()
```

它的含义是注册映射：

```text
GET /stats -> stats() 函数
```

## 4. PowerShell 里用到的命令

进入项目目录：

```powershell
cd D:\Projects\career-match-service
```

启动后端：

```powershell
.\.venv-codex\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

请求接口：

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8010/stats' | ConvertTo-Json
```

看 Git 状态：

```powershell
git status
```

## 5. 这次学到的后端模式

新增一个接口通常分三步：

```text
schemas.py  定义输入/输出结构
storage.py  写数据库读写逻辑
main.py     注册路由
```

这和 C++ 项目拆分很像：

```text
struct 定义数据结构
solve / helper 处理逻辑
main 调用函数
```

区别是后端的 main.py 不是一次性读输入，而是长期运行，等待很多 HTTP 请求。

## 6. 面试讲法

我给项目增加了 `/stats` 统计接口，用于观察系统当前数据规模。接口通过 storage 层分别查询 analysis_records、knowledge_chunks、prompt_templates 和 workflow_runs 四张表的记录数，再通过 FastAPI 返回结构化 JSON。这个功能体现了后端系统除了业务处理之外，还需要具备可观察和可管理能力。
