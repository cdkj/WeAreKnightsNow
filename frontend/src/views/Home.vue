<template>
  <div class="home fade-in">
    <div class="cosmic-bg">
      <div ref="starsContainer" class="stars-container"></div>
    </div>
    
    <!-- 输入界面 -->
    <div v-if="!showVisualization" class="main-content" :class="{ 'fade-out': isTransitioning }">
      <div class="title-section fade-in-up" style="animation-delay: 0.2s">
        <h1 class="cosmic-title">
          <span class="gradient-text">Visualize Your Git Repo</span>
        </h1>
        <div class="subtitle-glow fade-in-up" style="animation-delay: 0.4s">
          <p class="cosmic-subtitle">Transform your repository into a stunning animated timeline</p>
        </div>
      </div>
      
      <div class="input-container fade-in-up" style="animation-delay: 0.6s">
        <div class="cosmic-input-wrapper">
          <input
            v-model="form.repoPath"
            type="text"
            placeholder="Enter your Git repository path..."
            class="cosmic-input"
            @keyup.enter="startVisualization"
          />
          <div class="input-glow"></div>
        </div>
        
        <div class="controls fade-in-up" style="animation-delay: 0.8s">
          <button
            @click="startVisualization"
            :disabled="!form.repoPath.trim() || loading"
            class="cosmic-button"
          >
            <span v-if="!loading">Launch Visualization</span>
            <span v-else class="loading-text">Loading...</span>
            <div class="button-glow"></div>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 可视化界面 -->
    <div v-if="showVisualization" class="visualization-section">
      
      <!-- Git星空地图探险 -->
        <div v-if="showVisualization" class="starmap-adventure">
          <div ref="starmapContainer" class="starmap-container">
            <div class="starmap-content">
            <!-- 提交节点容器 -->
            <div ref="commitNodesContainer" class="commit-nodes-container">
              <!-- 动态生成的commit节点（旗子） -->
              <div 
                v-for="(position, index) in commitPositions" 
                :key="position.hash"
                class="commit-flag"
                :class="{
                  planted: position.flagPlanted,
                  current: currentCommit?.hash === position.hash
                }"
                :style="{
                  left: position.x + 'px',
                  top: position.y + 'px',
                  '--branch-color': position.branchColor
                }"
              >
                <!-- 旗杆 -->
                <div class="flag-pole"></div>
                <!-- 旗帜 -->
                <div class="flag" :style="{ backgroundColor: position.branchColor }"></div>
                <!-- 旗帜上的提交信息 -->
                <div class="flag-label">{{ position.message.length > 15 ? position.message.substring(0, 15) + '...' : position.message }}</div>
                
                <!-- Commit信息提示框 -->
                <div v-if="currentCommit?.hash === position.hash" class="commit-info-tooltip">
                  <div class="tooltip-header">
                    <span class="commit-hash">{{ position.hash.substring(0, 8) }}</span>
                    <span v-if="formatTime(position.time)" class="commit-time">{{ formatTime(position.time) }}</span>
                  </div>
                  <div class="commit-author">{{ position.author }}</div>
                  <div class="commit-message">{{ position.message }}</div>
                </div>
              </div>
              
              <!-- 探险者骑马 -->
              <div 
                class="explorer-on-horse"
                :class="{
                  moving: explorer.isMoving,
                  jumping: explorer.isJumping
                }"
                :style="{
                  left: explorer.x + 'px',
                  top: explorer.y + 'px'
                }"
              >
                <!-- 马匹 -->
                <div class="horse">
                  <div class="horse-body"></div>
                  <div class="horse-head"></div>
                  <div class="horse-legs">
                    <div class="horse-leg front-left"></div>
                    <div class="horse-leg front-right"></div>
                    <div class="horse-leg back-left"></div>
                    <div class="horse-leg back-right"></div>
                  </div>
                  <div class="horse-tail"></div>
                  <div class="horse-mane"></div>
                </div>
                
                <!-- 骑手（探险者） -->
                <div class="rider">
                  <div class="rider-body">
                    <div class="rider-head"></div>
                    <div class="rider-torso"></div>
                    <div class="rider-legs">
                      <div class="leg left"></div>
                      <div class="leg right"></div>
                    </div>
                    <div class="rider-arms">
                      <div class="arm left"></div>
                      <div class="arm right"></div>
                    </div>
                  </div>
                  <!-- 探险者背包 -->
                  <div class="rider-backpack"></div>
                </div>
              </div>
            </div>
            
            <!-- 连接线SVG -->
            <svg ref="connectionSvg" class="connections-svg">
              <defs>
                <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#4ecdc4;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#45b7d1;stop-opacity:1" />
                </linearGradient>
              </defs>
            </svg>
            
            </div>
          </div>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useGitStore } from '../stores/git'
import type { GitCommit } from '../stores/git'

const gitStore = useGitStore()
const loading = ref(false)
const isTransitioning = ref(false)
const showVisualization = ref(false)
const starsContainer = ref<HTMLElement>()

// 星空地图相关的refs
const starmapContainer = ref<HTMLElement>()
const commitNodesContainer = ref<HTMLElement>()
const connectionSvg = ref<SVGElement>()

// 动画状态
const currentCommitIndex = ref(0)
const currentCommit = ref<GitCommit | null>(null)
const animationId = ref<number | null>(null)
const commitPositions = ref<Array<GitCommit & { x: number, y: number, visible: boolean, connected: boolean, branchColor: string, flagPlanted: boolean }>>([]) 

// 小人探险者状态
const explorer = ref<{
  x: number
  y: number
  isMoving: boolean
  currentTarget: number
  isJumping: boolean
}>({ x: 0, y: 0, isMoving: false, currentTarget: -1, isJumping: false })

// 相机和视角控制
const cameraPosition = ref({ x: 0, y: 0, scale: 1 })
const isAnimating = ref(false)
const cameraTransition = ref(false) // 相机过渡状态
// 平滑相机跟随始终启用

const form = reactive({
  repoPath: ''
})

// 计算属性
const totalCommits = computed(() => gitStore.commits?.length || 0)

// 获取分支颜色
const getBranchColor = (branchName: string, branchIndex: number) => {
  const colors = [
    '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', 
    '#feca57', '#ff9ff3', '#54a0ff', '#5f27cd',
    '#00d2d3', '#ff9f43', '#ee5a24', '#0984e3'
  ]
  return colors[branchIndex % colors.length]
}

