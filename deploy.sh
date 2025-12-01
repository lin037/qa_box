#!/bin/bash

# ============================================
# QA Box 生产环境部署脚本
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 加载环境变量
if [ -f "backend/.env" ]; then
    set -a
    source backend/.env
    set +a
fi

# 默认配置 (可通过 .env 覆盖)
HOST=${HOST:-127.0.0.1}
PORT=${PORT:-18000}
FRONTEND_PORT=${FRONTEND_PORT:-13000}
WORKERS=${WORKERS:-2}

# PID 文件
BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"
FRONTEND_PID_FILE="$SCRIPT_DIR/.frontend.pid"

# 日志文件
BACKEND_LOG="$SCRIPT_DIR/backend.log"
FRONTEND_LOG="$SCRIPT_DIR/frontend.log"

# ============================================
# 辅助函数
# ============================================

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_title() {
    echo -e "${BLUE}$1${NC}"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -i:$port > /dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口空闲
    fi
}

# 获取占用端口的进程信息
get_port_process() {
    local port=$1
    lsof -i:$port -t 2>/dev/null | head -1
}

# 通过 PID 文件检查进程是否运行
check_pid_running() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "$pid"
            return 0
        fi
    fi
    return 1
}

# 停止指定 PID 的进程
kill_process() {
    local pid=$1
    local name=$2
    
    if ps -p "$pid" > /dev/null 2>&1; then
        print_info "停止 $name (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        
        # 等待进程结束
        local count=0
        while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
            sleep 0.5
            count=$((count + 1))
        done
        
        # 如果还在运行，强制杀死
        if ps -p "$pid" > /dev/null 2>&1; then
            kill -9 "$pid" 2>/dev/null || true
        fi
    fi
}

# ============================================
# 安装依赖
# ============================================

install_deps() {
    print_info "检查并安装依赖..."
    
    # 后端依赖
    if [ ! -d "backend/.venv" ]; then
        print_info "创建 Python 虚拟环境..."
        cd backend
        python3 -m venv .venv
        source .venv/bin/activate
        pip install --upgrade pip -q
        pip install -r requirements.txt -q
        cd ..
    fi
    
    # 激活虚拟环境
    source backend/.venv/bin/activate
    
    # 检查必要的包
    if ! pip show gunicorn > /dev/null 2>&1; then
        print_info "安装 gunicorn..."
        pip install gunicorn -q
    fi
    
    if ! pip show passlib > /dev/null 2>&1; then
        print_info "安装 passlib[bcrypt]..."
        pip install "passlib[bcrypt]" -q
    fi
    
    # 前端依赖
    if [ ! -d "frontend/node_modules" ]; then
        print_info "安装前端依赖..."
        cd frontend
        if command -v pnpm &> /dev/null; then
            pnpm install --silent
        elif command -v npm &> /dev/null; then
            npm install --silent
        else
            print_error "未找到 pnpm 或 npm，请先安装"
            exit 1
        fi
        cd ..
    fi
    
    print_info "依赖检查完成"
}

# ============================================
# 构建前端
# ============================================

build_frontend() {
    print_info "构建前端..."
    cd frontend
    
    if command -v pnpm &> /dev/null; then
        pnpm build
    else
        npm run build
    fi
    
    cd ..
    print_info "前端构建完成"
}

# ============================================
# 启动后端
# ============================================

