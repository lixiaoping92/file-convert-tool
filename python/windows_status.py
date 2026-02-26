import subprocess
import win32gui
import win32con
import time
import os
import re
import pygetwindow as gw
import pyautogui
import pytesseract
from pathlib import Path

#CONVSP.exe转换状态窗口检测器
class ConvspStatusDetector:
    number = 0
    addnumber = 0
    #初始化检测器"Sentinel LDK Protection System","Sentinel key not found(H0007)", "Conversion successful","Different No. of Axis"
    def __init__(self, window_keywords: list = None, timeout: int = 2):
        # self.window_keywords = window_keywords or ["CONVSP", "Sentinel LDK Protection System", "Sentinel key not found(H0007)","Conversion successful","Different No. of Axis"]         #window_keywords:窗口识别关键词列表（默认：["CONVSP", "转换", "状态"]）
        self.window_keywords = window_keywords or ["CONVSP", "Sentinel LDK Protection System"]         #window_keywords:窗口识别关键词列表（默认：["CONVSP", "转换", "状态"]）
        self.timeout = timeout                                                      #timeout:等待窗口出现的超时时间（秒，默认10）
        self.status_window_hwnd = None                                              # 状态窗口句柄
        self.convsp_process = None                                                  # CONVSP进程对象
    
    """使用正则表达式检查 sub_str 是否在 main_str 中，不区分大小写"""
    def contains_ignore_case_regex(main_str, sub_str):
        pattern = re.compile(re.escape(sub_str), re.IGNORECASE)
        return bool(pattern.search(main_str))

    """统计指定目录中的文件数量（仅当前目录，不包含子目录）"""
    def count_files_current_dir(self,directory):
        try:
            # 获取目录中的所有条目
            entries = os.listdir(directory)
            # 过滤出文件（排除目录）
            files = [entry for entry in entries if os.path.isfile(os.path.join(directory, entry))]
            return len(files)
        except FileNotFoundError:
            print(f"错误：目录 '{directory}' 不存在")
            return -1
        except PermissionError:
            print(f"错误：没有访问目录 '{directory}' 的权限")
            return -1
        except Exception as e:
            print(f"错误：{e}")
            return -1

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
        buf = win32gui.PyMakeBuffer(buf_size)
        win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, buf_size, buf)
        buffer_bytes = buf.tobytes()
        content = buffer_bytes.decode(encoding="utf-8", errors="ignore")
        content = content.replace("\x00", "").strip()
    
        # windows = gw.getWindowsWithTitle("CONVSP")
        # windows[0].activate()
        # pyautogui.sleep(0.5)
        # screenshot = pyautogui.screenshot(region=(windows[0].left,windows[0].top,windows[0].width,windows[0].height))
        # content = pytesseract.image_to_string(screenshot)
        
        # windows_key = gw.getWindowsWithTitle("Sentinel LDK Protection System")
        return content.strip()
        
    
    #检测并提取转换状态窗口信息
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
                content_lower = detect_result["content"].lower()
                print("content_lower = ",content_lower)
                if r"Sentinel LDK Protection System".lower() in content_lower:
                    detect_result["content"] = r"Sentinel key not found(H0007)"
                elif r"CONVSP".lower() in content_lower:
                    addnumber = self.count_files_current_dir(r"D:\LXPmyAPP\publish\C9110011")
                    if addnumber > self.number:
                        detect_result["content"] = r"Conversion successful"
                    else:
                        detect_result["content"] = r"Different No. of Axis"
                    # 提取错误信息
                    error_keywords = ["Sentinel key not found(H0007)", "Different No. of Axis"]
                    for keyword in error_keywords:
                        if keyword in content_lower:
                            print("keyword = ",keyword)
                            error_start = detect_result["content"].lower().index(keyword)
                            detect_result["error_msg"] = detect_result["content"][error_start:].strip()
                            break
            time.sleep(0.5)  # 每0.5秒检查一次
        return detect_result
    
    def close_status_window(self):
        #关闭状态窗口（如果存在）
        print("status_window_hwnd = ",self.status_window_hwnd)
        if self.status_window_hwnd:
            try:
                # 发送关闭消息
                win32gui.PostMessage(self.status_window_hwnd, win32con.WM_CLOSE, 0, 0)
                self.status_window_hwnd = None  # 重置句柄
                return True
            except Exception as e:
                print(f"关闭窗口失败：{e}")
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

    