// 无交叉路径生成算法 - 基于最小生成树的探险路径
const generateStarmapLayout = () => {
  if (!gitStore.commits || !starmapContainer.value) return
  
  const container = starmapContainer.value
  const containerWidth = container.clientWidth
  const containerHeight = container.clientHeight
  
  // 按时间排序commits
  const sortedCommits = [...gitStore.commits].sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime())
  
  // 分析分支结构
  const branches: { [key: string]: GitCommit[] } = {}
  const branchNames: string[] = []
  
  sortedCommits.forEach(commit => {
    const branchName = commit.branch || 'main'
    if (!branches[branchName]) {
      branches[branchName] = []
      branchNames.push(branchName)
    }
    branches[branchName].push(commit)
  })
  
  const positions: Array<GitCommit & { x: number, y: number, visible: boolean, connected: boolean, branchColor: string }> = []
  const minDistance = 200 // 最小间距
  
  // 线段相交检测函数
  const doLinesIntersect = (p1: {x: number, y: number}, p2: {x: number, y: number}, p3: {x: number, y: number}, p4: {x: number, y: number}) => {
    const d1 = direction(p3, p4, p1)
    const d2 = direction(p3, p4, p2)
    const d3 = direction(p1, p2, p3)
    const d4 = direction(p1, p2, p4)
    
    if (((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) && ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))) {
      return true
    }
    
    return false
  }
  
  const direction = (pi: {x: number, y: number}, pj: {x: number, y: number}, pk: {x: number, y: number}) => {
    return (pk.x - pi.x) * (pj.y - pi.y) - (pj.x - pi.x) * (pk.y - pi.y)
  }
  
  // 生成有机分布的候选点 - 创建不规则图形和留白区域
  const generateCandidatePoints = (numPoints: number) => {
    const points: {x: number, y: number}[] = []
    const margin = 80
    
    // 随机生成3-5个大块留白区域，总面积约占30%屏幕
    const numBlankZones = Math.floor(Math.random() * 3) + 3 // 3-5个留白区域
    const blankZones: {centerX: number, centerY: number, radiusX: number, radiusY: number}[] = []
    
    // 计算每个留白区域的平均面积（30%屏幕 / 区域数量）
    const totalBlankArea = 0.3 // 30%的屏幕面积
    const avgBlankAreaPerZone = totalBlankArea / numBlankZones
    
    // 生成随机留白区域
    for (let i = 0; i < numBlankZones; i++) {
      // 随机位置（避免边缘）
      const centerX = 0.15 + Math.random() * 0.7 // 15%-85%
      const centerY = 0.15 + Math.random() * 0.7 // 15%-85%
      
      // 根据面积计算半径（椭圆面积 = π * radiusX * radiusY）
      const baseRadius = Math.sqrt(avgBlankAreaPerZone / Math.PI)
      const radiusX = baseRadius * (0.8 + Math.random() * 0.4) // 0.8-1.2倍变化
      const radiusY = baseRadius * (0.8 + Math.random() * 0.4) // 0.8-1.2倍变化
      
      // 确保留白区域不重叠太多
      let validPosition = true
      for (const existingZone of blankZones) {
        const distance = Math.sqrt(
          Math.pow(centerX - existingZone.centerX, 2) + 
          Math.pow(centerY - existingZone.centerY, 2)
        )
        const minDistance = (radiusX + existingZone.radiusX + radiusY + existingZone.radiusY) / 4
        if (distance < minDistance * 0.7) { // 允许一些重叠但不要太多
          validPosition = false
          break
        }
      }
      
      if (validPosition) {
        blankZones.push({ centerX, centerY, radiusX, radiusY })
      }
    }
    
    console.log(`🎯 生成了 ${blankZones.length} 个留白区域:`, blankZones)
    
    // 定义探索区域（屏幕的70%，分布在留白区域之外）
    const distributionZones = [
      {
        type: 'exploration-area-1',
        weight: 0.4,
        bounds: {
          minX: margin,
          maxX: containerWidth - margin,
          minY: margin,
          maxY: containerHeight - margin
        }
      },
      {
        type: 'exploration-area-2', 
        weight: 0.35,
        bounds: {
          minX: margin,
          maxX: containerWidth - margin,
          minY: margin,
          maxY: containerHeight - margin
        }
      },
      {
        type: 'exploration-area-3',
        weight: 0.25,
        bounds: {
          minX: margin,
          maxX: containerWidth - margin,
          minY: margin,
          maxY: containerHeight - margin
        }
      }
    ]
    
    // 检查点是否在留白区域内（应该避免的区域）
    const isPointInBlankZone = (x: number, y: number) => {
      const normalizedX = x / containerWidth
      const normalizedY = y / containerHeight
      
      for (const blankZone of blankZones) {
        const dx = (normalizedX - blankZone.centerX) / blankZone.radiusX
        const dy = (normalizedY - blankZone.centerY) / blankZone.radiusY
        
        // 椭圆内部检测
        const distanceSquared = dx * dx + dy * dy
        if (distanceSquared <= 1) {
          return true // 在留白区域内
        }
      }
      return false // 不在任何留白区域内
    }
    
    // 检查点是否在探索区域边界内
    const isPointInExplorationBounds = (x: number, y: number, zone: any) => {
      return x >= zone.bounds.minX && x <= zone.bounds.maxX &&
             y >= zone.bounds.minY && y <= zone.bounds.maxY
    }
    
    // 为每个探索区域分配点数
    let remainingPoints = numPoints
    
    for (const zone of distributionZones) {
      const zonePoints = Math.floor(numPoints * zone.weight)
      let attempts = 0
      let placedInZone = 0
      
      while (placedInZone < zonePoints && attempts < zonePoints * 20) {
        attempts++
        
        // 在区域边界内生成随机点
        const x = zone.bounds.minX + Math.random() * (zone.bounds.maxX - zone.bounds.minX)
        const y = zone.bounds.minY + Math.random() * (zone.bounds.maxY - zone.bounds.minY)
        
        // 检查是否在探索区域边界内且不在留白区域内
        if (isPointInExplorationBounds(x, y, zone) && !isPointInBlankZone(x, y)) {
          // 检查与已有点的最小距离
          let validPlacement = true
          const minDist = 120 // 最小距离
          
          for (const existingPoint of points) {
            const dist = Math.sqrt(Math.pow(x - existingPoint.x, 2) + Math.pow(y - existingPoint.y, 2))
            if (dist < minDist) {
              validPlacement = false
              break
            }
          }
          
          if (validPlacement) {
            points.push({ x, y })
            placedInZone++
            remainingPoints--
          }
        }
      }
    }
    
    // 如果还有剩余点，随机分布在可用区域（避开留白区域）
    let attempts = 0
    while (remainingPoints > 0 && attempts < remainingPoints * 30) {
      attempts++
      
      const x = margin + Math.random() * (containerWidth - 2 * margin)
      const y = margin + Math.random() * (containerHeight - 2 * margin)
      
      // 检查是否不在留白区域内
      if (!isPointInBlankZone(x, y)) {
        // 检查最小距离
        let validPlacement = true
        const minDist = 120 // 保持较大的最小距离
        
        for (const existingPoint of points) {
          const dist = Math.sqrt(Math.pow(x - existingPoint.x, 2) + Math.pow(y - existingPoint.y, 2))
          if (dist < minDist) {
            validPlacement = false
            break
          }
        }
        
        if (validPlacement) {
          points.push({ x, y })
          remainingPoints--
        }
      }
    }
    
    // 如果仍有剩余点且尝试次数已用完，降低距离要求继续生成
    if (remainingPoints > 0) {
      console.warn(`⚠️ 降低距离要求，继续生成剩余的 ${remainingPoints} 个点`)
      attempts = 0
      while (remainingPoints > 0 && attempts < remainingPoints * 40) {
        attempts++
        
        const x = margin + Math.random() * (containerWidth - 2 * margin)
        const y = margin + Math.random() * (containerHeight - 2 * margin)
        
        // 仍然避开留白区域
        if (!isPointInBlankZone(x, y)) {
          // 检查最小距离（降低要求）
          let validPlacement = true
          const minDist = Math.max(60, 120 - attempts * 0.8) // 逐渐降低最小距离，但保持更大的最小值
        
          for (const existingPoint of points) {
            const dist = Math.sqrt(Math.pow(x - existingPoint.x, 2) + Math.pow(y - existingPoint.y, 2))
            if (dist < minDist) {
              validPlacement = false
              break
            }
          }
          
          if (validPlacement) {
            points.push({ x, y })
            remainingPoints--
          }
        }
      }
    }
    
    console.log(`🗺️ 生成了 ${points.length} 个分布点，目标 ${numPoints} 个`)
    return points
  }
  
  // 计算两点间距离
  const distance = (p1: {x: number, y: number}, p2: {x: number, y: number}) => {
    return Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2))
  }
  
  // Kruskal算法生成最小生成树
  const generateMST = (points: {x: number, y: number}[]) => {
    // 处理边界情况
    if (points.length <= 1) return []
    
    const edges: {from: number, to: number, weight: number}[] = []
    
    // 生成所有可能的边
    for (let i = 0; i < points.length; i++) {
      for (let j = i + 1; j < points.length; j++) {
        const weight = distance(points[i], points[j])
        edges.push({ from: i, to: j, weight })
      }
    }
    
    // 按权重排序
    edges.sort((a, b) => a.weight - b.weight)
    
    // 并查集
    const parent = Array.from({ length: points.length }, (_, i) => i)
    const find = (x: number): number => {
      if (parent[x] !== x) {
        parent[x] = find(parent[x])
      }
      return parent[x]
    }
    
    const union = (x: number, y: number) => {
      const rootX = find(x)
      const rootY = find(y)
      if (rootX !== rootY) {
        parent[rootX] = rootY
      }
    }
    
    const mstEdges: {from: number, to: number}[] = []
    
    for (const edge of edges) {
      if (find(edge.from) !== find(edge.to)) {
        mstEdges.push({ from: edge.from, to: edge.to })
        union(edge.from, edge.to)
        
        if (mstEdges.length === points.length - 1) {
          break
        }
      }
    }
    
    return mstEdges
  }
  
  // 从MST生成遍历路径
  const generateTraversalPath = (points: {x: number, y: number}[], mstEdges: {from: number, to: number}[]) => {
    // 处理边界情况
    if (points.length === 0) return []
    if (points.length === 1) return [0]
    
    // 构建邻接表
    const graph: number[][] = Array.from({ length: points.length }, () => [])
    mstEdges.forEach(edge => {
      graph[edge.from].push(edge.to)
      graph[edge.to].push(edge.from)
    })
    
    // 找到度数为1的节点作为起点（叶子节点）
    let startNode = 0
    for (let i = 0; i < graph.length; i++) {
      if (graph[i].length === 1) {
        startNode = i
        break
      }
    }
    
    // DFS遍历生成路径
    const visited = new Set<number>()
    const path: number[] = []
    
    const dfs = (node: number) => {
      visited.add(node)
      path.push(node)
      
      for (const neighbor of graph[node]) {
        if (!visited.has(neighbor)) {
          dfs(neighbor)
        }
      }
    }
    
    dfs(startNode)
    
    // 确保路径包含所有节点
    if (path.length < points.length) {
      console.warn(`⚠️ 路径长度 ${path.length} 小于节点数 ${points.length}，补充缺失节点`)
      for (let i = 0; i < points.length; i++) {
        if (!path.includes(i)) {
          path.push(i)
        }
      }
    }
    
    return path
  }
  
  // 主路径生成函数
  const createNonCrossingPath = (totalCommits: number) => {
    // 生成候选点
    let candidatePoints = generateCandidatePoints(totalCommits)
    
    // 如果生成的点数不足，补充随机点
    while (candidatePoints.length < totalCommits) {
      const x = 80 + Math.random() * (containerWidth - 160)
      const y = 80 + Math.random() * (containerHeight - 160)
      
      // 检查与已有点的最小距离
      let validPlacement = true
      const minDist = 100 // 保持较大的最小距离要求，增加留白
      
      for (const existingPoint of candidatePoints) {
        const dist = Math.sqrt(Math.pow(x - existingPoint.x, 2) + Math.pow(y - existingPoint.y, 2))
        if (dist < minDist) {
          validPlacement = false
          break
        }
      }
      
      if (validPlacement) {
        candidatePoints.push({ x, y })
      }
      
      // 防止无限循环
      if (candidatePoints.length === totalCommits) break
    }
    
    console.log(`🗺️ 最终生成了 ${candidatePoints.length} 个点，需要 ${totalCommits} 个`)
    
    // 如果点数仍然不足，直接使用网格布局作为后备
    if (candidatePoints.length < totalCommits) {
      console.warn('⚠️ 有机分布点数不足，使用网格布局作为后备')
      candidatePoints = []
      const cols = Math.ceil(Math.sqrt(totalCommits))
      const rows = Math.ceil(totalCommits / cols)
      const cellWidth = (containerWidth - 160) / cols
      const cellHeight = (containerHeight - 160) / rows
      
      for (let i = 0; i < totalCommits; i++) {
        const col = i % cols
        const row = Math.floor(i / cols)
        const x = 80 + col * cellWidth + cellWidth / 2 + (Math.random() - 0.5) * cellWidth * 0.3
        const y = 80 + row * cellHeight + cellHeight / 2 + (Math.random() - 0.5) * cellHeight * 0.3
        candidatePoints.push({ x, y })
      }
    }
    
    // 生成最小生成树
    const mstEdges = generateMST(candidatePoints)
    
    // 生成遍历路径
    const traversalPath = generateTraversalPath(candidatePoints, mstEdges)
    
    // 按遍历顺序返回点
    return traversalPath.map(index => candidatePoints[index])
  }
  
  // 使用新的无交叉路径算法为所有提交生成位置
  const allCommits = sortedCommits
  if (allCommits.length > 0) {
    const pathPoints = createNonCrossingPath(allCommits.length)
    
    allCommits.forEach((commit, index) => {
      const pathPoint = pathPoints[index]
      const branchName = commit.branch || 'main'
      const branchIndex = branchNames.indexOf(branchName)
      
      positions.push({
        ...commit,
        x: pathPoint.x,
        y: pathPoint.y,
        visible: false,
        connected: false,
        branchColor: getBranchColor(branchName, branchIndex),
        flagPlanted: false
      })
    })
  }
  
  commitPositions.value = positions
}

