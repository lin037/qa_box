# QA Box Frontend

基于 Vue 3 + Vite + TailwindCSS 构建的匿名提问箱前端应用。

## 技术栈

- **Vue 3** - 使用 Composition API
- **Vite** - 快速的前端构建工具
- **TailwindCSS** - 实用优先的 CSS 框架
- **Vue Router** - 路由管理
- **Axios** - HTTP 客户端

## 开发

```bash
# 安装依赖
pnpm install  # 或 npm install

# 启动开发服务器
pnpm dev      # 或 npm run dev

# 访问 http://localhost:5173
```

## 构建

```bash
# 生产构建
pnpm build    # 或 npm run build

# 预览构建结果
pnpm preview  # 或 npm run preview
```

## 环境变量配置

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

### 配置项说明

```bash
# 后端服务地址（用于开发时的代理）
VITE_BACKEND_HOST=127.0.0.1
VITE_BACKEND_PORT=18000

# 管理后台路由前缀
# 重要：必须与后端 ADMIN_ROUTE_PREFIX 保持一致
# 修改后需重新构建：pnpm build
VITE_ADMIN_ROUTE_PREFIX=/console-x7k9m
```

**⚠️ 重要提示：**

修改 `VITE_ADMIN_ROUTE_PREFIX` 后，必须重新构建前端才能生效：

```bash
pnpm build
# 或
npm run build
```

## 项目结构

```
src/
├── api/                  # API 接口封装
│   └── index.js         # 问题相关 API
├── utils/               # 工具函数
│   └── request.js       # Axios 请求封装
├── views/               # 页面组件
│   ├── AskPage.vue      # 提问页面
│   ├── AdminLogin.vue   # 管理员登录
│   └── AdminPage.vue    # 管理后台
├── router/              # 路由配置
│   └── index.js
├── App.vue              # 根组件
├── main.js              # 入口文件
└── style.css            # 全局样式
```

## 部署

详见项目根目录的 [DEPLOY.md](../DEPLOY.md)
