#!/usr/bin/env python3
"""
CORS HTTP Server - 一个支持CORS的简单HTTP文件服务器
类似于 `python3 -m http.server`，但添加了CORS头信息
"""

import argparse
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler


class CORSRequestHandler(SimpleHTTPRequestHandler):
    """扩展SimpleHTTPRequestHandler以添加CORS头信息"""
    
    def __init__(self, *args, **kwargs):
        # 从服务器获取cors_origin配置
        self.cors_origin = kwargs.pop('cors_origin', '*')
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        """添加CORS和缓存控制头信息"""
        self.send_header('Access-Control-Allow-Origin', self.cors_origin)
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

    def do_OPTIONS(self):
        """处理OPTIONS预检请求"""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """自定义日志输出格式"""
        if self.server.verbose:
            super().log_message(format, *args)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='CORS HTTP Server - 支持CORS的简单HTTP文件服务器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                    # 使用默认设置启动服务器 (127.0.0.1:9999)
  %(prog)s -p 8080            # 在端口8080上启动
  %(prog)s --host 0.0.0.0     # 在所有网络接口上监听
  %(prog)s -d ./public        # 服务./public目录
  %(prog)s -v                 # 启用详细日志
  %(prog)s --cors-origin http://example.com  # 限制CORS来源
        """
    )
    
    parser.add_argument(
        '--host', '-H',
        default='127.0.0.1',
        help='绑定主机地址 (默认: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=9999,
        help='端口号 (默认: 9999)'
    )
    
    parser.add_argument(
        '--directory', '-d',
        default='.',
        help='服务目录 (默认: 当前目录)'
    )
    
    parser.add_argument(
        '--bind', '-b',
        dest='host',  # 与--host参数相同
        help='绑定地址别名 (例如: 0.0.0.0 表示所有接口)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='启用详细日志输出'
    )
    
    parser.add_argument(
        '--cors-origin',
        default='*',
        help='Access-Control-Allow-Origin头信息的值 (默认: *)'
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    # 检查目录是否存在
    if not os.path.isdir(args.directory):
        print(f"错误: 目录 '{args.directory}' 不存在")
        sys.exit(1)
    
    # 切换到服务目录
    original_dir = os.getcwd()
    os.chdir(args.directory)
    
    # 创建服务器地址
    server_address = (args.host, args.port)
    
    # 创建自定义的Handler类，使用闭包捕获参数
    def make_handler_class(cors_origin, verbose):
        class CustomCORSRequestHandler(CORSRequestHandler):
            def __init__(self, *args, **kwargs):
                # 传递cors_origin到父类
                kwargs['cors_origin'] = cors_origin
                super().__init__(*args, **kwargs)
            
            def log_message(self, format, *args):
                """自定义日志输出格式"""
                if verbose:
                    super().log_message(format, *args)
        
        return CustomCORSRequestHandler
    
    try:
        # 创建自定义Handler类
        HandlerClass = make_handler_class(args.cors_origin, args.verbose)
        
        # 创建服务器
        httpd = HTTPServer(server_address, HandlerClass)
        
        print(f"CORS HTTP服务器启动在 http://{args.host}:{args.port}")
        print(f"服务目录: {os.path.abspath(args.directory)}")
        print(f"CORS来源: {args.cors_origin}")
        if args.verbose:
            print("详细日志: 启用")
        print("按 Ctrl+C 停止服务器")
        
        httpd.serve_forever()
        
    except PermissionError:
        print(f"错误: 没有权限在端口 {args.port} 上绑定")
        os.chdir(original_dir)  # 恢复原始目录
        sys.exit(1)
    except OSError as e:
        print(f"错误: 无法启动服务器 - {e}")
        os.chdir(original_dir)  # 恢复原始目录
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n服务器已停止")
        os.chdir(original_dir)  # 恢复原始目录
        sys.exit(0)
    except Exception as e:
        print(f"意外错误: {e}")
        os.chdir(original_dir)  # 恢复原始目录
        sys.exit(1)


if __name__ == '__main__':
    main()