// 时间格式化
const formatTime = (timeStr: string) => {
  const date = new Date(timeStr)
  // 检查是否为无效日期
  if (isNaN(date.getTime())) {
    return '' // 返回空字符串，不显示无效日期
  }
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// 相机聚焦到指定位置 - 优化平滑度
const focusCamera = (targetX: number, targetY: number, targetScale: number = 1.8, duration: number = 1500) => {
  if (!starmapContainer.value) return
  
  const container = starmapContainer.value
  const containerWidth = container.clientWidth
  const containerHeight = container.clientHeight
  
  const translateX = (containerWidth / 2 - targetX)
  const translateY = (containerHeight / 2 - targetY)

  // 检查是否需要移动相机（避免不必要的过渡）
  const currentPos = cameraPosition.value
  const deltaX = Math.abs(translateX - currentPos.x)
  const deltaY = Math.abs(translateY - currentPos.y)
  const deltaScale = Math.abs(targetScale - currentPos.scale)
  
  // 如果变化很小，跳过动画
  if (deltaX < 2 && deltaY < 2 && deltaScale < 0.01) {
    return
  }
  
  console.log('📷 相机聚焦参数:', {
    目标位置: { x: targetX, y: targetY },
    缩放倍数: targetScale,
    变化量: { deltaX: deltaX.toFixed(2), deltaY: deltaY.toFixed(2), deltaScale: deltaScale.toFixed(3) },
    持续时间: duration
  })
  
  cameraTransition.value = true
  
  // 使用CSS动画实现平滑过渡
  const starmap = container.querySelector('.starmap-content')
  if (starmap) {
    // 根据移动距离和持续时间调整缓动函数
    const easing = duration <= 300 ? 'cubic-bezier(0.25, 0.46, 0.45, 0.94)' : 'cubic-bezier(0.4, 0, 0.2, 1)'
    starmap.style.transition = `transform ${duration}ms ${easing}`
    starmap.style.transform = `scale(${targetScale}) translate(${translateX}px, ${translateY}px)`
  }
  
  // 更新相机状态
  setTimeout(() => {
    cameraPosition.value = {
      x: translateX,
      y: translateY,
      scale: targetScale
    }
    cameraTransition.value = false
    
    // 移除过渡效果，准备下次动画
    if (starmap) {
      starmap.style.transition = ''
    }
  }, duration)
}

// 重置相机到全景视图
const resetCamera = (duration: number = 1000) => {
  if (!starmapContainer.value) return
  
  const container = starmapContainer.value
  const starmap = container.querySelector('.starmap-content')
  
  if (starmap) {
    starmap.style.transition = `transform ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`
    starmap.style.transform = 'scale(1) translate(0px, 0px)'
    
    console.log('📷 重置相机到全景视图')
  }
  
  // 更新相机状态
  setTimeout(() => {
    cameraPosition.value = { x: 0, y: 0, scale: 1 }
    cameraTransition.value = false
    
    if (starmap) {
      starmap.style.transition = ''
    }
  }, duration)
}

// 自动开始星空地图探险
const startStarmapAdventure = async () => {
  if (!gitStore.commits || gitStore.commits.length === 0) return
  
  // 生成星空地图布局
  generateStarmapLayout()
  
  // 初始化探险者
  initializeExplorer()
  
  // 开始动画
  await nextTick()
  startStarmapAnimation()
}

// 星空地图动画循环 - 小人探险版
const animateStarmap = () => {
  if (currentCommitIndex.value >= commitPositions.value.length) {
    // 动画结束，显示所有连接线
    drawAllConnections()
    explorer.value.isMoving = false
    
    // 让最后一个提交卡片也消失
    setTimeout(() => {
      fadeOutCommitCard()
      // 清理所有视觉效果
      setTimeout(() => {
        cleanupVisualEffects()
      }, 400) // 等待卡片淡出完成后再清理
    }, 2000) // 增加延迟时间确保卡片消失
    
    isAnimating.value = false
    return
  }
  
  const currentPos = commitPositions.value[currentCommitIndex.value]
  if (currentPos) {
    // 如果是第一个提交，直接显示卡片
    if (currentCommitIndex.value === 0) {
      currentCommit.value = currentPos
      currentPos.flagPlanted = true
      setTimeout(() => {
        fadeInCommitCard()
      }, 500)
      
      setTimeout(() => {
        currentCommitIndex.value++
        animateStarmap()
      }, 1000)
      return
    }
    
    // 检查是否需要分支跳变
    const needsJump = shouldJumpToBranch(currentCommitIndex.value)
    
    if (needsJump) {
      // 执行跳变动画
      performBranchJump(currentPos, () => {
        moveToCommitAndPlantFlag(currentPos)
      })
    } else {
      // 正常移动到提交位置
      moveToCommitAndPlantFlag(currentPos)
    }
  }
}

// 检查是否需要分支跳变
const shouldJumpToBranch = (index: number): boolean => {
  if (index === 0) return false
  
  const currentBranch = commitPositions.value[index]?.branch || 'main'
  const previousBranch = commitPositions.value[index - 1]?.branch || 'main'
  
  return currentBranch !== previousBranch
}

// 执行分支跳变动画
const performBranchJump = (targetPos: any, callback: () => void) => {
  explorer.value.isJumping = true
  
  // 跳跃动画持续时间 - 优化为更快的跳跃
  setTimeout(() => {
    explorer.value.isJumping = false
    callback()
  }, 300) // 减少跳跃动画时间，提高流畅度
}

// 移动到提交位置
const moveToCommitAndPlantFlag = (targetPos: any) => {
  explorer.value.isMoving = true
  explorer.value.currentTarget = currentCommitIndex.value
  
  // 计算移动距离和时间 - 保持匀速移动，放慢速度让卡片有更多显示时间
  const distance = Math.sqrt(
    Math.pow(targetPos.x - explorer.value.x, 2) + 
    Math.pow(targetPos.y - explorer.value.y, 2)
  )
  const moveTime = Math.max(1200, Math.min(2400, distance * 4)) // 大幅放慢奔跑速度，让卡片有更多时间显示
  
  // 开始移动动画，路过时插旗
  animateExplorerMovement(targetPos, moveTime, onMovementComplete)
}

// 小人移动动画 - 持续奔跑，路过时插旗，线条跟随脚步
const animateExplorerMovement = (targetPos: any, duration: number, callback: () => void) => {
  const startX = explorer.value.x
  const startY = explorer.value.y
  const deltaX = targetPos.x - startX
  const deltaY = targetPos.y - startY
  const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
  
  let flagPlanted = false // 标记是否已经插旗
  let lineStarted = false // 标记是否已经开始绘制线条
  
  const startTime = Date.now()
  
  const moveStep = () => {
    const currentTime = Date.now()
    const elapsed = currentTime - startTime
    
    const progress = Math.min(elapsed / duration, 1)
    
    // 使用线性移动保持匀速
    const easeProgress = progress
    
    // 添加轻微的上下摆动模拟奔跑节奏
    const runningBounce = Math.sin(progress * distance * 0.05) * 2
    
    explorer.value.x = startX + deltaX * easeProgress
    explorer.value.y = startY + deltaY * easeProgress + runningBounce
    
    // 相机实时跟随骑士位置
    focusCamera(explorer.value.x, explorer.value.y, 1.8, 100)
    
    // 当开始移动时（10%进度）就开始绘制线条，跟随骑士脚步
    if (!lineStarted && progress >= 0.1 && currentCommitIndex.value > 0) {
      lineStarted = true
      drawConnectionLineWithMovement(currentCommitIndex.value - 1, currentCommitIndex.value, duration * 0.9)
    }
    
    // 当接近目标位置时（80%进度）插旗，但继续移动
    if (!flagPlanted && progress >= 0.8) {
      flagPlanted = true
      // 在当前位置插旗和显示效果（不再绘制线条，因为已经在移动时绘制了）
      plantFlagAtPositionWithoutLine(targetPos)
    }
    
    if (progress < 1) {
      requestAnimationFrame(moveStep)
    } else {
      // 移动完成，继续下一个目标
      callback()
    }
  }
  
  requestAnimationFrame(moveStep)
}

// 在指定位置插旗（路过时调用，不绘制连接线）
const plantFlagAtPositionWithoutLine = (targetPos: any) => {
  // 插旗
  targetPos.flagPlanted = true
  
  // 创建旗子的白色光晕效果
  createFlagGlow(targetPos)
  
  // 创建透明陆地边界
  createLandBoundary(targetPos)
  
  // 如果有当前卡片，让它开始延迟消失过程
  if (currentCommit.value) {
    fadeOutCommitCard()
  }
  
  // 设置当前提交并淡入显示卡片
  currentCommit.value = targetPos
  setTimeout(() => {
    fadeInCommitCard()
  }, 200)
  
  // 输出当前卡片信息到控制台
  console.log('🚩 探险者路过并插旗:', {
    索引: currentCommitIndex.value + 1,
    总数: commitPositions.value.length,
    提交哈希: targetPos.hash,
    短哈希: targetPos.hash?.substring(0, 8),
    作者: targetPos.author,
    邮箱: targetPos.email,
    时间: targetPos.time,
    格式化时间: formatTime(targetPos.time),
    提交信息: targetPos.message,
    分支: targetPos.branch || 'main',
    分支颜色: targetPos.branchColor,
    位置: { x: targetPos.x, y: targetPos.y }
  })
  
  // 延迟开始当前位置的陆地边界消失动画，传入正确的索引
  const currentIndex = currentCommitIndex.value // 保存当前索引
  setTimeout(() => {
    fadeOutCurrentLandBoundary(currentIndex)
  }, 1500) // 给用户足够时间观看边界效果
}

// 在指定位置插旗（兼容旧版本调用，包含绘制连接线）
const plantFlagAtPosition = (targetPos: any) => {
  // 调用不绘制线条的版本
  plantFlagAtPositionWithoutLine(targetPos)
  
  // 绘制路径线
  if (currentCommitIndex.value > 0) {
    drawConnectionLine(currentCommitIndex.value - 1, currentCommitIndex.value)
  }
}

// 移动完成后的回调
const onMovementComplete = () => {
  explorer.value.isMoving = false
  
  if (currentCommitIndex.value < commitPositions.value.length - 1) {
    currentCommitIndex.value++
    // 立即继续下一个目标，保持持续奔跑
    animateStarmap()
  } else {
    // 动画结束，回到全景视图
    setTimeout(() => {
      resetCamera(1500)
      isAnimating.value = false
    }, 800)
  }
}

// 创建旗子白色光晕效果
const createFlagGlow = (targetPos: any) => {
  if (!starsContainer.value) return
  
  const glow = document.createElement('div')
  glow.className = 'flag-glow'
  glow.style.cssText = `
    position: absolute;
    left: ${targetPos.x - 15}px;
    top: ${targetPos.y + 25}px;
    width: 30px;
    height: 30px;
    background: radial-gradient(circle, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0.4) 40%, rgba(255,255,255,0) 70%);
    border-radius: 50%;
    pointer-events: none;
    animation: flagGlow 2s ease-in-out infinite alternate;
    z-index: 10;
  `
  
  starsContainer.value.appendChild(glow)
}

// 创建透明陆地边界
const createLandBoundary = (targetPos: any) => {
  if (!connectionSvg.value) return
  
  // 生成不规则的陆地形状（类似某个省份的边界）
  const landPath = generateLandShape(targetPos.x, targetPos.y)
  
  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
  path.setAttribute('d', landPath)
  path.setAttribute('fill', 'none')
  path.setAttribute('stroke', 'rgba(255,255,255,0.6)')
  path.setAttribute('stroke-width', '1.5')
  path.setAttribute('opacity', '0')
  path.setAttribute('class', 'land-boundary')
  path.setAttribute('data-commit-index', currentCommitIndex.value.toString()) // 添加索引标识
  
  connectionSvg.value.appendChild(path)
  
  // 动画显示边界 - 更快显示让用户能看到
  setTimeout(() => {
    path.setAttribute('opacity', '0.6')
  }, 100)
}

// 让指定位置的陆地边界渐淡消失
const fadeOutCurrentLandBoundary = (commitIndex: number) => {
  if (!connectionSvg.value) return
  
  // 找到指定提交位置对应的陆地边界
  const currentBoundary = connectionSvg.value.querySelector(`path.land-boundary[data-commit-index="${commitIndex}"]`)
  
  if (currentBoundary) {
    console.log('🌍 开始陆地边界消失动画，索引:', commitIndex)
    // 延迟开始消失动画，让边界显示更长时间
    setTimeout(() => {
      // 添加CSS过渡效果
      currentBoundary.style.transition = 'opacity 1.2s ease-out'
      currentBoundary.setAttribute('opacity', '0')
      
      // 延迟移除元素
      setTimeout(() => {
        if (currentBoundary.parentNode) {
          currentBoundary.parentNode.removeChild(currentBoundary)
          console.log('🌍 陆地边界已移除，索引:', commitIndex)
        }
      }, 1200) // 与过渡时间匹配
    }, 1000) // 延迟1秒开始消失，让用户有时间观看
  } else {
    console.warn('⚠️ 未找到陆地边界元素，索引:', commitIndex)
  }
}

// 生成不规则陆地形状
const generateLandShape = (centerX: number, centerY: number) => {
  const baseRadius = (20 + Math.random() * 10) * 1.3 // 基础半径26-39px (扩大到1.3倍)
  const points: string[] = []
  const numPoints = 8 + Math.floor(Math.random() * 4) // 8-12个点
  
  for (let i = 0; i < numPoints; i++) {
    const angle = (i / numPoints) * 2 * Math.PI
    // 添加随机变化使形状不规则
    const radiusVariation = 0.7 + Math.random() * 0.6 // 0.7-1.3倍变化
    const angleVariation = (Math.random() - 0.5) * 0.3 // 角度微调
    
    const radius = baseRadius * radiusVariation
    const adjustedAngle = angle + angleVariation
    
    const x = centerX + Math.cos(adjustedAngle) * radius
    const y = centerY + Math.sin(adjustedAngle) * radius
    
    if (i === 0) {
      points.push(`M ${x} ${y}`)
    } else {
      // 使用二次贝塞尔曲线创建平滑的边界
      const prevAngle = ((i - 1) / numPoints) * 2 * Math.PI
      const prevX = centerX + Math.cos(prevAngle) * baseRadius * (0.7 + Math.random() * 0.6)
      const prevY = centerY + Math.sin(prevAngle) * baseRadius * (0.7 + Math.random() * 0.6)
      
      const controlX = (prevX + x) / 2 + (Math.random() - 0.5) * 10
      const controlY = (prevY + y) / 2 + (Math.random() - 0.5) * 10
      
      points.push(`Q ${controlX} ${controlY} ${x} ${y}`)
    }
  }
  
  points.push('Z') // 闭合路径
  return points.join(' ')
}

// 清理所有视觉效果
const cleanupVisualEffects = () => {
  // 清理所有旗子光晕效果
  if (starsContainer.value) {
    const glows = starsContainer.value.querySelectorAll('.flag-glow')
    glows.forEach(glow => {
      glow.style.opacity = '0'
      setTimeout(() => {
        glow.remove()
      }, 500)
    })
  }
  
  // 清理所有陆地边界
  if (connectionSvg.value) {
    const boundaries = connectionSvg.value.querySelectorAll('.land-boundary')
    boundaries.forEach(boundary => {
      boundary.setAttribute('opacity', '0')
      setTimeout(() => {
        boundary.remove()
      }, 500)
    })
  }
}

// 卡片淡出动画 - 使用延迟渐淡消失效果
const fadeOutCommitCard = () => {
  const cardElement = document.querySelector('.current-commit-info')
  if (cardElement) {
    console.log('💳 开始卡片延迟消失动画')
    // 延迟开始消失动画，让卡片显示更长时间，配合更慢的骑士移动速度
    setTimeout(() => {
      cardElement.classList.remove('show')
      // 等待CSS过渡完成后清除currentCommit
      setTimeout(() => {
        currentCommit.value = null
        console.log('💳 卡片已完全消失')
      }, 300) // 与CSS过渡时间匹配
    }, 2000) // 延迟2秒开始消失，给卡片更多显示时间
  } else {
    // 如果没有找到卡片元素，直接清除currentCommit
    currentCommit.value = null
  }
}

// 卡片淡入动画
const fadeInCommitCard = () => {
  const cardElement = document.querySelector('.current-commit-info')
  if (cardElement) {
    cardElement.classList.add('show')
  }
}

// 绘制连接线 - 跟随骑士移动同步绘制弯曲虚线（九曲山路十八弯风格）
const drawConnectionLineWithMovement = (fromIndex: number, toIndex: number, moveDuration: number) => {
  if (!connectionSvg.value) return
  
  const fromPos = commitPositions.value[fromIndex]
  const toPos = commitPositions.value[toIndex]
  
  if (!fromPos || !toPos) return
  
  // 计算基础参数
  const dx = toPos.x - fromPos.x
  const dy = toPos.y - fromPos.y
  const distance = Math.sqrt(dx * dx + dy * dy)
  
  // 生成多个控制点，创建"九曲山路十八弯"效果
  const numCurves = Math.max(3, Math.floor(distance / 60)) // 根据距离决定弯曲次数
  const controlPoints: {x: number, y: number}[] = []
  
  for (let i = 1; i < numCurves; i++) {
    const t = i / numCurves
    const baseX = fromPos.x + dx * t
    const baseY = fromPos.y + dy * t
    
    // 计算垂直偏移
    const perpX = -dy / distance
    const perpY = dx / distance
    
    // 创建不规律的弯曲
    const amplitude = Math.min(distance * 0.2, 60) // 弯曲幅度
    const frequency = 2 + Math.sin(fromIndex * 1.3) // 频率变化
    const phase = fromIndex * 0.8 + i * 1.2 // 相位偏移
    
    const offset = Math.sin(t * Math.PI * frequency + phase) * amplitude * 
                   (1 + Math.sin(t * Math.PI * 3 + phase * 0.5) * 0.3) // 叠加波形
    
    controlPoints.push({
      x: baseX + perpX * offset,
      y: baseY + perpY * offset
    })
  }
  
  // 创建SVG路径元素
  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
  const initialPath = `M ${fromPos.x} ${fromPos.y}`
  path.setAttribute('d', initialPath)
  path.setAttribute('stroke', 'rgba(78, 205, 196, 0.7)') // 带透明度的蓝色
  path.setAttribute('stroke-width', '2')
  path.setAttribute('stroke-dasharray', '8,6') // 更虚的虚线样式
  path.setAttribute('stroke-linecap', 'round')
  path.setAttribute('fill', 'none')
  path.setAttribute('opacity', '0.8')
  path.setAttribute('class', 'connection-line')
  
  connectionSvg.value.appendChild(path)
  
  // 动画绘制曲线 - 与骑士移动同步
  const startTime = Date.now()
  
  const animate = () => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / moveDuration, 1)
    
    if (progress === 0) {
      path.setAttribute('d', `M ${fromPos.x} ${fromPos.y}`)
    } else {
      // 构建复杂的曲线路径
      let pathData = `M ${fromPos.x} ${fromPos.y}`
      
      // 根据进度决定显示多少个控制点
      const visiblePoints = Math.floor(controlPoints.length * progress)
      const remainingProgress = (controlPoints.length * progress) % 1
      
      if (visiblePoints === 0 && remainingProgress > 0) {
        // 第一段曲线
        const targetX = fromPos.x + (controlPoints[0].x - fromPos.x) * remainingProgress
        const targetY = fromPos.y + (controlPoints[0].y - fromPos.y) * remainingProgress
        pathData += ` Q ${controlPoints[0].x} ${controlPoints[0].y} ${targetX} ${targetY}`
      } else {
        // 绘制完整的控制点段
        for (let i = 0; i < visiblePoints; i++) {
          const nextPoint = i < controlPoints.length - 1 ? controlPoints[i + 1] : toPos
          pathData += ` Q ${controlPoints[i].x} ${controlPoints[i].y} ${nextPoint.x} ${nextPoint.y}`
        }
        
        // 绘制部分的最后一段
        if (remainingProgress > 0 && visiblePoints < controlPoints.length) {
          const currentControl = controlPoints[visiblePoints]
          const nextTarget = visiblePoints < controlPoints.length - 1 ? controlPoints[visiblePoints + 1] : toPos
          const partialX = currentControl.x + (nextTarget.x - currentControl.x) * remainingProgress
          const partialY = currentControl.y + (nextTarget.y - currentControl.y) * remainingProgress
          pathData += ` Q ${currentControl.x} ${currentControl.y} ${partialX} ${partialY}`
        }
        
        // 如果已经到达终点
        if (progress === 1 && visiblePoints >= controlPoints.length) {
          const lastControl = controlPoints[controlPoints.length - 1]
          pathData += ` Q ${lastControl.x} ${lastControl.y} ${toPos.x} ${toPos.y}`
        }
      }
      
      path.setAttribute('d', pathData)
    }
    
    if (progress < 1) {
      requestAnimationFrame(animate)
    }
  }
  
  requestAnimationFrame(animate)
}

