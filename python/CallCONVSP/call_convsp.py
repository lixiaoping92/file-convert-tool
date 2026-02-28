import subprocess
import win32gui
import win32con
import time
import os
import ctypes
from pathlib import Path

#CONVSP.exe转换状态窗口检测器
class ConvspStatusDetector:
    # init_number = 0
    # addnumber = 0

    #初始化检测器"Sentinel LDK Protection System","Sentinel key not found(H0007)", "Conversion successful","Different No. of Axis"
    def __init__(self, window_keywords: list = [], timeout: int = 2):
        # self.window_keywords = window_keywords or ["CONVSP", "Sentinel LDK Protection System", "Sentinel key not found(H0007)","Conversion successful","Different No. of Axis"]         #window_keywords:窗口识别关键词列表（默认：["CONVSP", "转换", "状态"]）
        self.window_keywords = window_keywords or ["CONVSP", "Sentinel LDK Protection System"]         #window_keywords:窗口识别关键词列表（默认：["CONVSP", "转换", "状态"]）
        self.timeout = timeout                                                      #timeout:等待窗口出现的超时时间（秒，默认10）
        self.status_window_hwnd = None                                              # 状态窗口句柄
        self.convsp_process = None                                                  # CONVSP进程对象
        # 在初始化方法中设置init_number
        # self.init_number = self.count_files_current_dir(r"D:\LXPmyAPP\publish\C9110011")

    # """统计指定目录中的文件数量（仅当前目录，不包含子目录）"""
    # def count_files_current_dir(self,directory):
    #     try:
    #         # 获取目录中的所有条目
    #         entries = os.listdir(directory)
    #         # 过滤出文件（排除目录）
    #         files = [entry for entry in entries if os.path.isfile(os.path.join(directory, entry))]
    #         return len(files)
    #     except FileNotFoundError:
    #         print(f"错误：目录 '{directory}' 不存在")
    #         return -1
    #     except PermissionError:
    #         print(f"错误：没有访问目录 '{directory}' 的权限")
    #         return -1
    #     except Exception as e:
    #         print(f"错误：{e}")
    #         return -1
        

    # 判断窗口是否为CONVSP状态窗口
    def _is_status_window(self, hwnd: int) -> bool: 
        if not win32gui.IsWindowVisible(hwnd):
            return False    
        # 匹配标题关键词
        title = win32gui.GetWindowText(hwnd)   
        for keyword in self.window_keywords:
            if keyword in title:
                return True
        return False
    
    #提取窗口内容文本
    def _extract_window_content(self, hwnd: int) -> str:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,win32con.SWP_NOMOVE | win32con.SWP_NOACTIVATE | win32con.SWP_NOOWNERZORDER | win32con.SWP_SHOWWINDOW | win32con.SWP_NOSIZE)         # 通过句柄窗口置顶
        class_name = win32gui.GetClassName(hwnd)
        buf_size = 512  # 缓冲区大小
        buf = ctypes.create_string_buffer(buf_size)
        win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, buf_size, buf)
        content = buf.value.decode(encoding="utf-8", errors="ignore")
        content = content.replace("\x00", "").strip()
        return content.strip()
        
    
    #检测并提取转换状态窗口信息，返回转换窗口的标题和内容（转换状态）
    def detect_status_window(self) -> dict:
        #返回：
        detect_result = {
            "found": False,         # 是否找到窗口
            "title": "",            # 窗口标题
            "content": "",          # 窗口内容
            # "status": "unknown",    # 转换状态（成功/轴配置/没有key）
            # "progress": "",         # 进度信息（如果有）
            "error_msg": ""         # 错误信息（如果失败）
        }
        
        # 窗口回调函数：查找状态窗口并提取信息
        def enum_window_callback(hwnd, ctx):
            if self._is_status_window(hwnd):
                ctx["found"] = True
                ctx["hwnd"] = hwnd 
                ctx["title"] = win32gui.GetWindowText(hwnd)
                if ctx["title"] in ["CONVSP","Sentinel LDK Protection System"]:
                    ctx["content"] = self._extract_window_content(hwnd)
                    return False        # 找到后停止枚举
            return True
        
        # 等待窗口出现
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            window_ctx = {"found": False}
            win32gui.EnumWindows(enum_window_callback, window_ctx)   
            if window_ctx["found"]:
                # 保存窗口句柄
                self.status_window_hwnd = window_ctx["hwnd"]
                # 更新结果
                detect_result["found"] = True
                detect_result["title"] = window_ctx["title"]
                detect_result["content"] = window_ctx["content"]
                
                # 解析状态（根据实际窗口内容调整关键词）"Sentinel LDK Protection System","Sentinel key not found(H0007)", "Conversion successful","Different No. of Axis"
                # content_lower = detect_result["content"].lower()
                # if r"Sentinel LDK Protection System".lower() in content_lower:
                #     detect_result["content"] = r"Sentinel key not found(H0007)"
                # elif r"CONVSP".lower() in content_lower:
                #     # addnumber = self.count_files_current_dir(r"D:\LXPmyAPP\publish\C9110011")
                #     if addnumber > self.init_number:
                #         detect_result["content"] = r"Conversion successful" 
                #     elif addnumber == self.init_number:
                #         detect_result["content"] = r"Different No. of Axis"
                        
            time.sleep(0.5)  # 每0.5秒检查一次
            # print("窗口标题：",detect_result['title'])
            # print("窗口内容：",detect_result['content'])
        return detect_result
    
    def close_status_window(self):
        #关闭状态窗口（如果存在）
        if self.status_window_hwnd:
            try:
                # 发送关闭消息
                win32gui.PostMessage(self.status_window_hwnd, win32con.WM_CLOSE, 0, 0)
                self.status_window_hwnd = None  # 重置句柄
                return True
            except Exception as e:
                # print(f"关闭窗口失败：{e}")
                return False
        return False
    
    #调用CONVSP.exe并检测状态窗口,convsp_path: CONVSP.EXE的路径,args: 传递给CONVSP.EXE的参数列表
    def call_convsp(self, convsp_path: str, args: list) -> dict:
        #返回：dict: 包含进程信息和状态窗口信息
      
        exe_path = str(Path(convsp_path).absolute())    # 处理路径      
        cmd = [exe_path] + args                              
        
        # 异步调用CONVSP.exe
        self.convsp_process = subprocess.Popen(
            cmd,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="gbk"
        )
        
        # 等待并检测状态窗口
        status_result = self.detect_status_window()
        
        # 自动关闭状态窗口（可选）
        if status_result['found']:
            self.close_status_window()
            # print("\n状态窗口已关闭")


        # 等待进程结束，获取命令行输出
        stdout, stderr = self.convsp_process.communicate()
        
        

        return {
            "process": {
            "returncode": self.convsp_process.returncode,
            "stdout": stdout.strip(),
            "stderr": stderr.strip()
            },
            "status_window": status_result
            # "overall_status": status_result.get("status", "unknown")
        }