start_backend() {
    # 检查 PID 文件中的进程
    local existing_pid=$(check_pid_running "$BACKEND_PID_FILE")
    if [ -n "$existing_pid" ]; then
        print_warn "后端服务已在运行 (PID: $existing_pid)"
        return 0
    fi
    
    # 检查端口是否被占用
    if check_port $PORT; then
        local occupying_pid=$(get_port_process $PORT)
        print_error "端口 $PORT 已被占用 (PID: $occupying_pid)"
        print_info "你可以运行: kill $occupying_pid 来释放端口"
        print_info "或修改 backend/.env 中的 PORT 配置"
        return 1
    fi
    
    print_info "启动后端服务 (端口: $PORT)..."
    
    source backend/.venv/bin/activate
    
    cd "$SCRIPT_DIR"
    
    # 使用 gunicorn + uvicorn workers
    nohup gunicorn backend.main:app \
        -k uvicorn.workers.UvicornWorker \
        -w "$WORKERS" \
        -b "$HOST:$PORT" \
        --access-logfile "$BACKEND_LOG" \
        --error-logfile "$BACKEND_LOG" \
        --capture-output \
        --pid "$BACKEND_PID_FILE" \
        > /dev/null 2>&1 &
    
    # gunicorn 会自己写 PID 文件，等待一下
    sleep 2
    
    if check_port $PORT; then
        local pid=$(cat "$BACKEND_PID_FILE" 2>/dev/null || get_port_process $PORT)
        print_info "后端服务启动成功 (PID: $pid)"
        print_info "  监听: http://$HOST:$PORT"
        print_info "  文档: http://$HOST:$PORT/docs"
        return 0
    else
        print_error "后端服务启动失败，请查看日志: $BACKEND_LOG"
        return 1
    fi
}

# ============================================
# 启动前端
# ============================================

start_frontend() {
    # 检查 PID 文件中的进程
    local existing_pid=$(check_pid_running "$FRONTEND_PID_FILE")
    if [ -n "$existing_pid" ]; then
        print_warn "前端服务已在运行 (PID: $existing_pid)"
        return 0
    fi
    
    # 检查端口是否被占用
    if check_port $FRONTEND_PORT; then
        local occupying_pid=$(get_port_process $FRONTEND_PORT)
        print_error "端口 $FRONTEND_PORT 已被占用 (PID: $occupying_pid)"
        print_info "你可以运行: kill $occupying_pid 来释放端口"
        print_info "或修改 backend/.env 中的 FRONTEND_PORT 配置"
        return 1
    fi
    
    # 检查是否已构建
    if [ ! -d "frontend/dist" ]; then
        print_warn "前端未构建，正在构建..."
        build_frontend
    fi
    
    print_info "启动前端服务 (端口: $FRONTEND_PORT)..."
    
    cd frontend
    
    # 使用 vite preview 作为静态服务器
    if command -v pnpm &> /dev/null; then
        nohup pnpm preview --host 0.0.0.0 --port "$FRONTEND_PORT" > "$FRONTEND_LOG" 2>&1 &
    else
        nohup npm run preview -- --host 0.0.0.0 --port "$FRONTEND_PORT" > "$FRONTEND_LOG" 2>&1 &
    fi
    
    local frontend_pid=$!
    echo "$frontend_pid" > "$FRONTEND_PID_FILE"
    
    cd ..
    
    sleep 2
    
    if check_port $FRONTEND_PORT; then
        print_info "前端服务启动成功 (PID: $frontend_pid)"
        print_info "  地址: http://0.0.0.0:$FRONTEND_PORT"
        return 0
    else
        print_error "前端服务启动失败，请查看日志: $FRONTEND_LOG"
        rm -f "$FRONTEND_PID_FILE"
        return 1
    fi
}

# ============================================
# 停止服务
# ============================================

stop_backend() {
    print_info "停止后端服务..."
    
    # 1. 先尝试通过 PID 文件停止
    if [ -f "$BACKEND_PID_FILE" ]; then
        local pid=$(cat "$BACKEND_PID_FILE")
        kill_process "$pid" "后端主进程"
        rm -f "$BACKEND_PID_FILE"
    fi
    
    # 2. 杀死所有 gunicorn 相关进程
    pkill -f "gunicorn backend.main:app" 2>/dev/null || true
    
    # 3. 检查端口是否释放
    sleep 1
    if check_port $PORT; then
        local pid=$(get_port_process $PORT)
        print_warn "端口 $PORT 仍被占用，强制停止 (PID: $pid)"
        kill -9 "$pid" 2>/dev/null || true
    fi
    
    print_info "后端服务已停止"
}

stop_frontend() {
    print_info "停止前端服务..."
    
    # 1. 通过 PID 文件停止
    if [ -f "$FRONTEND_PID_FILE" ]; then
        local pid=$(cat "$FRONTEND_PID_FILE")
        kill_process "$pid" "前端服务"
        rm -f "$FRONTEND_PID_FILE"
    fi
    
    # 2. 检查端口是否释放
    sleep 1
    if check_port $FRONTEND_PORT; then
        local pid=$(get_port_process $FRONTEND_PORT)
        print_warn "端口 $FRONTEND_PORT 仍被占用，强制停止 (PID: $pid)"
        kill -9 "$pid" 2>/dev/null || true
    fi
    
    print_info "前端服务已停止"
}