// 绘制连接线 - 兼容旧版本调用（立即绘制）
const drawConnectionLine = (fromIndex: number, toIndex: number) => {
  drawConnectionLineWithMovement(fromIndex, toIndex, 800)
}

// 绘制所有连接线 - 按照无交叉路径顺序连接（九曲山路十八弯风格）
const drawAllConnections = () => {
  if (!connectionSvg.value || commitPositions.value.length < 2) return
  
  // 清除现有连接线
  connectionSvg.value.innerHTML = connectionSvg.value.querySelector('defs')?.outerHTML || ''
  
  // 按照时间顺序连接相邻的提交节点
  for (let i = 1; i < commitPositions.value.length; i++) {
    const fromPos = commitPositions.value[i - 1]
    const toPos = commitPositions.value[i]
    
    // 计算基础参数
    const dx = toPos.x - fromPos.x
    const dy = toPos.y - fromPos.y
    const distance = Math.sqrt(dx * dx + dy * dy)
    
    // 生成多个控制点，创建"九曲山路十八弯"效果
    const numCurves = Math.max(3, Math.floor(distance / 60)) // 根据距离决定弯曲次数
    const controlPoints: {x: number, y: number}[] = []
    
    for (let j = 1; j < numCurves; j++) {
      const t = j / numCurves
      const baseX = fromPos.x + dx * t
      const baseY = fromPos.y + dy * t
      
      // 计算垂直偏移
      const perpX = -dy / distance
      const perpY = dx / distance
      
      // 创建不规律的弯曲
      const amplitude = Math.min(distance * 0.2, 60) // 弯曲幅度
      const frequency = 2 + Math.sin((i-1) * 1.3) // 频率变化
      const phase = (i-1) * 0.8 + j * 1.2 // 相位偏移
      
      const offset = Math.sin(t * Math.PI * frequency + phase) * amplitude * 
                     (1 + Math.sin(t * Math.PI * 3 + phase * 0.5) * 0.3) // 叠加波形
      
      controlPoints.push({
        x: baseX + perpX * offset,
        y: baseY + perpY * offset
      })
    }
    
    // 构建复杂的曲线路径
    let pathData = `M ${fromPos.x} ${fromPos.y}`
    
    // 绘制所有控制点段
    for (let j = 0; j < controlPoints.length; j++) {
      const nextPoint = j < controlPoints.length - 1 ? controlPoints[j + 1] : toPos
      pathData += ` Q ${controlPoints[j].x} ${controlPoints[j].y} ${nextPoint.x} ${nextPoint.y}`
    }
    
    // 如果没有控制点，直接连到终点
    if (controlPoints.length === 0) {
      pathData += ` L ${toPos.x} ${toPos.y}`
    }
    
    // 创建SVG路径元素
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
    path.setAttribute('d', pathData)
    path.setAttribute('stroke', 'rgba(78, 205, 196, 0.5)') // 带透明度的蓝色，稍微更透明
    path.setAttribute('stroke-width', '3')
    path.setAttribute('stroke-dasharray', '8,6') // 更虚的虚线样式
    path.setAttribute('opacity', '0.6')
    path.setAttribute('stroke-linecap', 'round')
    path.setAttribute('fill', 'none')
    
    connectionSvg.value.appendChild(path)
  }
  
  // 标记所有节点为已连接
  commitPositions.value.forEach(pos => {
    pos.connected = true
  })
}

