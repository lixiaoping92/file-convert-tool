# 安装: pip install watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

class FileChangeHandler(FileSystemEventHandler):
    """处理文件变化事件"""
    def __init__(self, target_file):
        self.target_file = target_file
    
    def on_modified(self, event):
        # 只处理目标文件的修改
        if not event.is_directory and event.src_path == self.target_file:
            print(f"文件已更新: {event.src_path}")
            print(f"更新时间: {time.ctime()}")
           
    
def monitor_file_with_watchdog(file_path)->bool:
    """
    使用 watchdog 监控文件变化
    
    参数:
        file_path: 要监控的文件路径
    """
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在")
        return
    
    # 创建事件处理器
    event_handler = FileChangeHandler(file_path)
    
    # 创建观察者
    observer = Observer()
    
    # 监控文件所在目录（watchdog 只能监控目录）
    directory = os.path.dirname(file_path)
    observer.schedule(event_handler, directory, recursive=False)
    
    # 启动观察者
    observer.start()
    print(f"开始监控文件: {file_path}")
    
    try:
        while True:
            time.sleep(0.5)
            # observer.join()
            if event_handler.on_modified:
                return True
            else:    
                return False
            
            
    except KeyboardInterrupt:
        observer.stop()
        print("\n监控已停止")
    
    # observer.join()
    # if event_handler.on_modified:
    #     return True
    # else:    
    #     return False

# # 使用示例
# file_to_monitor = r"D:\LXPmyAPP\publish\C9110011\1212.TXT"
# monitor_file_with_watchdog(file_to_monitor)