# Carryout

本文件记录项目每一轮建设的改动说明、设计理由、验证方式和下一步计划。

---


## Round 1 - 全栈项目骨架

### 本轮目标

按照 `study.md` 的第 1 阶段，先建立可持续迭代的前后端基础骨架：

1. 创建 `frontend` 和 `backend` 两个顶层目录。
2. 初始化 Vue 3 前端应用。
3. 初始化 FastAPI 后端应用。
4. 添加基础健康检查接口。
5. 建立第一条自动化测试链路。

### 前端改动

创建了 `frontend` 目录，并使用 Vite 作为前端构建工具。

当前前端技术栈：

1. Vue 3
2. TypeScript
3. Vite
4. Vue Router
5. Pinia
6. Tailwind CSS
7. lucide-vue-next

主要文件：

1. `frontend/src/main.ts`：前端入口文件，负责创建 Vue 应用，并挂载 Pinia、Router 和全局样式。
2. `frontend/src/App.vue`：前端全局布局组件，负责顶部导航、页面容器和路由出口。
3. `frontend/src/router/index.ts`：前端路由配置文件，当前注册首页、聊天页、行程页。
4. `frontend/src/stores/app.ts`：Pinia 全局状态文件，当前保存 API 地址和当前任务 ID。
5. `frontend/src/views/DashboardView.vue`：首页工作台页面，展示旅行助手项目的第一屏。
6. `frontend/src/views/ChatView.vue`：AI 聊天页面占位，后续用于接入 SSE 流式聊天。
7. `frontend/src/views/TripsView.vue`：行程规划页面占位，后续用于接入异步任务和行程结果展示。
8. `frontend/src/style.css`：全局样式入口，接入 Tailwind CSS，并定义基础页面样式。
9. `frontend/vite.config.ts`：Vite 配置文件，接入 Vue 插件和 Tailwind 插件。
10. `frontend/src/vite-env.d.ts`：Vue 单文件组件类型声明，让 TypeScript 能识别 `.vue` 文件导入。

### 后端改动

创建了 `backend` 目录，并建立 FastAPI 应用骨架。

主要文件：

1. `backend/requirements.txt`：后端依赖清单。
2. `backend/app/main.py`：FastAPI 应用入口，负责创建应用、配置 CORS、注册路由。
3. `backend/app/core/config.py`：后端配置中心，集中管理应用名、版本号、接口前缀和跨域来源。
4. `backend/app/api/routes/health.py`：健康检查路由，提供 `/api/health` 接口。
5. `backend/tests/test_health.py`：健康检查接口测试。

### TDD 记录

后端健康检查接口按测试优先方式实现。

先创建 `backend/tests/test_health.py`，测试期望 `/api/health` 返回：

```json
{
  "status": "ok",
  "service": "ai-travel-assistant-api",
  "version": "0.1.0"
}
```

第一次运行测试时失败，原因是 `app.main` 还不存在。随后实现 `app/main.py`、`app/core/config.py`、`app/api/routes/health.py`，再次运行后测试通过。

### 构建问题处理记录

第一次运行 `npm run build` 时，TypeScript 报错：

```text
Cannot find module './App.vue' or its corresponding type declarations.
```

根因是项目最初由 Vite 普通 TypeScript 模板生成，后续改造成 Vue 单文件组件结构后，缺少 `.vue` 模块类型声明。

处理方式：

1. 新增 `frontend/src/vite-env.d.ts`。
2. 声明 `*.vue` 模块。
3. 重新运行 `npm run build`。

处理后前端构建通过。

### 验证方式

后端测试：

```bash
cd backend
python -m pytest
```

前端构建：

```bash
cd frontend
npm run build
```

### 本轮产出

本轮完成后，项目已经具备：

1. 可构建的 Vue 3 前端骨架。
2. 可测试的 FastAPI 后端骨架。
3. 前后端目录隔离。
4. 第一条后端自动化测试。
5. 后续开发记录文件 `Carryout.md`。

---




## Round 2 - 用户认证系统

### 本轮目标

本轮进入 `study.md` 的第 2 阶段：用户系统。

这一轮不是只写一个登录接口，而是先把后端用户认证的基础链路搭完整：