// 星星生成函数
const generateStars = () => {
  if (!starsContainer.value) return
  
  // 清除现有星星
  starsContainer.value.innerHTML = ''
  
  // 生成200-300个随机星星
  const starCount = Math.floor(Math.random() * 100) + 200
  
  for (let i = 0; i < starCount; i++) {
    const star = document.createElement('div')
    star.className = 'star'
    
    // 随机位置
    const x = Math.random() * 100
    const y = Math.random() * 100
    
    // 随机大小 (1-4px)
    const size = Math.random() * 3 + 1
    
    // 随机形状 (圆形或方形)
    const isCircle = Math.random() > 0.3
    
    // 随机透明度
    const opacity = Math.random() * 0.8 + 0.2
    
    // 随机颜色 (白色系)
    const colors = ['#ffffff', '#f0f8ff', '#e6e6fa', '#faf0e6', '#f5f5dc']
    const color = colors[Math.floor(Math.random() * colors.length)]
    
    // 设置样式
    star.style.cssText = `
      position: absolute;
      left: ${x}%;
      top: ${y}%;
      width: ${size}px;
      height: ${size}px;
      background-color: ${color};
      opacity: ${opacity};
      border-radius: ${isCircle ? '50%' : '0'};
      pointer-events: none;
    `
    
    // 30%的星星有闪烁效果
    if (Math.random() < 0.3) {
      const duration = Math.random() * 3 + 2 // 2-5秒
      const delay = Math.random() * 2 // 0-2秒延迟
      star.style.animation = `twinkle ${duration}s ease-in-out ${delay}s infinite alternate`
    }
    
    // 10%的星星有移动效果
    if (Math.random() < 0.1) {
      const duration = Math.random() * 20 + 10 // 10-30秒
      star.style.animation += `, drift ${duration}s linear infinite`
    }
    
    starsContainer.value.appendChild(star)
  }
}

