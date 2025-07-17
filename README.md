# Git 提交历史可视化项目

一个完整的 Git 提交历史可视化解决方案，包含 Python Flask 后端和 Vue.js + D3.js 前端，将您的 Git 仓库历史转化为美丽的时间轴动画。

## 🎯 项目概述

这个项目旨在为开发者提供一个直观、美观的方式来查看和分析 Git 仓库的提交历史。通过时间轴动画，您可以：

- 📈 观察项目的发展历程
- 👥 了解团队成员的贡献情况
- 🌳 可视化分支的创建和合并
- 🎬 以动画形式重现开发过程
- 📊 获取详细的统计信息

## 🏗️ 项目结构

```
git-to-graph/
├── backend/                 # Python Flask 后端
│   ├── app.py              # Flask 应用主文件
│   ├── config.py           # 配置管理
│   ├── run.py              # 启动脚本
│   ├── requirements.txt    # Python 依赖
│   ├── test_api.py         # API 测试脚本
│   ├── utils/              # 工具模块
│   │   ├── __init__.py
│   │   └── git_utils.py    # Git 操作工具
│   └── README.md           # 后端文档
├── frontend/               # Vue.js + D3.js 前端
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   ├── views/          # 页面组件
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── router/         # 路由配置
│   │   ├── styles/         # 样式文件
│   │   └── main.ts         # 应用入口
│   ├── package.json        # 前端依赖
│   └── README.md           # 前端文档
└── README.md               # 项目总览（本文件）
```

## ✨ 功能特性

### 后端功能
- 🔍 Git 仓库信息获取
- 📝 提交历史解析
- 📊 统计数据计算
- 🌐 RESTful API 接口
- ⚡ 高性能数据处理
- 🛡️ 错误处理和验证

### 前端功能
- 🎬 时间轴动画播放
- 🎨 现代化 UI 设计
- 📱 响应式布局
- 🎛️ 动画控制面板
- 🔍 提交详情查看
- 📈 实时统计展示

## 🚀 快速开始

### 环境要求

- **后端**: Python 3.7+
- **前端**: Node.js 16+
- **Git**: 已安装并可在命令行使用

### 1. 启动后端服务

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py
```

后端服务将在 `http://localhost:5000` 启动

### 2. 启动前端应用

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 `http://localhost:5173` 启动

### 3. 使用应用

1. 在浏览器中打开 `http://localhost:5173`
2. 输入您的 Git 仓库本地路径
3. 设置最大提交数量（可选）
4. 点击"开始可视化"按钮
5. 享受美丽的时间轴动画！

## 🎨 可视化效果

### 提交节点
- **🔵 普通提交**: 日常代码提交
- **🟢 合并提交**: 分支合并操作
- **🟡 功能提交**: 新功能开发
- **🔴 修复提交**: Bug 修复

### 动画特效
- 按时间顺序逐个显示提交
- 平滑的节点出现动画
- 连接线动态绘制
- 可调节播放速度

### 交互功能
- 点击节点查看提交详情
- 悬停效果和工具提示
- 播放/暂停/重置控制
- 进度条显示

## 🔧 配置说明

### 后端配置

在 `backend/config.py` 中可以调整：

```python
class Config:
    # Flask 配置
    DEBUG = True
    
    # 服务器配置
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Git 配置
    MAX_COMMITS = 1000
    GIT_TIMEOUT = 30
```

### 前端配置

在 `frontend/src/stores/git.ts` 中可以修改 API 地址：

```typescript
const API_BASE_URL = 'http://localhost:5000/api'
```

## 📊 API 接口

### 健康检查
```
GET /api/health
```

### 获取 Git 日志
```
GET /api/git-log?repo_path=<path>&max_count=<number>
```

### 获取仓库信息
```
GET /api/repository-info?repo_path=<path>
```

详细的 API 文档请参考 [backend/README.md](backend/README.md)

## 🐛 故障排除

### 常见问题

1. **后端启动失败**
   - 检查 Python 版本和依赖安装
   - 确保端口 5000 未被占用
   - 查看控制台错误信息

2. **前端无法连接后端**
   - 确保后端服务已启动
   - 检查防火墙设置
   - 验证 API 地址配置

3. **Git 仓库无法识别**
   - 确保路径指向有效的 Git 仓库
   - 检查文件系统权限
   - 验证 Git 命令可用性

4. **动画性能问题**
   - 减少提交数量限制
   - 降低动画播放速度
   - 使用现代浏览器

### 调试技巧

- 查看浏览器开发者工具的控制台
- 检查网络请求状态
- 使用后端测试脚本验证 API
- 查看后端日志输出

## 🛠️ 开发指南

### 后端开发

```bash
# 运行测试
python test_api.py

# 开发模式启动
FLASK_ENV=development python run.py
```

### 前端开发

```bash
# 类型检查
npm run type-check

# 代码检查
npm run lint

# 构建生产版本
npm run build
```

## 🤝 贡献指南

我们欢迎任何形式的贡献！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范

- 遵循现有代码风格
- 添加适当的注释和文档
- 确保测试通过
- 更新相关文档

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢以下开源项目的支持：

- [Flask](https://flask.palletsprojects.com/) - Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [D3.js](https://d3js.org/) - 数据驱动的文档
- [Element Plus](https://element-plus.org/) - Vue 3 组件库
- [Vite](https://vitejs.dev/) - 下一代前端构建工具

## 📞 联系我们

如果您有任何问题或建议，请通过以下方式联系我们：

- 提交 Issue
- 发起 Discussion
- 发送邮件

---

**让我们一起用美丽的可视化来纪念每一次代码提交！** 🎉