# 🎯 QA Box - Anonymous Question Box

<div align="center">

An elegant anonymous question box web application that makes interaction more engaging.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Vue 3](https://img.shields.io/badge/vue-3.x-green.svg)](https://vuejs.org/)

[Live Demo](#) | [Quick Start](#-quick-start) | [Deployment Guide](DEPLOY.md)

</div>

---

## 📸 Screenshots

<div align="center">

### Question Page
![Question Interface](screenshots/screenshot-1.png)

### Admin Panel
![Admin Panel](screenshots/screenshot-2.png)

### Share Card
![Share Card](screenshots/screenshot-3.png)

</div>

## ✨ Key Features

### 🎨 User Experience
- **Beautiful Animations** - Mailbox drop animation effects for a more ceremonial questioning experience
- **Responsive Design** - Perfectly adapted for desktop and mobile
- **Real-time Feedback** - Question status updates in real-time with revoke support
- **Share Cards** - Generate beautiful Q&A share cards with one click

### 📷 Image Functionality
- **Image Upload** - Support uploading images in questions and answers (up to 9 images)
- **Smart Limits** - Frontend: 10MB/image, 50MB/batch; Admin: no limit
- **Weekly Storage** - Automatically organize uploaded files by week
- **Image Compression** - Auto-compress when exporting cards for faster generation

### 🔒 Security Mechanisms
- **JWT Authentication** - Questioners can revoke unanswered questions with token
- **Admin Panel** - Password protection + automatic token renewal
- **Hidden Routes** - Customizable admin panel path, defaults to `/console-x7k9m`
- **Backend Validation** - Dual image size validation (frontend + backend)

### 💾 Data Management
- **Auto Backup** - Scheduled automatic SQLite database backups
- **Backup Cleanup** - Auto-clean old backups, keep latest 7
- **Zero Configuration** - Uses SQLite, no additional database service required

## 🚀 Quick Start

### One-Click Deployment (Recommended)

```bash
# 1. Clone the project
git clone https://github.com/yourusername/qa_box.git
cd qa_box

# 2. Configure environment variables
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit backend/.env and frontend/.env, modify necessary configurations (SECRET_KEY, ADMIN_PASSWORD, etc.)

# 3. Start services
chmod +x deploy.sh
./deploy.sh start
```

After services start, visit:
- 📱 **Frontend Page**: http://localhost:13000
- 🔐 **Admin Panel**: http://localhost:13000/console-x7k9m
- 📖 **API Docs**: http://localhost:18000/docs

### Other Deployment Commands

```bash
./deploy.sh stop      # Stop all services
./deploy.sh restart   # Restart all services
./deploy.sh status    # Check service status
./deploy.sh logs      # View logs
./deploy.sh build     # Rebuild frontend only
```

### Development Environment

<details>
<summary>Click to expand development environment setup</summary>

**Backend Development**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Development**
```bash
cd frontend
pnpm install  # or npm install
pnpm dev      # or npm run dev
```

</details>

## 📦 Tech Stack

### Backend
- **FastAPI** - Modern high-performance Python web framework
- **SQLAlchemy 2.0** - Powerful ORM framework
- **SQLite** - Lightweight embedded database (aiosqlite async driver)
- **JWT** - Authentication and revoke mechanism
- **Gunicorn + Uvicorn** - Production-grade ASGI server

### Frontend
- **Vue 3** - Progressive JavaScript framework (Composition API)
- **Vite** - Lightning-fast frontend build tool
- **TailwindCSS** - Utility-first CSS framework
- **Axios** - Promise-based HTTP client
- **Vue Router** - Official routing manager
- **html2canvas** - Card generation library

## 🔧 Core Configuration

### Backend Environment Variables (`backend/.env`)

```bash
# ============================================
# Security Configuration (Must change in production!)
# ============================================
SECRET_KEY=your-secret-key-please-change-in-production-min-32-chars
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-strong-password

# ============================================
# Admin Panel Configuration
# ============================================
# Admin route prefix (recommended to change to random path)
# IMPORTANT: Must sync with frontend VITE_ADMIN_ROUTE_PREFIX
ADMIN_ROUTE_PREFIX=/console-x7k9m

# Admin token expiration days
ADMIN_TOKEN_EXPIRE_DAYS=7

# Auto-refresh when remaining days is less than this value
ADMIN_TOKEN_REFRESH_DAYS=1

# ============================================
# Server Configuration
# ============================================
HOST=127.0.0.1                              # Listen address
PORT=18000                                  # Backend port
FRONTEND_PORT=13000                         # Frontend port
WORKERS=2                                   # Gunicorn worker count

# ============================================
# Backup Configuration
# ============================================
BACKUP_INTERVAL_HOURS=24                    # Auto backup interval (hours), 0 to disable
BACKUP_MAX_COUNT=7                          # Number of backups to keep
```

### Frontend Environment Variables (`frontend/.env`)

```bash
# Backend service address (for Vite proxy)
VITE_BACKEND_HOST=127.0.0.1
VITE_BACKEND_PORT=18000

# Admin panel route prefix - must sync with backend ADMIN_ROUTE_PREFIX
# IMPORTANT: Rebuild frontend after changing: pnpm build
VITE_ADMIN_ROUTE_PREFIX=/console-x7k9m
```

**⚠️ Important Notes:**
1. The `ADMIN_ROUTE_PREFIX` (backend) and `VITE_ADMIN_ROUTE_PREFIX` (frontend) **MUST match**
2. After changing admin route prefix:
   - Backend: restart service `./deploy.sh restart`
   - Frontend: rebuild `./deploy.sh build` or `cd frontend && pnpm build`
3. For security, use a random, hard-to-guess path like `/admin-abc123xyz`

For complete configuration details, see [`backend/.env.example`](backend/.env.example) and [`frontend/.env.example`](frontend/.env.example)

## 📚 Documentation

- 📖 [Deployment Guide](DEPLOY.md) - Detailed production environment deployment guide
- 🔧 [Backend API Docs](http://localhost:18000/docs) - Visit after starting services
- 🎨 [Frontend Development Guide](frontend/README.md) - Frontend project structure and development guide

## 🗂️ Project Structure

```
qa_box/
├── backend/                    # Backend service
│   ├── main.py                # FastAPI app entry point
│   ├── main_router.py         # Route definitions
│   ├── models.py              # Data models
│   ├── schemas.py             # Pydantic validation schemas
│   ├── config.py              # Configuration management
│   ├── auth.py                # Authentication module
│   ├── backup.py              # Auto backup module
│   ├── upload_utils.py        # File upload utilities
│   ├── .env.example           # Environment variables template
│   └── requirements.txt       # Python dependencies
├── frontend/                   # Frontend application
│   ├── src/
│   │   ├── views/             # Page components
│   │   │   ├── AskPage.vue           # Question page
│   │   │   ├── AdminPage.vue         # Admin panel
│   │   │   └── AdminLogin.vue        # Login page
│   │   ├── api/               # API wrapper
│   │   ├── utils/             # Utility functions
│   │   └── router/            # Route configuration
│   ├── .env.example           # Environment variables template
│   ├── package.json
│   └── vite.config.js
├── uploads/                    # Image upload directory (organized by week)
├── backups/                    # Database backup directory
├── screenshots/                # Project screenshots
├── deploy.sh                   # One-click deployment script
├── .gitignore                  # Git ignore configuration
├── README.md                   # Chinese README
├── README_EN.md                # This file
└── DEPLOY.md                   # Deployment tutorial (Chinese)
```

## 🛡️ Security Recommendations

### Production Must-Do

1. ✅ **Change Default Password** - Modify `ADMIN_PASSWORD`
2. ✅ **Generate Strong Secret** - Use 32+ character random string for `SECRET_KEY`
3. ✅ **Customize Admin Path** - Change `ADMIN_ROUTE_PREFIX` and `VITE_ADMIN_ROUTE_PREFIX` to hard-to-guess paths
4. ✅ **Configure HTTPS** - Use Nginx + Let's Encrypt certificate
5. ✅ **Restrict Access IP** - Configure Nginx whitelist to restrict admin panel access

### Optional Hardening

- 🔒 **Two-Factor Authentication** - Add 2FA for admin panel
- 🚫 **IP Blacklist** - Auto-ban brute-force attack IPs
- 📊 **Access Logs** - Record and monitor abnormal access
- 🔐 **SSH Tunnel** - Access admin panel only via SSH

## 📊 Performance Optimization

- **Frontend Build Optimization** - Vite production build with code splitting and compression
- **Image Lazy Loading** - Load large images on demand
- **Database Indexing** - Index key fields
- **Static Resource Caching** - Nginx static file caching
- **Async Processing** - FastAPI async endpoints + aiosqlite

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

[MIT License](LICENSE) - Free to use, just keep the copyright notice.

## 🙏 Acknowledgments

Thanks to all open-source project contributors.

---

<div align="center">

**If this project helps you, please give it a ⭐️ Star!**

Made with ❤️ by [Lin037]

</div>