const startVisualization = async () => {
  if (!form.repoPath.trim()) {
    ElMessage.warning('Please enter a repository path')
    return
  }
  
  loading.value = true
  isTransitioning.value = true
  
  try {
    // 设置仓库配置
    gitStore.setRepoConfig({
      path: form.repoPath.trim(),
      maxCount: 0
    })
    
    // 检查后端服务
    const isHealthy = await gitStore.checkHealth()
    if (!isHealthy) {
      throw new Error('Backend service unavailable, please ensure backend is running')
    }
    
    // 加载Git仓库数据
    await gitStore.loadData()
    
    // 等待渐变消失动画完成
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 切换到可视化界面
    showVisualization.value = true
    
    // 等待DOM更新完成后自动开始星空地图探险
    await nextTick()
    
    // 清理之前的状态
    if (connectionSvg.value) {
      connectionSvg.value.innerHTML = connectionSvg.value.querySelector('defs')?.outerHTML || ''
    }
    
    // 稍微延迟一下确保界面完全渲染
    setTimeout(() => {
      startStarmapAdventure()
    }, 500)
    
  } catch (error: any) {
    console.error('Failed to load git repository:', error)
    ElMessage.error(error.message || 'Failed to load repository data')
    showVisualization.value = false
    isTransitioning.value = false
  } finally {
    loading.value = false
  }
}

// 开始星图动画
const startStarmapAnimation = () => {
  if (isAnimating.value || !commitPositions.value.length) return
  
  isAnimating.value = true
  currentCommitIndex.value = 0
  
  // 重置所有状态
  commitPositions.value.forEach(commit => {
    commit.visible = false
    commit.connected = false
    commit.flagPlanted = false
  })
  
  // 隐藏卡片
  fadeOutCommitCard()
  
  // 先聚焦到骑士当前位置
  console.log('🎬 开始动画，聚焦到骑士位置:', {
    x: explorer.value.x,
    y: explorer.value.y
  })
  focusCamera(explorer.value.x, explorer.value.y, 1.8, 1000)
  
  // 延迟开始动画，等待相机聚焦完成
  setTimeout(() => {
    animateStarmap()
  }, 1200)
}

// 相机现在直接在移动动画中跟随骑士，无需复杂的watch逻辑

// 初始化探险者位置
const initializeExplorer = () => {
  if (!commitPositions.value.length) return
  
  // 重置状态
  currentCommitIndex.value = 0
  currentCommit.value = null
  
  // 清除之前的动画
  if (animationId.value) {
    clearTimeout(animationId.value)
  }
  
  // 重置所有commit的可见性、连接状态和旗子状态
  commitPositions.value.forEach(pos => {
    pos.visible = false
    pos.connected = false
    pos.flagPlanted = false
  })
  
  // 初始化探险者位置到第一个提交位置
  if (commitPositions.value.length > 0) {
    const firstCommit = commitPositions.value[0]
    explorer.value.x = firstCommit.x
    explorer.value.y = firstCommit.y
    explorer.value.isMoving = false
    explorer.value.isJumping = false
    explorer.value.currentTarget = -1
    
    console.log('🏇 初始化骑士位置:', {
      x: explorer.value.x,
      y: explorer.value.y,
      firstCommit: firstCommit
    })
  }
  
  // 确保卡片初始状态为隐藏
  fadeOutCommitCard()
  
  // 聚焦到骑士位置
  setTimeout(() => {
    if (commitPositions.value.length > 0) {
      console.log('📷 相机聚焦到骑士位置:', {
        x: explorer.value.x,
        y: explorer.value.y,
        容器尺寸: {
          width: starmapContainer.value?.clientWidth,
          height: starmapContainer.value?.clientHeight
        }
      })
      
      // 添加骑士元素的实际DOM位置检查
      const explorerElement = document.querySelector('.explorer-on-horse')
      if (explorerElement) {
        const rect = explorerElement.getBoundingClientRect()
        console.log('🏇 骑士DOM元素位置:', {
          left: explorerElement.style.left,
          top: explorerElement.style.top,
          boundingRect: {
            x: rect.x,
            y: rect.y,
            width: rect.width,
            height: rect.height
          }
        })
      }
      
      focusCamera(explorer.value.x, explorer.value.y, 1.8)
    }
  }, 500)
}



// 窗口大小变化处理
const handleResize = () => {
  if (starmapContainer.value && commitPositions.value.length > 0) {
    // 重新生成布局
    generateStarmapLayout()
  }
}

// 组件挂载时生成星星和添加事件监听
onMounted(() => {
  generateStars()
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
onUnmounted(() => {
  if (starsContainer.value) {
    starsContainer.value.innerHTML = ''
  }
  
  // 清理动画
  if (animationId.value) {
    clearTimeout(animationId.value)
  }
  
  // 移除事件监听
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

.home {
  position: relative;
  width: 100%;
  height: 100vh;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  overflow: hidden;
  font-family: 'Orbitron', monospace;
}

// 宇宙背景
.cosmic-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
  z-index: -3;
}

// 动态星星容器
.stars-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -2;
  overflow: hidden;
}

// 星星动画
@keyframes twinkle {
  0% { opacity: 0.2; }
  50% { opacity: 1; }
  100% { opacity: 0.2; }
}

@keyframes drift {
  0% { transform: translateX(0) translateY(0); }
  25% { transform: translateX(10px) translateY(-5px); }
  50% { transform: translateX(-5px) translateY(-10px); }
  75% { transform: translateX(-10px) translateY(5px); }
  100% { transform: translateX(0) translateY(0); }
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes inputGradientShift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

// 淡入向上动画
@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

// 淡入动画类
.fade-in-up {
  opacity: 0;
  animation: fadeInUp 0.8s ease-out forwards;
}

// 整体淡入动画
@keyframes fadeIn {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

.fade-in {
  opacity: 0;
  animation: fadeIn 1s ease-out forwards;
}

// 旗子光晕动画
@keyframes flagGlow {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.2);
    opacity: 0.4;
  }
}



// 主内容区域
.main-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  transition: all 1s ease-out;
  
  &.fade-out {
    opacity: 0;
    transform: scale(0.9) translateY(-50px);
  }
}

// 标题区域
.title-section {
  text-align: center;
  margin-bottom: 4rem;
  
  .cosmic-title {
    font-size: 4rem;
    font-weight: 900;
    margin-bottom: 1rem;
    
    .gradient-text {
      background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57, #ff9ff3, #54a0ff);
      background-size: 400% 400%;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      animation: gradientShift 8s ease infinite;
      text-shadow: 0 0 30px rgba(255, 255, 255, 0.3);
    }
  }
  
  .subtitle-glow {
    position: relative;
    
    .cosmic-subtitle {
      font-size: 1.2rem;
      color: rgba(255, 255, 255, 0.8);
      font-weight: 400;
      letter-spacing: 1px;
      text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
    }
  }
}



// 输入容器
.input-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  width: 100%;
  max-width: 1200px;
}