1. 建立 SQLite 数据库连接。
2. 创建 `users` 用户表模型。
3. 实现注册接口。
4. 实现登录接口。
5. 实现 JWT 签发。
6. 实现 bcrypt 密码哈希。
7. 实现 `/api/auth/me` 当前用户接口。
8. 给认证链路补自动化测试。

### 本轮新增和修改的文件

#### `docs/superpowers/plans/2026-05-14-auth-system.md`

用途：

这是本轮用户认证系统的实施计划文件。它记录本轮要做哪些任务、每个任务涉及哪些文件、测试先写什么、实现顺序是什么。这个文件的价值是把“下一步做什么”固定下来，避免开发过程中边想边改导致结构混乱。

后续如果你忘记这一轮为什么这么拆，可以先看这个计划文件。

#### `backend/tests/conftest.py`

用途：

这是 pytest 的测试夹具文件，用来给认证测试准备一个隔离的测试环境。

它主要做三件事：

1. 创建一个临时 SQLite 内存数据库。
2. 创建所有 SQLAlchemy 表。
3. 覆盖 FastAPI 的 `get_db` 数据库依赖，让测试接口访问测试数据库，而不是访问真实开发数据库。

为什么要这样做：

认证接口会写入用户数据。如果测试直接使用真实数据库，测试之间会互相污染，比如第一个测试注册了邮箱，第二个测试再注册同一个邮箱就会失败。使用独立测试数据库后，每个测试都有干净环境，测试结果更稳定。

#### `backend/tests/test_auth.py`

用途：

这是用户认证模块的自动化测试文件。

它覆盖了 5 条核心业务链路：

1. 注册新用户成功，并返回 JWT。
2. 重复邮箱注册时返回 `409`。
3. 使用正确邮箱和密码登录成功，并返回 JWT。
4. 使用错误账号或密码登录时返回 `401`。
5. 带着 Bearer Token 请求 `/api/auth/me`，能拿到当前登录用户信息。

为什么先写这个文件：

这一轮采用测试先行方式。先用测试定义“认证系统应该表现成什么样”，再实现后端代码。这样可以避免接口写完后才发现返回结构、状态码或认证逻辑不符合预期。

#### `backend/app/db/__init__.py`

用途：

这是 `app.db` 包的初始化文件。它本身没有业务代码，作用是告诉 Python：`app/db` 是一个可以被导入的模块目录。后续数据库连接、迁移、基础模型都会放在这个目录下。

#### `backend/app/db/base.py`

用途：

这是 SQLAlchemy ORM 的基础模型文件。

它定义了 `Base`，所有 ORM 模型都要继承这个 `Base`。例如本轮新增的 `User` 模型就是基于它创建数据库表结构。

这个文件还导入了 `app.models.user.User`，目的是让 `Base.metadata.create_all()` 能够知道项目里有哪些模型需要建表。

为什么需要它：

如果没有统一的 `Base`，后续 `users`、`trips`、`tasks`、`chat_messages` 等表就没有统一的模型注册入口，数据库初始化会变得混乱。

#### `backend/app/db/session.py`

用途：

这是数据库连接和会话管理文件。

它主要提供：

1. `engine`：SQLAlchemy 连接数据库的核心对象。
2. `SessionLocal`：用于创建数据库会话。
3. `get_db()`：FastAPI 依赖函数，每次接口请求时创建一个数据库会话，请求结束后关闭。

为什么要单独拆这个文件：

接口层不应该直接关心数据库怎么连接。后续所有需要访问数据库的接口，只需要依赖 `get_db()`。这样数据库从 SQLite 换成 MySQL 时，主要改这个文件和配置即可。

#### `backend/app/models/__init__.py`

用途：

这是 `app.models` 包的初始化文件。当前没有业务逻辑，作用是让 `app/models` 成为 Python 模块目录。后续用户表、行程表、任务表、聊天表等 ORM 模型都会放在这里。

#### `backend/app/models/user.py`

用途：

这是用户表的 SQLAlchemy ORM 模型文件。

它定义了 `User` 类，对应数据库中的 `users` 表。

当前字段包括：

1. `id`：用户主键。
2. `username`：用户名。
3. `email`：邮箱，唯一索引，用于登录。
4. `password_hash`：密码哈希值，不保存明文密码。
5. `is_guest`：是否游客用户，后续支持匿名用户迁移时会用到。
6. `guest_uid`：游客唯一标识，后续游客模式使用。
7. `created_at`：创建时间。
8. `updated_at`：更新时间。