stop_all() {
    stop_backend
    stop_frontend
}

# ============================================
# 状态检查
# ============================================

status() {
    echo ""
    print_title "========== QA Box 服务状态 =========="
    echo ""
    
    # 后端状态
    echo -n "后端服务: "
    if check_port $PORT; then
        local pid=$(get_port_process $PORT)
        echo -e "${GREEN}运行中${NC} (PID: $pid, 端口: $PORT)"
        echo "  - API: http://$HOST:$PORT"
        echo "  - 文档: http://$HOST:$PORT/docs"
    else
        echo -e "${RED}未运行${NC}"
    fi
    
    echo ""
    
    # 前端状态
    echo -n "前端服务: "
    if check_port $FRONTEND_PORT; then
        local pid=$(get_port_process $FRONTEND_PORT)
        echo -e "${GREEN}运行中${NC} (PID: $pid, 端口: $FRONTEND_PORT)"
        echo "  - 地址: http://0.0.0.0:$FRONTEND_PORT"
    else
        echo -e "${RED}未运行${NC}"
    fi
    
    echo ""
    
    # 配置信息
    print_title "========== 当前配置 =========="
    echo "后端端口: $PORT"
    echo "前端端口: $FRONTEND_PORT"
    echo "Workers: $WORKERS"
    echo "管理后台: ${ADMIN_ROUTE_PREFIX:-/console-x7k9m}"
    
    echo ""
    print_title "====================================="
    echo ""
}

# ============================================
# 查看日志
# ============================================

show_logs() {
    local lines=${1:-50}
    
    echo ""
    print_title "========== 后端日志 (最近 $lines 行) =========="
    if [ -f "$BACKEND_LOG" ]; then
        tail -$lines "$BACKEND_LOG"
    else
        echo "无日志文件"
    fi
    
    echo ""
    print_title "========== 前端日志 (最近 $lines 行) =========="
    if [ -f "$FRONTEND_LOG" ]; then
        tail -$lines "$FRONTEND_LOG"
    else
        echo "无日志文件"
    fi
}

# ============================================
# 清理
# ============================================

clean() {
    print_info "清理临时文件..."
    rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"
    rm -f "$BACKEND_LOG" "$FRONTEND_LOG"
    print_info "清理完成"
}

# ============================================
# 帮助信息
# ============================================

show_help() {
    echo ""
    print_title "QA Box 部署脚本"
    echo ""
    echo "用法: $0 <命令> [参数]"
    echo ""
    echo "命令:"
    echo "  start       启动所有服务 (生产模式)"
    echo "  stop        停止所有服务"
    echo "  restart     重启所有服务"
    echo "  status      查看服务状态"
    echo "  build       仅构建前端"
    echo "  backend     仅启动后端"
    echo "  frontend    仅启动前端"
    echo "  logs [n]    查看最近 n 行日志 (默认 50)"
    echo "  clean       清理 PID 和日志文件"
    echo "  help        显示此帮助信息"
    echo ""
    echo "配置:"
    echo "  所有配置项在 backend/.env 文件中"
    echo "  参考 backend/.env.example"
    echo ""
    echo "示例:"
    echo "  $0 start           # 启动所有服务"
    echo "  $0 stop            # 停止所有服务"
    echo "  $0 logs 100        # 查看最近 100 行日志"
    echo ""
}

# ============================================
# 主命令
# ============================================

case "$1" in
    start)
        install_deps
        start_backend
        start_frontend
        echo ""
        status
        ;;
    stop)
        stop_all
        ;;
    restart)
        stop_all
        sleep 2
        install_deps
        start_backend
        start_frontend
        echo ""
        status
        ;;
    status)
        status
        ;;
    build)
        install_deps
        build_frontend
        ;;
    backend)
        install_deps
        start_backend
        ;;
    frontend)
        install_deps
        start_frontend
        ;;
    logs)
        show_logs ${2:-50}
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac
