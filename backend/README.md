# QA Box 后端服务

基于 FastAPI + SQLite 的匿名提问箱后端服务。

## 技术栈

- **FastAPI** - 现代高性能 Web 框架
- **SQLite** - 轻量级嵌入式数据库（使用 aiosqlite 异步驱动）
- **SQLAlchemy 2.0** - ORM 框架
- **JWT** - 用户认证和撤回机制

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 开发模式
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 或使用相对导入
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 访问 API

- API 文档: http://localhost:8000/docs
- 数据库文件: `./qa_box.db` (自动创建)
- 上传文件目录: `./uploads/` (自动创建)

## 数据库说明

使用 SQLite 替代 PostgreSQL 的优势：
- ✅ 零配置，无需额外安装数据库服务
- ✅ 单文件存储，备份和迁移简单
- ✅ 适合中小型应用（< 100k 请求/天）
- ✅ 部署方便，只需一个 `.db` 文件

数据库文件位置：`./qa_box.db`

### 备份数据库

```bash
# 简单复制即可
cp qa_box.db qa_box_backup_$(date +%Y%m%d).db
```

## API 端点

### 用户端点

- `POST /api/upload` - 上传图片
- `POST /api/questions` - 提交问题
- `POST /api/questions/revoke` - 撤回问题
- `GET /api/public/questions` - 获取公开问答列表

### 管理端点

- `GET /api/admin/questions` - 获取所有问题
- `POST /api/admin/questions/{id}/answer` - 回答问题

## 环境变量

创建 `.env` 文件（可选）：

```env
DATABASE_URL=sqlite+aiosqlite:///./qa_box.db
SECRET_KEY=your-secret-key-change-this-in-production
UPLOAD_DIR=uploads
```

## 生产部署

### 使用 Gunicorn + Uvicorn Workers

```bash
pip install gunicorn

gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 使用 Supervisor 守护进程

创建 `/etc/supervisor/conf.d/qa_box.conf`:

```ini
[program:qa_box]
directory=/path/to/qa_box/backend
command=/path/to/venv/bin/gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/qa_box.err.log
stdout_logfile=/var/log/qa_box.out.log
```

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /uploads {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

## 注意事项

1. **SECRET_KEY**: 生产环境务必修改为随机密钥
2. **CORS**: 在 `main.py` 中配置允许的前端域名
3. **文件上传**: 默认无大小限制，建议添加限制
4. **SQLite 并发**: SQLite 适合读多写少的场景，高并发写入可能成为瓶颈

## 数据迁移

如果未来需要从 SQLite 迁移到 PostgreSQL：

1. 修改 `config.py` 中的 `DATABASE_URL`
2. 修改 `models.py` 中的类型定义
3. 安装 `asyncpg` 替换 `aiosqlite`
4. 使用工具迁移数据（如 `sqlite3 .dump | psql`）