为什么现在就保留 `is_guest` 和 `guest_uid`：

`study.md` 里后续会做“匿名用户体验 + 注册后数据迁移”。提前把字段放进用户模型，可以让后续升级游客模式时不需要大改用户表结构。

#### `backend/app/schemas/__init__.py`

用途：

这是 `app.schemas` 包的初始化文件。`schemas` 目录用来放 Pydantic 请求和响应模型。它负责定义接口的输入输出数据格式，不直接访问数据库。

#### `backend/app/schemas/auth.py`

用途：

这是认证接口的数据结构定义文件。

它定义了：

1. `RegisterRequest`：注册接口请求体，包括用户名、邮箱、密码。
2. `LoginRequest`：登录接口请求体，包括邮箱、密码。
3. `UserResponse`：返回给前端的用户信息，不包含密码哈希。
4. `AuthResponse`：注册和登录成功后的响应结构，包括 `access_token`、`token_type` 和 `user`。

为什么要用 schema：

接口不能直接把 ORM 模型原样返回给前端，因为 ORM 里有 `password_hash` 这种敏感字段。用 `UserResponse` 可以明确控制返回什么，避免泄露密码哈希。

#### `backend/app/core/security.py`

用途：

这是认证安全工具文件。

它集中处理和安全相关的逻辑：

1. `hash_password()`：把明文密码转换成 bcrypt 哈希。
2. `verify_password()`：校验用户输入的密码是否匹配数据库中的哈希。
3. `create_access_token()`：根据用户 ID 生成 JWT。
4. `get_current_user()`：从请求头 Bearer Token 中解析当前用户。
5. `oauth2_scheme`：FastAPI 用来读取 Authorization 请求头的工具。

为什么要单独放到 `core/security.py`：

密码哈希和 token 签发是通用基础能力。后续聊天记录、行程历史、收藏接口都要用 `get_current_user()` 做鉴权，所以不能把它们写死在 `auth.py` 路由里。

#### `backend/app/services/__init__.py`

用途：

这是 `app.services` 包的初始化文件。`services` 目录用来放业务逻辑。它位于接口层和数据库模型之间，负责组织具体业务行为。

#### `backend/app/services/auth_service.py`

用途：

这是认证业务逻辑文件。

它提供：

1. `get_user_by_email()`：根据邮箱查询用户。
2. `register_user()`：创建新用户，并保存密码哈希。
3. `authenticate_user()`：验证邮箱和密码是否正确。

为什么不直接写在路由里：

路由层应该负责 HTTP 输入输出，例如状态码、请求体、响应模型。真正的业务逻辑放在 service 层，后续如果 Gradio 演示页、后台任务或其他接口也需要创建/验证用户，可以复用这里的函数。

#### `backend/app/api/routes/auth.py`

用途：

这是认证接口路由文件。

它新增了 3 个接口：

1. `POST /api/auth/register`：注册用户。
2. `POST /api/auth/login`：用户登录。
3. `GET /api/auth/me`：获取当前登录用户。

它还包含 `build_auth_response()`，用于统一生成注册和登录成功后的返回结构。

当前接口行为：

1. 注册成功返回 `201`。
2. 邮箱重复返回 `409`。
3. 登录成功返回 `200`。
4. 登录失败返回 `401`。
5. `/me` 没有合法 token 时会返回认证失败。

#### `backend/app/core/config.py`

修改用途：

本轮在配置中新增了认证和数据库相关字段：

1. `database_url`：数据库连接地址，当前默认使用 SQLite。
2. `jwt_secret_key`：JWT 签名密钥。
3. `jwt_algorithm`：JWT 加密算法，当前使用 `HS256`。
4. `access_token_expire_minutes`：token 有效期，当前默认 1 天。

为什么放在配置文件：

这些值在开发环境、测试环境、生产环境可能不同。集中放在 `Settings` 里，后续可以用 `.env` 覆盖，而不需要改业务代码。

#### `backend/app/main.py`

修改用途：

本轮在 FastAPI 应用启动组装中新增：

1. 导入并注册 `auth_router`。
2. 导入 `Base` 和 `engine`。
3. 调用 `Base.metadata.create_all(bind=engine)` 创建数据库表。

为什么这里直接 `create_all`：

当前项目还在学习和 MVP 阶段，直接自动建表最简单。等项目进入更正式阶段，可以再引入 Alembic 做数据库迁移管理。

