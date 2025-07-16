# Git Log 可视化后端服务

这是一个基于Flask的后端服务，用于解析Git仓库的提交历史并提供API接口给前端进行可视化展示。

## 功能特性

- 🔍 解析Git仓库的提交历史
- 📊 提供结构化的提交数据
- 🎨 保留Git图形化分支结构
- 📈 统计提交信息（作者、分支等）
- 🛡️ 安全的路径验证
- ⚡ 高性能的数据处理

## 项目结构

```
backend/
├── app.py              # 主应用文件
├── run.py              # 启动脚本
├── config.py           # 配置文件
├── requirements.txt    # 依赖包列表
├── utils/              # 工具模块
│   ├── __init__.py
│   └── git_utils.py    # Git操作工具
└── README.md           # 说明文档
```

## 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 运行服务

### 方式1：使用启动脚本（推荐）

```bash
python run.py
```

### 方式2：直接运行

```bash
python app.py
```

### 方式3：使用Flask命令

```bash
set FLASK_APP=app.py
set FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

## API接口

### 1. 获取Git日志数据

**POST** `/api/git-log`

请求体：
```json
{
    "repo_path": "/path/to/your/git/repository",
    "max_count": 100  // 可选，最大提交数量，不设置或设为0则获取所有提交
}
```

响应：
```json
{
    "success": true,
    "data": {
        "repository": {
            "name": "项目名称",
            "path": "仓库路径",
            "current_branch": "当前分支",
            "remote_url": "远程仓库URL"
        },
        "commits": [
            {
                "line_number": 1,
                "graph": "* ",
                "hash": "abc1234",
                "refs": "origin/main, main",
                "message": "提交信息",
                "time": "2 hours ago",
                "author": "作者名称",
                "raw_line": "原始行内容"
            }
        ],
        "statistics": {
            "total_commits": 100,
            "total_lines": 120,
            "authors": [
                {"name": "作者1", "count": 50},
                {"name": "作者2", "count": 30}
            ],
            "branches": ["main", "develop"]
        }
    }
}
```

### 2. 获取仓库信息

**POST** `/api/repository-info`

请求体：
```json
{
    "repo_path": "/path/to/your/git/repository"
}
```

### 3. 健康检查

**GET** `/api/health`

## 配置说明

可以通过环境变量配置服务：

- `FLASK_ENV`: 运行环境（development/production）
- `FLASK_HOST`: 服务主机地址（默认：0.0.0.0）
- `FLASK_PORT`: 服务端口（默认：5000）
- `FLASK_DEBUG`: 调试模式（默认：True）
- `MAX_COMMITS`: 最大提交数量限制（默认：1000）
- `GIT_TIMEOUT`: Git命令超时时间（默认：30秒）

## 错误处理

服务会返回详细的错误信息：

- 400: 请求参数错误
- 500: 服务器内部错误

常见错误：
- 路径不存在
- 不是有效的Git仓库
- Git命令执行失败
- 权限不足

## 开发说明

### 添加新功能

1. 在 `utils/git_utils.py` 中添加Git相关工具函数
2. 在 `app.py` 中添加新的API路由
3. 更新配置文件（如需要）

### 测试

可以使用curl或Postman测试API：

```bash
curl -X POST http://localhost:5000/api/git-log \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/path/to/repo"}'
```

## 注意事项

1. 确保系统已安装Git命令行工具
2. 服务需要对Git仓库有读取权限
3. 大型仓库可能需要较长处理时间
4. 建议在生产环境中使用WSGI服务器（如Gunicorn）

## 许可证

MIT License