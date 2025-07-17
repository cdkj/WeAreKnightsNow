# 现在我们是骑士啦 - 后端服务 🚀

基于 Flask 构建的轻量级后端服务，为骑士的星空探险提供强大的 Git 仓库数据分析和处理能力。

## 🛠️ 技术栈

- **Flask** - 轻量级 Python Web 框架
- **Flask-CORS** - 跨域资源共享支持
- **Werkzeug** - WSGI 工具库
- **Python 3.8+** - 现代 Python 运行环境
- **Git** - 版本控制系统集成

## 📁 项目结构

```
backend/
├── app.py                  # Flask 应用主文件
├── requirements.txt        # Python 依赖配置
├── run.py                 # 应用启动脚本
├── utils/                 # 工具模块（如果有）
├── config/                # 配置文件（如果有）
└── README.md              # 本文档
```

## ✨ 核心功能

### 📊 Git 数据分析
- **提交历史解析**：完整的 Git 日志信息提取
- **分支信息**：分支结构和关系分析
- **统计数据**：提交数量、作者统计、文件变更统计
- **仓库信息**：仓库基本信息和元数据

### 🔌 RESTful API
- **标准化接口**：遵循 REST 设计原则
- **JSON 响应**：统一的数据格式
- **错误处理**：完善的异常处理机制
- **CORS 支持**：跨域请求支持

### ⚡ 性能优化
- **数据缓存**：智能缓存机制
- **分页支持**：大量数据的分页处理
- **异步处理**：非阻塞的数据处理
- **内存优化**：高效的内存使用

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Git 命令行工具
- pip 包管理器

### 安装依赖
```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 启动服务
```bash
# 开发模式
python run.py

# 或直接运行 Flask 应用
python app.py
```

服务将在 `http://localhost:5000` 启动

### 生产部署
```bash
# 使用 Gunicorn（推荐）
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 或使用 uWSGI
pip install uwsgi
uwsgi --http :5000 --wsgi-file app.py --callable app
```

## 📡 API 接口

### 1. 获取 Git 日志

**接口**: `POST /api/git-log`

**描述**: 获取指定仓库的 Git 提交历史

**请求参数**:
```json
{
  "repo_path": "/path/to/repository",
  "max_count": 100  // 可选，最大提交数量，0表示全部
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "commits": [
      {
        "hash": "abc123...",
        "author": "John Doe",
        "email": "john@example.com",
        "date": "2024-01-15T10:30:00Z",
        "message": "feat: add new feature",
        "branch": "main",
        "files_changed": 3,
        "insertions": 45,
        "deletions": 12,
        "parents": ["def456..."]
      }
    ],
    "total_count": 150
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "Repository not found or invalid path",
  "code": "REPO_NOT_FOUND"
}
```

### 2. 获取仓库信息

**接口**: `POST /api/repository-info`

**描述**: 获取仓库的基本信息和统计数据

**请求参数**:
```json
{
  "repo_path": "/path/to/repository"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "name": "my-project",
    "path": "/path/to/repository",
    "current_branch": "main",
    "total_commits": 150,
    "total_branches": 5,
    "total_contributors": 8,
    "first_commit_date": "2023-01-01T00:00:00Z",
    "last_commit_date": "2024-01-15T10:30:00Z",
    "statistics": {
      "commits_by_author": {
        "John Doe": 45,
        "Jane Smith": 32
      },
      "commits_by_month": {
        "2024-01": 15,
        "2023-12": 23
      },
      "file_types": {
        ".js": 120,
        ".py": 85,
        ".md": 12
      }
    }
  }
}
```

### 3. 健康检查

**接口**: `GET /api/health`

**描述**: 检查服务运行状态

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "uptime": 3600
}
```

## 🏗️ 核心模块

### app.py - Flask 应用主文件

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 启用跨域支持

@app.route('/api/git-log', methods=['POST'])
def get_git_log():
    """获取 Git 提交历史"""
    try:
        data = request.get_json()
        repo_path = data.get('repo_path')
        max_count = data.get('max_count', 0)
        
        # 验证仓库路径
        if not os.path.exists(repo_path):
            return jsonify({
                'success': False,
                'error': 'Repository path does not exist',
                'code': 'REPO_NOT_FOUND'
            }), 404
        
        # 构建 Git 命令
        cmd = ['git', 'log', '--pretty=format:%H|%an|%ae|%ad|%s|%P', '--date=iso']
        if max_count > 0:
            cmd.extend(['-n', str(max_count)])
        
        # 执行 Git 命令
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': 'Failed to execute git command',
                'details': result.stderr
            }), 500
        
        # 解析提交数据
        commits = parse_git_log(result.stdout)
        
        return jsonify({
            'success': True,
            'data': {
                'commits': commits,
                'total_count': len(commits)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500

def parse_git_log(log_output):
    """解析 Git 日志输出"""
    commits = []
    for line in log_output.strip().split('\n'):
        if line:
            parts = line.split('|')
            if len(parts) >= 5:
                commit = {
                    'hash': parts[0],
                    'author': parts[1],
                    'email': parts[2],
                    'date': parts[3],
                    'message': parts[4],
                    'parents': parts[5].split() if len(parts) > 5 else []
                }
                commits.append(commit)
    return commits

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 数据处理工具

```python
# utils/git_parser.py
import subprocess
import re
from datetime import datetime
from typing import List, Dict, Any

