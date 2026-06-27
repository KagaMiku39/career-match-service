# GitHub 工作流入门：把这个后端项目传上去

这份文档按你现在的情况写：你已经有一个可运行的 `ai_resume_backend` 项目，但还不熟悉 Git/GitHub。

## 1. 要不要上传 GitHub

建议上传。

原因：

```text
简历上的项目如果只有文字，可信度一般。
如果有 GitHub 链接、README、接口说明、运行方式，可信度会明显更高。
```

但是不要上传整个 Unity 工程。

你应该上传：

```text
ai_resume_backend
```

不建议上传：

```text
整个 Farm_Final_Integration
Unity Library/
虚拟环境 .venv-codex/
本地数据库 data/analysis.db
API Key
```

原因：

```text
Unity 工程太大，Library 是生成文件。
虚拟环境是本地依赖目录，别人应该用 requirements.txt 自己安装。
数据库文件是运行产生的数据，不是源码。
API Key 是密钥，绝对不能上传。
```

## 2. Git 和 GitHub 的区别

Git 是本地版本管理工具。

GitHub 是远程代码托管网站。

类比：

```text
Git
  像你本机的存档系统。

GitHub
  像云端仓库，可以把本地存档同步上去。
```

## 3. Git 的基本概念

### repository 仓库

一个被 Git 管理的项目目录。

### commit 提交

一次代码快照。

可以理解成游戏存档：

```text
当前项目状态 -> 保存成一个 commit
```

### branch 分支

一条开发线。

现在你先只用：

```text
main
```

### remote 远程仓库

GitHub 上对应的仓库地址。

例如：

```text
https://github.com/你的用户名/ai_resume_backend.git
```

### push 推送

把本地 commit 上传到 GitHub。

### pull 拉取

把 GitHub 上的新内容拉到本地。

## 4. 什么文件该上传

应该上传：

```text
app/
README.md
requirements.txt
.gitignore
.env.example
*.md 学习说明文档
```

不应该上传：

```text
.venv-codex/
data/
.env
__pycache__/
*.db
```

这些已经写进 `.gitignore`。

`.gitignore` 的作用是：

```text
告诉 Git 哪些文件不要纳入版本管理。
```

## 5. 第一次上传流程

进入项目目录：

```powershell
cd D:\Unity\Experiment\Farm_Final_Integration\ai_resume_backend
```

初始化 Git 仓库：

```powershell
git init
```

查看状态：

```powershell
git status
```

加入文件到暂存区：

```powershell
git add .
```

提交：

```powershell
git commit -m "Initial FastAPI resume analyzer backend"
```

去 GitHub 网站创建一个新仓库，名字可以叫：

```text
ai_resume_backend
```

创建时建议：

```text
不要勾选 README
不要勾选 .gitignore
不要勾选 license
```

因为本地已经有这些文件。

然后 GitHub 会给你远程地址，类似：

```text
https://github.com/你的用户名/ai_resume_backend.git
```

绑定远程仓库：

```powershell
git remote add origin https://github.com/你的用户名/ai_resume_backend.git
```

设置主分支名：

```powershell
git branch -M main
```

推送：

```powershell
git push -u origin main
```

## 6. 以后修改代码怎么上传

每次改完：

```powershell
git status
git add .
git commit -m "描述你这次改了什么"
git push
```

比如：

```powershell
git commit -m "Add SQLite analysis history APIs"
```

## 7. 常见错误

### 忘了 git init

错误：

```text
fatal: not a git repository
```

意思是当前目录还不是 Git 仓库。

解决：

```powershell
git init
```

### 远程仓库需要登录

如果 push 时要求登录 GitHub，你可以用：

```text
GitHub Desktop
Git Credential Manager
Personal Access Token
```

最简单的是先装 GitHub Desktop，然后用它登录 GitHub。

### 不小心把 .venv 加进去了

先确认 `.gitignore` 有：

```text
.venv-codex/
```

如果已经 add 了，需要：

```powershell
git rm -r --cached .venv-codex
```

意思是：

```text
从 Git 暂存/跟踪里移除，但不删除本地文件。
```

## 8. 简历里怎么写 GitHub 链接

可以写：

```text
GitHub: https://github.com/你的用户名/ai_resume_backend
```

项目描述里写：

```text
项目已上传 GitHub，README 包含启动方式、接口说明、请求示例和学习笔记。
```

前提是 README 真写清楚了。

