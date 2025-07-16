import subprocess
import os
import re
from typing import List, Dict, Any, Optional
from config import Config

class GitRepository:
    """
    Git仓库操作类
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        self._validate_repository()
    
    def _validate_repository(self) -> None:
        """
        验证仓库路径的有效性
        """
        if not os.path.exists(self.repo_path):
            raise ValueError(f"路径不存在: {self.repo_path}")
        
        if not os.path.isdir(self.repo_path):
            raise ValueError(f"路径不是目录: {self.repo_path}")
        
        git_dir = os.path.join(self.repo_path, '.git')
        if not os.path.exists(git_dir):
            raise ValueError(f"不是有效的Git仓库: {self.repo_path}")
    
    def get_git_log(self, max_count: Optional[int] = None) -> str:
        """
        获取git log输出
        """
        cmd = [
            'git', 'log', '--all', '--graph',
            '--pretty=format:%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset',
            '--abbrev-commit'
        ]
        
        if max_count:
            cmd.extend(['-n', str(max_count)])
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=Config.TIMEOUT
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Git命令执行失败: {result.stderr}")
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Git命令执行超时（{Config.TIMEOUT}秒）")
        except Exception as e:
            raise RuntimeError(f"执行Git命令时发生错误: {str(e)}")
    
    def get_repository_info(self) -> Dict[str, Any]:
        """
        获取仓库基本信息
        """
        try:
            # 获取仓库名称
            repo_name = os.path.basename(self.repo_path)
            
            # 获取当前分支
            branch_result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else 'unknown'
            
            # 获取远程URL
            remote_result = subprocess.run(
                ['git', 'config', '--get', 'remote.origin.url'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            remote_url = remote_result.stdout.strip() if remote_result.returncode == 0 else ''
            
            return {
                'name': repo_name,
                'path': self.repo_path,
                'current_branch': current_branch,
                'remote_url': remote_url
            }
            
        except Exception as e:
            return {
                'name': os.path.basename(self.repo_path),
                'path': self.repo_path,
                'current_branch': 'unknown',
                'remote_url': '',
                'error': str(e)
            }

class GitLogParser:
    """
    Git log解析器
    """
    
    def __init__(self):
        # 匹配提交行的正则表达式
        self.commit_pattern = re.compile(
            r'^([*|\\\/ ]+)([a-f0-9]+)\s*-\s*(\([^)]*\))?\s*(.+?)\s+\(([^)]+)\)\s+<([^>]+)>$'
        )
        # ANSI颜色代码清理
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    def parse(self, git_log_output: str) -> List[Dict[str, Any]]:
        """
        解析git log输出
        """
        if not git_log_output.strip():
            return []
        
        lines = git_log_output.strip().split('\n')
        commits = []
        
        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue
            
            commit_info = self._parse_commit_line(line, line_num)
            if commit_info:
                commits.append(commit_info)
        
        return commits
    
    def _parse_commit_line(self, line: str, line_num: int) -> Optional[Dict[str, Any]]:
        """
        解析单行提交信息
        """
        # 清理ANSI颜色代码
        clean_line = self.ansi_escape.sub('', line)
        
        # 尝试匹配提交行
        match = self.commit_pattern.match(clean_line)
        
        if match:
            graph, hash_val, refs, message, time, author = match.groups()
            
            return {
                'line_number': line_num,
                'graph': graph.rstrip(),
                'hash': hash_val.strip(),
                'refs': refs.strip('() ') if refs else '',
                'message': message.strip(),
                'time': time.strip(),
                'author': author.strip(),
                'raw_line': line
            }
        
        # 如果不匹配提交格式，可能是纯图形行
        if re.match(r'^[*|\\\/ ]+$', clean_line.strip()):
            return {
                'line_number': line_num,
                'graph': clean_line.rstrip(),
                'hash': '',
                'refs': '',
                'message': '',
                'time': '',
                'author': '',
                'raw_line': line,
                'is_graph_only': True
            }
        
        return None
    
    def get_statistics(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取提交统计信息
        """
        if not commits:
            return {
                'total_commits': 0,
                'authors': [],
                'branches': []
            }
        
        # 过滤出真正的提交（非纯图形行）
        real_commits = [c for c in commits if not c.get('is_graph_only', False)]
        
        # 统计作者
        authors = {}
        for commit in real_commits:
            author = commit.get('author', '')
            if author:
                authors[author] = authors.get(author, 0) + 1
        
        # 统计分支引用
        branches = set()
        for commit in real_commits:
            refs = commit.get('refs', '')
            if refs:
                # 解析分支名称
                branch_matches = re.findall(r'origin/([^,\)]+)', refs)
                branches.update(branch_matches)
        
        return {
            'total_commits': len(real_commits),
            'total_lines': len(commits),
            'authors': [{'name': name, 'count': count} for name, count in sorted(authors.items(), key=lambda x: x[1], reverse=True)],
            'branches': list(branches)
        }