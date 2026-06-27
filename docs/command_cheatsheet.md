# Git / PowerShell / Linux 命令速查

这份文档按“能看懂但还不太会写命令”的状态来整理。

## 1. 命令行是什么

命令行就是用文字操作系统。

你可以把它理解成：

```text
图形界面：用鼠标点文件夹、按钮
命令行：输入命令让系统做事
```

比如：

```powershell
cd D:\Unity\Experiment\Farm_Final_Integration\career_match_service
```

意思是进入这个目录。

## 2. PowerShell 和 Linux Shell 的区别

PowerShell 是 Windows 的命令行。

Linux 常用的是 bash/zsh。

很多基础命令相似，但不完全一样。

| 功能 | PowerShell | Linux |
|---|---|---|
| 查看当前路径 | `pwd` | `pwd` |
| 进入目录 | `cd path` | `cd path` |
| 列出文件 | `dir` 或 `Get-ChildItem` | `ls` |
| 查看文件内容 | `Get-Content file` | `cat file` |
| 删除文件 | `Remove-Item file` | `rm file` |
| 创建目录 | `New-Item -ItemType Directory name` | `mkdir name` |
| 复制文件 | `Copy-Item a b` | `cp a b` |
| 移动/重命名 | `Move-Item a b` | `mv a b` |

## 3. 路径

Windows 路径：

```text
D:\Unity\Experiment\Farm_Final_Integration
```

Linux 路径：

```text
/home/kagamiku39/code
```

区别：

```text
Windows 用盘符 D:
Linux 从根目录 / 开始
Windows 常见反斜杠 \
Linux 常见正斜杠 /
```

PowerShell 里很多时候 `/` 和 `\` 都能用，但 Windows 原生路径一般写 `\`。

## 4. 当前目录

当前目录就是命令现在所在的位置。

查看当前目录：

```powershell
pwd
```

进入项目：

```powershell
cd D:\Unity\Experiment\Farm_Final_Integration\career_match_service
```

回上一级：

```powershell
cd ..
```

## 5. Git 是什么

Git 是版本管理工具。

你可以把一次 commit 理解成一次“项目存档”。

GitHub 是远程仓库网站。

```text
git commit
  本地存档

git push
  把本地存档上传到 GitHub

git pull
  把 GitHub 上的新存档拉下来
```

## 6. 常用 Git 命令

查看当前状态：

```powershell
git status
```

查看简洁状态：

```powershell
git status --short
```

查看提交历史：

```powershell
git log --oneline
```

把所有改动加入暂存区：

```powershell
git add .
```

提交：

```powershell
git commit -m "Update README"
```

上传：

```powershell
git push
```

第一次上传某个分支：

```powershell
git push -u origin main
```

拉取远程更新：

```powershell
git pull origin main
```

查看远程仓库地址：

```powershell
git remote -v
```

修改远程仓库地址：

```powershell
git remote set-url origin https://github.com/KagaMiku39/career-match-service.git
```

## 7. 你的日常 Git 流程

以后你改了项目，一般这样：

```powershell
cd D:\Unity\Experiment\Farm_Final_Integration\career_match_service
git status
git add .
git commit -m "Describe what changed"
git push
```

如果你在 GitHub 网页上也改了文件，本地改之前先：

```powershell
git pull origin main
```

## 8. 不要上传什么

这些不要上传：

```text
.venv/
.venv-codex/
data/
.env
*.db
__pycache__/
```

它们已经写进 `.gitignore`。

`.gitignore` 的意思是：

```text
告诉 Git 忽略这些文件。
```

## 9. 启动当前后端项目

进入项目：

```powershell
cd D:\Unity\Experiment\Farm_Final_Integration\career_match_service
```

激活虚拟环境：

```powershell
.\.venv-codex\Scripts\Activate.ps1
```

启动服务：

```powershell
uvicorn app.main:app --reload --port 8000
```

浏览器打开：

```text
http://127.0.0.1:8000/docs
```

停止服务：

```text
Ctrl + C
```

## 10. Swagger /docs 怎么用

1. 打开 `/docs`。
2. 点开 `POST /resume/analyze`。
3. 点 `Try it out`。
4. 在 Request body 里填 JSON。
5. 点 `Execute`。
6. 看下面的 Response body。

请求示例：

```json
{
  "resume_text": "数字媒体技术专业，长期进行 ACM Codeforces AtCoder 算法训练，开发过 Unity C# JSON EventBus CommandBus 农场项目，也在学习 Python FastAPI API Prompt 大模型。",
  "job_description": "大模型应用后端开发实习生，要求 Python FastAPI LLM API Prompt MySQL Redis RAG Docker 数据库。",
  "target_role": "大模型应用后端开发实习生",
  "use_llm": false
}
```

如果返回 422，通常是：

```text
JSON 格式不对
字段少了
字符串太短
类型不对
```

## 11. 常见状态码

```text
200 OK
  成功

404 Not Found
  路径或数据不存在

422 Validation Error
  请求数据不符合 Pydantic schema

500 Internal Server Error
  后端程序内部错误
```