# # 调用
# if __name__ == "__main__":
    
    #列举出所有窗口
    # def list_all_windows():
    #   def callback(hwnd, _):
    #       if win32gui.IsWindowVisible(hwnd):
    #           title = win32gui.GetWindowText(hwnd)
    #           if title:
    #               print(f"标题：{title}，句柄：{hwnd}")
    #   win32gui.EnumWindows(callback, None)
    # list_all_windows()
    
    # # 配置CONVSP.EXE路径和参数
    # convsp_path = r"D:\LXPmyAPP\publish\C9110011\CONVSP.EXE"
    # input_file = r"D:\LXPmyAPP\publish\C9110011\1212.PKT"
    # output_file = r"D:\LXPmyAPP\publish\C9110011\output.p"
    
    # # 创建检测器实例
    # detector = ConvspStatusDetector(
    #     window_keywords=["CONVSP", "Sentinel LDK Protection System"],
    #     timeout=3  # 15秒超时
    # )

    # # 调用CONVSP.exe并检测状态窗口 convsp_path: CONVSP.EXE的路径,args: 传递给CONVSP.EXE的参数列表
    # result = detector.call_convsp(
    #     convsp_path,
    #     [input_file, output_file]    #input_file: 输入文件路径，output_file: 输出文件路径
    # )
    
    # # 打印结果
    # print("=== CONVSP调用结果 ===")
    # # print(f"进程返回码：{result['process']['returncode']}")
    # print(f"命令行输出：{result['process']['stdout']}")
    # print(f"\n=== 状态窗口信息 ===")
    # print(f"找到窗口：{result['status_window']['found']}")
    # print(f"窗口标题：{result['status_window']['title']}")
    # print(f"窗口内容：{result['status_window']['content']}")
    # # print(f"错误信息：{result['status_window']['error_msg']}")
    
   
