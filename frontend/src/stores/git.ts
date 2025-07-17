import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export interface GitCommit {
  hash: string
  author: string
  email?: string
  time: string
  message: string
  files_changed?: number
  insertions?: number
  deletions?: number
  branch?: string
  graph?: string
  refs?: string
  line_number?: number
  raw_line?: string
  is_graph_only?: boolean
}

export interface GitStats {
  total_commits: number
  total_authors: number
  date_range: {
    start: string
    end: string
  }
  top_authors: Array<{
    author: string
    commits: number
  }>
}

export interface RepoInfo {
  name: string
  path: string
  current_branch: string
  total_branches: number
  remote_url?: string
}

export interface RepoConfig {
  path: string
  maxCount: number
}

const API_BASE_URL = 'http://localhost:5000/api'

export const useGitStore = defineStore('git', () => {
  // 状态
  const commits = ref<GitCommit[]>([])
  const stats = ref<GitStats | null>(null)
  const repoInfo = ref<RepoInfo | null>(null)
  const repoConfig = ref<RepoConfig | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 计算属性
  const hasData = computed(() => commits.value.length > 0)
  const authorList = computed(() => {
    const authors = new Set(commits.value.map(commit => commit.author))
    return Array.from(authors)
  })
  
  const commitsByDate = computed(() => {
    const grouped: Record<string, GitCommit[]> = {}
    commits.value.forEach(commit => {
      const date = commit.time.split('T')[0] || commit.time.split(' ')[0] // 获取日期部分
      if (!grouped[date]) {
        grouped[date] = []
      }
      grouped[date].push(commit)
    })
    return grouped
  })
  
  const timeRange = computed(() => {
    if (commits.value.length === 0) return null
    
    const dates = commits.value.map(commit => new Date(commit.time))
    const minDate = new Date(Math.min(...dates.map(d => d.getTime())))
    const maxDate = new Date(Math.max(...dates.map(d => d.getTime())))
    
    return { start: minDate, end: maxDate }
  })
  
  // 动作
  const setRepoConfig = (config: RepoConfig) => {
    repoConfig.value = config
  }
  
  const fetchGitLog = async () => {
    if (!repoConfig.value) {
      throw new Error('仓库配置未设置')
    }
    
    loading.value = true
    error.value = null
    
    try {
      const params: any = {
        repo_path: repoConfig.value.path
      }
      
      if (repoConfig.value.maxCount > 0) {
        params.max_count = repoConfig.value.maxCount
      }
      
      const response = await axios.post(`${API_BASE_URL}/git-log`, params)
      
      if (response.data.success) {
        commits.value = response.data.data.commits
        stats.value = response.data.data.stats
      } else {
        throw new Error(response.data.error || '获取Git日志失败')
      }
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message || '网络请求失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const fetchRepoInfo = async () => {
    if (!repoConfig.value) {
      throw new Error('仓库配置未设置')
    }
    
    try {
      const response = await axios.post(`${API_BASE_URL}/repository-info`, {
        repo_path: repoConfig.value.path
      })
      
      if (response.data.success) {
        repoInfo.value = response.data.data
      } else {
        throw new Error(response.data.error || '获取仓库信息失败')
      }
    } catch (err: any) {
      console.warn('获取仓库信息失败:', err.message)
      // 仓库信息获取失败不阻断主流程
    }
  }
  
  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`)
      return response.data.status === 'healthy'
    } catch {
      return false
    }
  }
  
  const clearData = () => {
    commits.value = []
    stats.value = null
    repoInfo.value = null
    error.value = null
  }
  
  const loadData = async () => {
    await Promise.all([
      fetchGitLog(),
      fetchRepoInfo()
    ])
  }
  
  return {
    // 状态
    commits,
    stats,
    repoInfo,
    repoConfig,
    loading,
    error,
    
    // 计算属性
    hasData,
    authorList,
    commitsByDate,
    timeRange,
    
    // 动作
    setRepoConfig,
    fetchGitLog,
    fetchRepoInfo,
    checkHealth,
    clearData,
    loadData
  }
})