# 📝 配置指南 / Configuration Guide

[English](#english) | [中文](#中文)

---

## 中文

### 管理后台路由前缀配置

为了提高安全性，管理后台使用了隐藏路由。您可以自定义管理路由前缀，使其更难被猜测。

#### ⚠️ 重要说明

**后端和前端的管理路由前缀必须保持一致！**

- 后端配置：`backend/.env` 中的 `ADMIN_ROUTE_PREFIX`
- 前端配置：`frontend/.env` 中的 `VITE_ADMIN_ROUTE_PREFIX`

#### 配置步骤

##### 1. 配置后端

编辑 `backend/.env`：

```bash
# 管理路由前缀（建议改为随机路径）
ADMIN_ROUTE_PREFIX=/admin-abc123xyz
```

##### 2. 配置前端

编辑 `frontend/.env`：

```bash
# 管理后台路由前缀 - 必须与后端保持一致
VITE_ADMIN_ROUTE_PREFIX=/admin-abc123xyz
```

##### 3. 重启服务

```bash
# 停止服务
./deploy.sh stop

# 重新构建并启动（会自动重新构建前端）
./deploy.sh start
```

#### 访问管理后台

配置完成后，您的管理后台地址将变为：

```
http://your-domain.com/admin-abc123xyz
```

#### 安全建议

1. **使用随机字符串**：建议使用包含字母、数字的随机字符串
   - ✅ 好的示例：`/console-k9m2x7p`, `/admin-xyz789abc`
   - ❌ 不好的示例：`/admin`, `/console`, `/backend`

2. **足够长度**：建议至少 8-15 个字符

3. **生成随机路径**：
   ```bash
   # 使用 Python 生成随机路径
   python3 -c "import secrets; print('/admin-' + secrets.token_hex(6))"
   # 输出示例: /admin-3f8d2a1b4e9c
   ```

4. **定期更换**：建议每隔一段时间更换管理路由前缀

---

## English

### Admin Panel Route Prefix Configuration

For enhanced security, the admin panel uses a hidden route. You can customize the admin route prefix to make it harder to guess.

#### ⚠️ Important Notice

**The admin route prefix must be consistent between backend and frontend!**

- Backend config: `ADMIN_ROUTE_PREFIX` in `backend/.env`
- Frontend config: `VITE_ADMIN_ROUTE_PREFIX` in `frontend/.env`

#### Configuration Steps

##### 1. Configure Backend

Edit `backend/.env`:

```bash
# Admin route prefix (recommended to use random path)
ADMIN_ROUTE_PREFIX=/admin-abc123xyz
```

##### 2. Configure Frontend

Edit `frontend/.env`:

```bash
# Admin panel route prefix - must match backend
VITE_ADMIN_ROUTE_PREFIX=/admin-abc123xyz
```

##### 3. Restart Services

```bash
# Stop services
./deploy.sh stop

# Rebuild and start (will automatically rebuild frontend)
./deploy.sh start
```

#### Access Admin Panel

After configuration, your admin panel URL will be:

```
http://your-domain.com/admin-abc123xyz
```

#### Security Recommendations

1. **Use Random Strings**: Recommended to use random combinations of letters and numbers
   - ✅ Good examples: `/console-k9m2x7p`, `/admin-xyz789abc`
   - ❌ Bad examples: `/admin`, `/console`, `/backend`

2. **Sufficient Length**: Recommended at least 8-15 characters

3. **Generate Random Path**:
   ```bash
   # Use Python to generate random path
   python3 -c "import secrets; print('/admin-' + secrets.token_hex(6))"
   # Example output: /admin-3f8d2a1b4e9c
   ```

4. **Regular Rotation**: Recommended to change the admin route prefix periodically

---

## 常见问题 / FAQ

### 中文

**Q: 修改配置后无法访问管理后台？**

A: 请检查：
1. 后端和前端的路由前缀是否一致
2. 是否重新构建了前端（`./deploy.sh build` 或 `./deploy.sh restart`）
3. 查看浏览器控制台是否有 404 错误

**Q: 忘记了管理路由前缀怎么办？**

A: 查看配置文件：
```bash
cat backend/.env | grep ADMIN_ROUTE_PREFIX
cat frontend/.env | grep VITE_ADMIN_ROUTE_PREFIX
```

**Q: 是否需要同时修改 Nginx 配置？**

A: 不需要。Nginx 会将所有请求转发到前端，前端路由会自动处理。

### English

**Q: Cannot access admin panel after changing configuration?**

A: Please check:
1. Are backend and frontend route prefixes identical?
2. Did you rebuild the frontend? (`./deploy.sh build` or `./deploy.sh restart`)
3. Check browser console for 404 errors

**Q: Forgot the admin route prefix?**

A: Check configuration files:
```bash
cat backend/.env | grep ADMIN_ROUTE_PREFIX
cat frontend/.env | grep VITE_ADMIN_ROUTE_PREFIX
```

**Q: Do I need to modify Nginx configuration?**

A: No. Nginx forwards all requests to the frontend, which handles routing automatically.

---

## 技术细节 / Technical Details

### 中文

管理路由前缀的工作原理：

1. **后端**：`backend/config.py` 从环境变量读取 `ADMIN_ROUTE_PREFIX`，所有管理 API 路由都加上此前缀
2. **前端路由**：`frontend/src/router/index.js` 从环境变量读取 `VITE_ADMIN_ROUTE_PREFIX`，配置管理页面路由
3. **前端 API**：`frontend/src/api/index.js` 使用同样的前缀构建管理 API 请求路径

### English

How admin route prefix works:

1. **Backend**: `backend/config.py` reads `ADMIN_ROUTE_PREFIX` from env vars, all admin API routes use this prefix
2. **Frontend Router**: `frontend/src/router/index.js` reads `VITE_ADMIN_ROUTE_PREFIX` from env vars to configure admin page routes
3. **Frontend API**: `frontend/src/api/index.js` uses the same prefix to build admin API request paths

---

**配置有问题？请查看 [DEPLOY.md](DEPLOY.md) 或提交 Issue。**

**Having configuration issues? Please check [DEPLOY.md](DEPLOY.md) or submit an Issue.**
