#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本
用于测试Git Log可视化后端服务的各个API端点
"""

import requests
import json
import os
import sys
from typing import Dict, Any

class APITester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def test_health(self) -> bool:
        """
        测试健康检查端点
        """
        print("🔍 测试健康检查...")
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康检查通过: {data.get('message', '')}")
                return True
            else:
                print(f"❌ 健康检查失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    def test_repository_info(self, repo_path: str) -> bool:
        """
        测试仓库信息获取
        """
        print(f"🔍 测试仓库信息获取: {repo_path}")
        try:
            payload = {"repo_path": repo_path}
            response = self.session.post(
                f"{self.base_url}/api/repository-info",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    repo_info = data.get('data', {})
                    print(f"✅ 仓库信息获取成功:")
                    print(f"   名称: {repo_info.get('name', 'N/A')}")
                    print(f"   当前分支: {repo_info.get('current_branch', 'N/A')}")
                    print(f"   远程URL: {repo_info.get('remote_url', 'N/A')}")
                    return True
                else:
                    print(f"❌ 仓库信息获取失败: {data.get('error', '未知错误')}")
                    return False
            else:
                print(f"❌ 仓库信息获取失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 仓库信息获取异常: {e}")
            return False
    
    def test_git_log(self, repo_path: str, max_count: int = None) -> bool:
        """
        测试Git日志获取
        """
        if max_count:
            print(f"🔍 测试Git日志获取: {repo_path} (最多{max_count}条)")
            payload = {
                "repo_path": repo_path,
                "max_count": max_count
            }
        else:
            print(f"🔍 测试Git日志获取: {repo_path} (获取所有提交)")
            payload = {
                "repo_path": repo_path
            }
        try:
            response = self.session.post(
                f"{self.base_url}/api/git-log",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result_data = data.get('data', {})
                    commits = result_data.get('commits', [])
                    statistics = result_data.get('statistics', {})
                    
                    print(f"✅ Git日志获取成功:")
                    print(f"   总行数: {statistics.get('total_lines', 0)}")
                    print(f"   提交数: {statistics.get('total_commits', 0)}")
                    print(f"   作者数: {len(statistics.get('authors', []))}")
                    print(f"   分支数: {len(statistics.get('branches', []))}")
                    
                    # 显示前几条提交
                    real_commits = [c for c in commits if not c.get('is_graph_only', False)]
                    if real_commits:
                        print(f"\n   最近的提交:")
                        for i, commit in enumerate(real_commits[:3]):
                            print(f"   {i+1}. {commit.get('hash', '')[:8]} - {commit.get('message', '')[:50]}...")
                            print(f"      作者: {commit.get('author', '')} ({commit.get('time', '')})")
                    
                    return True
                else:
                    print(f"❌ Git日志获取失败: {data.get('error', '未知错误')}")
                    return False
            else:
                print(f"❌ Git日志获取失败: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   错误详情: {error_data.get('error', '无详情')}")
                except:
                    print(f"   响应内容: {response.text[:200]}...")
                return False
        except Exception as e:
            print(f"❌ Git日志获取异常: {e}")
            return False
    
    def run_tests(self, repo_path: str = None) -> None:
        """
        运行所有测试
        """
        print("🚀 开始API测试...\n")
        
        # 测试健康检查
        health_ok = self.test_health()
        print()
        
        if not health_ok:
            print("❌ 服务不可用，请检查服务是否正常启动")
            return
        
        # 如果没有提供仓库路径，尝试使用当前目录
        if not repo_path:
            current_dir = os.getcwd()
            if os.path.exists(os.path.join(current_dir, '.git')):
                repo_path = current_dir
                print(f"📁 使用当前目录作为测试仓库: {repo_path}\n")
            else:
                print("❌ 请提供有效的Git仓库路径")
                return
        
        # 测试仓库信息
        repo_info_ok = self.test_repository_info(repo_path)
        print()
        
        # 测试Git日志
        git_log_ok = self.test_git_log(repo_path)
        print()
        
        # 总结
        total_tests = 3
        passed_tests = sum([health_ok, repo_info_ok, git_log_ok])
        
        print(f"📊 测试结果: {passed_tests}/{total_tests} 通过")
        if passed_tests == total_tests:
            print("🎉 所有测试通过！")
        else:
            print("⚠️  部分测试失败，请检查服务配置")

def main():
    """
    主函数
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Git Log API测试工具')
    parser.add_argument('--url', default='http://localhost:5000', help='API服务地址')
    parser.add_argument('--repo', help='Git仓库路径')
    
    args = parser.parse_args()
    
    tester = APITester(args.url)
    tester.run_tests(args.repo)

if __name__ == '__main__':
    main()