#### `backend/requirements.txt`

修改用途：

本轮新增了认证和数据库依赖：

1. `SQLAlchemy`：ORM 和数据库访问。
2. `passlib[bcrypt]`：密码哈希。
3. `bcrypt==4.0.1`：bcrypt 后端实现，固定版本是为了兼容 `passlib==1.7.4`。
4. `python-jose[cryptography]`：JWT 编码和解码。
5. `email-validator`：让 Pydantic 的 `EmailStr` 能校验邮箱格式。

### 认证流程说明

#### 注册流程

1. 前端请求 `POST /api/auth/register`。
2. 后端用 `RegisterRequest` 校验用户名、邮箱、密码格式。
3. `auth_service.get_user_by_email()` 检查邮箱是否已存在。
4. 如果邮箱已存在，返回 `409`。
5. 如果邮箱不存在，用 `hash_password()` 对密码做 bcrypt 哈希。
6. 创建 `User` 记录并写入数据库。
7. 用 `create_access_token()` 生成 JWT。
8. 返回 token 和用户基础信息。

#### 登录流程

1. 前端请求 `POST /api/auth/login`。
2. 后端用 `LoginRequest` 校验邮箱和密码格式。
3. `authenticate_user()` 根据邮箱查询用户。
4. 使用 `verify_password()` 校验明文密码和密码哈希是否匹配。
5. 校验失败返回 `401`。
6. 校验成功返回 JWT 和用户基础信息。

#### 当前用户流程

1. 前端请求 `GET /api/auth/me`。
2. 请求头携带 `Authorization: Bearer <token>`。
3. `get_current_user()` 解析 token。
4. 从 token 的 `sub` 字段取出用户 ID。
5. 根据用户 ID 查询数据库。
6. 查询成功后返回当前用户信息。





### 本轮调试记录

第一次安装 `requirements.txt` 时命令超时，随后检查发现：

1. `SQLAlchemy` 已存在。
2. `passlib`、`python-jose`、`email-validator` 不存在。

于是改为单独安装缺失依赖。

之后运行认证测试时出现 bcrypt 兼容问题：

```text
ValueError: password cannot be longer than 72 bytes
```

根因：

`passlib==1.7.4` 和 `bcrypt==5.0.0` 存在兼容问题。`passlib` 在初始化 bcrypt 后端时会使用内部探测逻辑，bcrypt 5 对超长密码更严格，导致初始化阶段抛错。

处理方式：

把 `bcrypt` 显式固定为 `4.0.1`。

处理后认证测试全部通过。

### TDD 记录

本轮先写测试：

1. `backend/tests/conftest.py`
2. `backend/tests/test_auth.py`

第一次运行：

```bash
cd backend
python -m pytest tests/test_auth.py -v
```

失败原因：

```text
ModuleNotFoundError: No module named 'app.db.base'
```

这个失败符合预期，因为数据库层和认证路由还未实现。

随后实现数据库、模型、schema、安全工具、service 和路由。

修复依赖兼容问题后，再次运行认证测试，5 个认证测试全部通过。

### 验证方式

后端测试：

```bash
cd backend
python -m pytest
```

前端构建：

```bash
cd frontend
npm run build
```

### 本轮产出

本轮完成后，后端已经具备基础用户认证能力：

1. 用户可以注册。
2. 用户可以登录。
3. 密码不会明文入库，只保存 bcrypt 哈希。
4. 注册和登录成功后会返回 JWT。
5. 前端后续可以带 Bearer Token 请求需要登录的接口。
6. `/api/auth/me` 可以识别当前登录用户。
7. 认证接口有自动化测试覆盖。

### 下一轮计划

下一轮建议进入前端认证接入：

1. 创建前端 auth API 封装。
2. 扩展 Pinia store 保存 token 和用户信息。
3. 增加登录/注册页面。
4. 调用后端注册、登录、`/me` 接口。
5. 给需要登录的页面预留路由守卫。

完成这一步后，项目就会有真正的前后端登录闭环。

---

## Round 3 - 聊天基础功能

### 新增/修改文件及作用

