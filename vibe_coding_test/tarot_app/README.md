# Tarot GUI（Streamlit）

一个带可视化界面的塔罗抽牌/解读小项目。

## 使用方法

### 第一次运行（只需要做一次）

在本项目目录下执行：

```powershell
cd "C:\Users\24528\Desktop\github_test\vibe_coding_test\tarot_app"

# 如果你的 python 安装路径带空格，用 & 来调用（示例路径按你的实际情况替换）
& "D:\Program Files\Python\python.exe" -m venv .venv

# PowerShell 允许本进程执行激活脚本
Set-ExecutionPolicy -Scope Process Bypass

# 激活虚拟环境（正确的 PowerShell 脚本名）
.\.venv\Scripts\Activate.ps1

# 安装依赖
python -m pip install -r requirements.txt
```

### 之后每次运行（常用）

```powershell
cd "C:\Users\24528\Desktop\github_test\vibe_coding_test\tarot_app"
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

启动后浏览器打开：

- `http://localhost:8501`

停止服务：回到终端按 `Ctrl+C`。

## 功能

- 牌阵：单张牌、三张牌（过去/现在/未来）
- 支持逆位（默认 50% 概率，可关闭）
- 展示本次解读与抽牌历史（会话内）

## 牌阵说明

- **单张牌**：抽 1 张，给一个总体指引/建议。
- **三张牌（过去/现在/未来）**：抽 3 张，分别表示背景影响、当前处境、趋势走向。

## 分享给别人访问（重要）

- `localhost` 只能你自己电脑访问，**不能直接分享给别人**。
- 如果想让同一局域网的人访问，可以使用终端里输出的 `Network URL`（如 `http://192.168.x.x:8501`），但需要你这边保持运行且防火墙允许。
- 如果想公网访问，需要把应用部署到云端平台（部署后会有公网地址）。

## 常见问题

- **PowerShell 里运行 `"D:\...\python.exe" -m venv .venv` 报错**：请用 `& "D:\...\python.exe" -m venv .venv`（用 `&` 调用带空格路径）。
- **打开网页红屏报错**：优先看终端报错堆栈，通常是代码里某个参数不合法或依赖缺失导致。

