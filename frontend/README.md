# 现在我们是骑士啦 - 前端应用 🎨

基于 Vue 3 + TypeScript + D3.js 构建的现代化前端应用，让您化身为勇敢的骑士，在星空地图中探索 Git 提交历史的奇妙冒险。

## 🛠️ 技术栈

- **Vue 3** - 组合式 API，响应式系统
- **TypeScript** - 类型安全的 JavaScript 超集
- **Vite** - 极速的前端构建工具
- **D3.js** - 强大的数据可视化库
- **Element Plus** - Vue 3 组件库
- **Pinia** - Vue 官方状态管理库
- **Vue Router** - 官方路由管理器
- **SCSS** - CSS 预处理器
- **Axios** - HTTP 客户端

## 📁 项目结构

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/              # 静态资源
│   ├── components/          # 可复用组件
│   ├── router/              # 路由配置
│   │   └── index.ts
│   ├── stores/              # Pinia 状态管理
│   │   └── git.ts          # Git 数据状态
│   ├── styles/              # 全局样式
│   ├── views/               # 页面组件
│   │   └── Home.vue        # 主页面（星空地图）
│   ├── App.vue             # 根组件
│   └── main.ts             # 应用入口
├── index.html              # HTML 模板
├── package.json            # 依赖配置
├── tsconfig.json           # TypeScript 配置
├── vite.config.ts          # Vite 配置
└── README.md               # 本文档
```

## ✨ 核心功能

### 🌟 星空地图可视化
- **动态星空背景**：使用 Canvas 渲染闪烁的星星
- **提交节点布局**：智能算法排列提交位置
- **分支颜色系统**：不同分支使用不同颜色标识
- **响应式设计**：适配各种屏幕尺寸

### 🏇 骑士探险动画
- **角色动画**：精美的骑士和马匹 CSS 动画
- **移动轨迹**：平滑的移动动画和路径跟随
- **相机跟随**：智能相机系统实时跟随骑士
- **动画控制**：播放、暂停、重置功能

### 🎨 视觉效果
- **九曲山路十八弯**：使用贝塞尔曲线绘制弯曲连线
- **虚线动画**：连线跟随骑士移动逐步绘制
- **光晕效果**：旗帜插入时的白色光晕
- **陆地边界**：动态生成的不规则边界形状

### 📊 数据展示
- **提交信息卡片**：详细的提交信息展示
- **实时统计**：动态更新的统计数据
- **交互反馈**：悬停效果和点击响应

## 🚀 快速开始

### 环境要求
- Node.js 18+
- npm 或 pnpm

### 安装依赖
```bash
npm install
# 或
pnpm install
```

### 开发模式
```bash
npm run dev
# 或
pnpm dev
```

应用将在 `http://localhost:5173` 启动

### 构建生产版本
```bash
npm run build
# 或
pnpm build
```

### 类型检查
```bash
npm run type-check
# 或
pnpm type-check
```

### 预览构建结果
```bash
npm run preview
# 或
pnpm preview
```

## 🏗️ 核心组件

### Home.vue - 主页面组件

这是应用的核心组件，包含了所有主要功能：

#### 主要功能模块

1. **数据管理**
   - 使用 Pinia store 管理 Git 数据
   - 响应式的提交位置计算
   - 实时统计数据更新

2. **可视化渲染**
   - D3.js 驱动的 SVG 图形渲染
   - Canvas 星空背景动画
   - 动态连线绘制

3. **动画系统**
   - 骑士移动动画
   - 相机跟随逻辑
   - 连线绘制动画
   - 视觉效果动画

4. **交互控制**
   - 用户输入处理
   - 动画控制面板
   - 响应式布局

#### 关键方法

```typescript
// 生成星空地图布局
const generateStarmapLayout = () => {
  // 智能布局算法
}

// 骑士移动动画
const animateExplorerMovement = (targetPos, duration, callback) => {
  // 平滑移动动画
  // 相机实时跟随
}

// 绘制弯曲连线
const drawConnectionLineWithMovement = (fromIndex, toIndex, moveDuration) => {
  // 贝塞尔曲线绘制
  // 动画同步
}

// 相机聚焦
const focusCamera = (targetX, targetY, targetScale, duration) => {
  // 平滑相机过渡
}
```