1. `docs/superpowers/plans/2026-05-14-chat-foundation.md`：第三阶段实施计划，记录聊天基础功能的任务拆分。
2. `backend/tests/test_chat.py`：聊天接口测试，覆盖创建会话、按用户隔离会话、SSE 回复和消息持久化。
3. `backend/app/models/chat.py`：新增 `ChatSession` 和 `ChatMessage` ORM 模型，对应会话表和消息表。
4. `backend/app/schemas/chat.py`：聊天模块 Pydantic 入参/出参模型。
5. `backend/app/services/chat_service.py`：聊天业务逻辑，负责会话查询、消息保存和当前阶段的模拟助手回复。
6. `backend/app/api/routes/chat.py`：聊天接口路由，提供会话创建、会话列表、消息列表和 SSE 流式回复接口。
7. `backend/app/db/base.py`：注册聊天模型，确保自动建表时包含 `chat_sessions` 和 `chat_messages`。
8. `backend/app/main.py`：注册聊天路由到 FastAPI 应用。
9. `frontend/src/api/http.ts`：前端通用 API 请求封装。
10. `frontend/src/api/chat.ts`：前端聊天 API 封装，包含会话接口、消息接口和 SSE 读取逻辑。
11. `frontend/src/stores/app.ts`：扩展 token/user 状态，为聊天接口调用预留认证信息。
12. `frontend/src/views/ChatView.vue`：将聊天占位页改为可创建会话、发送消息、显示流式回复的页面。

### 验证

1. `cd backend && python -m pytest`
2. `cd frontend && npm run build`

---

## Round 9 - 本地运行联调

### 本轮主要目的

修复本地启动时暴露的运行时问题，并确认项目已经能打开网页、注册登录、提交行程规划、查询任务结果。

### 新增/修改文件及作用

1. `backend/app/db/base.py`：移除模型反向导入，避免 uvicorn 启动时循环导入。
2. `backend/app/db/init_models.py`：集中导入 ORM 模型，保证 `create_all` 建表时能注册所有模型。
3. `backend/app/main.py`：加载 `init_models`，修复后端启动建表链路。
4. `frontend/package.json`：固定 `npm run dev` 的 host 和 port，方便直接访问 `http://127.0.0.1:5173`。

### 验证

1. `cd backend && python -m pytest`
2. `cd frontend && npm run build`
3. `http://127.0.0.1:8000/api/health`
4. `http://127.0.0.1:5173`
5. 注册用户后调用 `POST /api/trips/plan-async`，再用 `GET /api/tasks/{task_id}` 查询结果。

---

## Round 8 - 前端认证接入

### 本轮主要目的

打通前端注册/登录流程，让聊天和行程页面可以通过真实登录态访问后端受保护接口。

### 新增/修改文件及作用

1. `docs/superpowers/plans/2026-05-14-frontend-auth.md`：第八阶段实施计划。
2. `frontend/src/api/auth.ts`：前端认证 API 封装，包含注册、登录和获取当前用户。
3. `frontend/src/stores/app.ts`：扩展认证状态，保存 token/user，并支持登录恢复和退出。
4. `frontend/src/views/AuthView.vue`：新增登录/注册页面。
5. `frontend/src/router/index.ts`：新增 `/auth` 路由，并给聊天、行程页添加登录守卫。
6. `frontend/src/main.ts`：整理 Vue 应用和 Pinia 初始化。
7. `frontend/src/App.vue`：顶部导航显示登录入口、当前用户和退出按钮。
8. `frontend/src/views/ChatView.vue`：未登录提示改为正式登录引导。
9. `frontend/src/views/TripsView.vue`：未登录提示改为正式登录引导。

### 验证

1. `cd backend && python -m pytest`
2. `cd frontend && npm run build`

---

## Round 7 - 异步任务与轮询

### 本轮主要目的

新增任务式行程规划协议：提交规划请求先返回 `task_id`，再通过任务接口查询状态和结果，为后续真正后台队列打基础。

### 新增/修改文件及作用

1. `docs/superpowers/plans/2026-05-14-async-trip-tasks.md`：第七阶段实施计划。
2. `backend/tests/test_tasks.py`：任务接口测试，覆盖异步提交、轮询结果、用户隔离和未登录拦截。
3. `backend/app/models/task.py`：新增 `Task` ORM 模型，用于保存任务状态、输入和输出。
4. `backend/app/schemas/task.py`：任务提交和任务详情响应模型。
5. `backend/app/services/task_service.py`：任务创建、完成、失败和查询逻辑。
6. `backend/app/api/routes/tasks.py`：任务轮询路由，提供 `GET /api/tasks/{task_id}`。
7. `backend/app/api/routes/trips.py`：新增 `POST /api/trips/plan-async`。
8. `backend/app/db/base.py`：注册 `Task` 模型。
9. `backend/app/main.py`：注册任务路由到 FastAPI 应用。