// 宇宙风格输入框
.cosmic-input-wrapper {
  position: relative;
  width: 100%;
  max-width: 400px;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: scale(1.01);
  }
  
  .cosmic-input {
    width: 100%;
    padding: 1.5rem 2rem;
    font-size: 1.1rem;
    font-family: 'Orbitron', monospace;
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 50px;
    color: white;
    backdrop-filter: blur(2px);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    z-index: 2;
    
    &::placeholder {
      color: rgba(255, 255, 255, 0.6);
    }
    
    &:hover {
      border-color: rgba(74, 144, 226, 0.8);
      background: rgba(255, 255, 255, 0.05);
      box-shadow: 0 0 30px rgba(74, 144, 226, 0.3);
      transform: translateY(-2px);
      backdrop-filter: blur(5px);
    }
    
    &:focus {
      outline: none;
      border-color: #4a90e2;
      background: rgba(255, 255, 255, 0.1);
      box-shadow: 0 0 40px rgba(74, 144, 226, 0.5);
      transform: translateY(-3px);
      backdrop-filter: blur(8px);
    }
  }
  
  .input-glow {
     position: absolute;
     top: -2px;
     left: -2px;
     right: -2px;
     bottom: -2px;
     border-radius: 27px;
     background: linear-gradient(45deg, #4a90e2, #63b3ed, #9f7aea, #4a90e2);
     background-size: 300% 300%;
     opacity: 0;
     z-index: 1;
     transition: opacity 0.4s ease;
     animation: inputGradientShift 3s ease-in-out infinite;
   }
   
   &:hover .input-glow {
     opacity: 0.4;
   }
   
   .cosmic-input:focus + .input-glow {
     opacity: 0.6;
   }
}