# 调用
if __name__ == "__main__":
    
    #列举出所有窗口
    # def list_all_windows():
    #   def callback(hwnd, _):
    #       if win32gui.IsWindowVisible(hwnd):
    #           title = win32gui.GetWindowText(hwnd)
    #           if title:
    #               print(f"标题：{title}，句柄：{hwnd}")
    #   win32gui.EnumWindows(callback, None)
    # list_all_windows()
    
    # 配置CONVSP.EXE路径和参数
    convsp_path = r"D:\LXPmyAPP\publish\C9110011\CONVSP.EXE"
    input_file = r"D:\LXPmyAPP\publish\C9110011\123.txt"
    output_file = r"D:\LXPmyAPP\publish\C9110011\output.s"
    
    # 创建检测器实例
    detector = ConvspStatusDetector(
        window_keywords=["CONVSP", "Sentinel LDK Protection System"],
        timeout=3  # 15秒超时
    )
    
    number = detector.count_files_current_dir(r"D:\LXPmyAPP\publish\C9110011")
    print("number = ",number)
    # 调用CONVSP.exe并检测状态窗口
    result = detector.call_convsp(
        convsp_path,
        [input_file, output_file]
    )
    
    print("ctx[\"content\"] = ",result['status_window']['content'])


     # 自动关闭状态窗口（可选）
    if result['status_window']['found']:
        detector.close_status_window()
        print("\n状态窗口已关闭")
    
    # 打印结果
    print("=== CONVSP调用结果 ===")
    # print(f"进程返回码：{result['process']['returncode']}")
    print(f"命令行输出：{result['process']['stdout']}")
    print(f"\n=== 状态窗口信息 ===")
    print(f"找到窗口：{result['status_window']['found']}")
    print(f"窗口标题：{result['status_window']['title']}")
    print(f"窗口内容：{result['status_window']['content']}")
    # print(f"转换状态：{result['status_window']['status']}")
    # print(f"进度信息：{result['status_window']['progress']}")
    print(f"错误信息：{result['status_window']['error_msg']}")
    
   



# ### 四、关键设计说明


# #### 1. 窗口识别机制
# - 通过**自定义关键词**匹配窗口标题（如"CONVSP"、"转换状态"）
# - 支持**多关键词**，提高匹配准确性
# - 过滤**不可见窗口**，避免无效检测


# #### 2. 状态解析逻辑
# - 根据窗口内容关键词判断状态：
#   - 成功："成功"、"完成"、"done"
#   - 失败："失败"、"error"、"错误"
#   - 进行中："进度"、"progress"、"转换中"
# - 支持提取**进度信息**（如"进度：50%"）
# - 自动提取**错误信息**，便于调试


# #### 3. 异步调用与窗口等待
# - 使用`subprocess.Popen`异步执行CONVSP.exe，不阻塞主线程
# - 循环检测窗口，每0.5秒检查一次，避免CPU占用过高
# - 设置**超时机制**（默认10秒），防止无限等待


# #### 4. 窗口控制（可选）
# - 提供`close_status_window`方法，自动关闭状态窗口
# - 使用`PostMessage`发送`WM_CLOSE`消息，优雅关闭窗口，不强制终止


# ### 五、注意事项


# #### 1. 窗口关键词调整
# - 根据实际CONVSP.exe弹出的窗口**标题**调整`window_keywords`
# - 可通过手动运行CONVSP.exe，观察窗口标题，获取准确关键词


# #### 2. 状态解析优化
# - 根据实际窗口**内容文本**调整状态关键词
# - 如需更精确的解析，可使用正则表达式匹配具体格式


# #### 3. 兼容性处理
# - 仅支持**Windows系统**（`win32gui`是Windows专用库）
# - 需以**管理员身份运行**（某些窗口可能需要管理员权限访问）


# #### 4. 调试建议
# - 首次运行时，可添加`print`语句输出窗口内容，便于调整解析逻辑
# - 使用`win32gui.EnumWindows`枚举所有窗口，查看完整窗口列表：

#   def list_all_windows():
#       def callback(hwnd, _):
#           if win32gui.IsWindowVisible(hwnd):
#               title = win32gui.GetWindowText(hwnd)
#               if title:
#                   print(f"标题：{title}，句柄：{hwnd}")
#       win32gui.EnumWindows(callback, None)
#   list_all_windows()



# ### 六、扩展功能（可选）


# #### 1. 实时进度监控
# - 循环检测窗口内容，实时更新进度
# - 适用于大文件转换，需要持续监控进度的场景


# #### 2. 多窗口支持
# - 扩展代码支持同时检测多个窗口（如Sentinel授权窗口+转换状态窗口）
# - 根据窗口类型分别处理，提高鲁棒性


# #### 3. 日志记录
# - 添加日志模块（如`logging`），记录窗口检测过程和结果
# - 便于自动化运行时的问题追踪


# 通过以上方案，可实现对CONVSP.exe转换状态窗口的**自动检测、状态提取和控制**，结合异步调用，确保在窗口出现时及时捕捉状态信息，提高自动化程度。