## 🎨 样式系统

### SCSS 架构
- **组件级样式**：每个组件的 scoped 样式
- **全局样式**：通用样式和变量
- **动画库**：丰富的 CSS 动画效果

### 关键动画

```scss
// 骑士奔跑动画
@keyframes horseGallop {
  0% { transform: translate(-50%, -100%) rotateZ(0deg) translateY(0px); }
  50% { transform: translate(-50%, -100%) rotateZ(0deg) translateY(-6px); }
  100% { transform: translate(-50%, -100%) rotateZ(0deg) translateY(0px); }
}

// 星星闪烁动画
@keyframes twinkle {
  0% { opacity: 0.2; }
  50% { opacity: 1; }
  100% { opacity: 0.2; }
}

// 旗帜光晕动画
@keyframes flagGlow {
  0% { transform: scale(1); opacity: 0.8; }
  100% { transform: scale(1.2); opacity: 0.4; }
}
```

## 📊 状态管理

### Git Store (Pinia)

```typescript
export const useGitStore = defineStore('git', () => {
  // 状态
  const commits = ref<GitCommit[]>([])
  const repository = ref<RepositoryInfo | null>(null)
  const statistics = ref<GitStatistics | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 动作
  const fetchGitLog = async (repoPath: string, maxCount?: number) => {
    // API 调用逻辑
  }

  const clearData = () => {
    // 清理状态
  }

  return {
    commits,
    repository,
    statistics,
    loading,
    error,
    fetchGitLog,
    clearData
  }
})
```

## 🔧 配置说明

### Vite 配置

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
```

### TypeScript 配置

项目使用严格的 TypeScript 配置，确保类型安全：

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

## 🎯 性能优化

### 渲染优化
- **虚拟滚动**：大量数据的高效渲染
- **防抖处理**：相机跟随的性能优化
- **动画帧控制**：使用 requestAnimationFrame
- **内存管理**：及时清理 DOM 元素和事件监听器

### 代码分割
- **路由懒加载**：按需加载页面组件
- **组件懒加载**：大型组件的异步加载
- **第三方库优化**：Tree shaking 和按需引入

## 🐛 调试技巧

### 开发工具
- **Vue DevTools**：组件状态调试
- **浏览器控制台**：日志输出和错误追踪
- **Network 面板**：API 请求监控
- **Performance 面板**：性能分析

### 常见问题

1. **动画卡顿**
   - 检查 CSS 动画性能
   - 使用 transform 代替 position 变化
   - 减少重绘和重排

2. **内存泄漏**
   - 清理事件监听器
   - 取消未完成的 API 请求
   - 清理定时器和动画帧

3. **类型错误**
   - 检查 TypeScript 配置
   - 确保类型定义完整
   - 使用类型断言谨慎

## 🔮 未来规划

### 功能扩展
- **多主题支持**：暗色/亮色主题切换
- **自定义动画**：用户可配置的动画效果
- **导出功能**：动画录制和图片导出
- **分支对比**：多分支并行可视化

### 技术升级
- **WebGL 渲染**：更高性能的 3D 可视化
- **Web Workers**：后台数据处理
- **PWA 支持**：离线使用能力
- **国际化**：多语言支持

## 🤝 贡献指南

### 开发流程
1. Fork 项目并创建功能分支
2. 遵循现有代码风格和命名规范
3. 添加必要的类型定义和注释
4. 确保所有测试通过
5. 提交 Pull Request

### 代码规范
- 使用 ESLint 和 Prettier 格式化代码
- 遵循 Vue 3 组合式 API 最佳实践
- 保持组件单一职责原则
- 编写清晰的 TypeScript 类型定义

---

**用现代化的前端技术，打造极致的用户体验！** ✨
