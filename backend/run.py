#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Log可视化后端服务启动脚本
"""

import os
import sys
from app import create_app

def main():
    """
    主函数
    """
    # 获取环境配置
    env = os.environ.get('FLASK_ENV', 'development')
    
    # 创建应用实例
    app = create_app(env)
    
    # 打印启动信息
    print(f"🚀 Git Log可视化服务启动中...")
    print(f"📁 环境: {env}")
    print(f"🌐 地址: http://{app.config['HOST']}:{app.config['PORT']}")
    print(f"🔧 调试模式: {'开启' if app.config['DEBUG'] else '关闭'}")
    print("\n可用的API端点:")
    print("  POST /api/git-log        - 获取Git日志数据")
    print("  POST /api/repository-info - 获取仓库信息")
    print("  GET  /api/health         - 健康检查")
    print("\n按 Ctrl+C 停止服务\n")
    
    try:
        # 启动服务
        app.run(
            debug=app.config['DEBUG'],
            host=app.config['HOST'],
            port=app.config['PORT'],
            use_reloader=app.config['DEBUG']
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()