### 验证

1. `cd backend && python -m pytest`
2. `cd frontend && npm run build`

---

## Round 6 - 多 Agent 行程编排

### 本轮主要目的

把行程规划从单个 service 拼装升级为 `Planner Agent + 3 个 Search Agent` 的清晰架构，为后续接入 LangChain/LangGraph 做铺垫。

### 新增/修改文件及作用

1. `docs/superpowers/plans/2026-05-14-agent-orchestration.md`：第六阶段实施计划。
2. `backend/tests/test_trip_agents.py`：Planner Agent 编排测试，确认 3 个 Search Agent 都参与生成结果。
3. `backend/tests/test_trips.py`：补充断言 `agent_trace`，保证 API 返回可解释的 Agent 执行轨迹。
4. `backend/app/agents/__init__.py`：Agent 包初始化文件。
5. `backend/app/agents/search_agents.py`：封装 Weather、POI、Route 三个 Search Agent。
6. `backend/app/agents/planner_agent.py`：Planner Agent，负责调用三个 Search Agent 并生成最终 itinerary。
7. `backend/app/schemas/trip.py`：为 itinerary 增加 `agent_trace` 字段。
8. `backend/app/services/trip_service.py`：改为委托 Planner Agent 生成行程。

### 验证

1. `cd backend && python -m pytest`
2. `cd frontend && npm run build`

---



## Round 4 - 旅行工具封装

### 新增/修改文件及作用

1. `docs/superpowers/plans/2026-05-14-travel-tools.md`：第四阶段实施计划，记录旅行工具接口的任务拆分。
2. `backend/tests/test_tools.py`：旅行工具接口测试，覆盖地点搜索、天气查询、路线规划和未登录拦截。
3. `backend/app/schemas/tools.py`：旅行工具请求和响应模型。
4. `backend/app/tools/__init__.py`：旅行工具包初始化文件。
5. `backend/app/tools/amap_client.py`：高德 Web 服务 API 客户端，封装地点、天气、路线请求。
6. `backend/app/services/travel_tool_service.py`：旅行工具业务层，统一高德结果格式，并在无 API Key 时返回 fallback。
7. `backend/app/api/routes/tools.py`：旅行工具路由，提供 `/api/tools/places/search`、`/api/tools/weather`、`/api/tools/routes`。
8. `backend/app/core/config.py`：新增高德 API Key、基础地址和外部 API 超时配置。
9. `backend/app/main.py`：注册旅行工具路由到 FastAPI 应用。

### 验证

1. `cd backend && python -m pytest`
2. `cd frontend && npm run build`




## Round 5 - 行程规划 MVP

### 本轮主要目的

打通第一版“提交旅行参数 -> 生成结构化行程 -> 保存行程 -> 前端展示结果”的完整闭环。

### 新增/修改文件及作用

1. `docs/superpowers/plans/2026-05-14-trip-planning-mvp.md`：第五阶段实施计划。
2. `backend/tests/test_trips.py`：行程规划接口测试，覆盖生成、列表、详情和未登录拦截。
3. `backend/app/models/trip.py`：新增 `Trip` ORM 模型，用于保存行程规划结果。
4. `backend/app/schemas/trip.py`：行程规划请求、响应和 itinerary 结构模型。
5. `backend/app/services/trip_service.py`：行程规划业务层，组合天气、地点、路线工具生成 MVP 行程。
6. `backend/app/api/routes/trips.py`：行程接口路由，提供 `/api/trips/plan`、`/api/trips`、`/api/trips/{trip_id}`。
7. `backend/app/db/base.py`：注册 `Trip` 模型，保证自动建表包含 `trips`。
8. `backend/app/main.py`：注册行程路由到 FastAPI 应用。
9. `frontend/src/api/trips.ts`：前端行程 API 封装。
10. `frontend/src/views/TripsView.vue`：行程页从占位页改为可提交表单并展示结构化 itinerary。

### 验证

1. `cd backend && python -m pytest`
2. `cd frontend && npm run build`

---
