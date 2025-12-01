# 🚀 QA Box 部署教程

本文档提供详细的生产环境部署指南，适用于 Linux 服务器（Ubuntu/Debian/CentOS）。

## 📋 目录

- [前置准备](#-前置准备)
- [服务器配置](#-服务器配置)
- [项目部署](#-项目部署)
- [Nginx 配置](#-nginx-配置)
- [HTTPS 配置](#-https-配置)
- [进程管理](#-进程管理)
- [备份策略](#-备份策略)
- [常见问题](#-常见问题)

---

## 📦 前置准备

### 服务器要求

| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | 1 核 | 2 核 |
| 内存 | 1GB | 2GB |
| 磁盘 | 10GB | 20GB+ |
| 系统 | Ubuntu 20.04+ | Ubuntu 22.04 LTS |

### 软件依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    nginx

# 安装 Node.js (使用 NodeSource)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 安装 pnpm (可选，也可用 npm)
npm install -g pnpm
```

---

## 🛠️ 服务器配置

### 1. 创建专用用户（推荐）

```bash
# 创建用户
sudo useradd -m -s /bin/bash qabox
sudo passwd qabox

# 授予必要权限
sudo usermod -aG sudo qabox

# 切换到该用户
su - qabox
```

### 2. 配置防火墙

```bash
# 启用 UFW
sudo ufw enable

# 开放必要端口
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS

# 查看状态
sudo ufw status
```

---

## 📥 项目部署

### 1. 克隆项目

```bash
# 进入工作目录
cd ~

# 克隆项目
git clone https://github.com/yourusername/qa_box.git
cd qa_box
```

### 2. 配置环境变量

#### 后端配置

```bash
# 复制示例配置
cp backend/.env.example backend/.env

# 编辑配置文件
nano backend/.env
```

**重要配置项**（必须修改）：

```bash
# 生成 SECRET_KEY (使用 Python)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# 将输出复制到下面

SECRET_KEY=<生成的密钥>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<设置强密码>
ADMIN_ROUTE_PREFIX=/console-<随机字符串>

# 服务器配置
HOST=127.0.0.1              # 仅本地访问（Nginx 反向代理）
PORT=18000
FRONTEND_PORT=13000
WORKERS=2                   # 根据 CPU 核数调整

# 备份配置
BACKUP_INTERVAL_HOURS=24
BACKUP_MAX_COUNT=7
```

#### 前端配置

```bash
# 复制示例配置
cp frontend/.env.example frontend/.env

# 编辑配置文件
nano frontend/.env
```

**重要配置项**：

```bash
# 后端服务地址
VITE_BACKEND_HOST=127.0.0.1
VITE_BACKEND_PORT=18000

# 管理后台路由前缀 - 必须与后端 ADMIN_ROUTE_PREFIX 保持一致！
VITE_ADMIN_ROUTE_PREFIX=/console-<随机字符串>
```

**⚠️ 重要提示：**
- 后端的 `ADMIN_ROUTE_PREFIX` 和前端的 `VITE_ADMIN_ROUTE_PREFIX` **必须完全一致**
- 修改管理路由前缀后，需重新构建前端（部署脚本会自动处理）

### 3. 一键部署

```bash
# 赋予执行权限
chmod +x deploy.sh

# 启动服务
./deploy.sh start
```

部署脚本会自动：
- ✅ 创建 Python 虚拟环境
- ✅ 安装后端依赖
- ✅ 安装前端依赖
- ✅ 构建前端项目
- ✅ 启动后端服务（Gunicorn + Uvicorn Workers）
- ✅ 启动前端服务（Vite Preview）

### 4. 验证服务

```bash
# 查看服务状态
./deploy.sh status

# 查看日志
./deploy.sh logs

# 测试访问
curl http://localhost:13000
curl http://localhost:18000/api/public/questions
```

---

## 🌐 Nginx 配置

### 1. 创建配置文件

```bash
sudo nano /etc/nginx/sites-available/qabox
```

**基础配置**（HTTP）：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 修改为你的域名

    # 访问日志
    access_log /var/log/nginx/qabox_access.log;
    error_log /var/log/nginx/qabox_error.log;

    # 客户端最大上传大小
    client_max_body_size 50M;

    # 前端静态文件
    location / {
        proxy_pass http://127.0.0.1:13000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 后端 API
    location /api {
        proxy_pass http://127.0.0.1:18000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 上传文件
    location /uploads {
        proxy_pass http://127.0.0.1:18000;
        proxy_set_header Host $host;
        
        # 缓存设置
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 2. 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/qabox /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 3. 高级配置（可选）

<details>
<summary>点击展开高级配置</summary>

**限制管理后台访问 IP**：

```nginx
# 在 server 块中添加
location ~ ^/console- {
    # 只允许特定 IP 访问
    allow 1.2.3.4;        # 你的 IP
    allow 5.6.7.8/24;     # IP 段
    deny all;
    
    proxy_pass http://127.0.0.1:13000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

**启用 Gzip 压缩**：

```nginx
# 在 server 块中添加
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript 
           application/json application/javascript application/xml+rss 
           application/rss+xml font/truetype font/opentype 
           application/vnd.ms-fontobject image/svg+xml;
```

**静态资源缓存**：

```nginx
# 在 server 块中添加
location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff|woff2|ttf|svg)$ {
    proxy_pass http://127.0.0.1:13000;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

</details>

---

## 🔒 HTTPS 配置

### 使用 Let's Encrypt（免费 SSL 证书）

Let's Encrypt 是一个免费、自动化、开放的证书颁发机构，提供免费的 SSL/TLS 证书。

#### 前置条件

1. **域名已解析**：确保你的域名 DNS 已正确指向服务器 IP
2. **Nginx 已运行**：HTTP (80 端口) 配置已完成
3. **防火墙开放**：80 和 443 端口已开放

```bash
# 检查域名解析
ping your-domain.com

# 检查 Nginx 配置
sudo nginx -t

# 确保防火墙开放端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

#### 安装 Certbot

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install -y certbot python3-certbot-nginx
```

#### 获取证书

**方法一：自动配置（推荐）**

Certbot 会自动修改 Nginx 配置，添加 HTTPS 支持：

```bash
# 单个域名
sudo certbot --nginx -d your-domain.com

# 多个域名（会申请一个证书覆盖所有域名）
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 交互式问答
# 1. 输入邮箱（用于证书过期提醒）
# 2. 同意服务条款（Y）
# 3. 是否接收新闻邮件（可选，N）
# 4. 选择重定向方式：
#    1: No redirect - HTTP 和 HTTPS 都可访问
#    2: Redirect - 自动将 HTTP 重定向到 HTTPS（推荐）
```

**方法二：手动配置**

只获取证书，不自动修改 Nginx 配置：

```bash
sudo certbot certonly --nginx -d your-domain.com

# 证书会保存在以下位置：
# 证书: /etc/letsencrypt/live/your-domain.com/fullchain.pem
# 私钥: /etc/letsencrypt/live/your-domain.com/privkey.pem
```

然后手动修改 Nginx 配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    # HTTP 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL 安全配置（推荐）
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # HSTS (可选，强制 HTTPS)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # OCSP Stapling（可选，提升性能）
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/your-domain.com/chain.pem;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # ... 其他配置同上
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:13000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://127.0.0.1:18000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /uploads {
        proxy_pass http://127.0.0.1:18000;
        proxy_set_header Host $host;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 测试 HTTPS

```bash
# 重新加载 Nginx
sudo nginx -t
sudo systemctl reload nginx

# 访问测试
curl -I https://your-domain.com

# SSL 评级测试（可选）
# 访问 https://www.ssllabs.com/ssltest/ 输入你的域名
```

#### 自动续期

Let's Encrypt 证书有效期为 **90 天**，需要定期续期。

```bash
# 测试自动续期（不会真正续期）
sudo certbot renew --dry-run

# Certbot 会自动创建定时任务
# 查看定时任务
sudo systemctl list-timers | grep certbot

# 手动续期（可选）
sudo certbot renew

# 续期后重启 Nginx
sudo systemctl reload nginx
```

**自动续期 + 重启 Nginx**（添加钩子）：

```bash
# 编辑 Certbot 配置
sudo nano /etc/letsencrypt/renewal/your-domain.com.conf

# 在文件末尾添加
[renewalparams]
renew_hook = systemctl reload nginx

# 或者创建全局钩子脚本
sudo nano /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh
```

内容：

```bash
#!/bin/bash
systemctl reload nginx
```

赋予执行权限：

```bash
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh
```

#### 通配符证书（可选）

如果需要 `*.your-domain.com` 的通配符证书，需要使用 DNS 验证：

```bash
# 使用 DNS 插件（以 Cloudflare 为例）
sudo apt install python3-certbot-dns-cloudflare

# 创建 API token 配置文件
sudo nano /etc/letsencrypt/cloudflare.ini
```

内容：

```ini
dns_cloudflare_api_token = your_cloudflare_api_token
```

```bash
# 设置权限
sudo chmod 600 /etc/letsencrypt/cloudflare.ini

# 申请通配符证书
sudo certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
  -d your-domain.com \
  -d *.your-domain.com
```

---

## 🌐 多域名 / 多网站配置

如果你的服务器需要托管多个网站，可以通过 Nginx 的虚拟主机（Server Blocks）实现。

### 基本原理

- **单个 Nginx 实例**监听 80 和 443 端口
- 根据 `Host` 请求头（域名）分发到不同的后端服务
- 每个网站使用不同的端口或目录

### 配置示例

假设你有两个网站：
- `qa.example.com` - QA Box 项目（端口 13000/18000）
- `blog.example.com` - 博客系统（端口 14000）

#### 1. QA Box 配置

`/etc/nginx/sites-available/qabox`：

```nginx
server {
    listen 80;
    server_name qa.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name qa.example.com;

    ssl_certificate /etc/letsencrypt/live/qa.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/qa.example.com/privkey.pem;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:13000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://127.0.0.1:18000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 2. 博客配置

`/etc/nginx/sites-available/blog`：

```nginx
server {
    listen 80;
    server_name blog.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name blog.example.com;

    ssl_certificate /etc/letsencrypt/live/blog.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/blog.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:14000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 3. 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/qabox /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

#### 4. 申请多个 SSL 证书

```bash
# 分别为每个域名申请证书
sudo certbot --nginx -d qa.example.com
sudo certbot --nginx -d blog.example.com

# 或者一次性申请多个
sudo certbot --nginx -d qa.example.com -d blog.example.com
```

### 工作流程

```
用户访问 qa.example.com
    ↓
Nginx 监听 443 端口
    ↓
检查 Host 头 = qa.example.com
    ↓
匹配 server_name qa.example.com
    ↓
转发到 127.0.0.1:13000
```

```
用户访问 blog.example.com
    ↓
Nginx 监听 443 端口
    ↓
检查 Host 头 = blog.example.com
    ↓
匹配 server_name blog.example.com
    ↓
转发到 127.0.0.1:14000
```

### 关键点

1. **端口共享**：多个网站共用 80/443 端口，Nginx 根据域名分发
2. **后端端口隔离**：每个项目使用不同的本地端口（13000, 14000, etc.）
3. **独立 SSL 证书**：每个域名需要单独申请证书（或使用通配符证书）
4. **独立配置文件**：每个网站使用独立的 Nginx 配置文件，便于管理

### 高级配置

<details>
<summary>点击展开：子路径部署（不推荐）</summary>

如果你只有一个域名，可以通过子路径区分：

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    # QA Box - 访问 example.com/qa
    location /qa {
        rewrite ^/qa(/.*)$ $1 break;
        proxy_pass http://127.0.0.1:13000;
        proxy_set_header Host $host;
    }

    # Blog - 访问 example.com/blog
    location /blog {
        rewrite ^/blog(/.*)$ $1 break;
        proxy_pass http://127.0.0.1:14000;
        proxy_set_header Host $host;
    }
}
```

**注意**：这种方式需要修改前端路由配置（Vue Router 的 `base` 选项），较为复杂，不推荐使用。
</details>

---

## 🔄 进程管理

### 使用 deploy.sh 脚本（推荐）

```bash
# 启动服务
./deploy.sh start

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看状态
./deploy.sh status

# 查看日志
./deploy.sh logs 100  # 查看最近 100 行
```

### 使用 Systemd（开机自启）

创建 systemd 服务文件：

**后端服务** (`/etc/systemd/system/qabox-backend.service`)：

```ini
[Unit]
Description=QA Box Backend Service
After=network.target

[Service]
Type=forking
User=qabox
WorkingDirectory=/home/qabox/qa_box
Environment="PATH=/home/qabox/qa_box/backend/.venv/bin"
ExecStart=/home/qabox/qa_box/backend/.venv/bin/gunicorn backend.main:app \
    -k uvicorn.workers.UvicornWorker \
    -w 2 \
    -b 127.0.0.1:18000 \
    --daemon \
    --access-logfile /home/qabox/qa_box/backend.log \
    --error-logfile /home/qabox/qa_box/backend.log \
    --pid /home/qabox/qa_box/.backend.pid
ExecStop=/bin/kill -TERM $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**前端服务** (`/etc/systemd/system/qabox-frontend.service`)：

```ini
[Unit]
Description=QA Box Frontend Service
After=network.target

[Service]
Type=simple
User=qabox
WorkingDirectory=/home/qabox/qa_box/frontend
Environment="NODE_ENV=production"
ExecStart=/usr/bin/pnpm preview --host 0.0.0.0 --port 13000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**启用服务**：

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable qabox-backend
sudo systemctl enable qabox-frontend

# 启动服务
sudo systemctl start qabox-backend
sudo systemctl start qabox-frontend

# 查看状态
sudo systemctl status qabox-backend
sudo systemctl status qabox-frontend
```

---

## 💾 备份策略

### 自动备份

项目内置自动备份功能（在 `backend/.env` 中配置）：

```bash
BACKUP_INTERVAL_HOURS=24    # 每 24 小时自动备份
BACKUP_MAX_COUNT=7          # 保留最近 7 个备份
```

备份文件存储在 `backups/` 目录。

### 手动备份脚本

创建 `~/backup.sh`：

```bash
#!/bin/bash

BACKUP_DIR="/home/qabox/qa_box_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份数据库
cp /home/qabox/qa_box/qa_box.db "$BACKUP_DIR/qa_box_$TIMESTAMP.db"

# 备份上传文件
tar -czf "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" \
    -C /home/qabox/qa_box uploads/

# 删除 30 天前的备份
find "$BACKUP_DIR" -name "qa_box_*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "uploads_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $TIMESTAMP"
```

**设置定时任务**：

```bash
# 编辑 crontab
crontab -e

# 添加每天凌晨 2 点备份
0 2 * * * /home/qabox/backup.sh >> /home/qabox/backup.log 2>&1
```

### 远程备份（推荐）

**使用 rsync 同步到远程服务器**：

```bash
# 一次性配置
rsync -avz --progress \
    /home/qabox/qa_box_backups/ \
    user@backup-server:/path/to/backups/

# 添加到 crontab（每天同步）
0 3 * * * rsync -avz /home/qabox/qa_box_backups/ user@backup-server:/path/to/backups/
```

---

## 🔧 维护操作

### 更新项目

```bash
cd /home/qabox/qa_box

# 停止服务
./deploy.sh stop

# 拉取最新代码
git pull origin main

# 重启服务（会自动重新构建）
./deploy.sh restart
```

### 查看日志

```bash
# 后端日志
tail -f /home/qabox/qa_box/backend.log

# 前端日志
tail -f /home/qabox/qa_box/frontend.log

# Nginx 日志
sudo tail -f /var/log/nginx/qabox_access.log
sudo tail -f /var/log/nginx/qabox_error.log
```

### 性能监控

```bash
# 查看资源占用
htop

# 查看端口监听
sudo netstat -tlnp | grep -E '(18000|13000)'

# 查看进程
ps aux | grep -E '(gunicorn|node)'
```

---

## ❓ 常见问题

### 1. 端口被占用

**问题**：启动时提示端口已被占用

```bash
# 查找占用端口的进程
sudo lsof -i :18000
sudo lsof -i :13000

# 杀死进程
sudo kill -9 <PID>

# 或修改 .env 中的端口配置
```

### 2. 权限错误

**问题**：提示权限不足

```bash
# 确保文件所有权正确
sudo chown -R qabox:qabox /home/qabox/qa_box

# 确保上传目录可写
chmod 755 /home/qabox/qa_box/uploads
```

### 3. 前端页面空白

**问题**：访问前端显示空白页面

```bash
# 检查前端是否构建
ls -la frontend/dist/

# 如果没有，重新构建
./deploy.sh build

# 重启服务
./deploy.sh restart
```

### 4. 502 Bad Gateway

**问题**：Nginx 返回 502 错误

```bash
# 检查后端服务是否运行
./deploy.sh status

# 检查后端日志
tail -f backend.log

# 检查 Nginx 配置
sudo nginx -t

# 重启服务
./deploy.sh restart
sudo systemctl restart nginx
```

### 5. 数据库锁定

**问题**：SQLite database is locked

```bash
# 检查是否有多个进程访问数据库
ps aux | grep gunicorn

# 停止所有服务
./deploy.sh stop

# 确保没有残留进程
pkill -f gunicorn

# 重启
./deploy.sh start
```

### 6. 图片上传失败

**问题**：上传图片时失败

```bash
# 检查上传目录权限
ls -ld uploads/

# 确保 Nginx 配置正确
# client_max_body_size 应大于 50M

# 检查后端日志
tail -f backend.log
```

---

## 🎯 性能优化建议

### 1. 数据库优化

```bash
# 定期清理和优化数据库
sqlite3 qa_box.db "VACUUM;"
```

### 2. 启用 Swap（小内存服务器）

```bash
# 创建 2GB Swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 3. Nginx 缓存

在 Nginx 配置中添加缓存层：

```nginx
# 定义缓存路径
proxy_cache_path /var/cache/nginx/qabox levels=1:2 
                 keys_zone=qabox_cache:10m max_size=1g 
                 inactive=60m use_temp_path=off;

# 在 location /api 中添加
proxy_cache qabox_cache;
proxy_cache_valid 200 5m;
proxy_cache_bypass $http_cache_control;
add_header X-Cache-Status $upstream_cache_status;
```

---

## 📞 获取帮助

- 📖 查看 [README.md](README.md)

---

**祝部署顺利！如有问题，欢迎反馈。** 🎉
