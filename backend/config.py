import os

class Config:
    """
    应用配置类
    """
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 服务器配置
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # Git配置
    MAX_COMMITS = int(os.environ.get('MAX_COMMITS', 1000))  # 最大提交数量限制
    TIMEOUT = int(os.environ.get('GIT_TIMEOUT', 30))  # Git命令超时时间（秒）
    
    # 安全配置
    ALLOWED_PATHS = os.environ.get('ALLOWED_PATHS', '').split(',') if os.environ.get('ALLOWED_PATHS') else []
    
class DevelopmentConfig(Config):
    """
    开发环境配置
    """
    DEBUG = True
    
class ProductionConfig(Config):
    """
    生产环境配置
    """
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}