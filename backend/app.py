from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from typing import Dict, Any
from config import config
from utils.git_utils import GitRepository, GitLogParser

def create_app(config_name='default'):
    """
    应用工厂函数
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 启用CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # 注册路由
    register_routes(app)
    
    return app

# 创建全局解析器实例
parser = GitLogParser()

def register_routes(app):
    """注册路由"""
    @app.route('/api/git-log', methods=['POST'])
    def get_git_log():
        """
        获取git log数据的API端点
        """
        try:
            data = request.get_json()
            if not data or 'repo_path' not in data:
                return jsonify({
                    'success': False,
                    'error': '请提供仓库路径'
                }), 400
            
            repo_path = data['repo_path']
            max_count = data.get('max_count')
            
            # 如果max_count为0或None，则获取所有提交
            if max_count == 0:
                max_count = None
            elif max_count is None:
                # 默认不限制，获取所有提交
                max_count = None
            
            # 验证路径
            if not repo_path or not isinstance(repo_path, str):
                return jsonify({
                    'success': False,
                    'error': '无效的仓库路径'
                }), 400
            
            # 创建Git仓库实例
            repo = GitRepository(repo_path)
            
            # 获取仓库信息
            repo_info = repo.get_repository_info()
            
            # 获取git log输出
            git_log_output = repo.get_git_log(max_count)
            
            # 解析git log
            commits = parser.parse(git_log_output)
            
            # 获取统计信息
            statistics = parser.get_statistics(commits)
            
            return jsonify({
                'success': True,
                'data': {
                    'repository': repo_info,
                    'commits': commits,
                    'statistics': statistics
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/repository-info', methods=['POST'])
    def get_repository_info():
        """
        获取仓库基本信息的API端点
        """
        try:
            data = request.get_json()
            if not data or 'repo_path' not in data:
                return jsonify({
                    'success': False,
                    'error': '请提供仓库路径'
                }), 400
            
            repo_path = data['repo_path']
            
            if not repo_path or not isinstance(repo_path, str):
                return jsonify({
                    'success': False,
                    'error': '无效的仓库路径'
                }), 400
            
            repo = GitRepository(repo_path)
            repo_info = repo.get_repository_info()
            
            return jsonify({
                'success': True,
                'data': repo_info
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """
        健康检查端点
        """
        return jsonify({
            'status': 'healthy',
            'message': 'Git Log API服务正常运行'
        })

if __name__ == '__main__':
    # 获取环境变量或使用默认配置
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env)
    
    # 启动应用
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    )
else:
    # 用于WSGI服务器
    app = create_app()