class GitParser:
    """Git 数据解析器"""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
    
    def get_commit_stats(self, commit_hash: str) -> Dict[str, int]:
        """获取提交的统计信息"""
        cmd = ['git', 'show', '--stat', '--format=', commit_hash]
        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return self.parse_stat_output(result.stdout)
        return {'files_changed': 0, 'insertions': 0, 'deletions': 0}
    
    def parse_stat_output(self, output: str) -> Dict[str, int]:
        """解析 git show --stat 输出"""
        lines = output.strip().split('\n')
        stats = {'files_changed': 0, 'insertions': 0, 'deletions': 0}
        
        for line in lines:
            if 'file' in line and 'changed' in line:
                # 解析统计行
                match = re.search(r'(\d+) files? changed', line)
                if match:
                    stats['files_changed'] = int(match.group(1))
                
                match = re.search(r'(\d+) insertions?', line)
                if match:
                    stats['insertions'] = int(match.group(1))
                
                match = re.search(r'(\d+) deletions?', line)
                if match:
                    stats['deletions'] = int(match.group(1))
        
        return stats
    
    def get_branch_info(self) -> List[str]:
        """获取分支信息"""
        cmd = ['git', 'branch', '-a']
        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            branches = []
            for line in result.stdout.strip().split('\n'):
                branch = line.strip().replace('* ', '').replace('remotes/', '')
                if branch and not branch.startswith('origin/HEAD'):
                    branches.append(branch)
            return list(set(branches))
        return []
```

## 🔧 配置管理

### 环境变量配置

```python
# config/settings.py
import os
from typing import Optional

class Config:
    """应用配置类"""
    
    # Flask 配置
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # CORS 配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Git 配置
    MAX_COMMITS_DEFAULT = int(os.getenv('MAX_COMMITS_DEFAULT', 1000))
    GIT_TIMEOUT = int(os.getenv('GIT_TIMEOUT', 30))
    
    # 缓存配置
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', 300))  # 5分钟
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

### 环境变量文件 (.env)

```bash
# Flask 配置
FLASK_DEBUG=true
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# CORS 配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Git 配置
MAX_COMMITS_DEFAULT=1000
GIT_TIMEOUT=30

# 缓存配置
CACHE_ENABLED=true
CACHE_TTL=300

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## 🛡️ 安全考虑

### 输入验证
```python
from werkzeug.utils import secure_filename
import os

def validate_repo_path(path: str) -> bool:
    """验证仓库路径安全性"""
    # 检查路径是否存在
    if not os.path.exists(path):
        return False
    
    # 检查是否为 Git 仓库
    git_dir = os.path.join(path, '.git')
    if not os.path.exists(git_dir):
        return False
    
    # 防止路径遍历攻击
    normalized_path = os.path.normpath(path)
    if '..' in normalized_path:
        return False
    
    return True

def sanitize_input(data: dict) -> dict:
    """清理输入数据"""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # 移除潜在的危险字符
            sanitized[key] = re.sub(r'[;&|`$]', '', value)
        else:
            sanitized[key] = value
    return sanitized
```

### 错误处理
```python
from functools import wraps
import logging

def handle_errors(f):
    """统一错误处理装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': 'Repository not found',
                'code': 'REPO_NOT_FOUND'
            }), 404
        except subprocess.CalledProcessError as e:
            logging.error(f"Git command failed: {e}")
            return jsonify({
                'success': False,
                'error': 'Git operation failed',
                'code': 'GIT_ERROR'
            }), 500
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'code': 'INTERNAL_ERROR'
            }), 500
    return decorated_function
```

## 📊 性能监控

### 请求日志
```python
import time
from flask import g

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    logging.info(f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s")
    return response
```

### 缓存机制
```python
from functools import lru_cache
import hashlib

class GitCache:
    """Git 数据缓存"""
    
    def __init__(self):
        self.cache = {}
    
    def get_cache_key(self, repo_path: str, max_count: int) -> str:
        """生成缓存键"""
        key_string = f"{repo_path}:{max_count}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str):
        """获取缓存数据"""
        return self.cache.get(key)
    
    def set(self, key: str, data: any, ttl: int = 300):
        """设置缓存数据"""
        self.cache[key] = {
            'data': data,
            'expires': time.time() + ttl
        }
    
    def is_expired(self, key: str) -> bool:
        """检查缓存是否过期"""
        if key not in self.cache:
            return True
        return time.time() > self.cache[key]['expires']
```

## 🚀 部署指南

### Docker 部署

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装 Git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - CORS_ORIGINS=http://localhost:5173
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

### Nginx 配置

```nginx
# /etc/nginx/sites-available/git-to-graph
server {
    listen 80;
    server_name your-domain.com;
    
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🧪 测试

### 单元测试
```python
# tests/test_api.py
import unittest
import json
from app import app

class APITestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_check(self):
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_git_log_invalid_path(self):
        response = self.app.post('/api/git-log', 
                                json={'repo_path': '/invalid/path'})
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

if __name__ == '__main__':
    unittest.main()
```

### API 测试脚本
```bash
#!/bin/bash
# test_api.sh

BASE_URL="http://localhost:5000/api"

echo "Testing health endpoint..."
curl -X GET "$BASE_URL/health"

echo "\nTesting git-log endpoint..."
curl -X POST "$BASE_URL/git-log" \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/path/to/test/repo", "max_count": 10}'

echo "\nTesting repository-info endpoint..."
curl -X POST "$BASE_URL/repository-info" \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/path/to/test/repo"}'
```

## 🤝 贡献指南

### 开发流程
1. Fork 项目并创建功能分支
2. 遵循 PEP 8 代码规范
3. 添加必要的测试用例
4. 确保所有测试通过
5. 提交 Pull Request

### 代码规范
- 使用 Black 格式化代码
- 使用 Flake8 进行代码检查
- 添加类型注解
- 编写清晰的文档字符串

---

**轻量级后端，强大的数据处理能力！** 🚀