// 控制区域
.controls {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

// 宇宙风格按钮
.cosmic-button {
  position: relative;
  padding: 1rem 2.5rem;
  font-size: 1.1rem;
  font-weight: 700;
  font-family: 'Orbitron', monospace;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  overflow: hidden;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(255, 255, 255, 0.2);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .loading-text {
    animation: pulse 1.5s ease-in-out infinite;
  }
  
}

// 可视化界面
.visualization-section {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}



// Git星空地图探险样式
.starmap-adventure {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.starmap-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.starmap-content {
  position: relative;
  width: 100%;
  height: 100%;
  transform-origin: center center;
  will-change: transform;
}

.git-starmap-adventure {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.starmap-background {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.commit-nodes-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 3;
  pointer-events: none;
}

.commit-node {
  position: absolute;
  width: 16px;
  height: 16px;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: all 0.5s ease;
  cursor: pointer;
  pointer-events: auto;
}

.commit-node.visible {
  opacity: 1;
  animation: nodeAppear 0.8s ease-out;
}

.commit-node.current {
  width: 24px;
  height: 24px;
  animation: pulse 2s infinite;
}

.commit-node.connected {
  opacity: 0.8;
}

.node-circle {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid #fff;
  background: var(--branch-color, #4ecdc4);
  box-shadow: 0 0 10px var(--branch-color, #4ecdc4);
}

.node-pulse {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200%;
  height: 200%;
  border-radius: 50%;
  border: 2px solid var(--branch-color, #4ecdc4);
  transform: translate(-50%, -50%);
  animation: pulseRing 2s infinite;
  opacity: 0;
}

.commit-info-tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 12px;
  min-width: 250px;
  z-index: 10;
  backdrop-filter: blur(10px);
  margin-top: 10px;
  color: white;
  font-size: 0.8rem;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.commit-hash {
  font-family: 'Courier New', monospace;
  color: #64ffda;
  font-weight: bold;
}

.commit-time {
  color: #888;
  font-size: 0.7rem;
}

.commit-author {
  color: #4ecdc4;
  margin-bottom: 4px;
  font-weight: 600;
}

.commit-message {
  color: #ccc;
  line-height: 1.3;
  word-wrap: break-word;
}

.connections-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  pointer-events: none;
}

.connection-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  pointer-events: none;
}

@keyframes nodeAppear {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 0;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.3);
  }
  100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }
}

@keyframes pulseRing {
  0% {
    transform: translate(-50%, -50%) scale(0.5);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(2);
    opacity: 0;
  }
}

/* 旗子样式 */
.commit-flag {
  position: absolute;
  transform: translate(-50%, -100%);
  z-index: 10;
  opacity: 0;
  transition: opacity 0.5s ease;
}

.commit-flag.planted {
  opacity: 1;
}

.flag-pole {
  width: 2px;
  height: 40px;
  background: linear-gradient(to bottom, #8B4513, #A0522D);
  margin: 0 auto;
  position: relative;
}

.flag {
  position: absolute;
  top: 0;
  left: 2px;
  width: 24px;
  height: 16px;
  clip-path: polygon(0 0, 100% 0, 85% 50%, 100% 100%, 0 100%);
  animation: flagWave 2s ease-in-out infinite;
  transform-origin: left center;
}

@keyframes flagWave {
  0%, 100% { transform: rotateY(0deg); }
  50% { transform: rotateY(10deg); }
}

.flag-label {
  position: absolute;
  top: -8px;
  left: 28px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  white-space: nowrap;
  pointer-events: none;
}

/* 骑马探险者样式 */
.explorer-on-horse {
  position: absolute;
  width: 24px;  /* 缩小人物尺寸以增强与路程的对比 */
  height: 28px; /* 缩小人物尺寸以增强与路程的对比 */
  transform: translate(-50%, -100%);
  z-index: 15;
  transition: all 0.1s ease;
}

.explorer-on-horse.moving {
  animation: horseGallop 0.6s ease-in-out infinite;
}

.explorer-on-horse.moving .horse-leg {
  animation: horseLegMove 0.3s ease-in-out infinite;
}

.explorer-on-horse.moving .horse-leg.front-left {
  animation-delay: 0s;
}

.explorer-on-horse.moving .horse-leg.back-right {
  animation-delay: 0s;
}

.explorer-on-horse.moving .horse-leg.front-right {
  animation-delay: 0.15s;
}

.explorer-on-horse.moving .horse-leg.back-left {
  animation-delay: 0.15s;
}

.explorer-on-horse.moving .horse-tail {
  animation: tailSwish 0.4s ease-in-out infinite;
}

.explorer-on-horse.moving .horse-mane {
  animation: maneFlow 0.6s ease-in-out infinite;
}

.explorer-on-horse.moving .rider {
  animation: riderBounce 0.6s ease-in-out infinite;
}

.explorer-on-horse.jumping {
  animation: horseJumping 0.6s ease-in-out;
}

/* 马匹样式 */
.horse {
  position: relative;
  width: 100%;
  height: 18px; /* 缩小马匹高度 */
}

.horse-body {
  position: absolute;
  bottom: 5px;
  left: 50%;
  transform: translateX(-50%);
  width: 18px; /* 缩小马匹身体宽度 */
  height: 8px;  /* 缩小马匹身体高度 */
  background: #8B4513;
  border-radius: 4px;
}

.horse-head {
  position: absolute;
  bottom: 10px;
  left: 1px;
  width: 5px;  /* 缩小马头宽度 */
  height: 6px;  /* 缩小马头高度 */
  background: #A0522D;
  border-radius: 3px 3px 1px 1px;
}

.horse-legs {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 18px;  /* 缩小腿部区域宽度 */
  height: 5px;  /* 缩小腿部区域高度 */
}

.horse-leg {
  position: absolute;
  width: 1.5px;  /* 缩小腿部宽度 */
  height: 5px;    /* 缩小腿部高度 */
  background: #654321;
  border-radius: 1px;
}

.horse-leg.front-left {
  left: 2px;  /* 调整前腿位置 */
}

.horse-leg.front-right {
  left: 5px;  /* 调整前腿位置 */
}

.horse-leg.back-left {
  right: 5px;  /* 调整后腿位置 */
}

.horse-leg.back-right {
  right: 2px;  /* 调整后腿位置 */
}

.horse-tail {
  position: absolute;
  bottom: 8px;  /* 调整尾巴位置 */
  right: 0;
  width: 2px;   /* 缩小尾巴宽度 */
  height: 5px;  /* 缩小尾巴高度 */
  background: #654321;
  border-radius: 0 0 1px 1px;
  transform-origin: top center;
}

.horse-mane {
  position: absolute;
  bottom: 12px;  /* 调整鬃毛位置 */
  left: 4px;
  width: 2px;    /* 缩小鬃毛宽度 */
  height: 4px;   /* 缩小鬃毛高度 */
  background: #654321;
  border-radius: 1px;
  transform-origin: bottom center;
}

/* 骑手样式 */
.rider {
  position: absolute;
  top: -10px;  /* 调整骑手位置 */
  left: 50%;
  transform: translateX(-50%);
  width: 10px;  /* 缩小骑手宽度 */
  height: 12px; /* 缩小骑手高度 */
}

.rider-body {
  position: relative;
  width: 100%;
  height: 100%;
}

.rider-head {
  width: 4px;   /* 缩小头部宽度 */
  height: 4px;  /* 缩小头部高度 */
  background: #FFE4B5;
  border-radius: 50%;
  margin: 0 auto 1px;
  border: 1px solid #DEB887;
}

.rider-torso {
  width: 5px;   /* 缩小躯干宽度 */
  height: 5px;  /* 缩小躯干高度 */
  background: #4169E1;
  margin: 0 auto 1px;
  border-radius: 1px;
  position: relative;
}

.rider-legs {
  position: absolute;
  top: 5px;   /* 调整腿部位置 */
  left: 50%;
  transform: translateX(-50%);
  width: 8px;  /* 缩小腿部区域宽度 */
  height: 5px; /* 缩小腿部区域高度 */
}

.rider-legs .leg {
  position: absolute;
  width: 1px;  /* 缩小腿部宽度 */
  height: 5px; /* 缩小腿部高度 */
  background: #2F4F4F;
  border-radius: 1px;
}

.rider-legs .leg.left {
  left: 1px;   /* 调整左腿位置 */
}

.rider-legs .leg.right {
  right: 1px;  /* 调整右腿位置 */
}

.rider-arms {
  position: absolute;
  top: 1px;
  left: 50%;
  transform: translateX(-50%);
  width: 8px;  /* 缩小手臂区域宽度 */
  height: 1px; /* 缩小手臂区域高度 */
}

.rider-arms .arm {
  position: absolute;
  width: 3px;  /* 缩小手臂宽度 */
  height: 1px; /* 缩小手臂高度 */
  background: #FFE4B5;
  border-radius: 1px;
}

.rider-arms .arm.left {
  left: 0;
  transform: rotate(-30deg);
}

.rider-arms .arm.right {
  right: 0;
  transform: rotate(30deg);
}

.rider-backpack {
  position: absolute;
  top: 4px;    /* 调整背包位置 */
  left: 50%;
  transform: translateX(-50%);
  width: 3px;  /* 缩小背包宽度 */
  height: 4px; /* 缩小背包高度 */
  background: #8B4513;
  border-radius: 1px;
  z-index: -1;
}

@keyframes legWalk1 {
  0%, 100% { transform: rotateX(0deg); }
  50% { transform: rotateX(20deg); }
}

@keyframes legWalk2 {
  0%, 100% { transform: rotateX(0deg); }
  50% { transform: rotateX(-20deg); }
}

@keyframes armSwingLeft {
  0%, 100% { transform: rotate(-20deg); }
  50% { transform: rotate(-40deg); }
}

@keyframes armSwingRight {
  0%, 100% { transform: rotate(20deg); }
  50% { transform: rotate(40deg); }
}

.explorer.jumping {
  animation: jumping 0.6s ease-in-out;
}

/* 马匹奔跑动画 */
@keyframes horseGallop {
  0% { transform: translate(-50%, -100%) rotateZ(0deg) translateY(0px); }
  12.5% { transform: translate(-50%, -100%) rotateZ(-2deg) translateY(-1px); }
  25% { transform: translate(-50%, -100%) rotateZ(-4deg) translateY(-3px); }
  37.5% { transform: translate(-50%, -100%) rotateZ(-2deg) translateY(-5px); }
  50% { transform: translate(-50%, -100%) rotateZ(0deg) translateY(-6px); }
  62.5% { transform: translate(-50%, -100%) rotateZ(2deg) translateY(-5px); }
  75% { transform: translate(-50%, -100%) rotateZ(4deg) translateY(-3px); }
  87.5% { transform: translate(-50%, -100%) rotateZ(2deg) translateY(-1px); }
  100% { transform: translate(-50%, -100%) rotateZ(0deg) translateY(0px); }
}

@keyframes horseLegMove {
  0% { transform: rotateX(0deg) translateY(0px); }
  25% { transform: rotateX(45deg) translateY(-1px); }
  50% { transform: rotateX(60deg) translateY(-2px); }
  75% { transform: rotateX(30deg) translateY(-1px); }
  100% { transform: rotateX(0deg) translateY(0px); }
}

@keyframes tailSwish {
  0% { transform: rotate(0deg); }
  16.7% { transform: rotate(-20deg); }
  33.3% { transform: rotate(-10deg); }
  50% { transform: rotate(5deg); }
  66.7% { transform: rotate(20deg); }
  83.3% { transform: rotate(10deg); }
  100% { transform: rotate(0deg); }
}

@keyframes maneFlow {
  0% { transform: rotate(0deg) translateY(0px); }
  25% { transform: rotate(-15deg) translateY(-1px); }
  50% { transform: rotate(-8deg) translateY(-2px); }
  75% { transform: rotate(5deg) translateY(-1px); }
  100% { transform: rotate(0deg) translateY(0px); }
}

@keyframes riderBounce {
  0% { transform: translateX(-50%) translateY(0px) rotateZ(0deg); }
  12.5% { transform: translateX(-50%) translateY(-1px) rotateZ(-1deg); }
  25% { transform: translateX(-50%) translateY(-2px) rotateZ(-2deg); }
  37.5% { transform: translateX(-50%) translateY(-3px) rotateZ(-1deg); }
  50% { transform: translateX(-50%) translateY(-4px) rotateZ(0deg); }
  62.5% { transform: translateX(-50%) translateY(-3px) rotateZ(1deg); }
  75% { transform: translateX(-50%) translateY(-2px) rotateZ(2deg); }
  87.5% { transform: translateX(-50%) translateY(-1px) rotateZ(1deg); }
  100% { transform: translateX(-50%) translateY(0px) rotateZ(0deg); }
}

@keyframes walking {
  0%, 100% { transform: translate(-50%, -100%) rotateZ(0deg) translateX(0px); }
  25% { transform: translate(-50%, -100%) rotateZ(-8deg) translateX(-3px); }
  50% { transform: translate(-50%, -100%) rotateZ(0deg) translateX(0px); }
  75% { transform: translate(-50%, -100%) rotateZ(8deg) translateX(3px); }
}

@keyframes jumping {
  0% { transform: translate(-50%, -100%) translateY(0) scale(1); }
  25% { transform: translate(-50%, -100%) translateY(-15px) scale(1.1); }
  50% { transform: translate(-50%, -100%) translateY(-20px) scale(1.2); }
  75% { transform: translate(-50%, -100%) translateY(-15px) scale(1.1); }
  100% { transform: translate(-50%, -100%) translateY(0) scale(1); }
}

@keyframes horseJumping {
  0% { transform: translate(-50%, -100%) translateY(0) scale(1) rotateZ(0deg); }
  25% { transform: translate(-50%, -100%) translateY(-20px) scale(1.1) rotateZ(-5deg); }
  50% { transform: translate(-50%, -100%) translateY(-30px) scale(1.2) rotateZ(0deg); }
  75% { transform: translate(-50%, -100%) translateY(-20px) scale(1.1) rotateZ(5deg); }
  100% { transform: translate(-50%, -100%) translateY(0) scale(1) rotateZ(0deg); }
}

.explorer-body {
  position: relative;
  width: 100%;
  height: 100%;
}

.explorer-head {
  width: 8px;
  height: 8px;
  background: #FFE4B5;
  border-radius: 50%;
  margin: 0 auto 2px;
  border: 1px solid #DEB887;
}

.explorer-torso {
  width: 10px;
  height: 12px;
  background: #4169E1;
  margin: 0 auto 2px;
  border-radius: 2px;
  position: relative;
}

.explorer-legs {
  display: flex;
  justify-content: space-between;
  width: 8px;
  margin: 0 auto;
}

.leg {
  width: 2px;
  height: 6px;
  background: #2F4F4F;
  border-radius: 1px;
}

.explorer-arms {
  position: absolute;
  top: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 14px;
  height: 2px;
}

.arm {
  position: absolute;
  width: 6px;
  height: 2px;
  background: #FFE4B5;
  border-radius: 1px;
}

.arm.left {
  left: 0;
  transform: rotate(-20deg);
}

.arm.right {
  right: 0;
  transform: rotate(20deg);
}

.explorer-backpack {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 8px;
  background: #8B4513;
  border-radius: 1px;
  z-index: -1;
}

// 当前提交信息卡片
.current-commit-info {
  position: fixed;
  top: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 16px;
  min-width: 280px;
  max-width: 350px;
  z-index: 15;
  backdrop-filter: blur(10px);
  color: white;
  font-size: 0.9rem;
  opacity: 0;
  transform: translateY(-10px);
  transition: opacity 0.3s ease, transform 0.3s ease;
  
  &.show {
    opacity: 1;
    transform: translateY(0);
  }
  
  .commit-hash {
    font-family: 'Courier New', monospace;
    color: #64ffda;
    font-weight: bold;
    margin-bottom: 8px;
  }
  
  .commit-time {
    color: #888;
    font-size: 0.8rem;
    margin-bottom: 8px;
  }
  
  .commit-author {
    color: #4ecdc4;
    margin-bottom: 8px;
    font-weight: 600;
  }
  
  .commit-message {
    color: #ccc;
    line-height: 1.4;
    margin-bottom: 12px;
    word-wrap: break-word;
  }
  
  .commit-stats {
    display: flex;
    gap: 12px;
    
    .stat-item {
      font-size: 0.8rem;
      font-weight: 600;
      
      &.additions {
        color: #28a745;
      }
      
      &.deletions {
        color: #dc3545;
      }
    }
  }
}







// 响应式设计
@media (max-width: 768px) {
  .cosmic-title {
    font-size: 2.5rem !important;
  }
  
  .cosmic-subtitle {
    font-size: 1rem !important;
  }
  
  .cosmic-button {
    width: 100%;
    max-width: 300px;
  }
    
  .current-commit-info {
    top: 10px;
    right: 10px;
    
    .commit-card {
      min-width: 250px;
      padding: 1rem;
    }
  }
  
  .commit-info-tooltip {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    min-width: 200px;
    max-width: 280px;
    margin-top: 0;
  }
  
  .commit-node {
    width: 12px;
    height: 12px;
  }
  
  .commit-node.current {
    width: 18px;
    height: 18px;
  }
}


</style>