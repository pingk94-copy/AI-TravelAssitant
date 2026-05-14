# AI 智能旅行助手

这是一个 `Vue 3 + FastAPI` 的全栈智能旅行助手项目，包含用户登录、AI 对话、行程规划、异步任务和大模型接入配置。

## 一键启动项目

打开 PowerShell，进入项目根目录：

```powershell
cd C:\Users\admin\Desktop\桌面\Ai-TravelAssitant
```

最推荐的启动方式：双击项目根目录里的这个文件：

```text
start-dev.vbs
```

它不会弹出后端/前端命令行窗口，会在后台启动项目，并自动打开浏览器。

如果你想在终端里启动，执行：

```powershell
.\start-dev.ps1
```

如果 PowerShell 不允许执行脚本，就执行：

```powershell
.\start-dev.bat
```

脚本会自动完成这些事：

- 清理旧的后端端口 `8000`
- 清理旧的前端端口 `5173`
- 在后台启动后端 FastAPI
- 在后台启动前端 Vite
- 启动成功后自动打开浏览器页面

浏览器会打开：

```text
http://127.0.0.1:5173
```

脚本不会再弹出两个后端/前端命令行窗口。日志会写到：

```text
logs\backend.out.log
logs\backend.err.log
logs\frontend.out.log
logs\frontend.err.log
```

## 配置大模型 API Key

后端读取的配置文件是：

```text
backend\.env
```

如果还没有这个文件，先复制模板：

```powershell
copy .env.example backend\.env
```

然后打开 `backend\.env`，填写你的真实密钥：

```env
OPENAI_API_KEY=你的真实API_KEY
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
OPENAI_MODEL=deepseek-ai/DeepSeek-V4-Flash
```

如果你使用其他 OpenAI 兼容服务商，把 `OPENAI_BASE_URL` 和 `OPENAI_MODEL` 改成对应服务商提供的值。

修改 `.env` 后，重新执行：

```powershell
.\start-dev.ps1
```

## 手动启动方式

如果你不想用一键脚本，也可以分别启动后端和前端。

启动后端：

```powershell
cd C:\Users\admin\Desktop\桌面\Ai-TravelAssitant\backend
..\.venv\Scripts\python -m pip install -r requirements.txt
..\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

启动前端需要另开一个 PowerShell 窗口：

```powershell
cd C:\Users\admin\Desktop\桌面\Ai-TravelAssitant\frontend
npm install
npm run dev
```

## 常用页面

- 首页：`http://127.0.0.1:5173`
- 登录/注册：`http://127.0.0.1:5173/auth`
- AI 对话：`http://127.0.0.1:5173/chat`
- 行程规划：`http://127.0.0.1:5173/trips`

## 验证命令

后端测试：

```powershell
cd C:\Users\admin\Desktop\桌面\Ai-TravelAssitant\backend
..\.venv\Scripts\python -m pytest
```

前端构建：

```powershell
cd C:\Users\admin\Desktop\桌面\Ai-TravelAssitant\frontend
npm run build
```

## 注意事项

- `backend\.env` 里放的是你的真实密钥，不要提交到 GitHub。
- 一键启动脚本会清理 `8000` 和 `5173` 端口上的旧进程。
- 如果页面仍然显示旧回复，通常是后端没有重启，重新执行 `.\start-dev.ps1` 即可。
