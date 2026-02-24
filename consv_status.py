import subprocess
import sys
from pathlib import Path

def call_convsp(exe_path: str, args: list = None, timeout: int = 60, realtime_output: bool = False) -> dict:
    """
    调用 CONVSP.exe 并捕捉完整调用状态
    
    参数：
        exe_path: CONVSP.exe 的完整路径（支持带空格的路径）
        args: 传递给 CONVSP.exe 的参数列表，如 ["-input", "file.txt"]
        timeout: 超时时间（秒），默认60秒
        realtime_output: 是否实时打印输出，默认False
    
    返回：
        dict: 包含调用状态的字典，结构如下：
            {
                "success": bool,       # 调用是否成功（返回码为0时为True）
                "returncode": int,      # 程序返回码
                "stdout": str,          # 标准输出内容
                "stderr": str,          # 标准错误内容
                "command": str,         # 完整调用命令
                "exe_path": str,        # 执行的EXE路径
                "timeout": int          # 使用的超时时间
            }
    """
    # 初始化返回结果
    result = {
        "success": False,
        "returncode": -1,
        "stdout": "",
        "stderr": "",
        "command": "",
        "exe_path": exe_path,
        "timeout": timeout
    }
    
    # 处理路径：确保是绝对路径，避免因工作目录问题找不到文件
    exe_path = str(Path(exe_path).absolute())
    
    # 构建命令列表（支持带空格的路径）
    cmd = [exe_path]
    if args:
        cmd.extend(args)
        print("cmd=:",cmd)
    # 记录完整命令
    result["command"] = " ".join(cmd)
    
    try:
        # 根据是否需要实时输出选择调用方式
        if realtime_output:
            # 实时输出模式：使用Popen逐行读取
            process = subprocess.Popen(
                cmd,
                shell=False,  # 禁用shell，更安全
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="gbk" if sys.platform == "win32" else "utf-8"  # Windows默认编码为gbk
            )
            
            # 实时读取输出
            stdout_lines = []
            stderr_lines = []
            
            while True:
                # 读取一行标准输出
                stdout_line = process.stdout.readline()
                if stdout_line:
                    print(f"[CONVSP OUT] {stdout_line.strip()}")
                    stdout_lines.append(stdout_line.strip())
                
                # 读取一行标准错误
                stderr_line = process.stderr.readline()
                if stderr_line:
                    print(f"[CONVSP ERR] {stderr_line.strip()}")
                    stderr_lines.append(stderr_line.strip())
                
                # 检查进程是否结束
                if process.poll() is not None:
                    # 读取剩余输出
                    remaining_stdout = process.stdout.read().strip()
                    if remaining_stdout:
                        print(f"[CONVSP OUT] {remaining_stdout}")
                        stdout_lines.append(remaining_stdout)
                    
                    remaining_stderr = process.stderr.read().strip()
                    if remaining_stderr:
                        print(f"[CONVSP ERR] {remaining_stderr}")
                        stderr_lines.append(remaining_stderr)
                    break
            
            # 更新结果
            result["returncode"] = process.returncode
            result["stdout"] = "\n".join(stdout_lines)
            result["stderr"] = "\n".join(stderr_lines)
        else:
            # 非实时模式：一次性获取所有输出
            proc_result = subprocess.run(
                cmd,
                shell=False,
                capture_output=True,
                text=True,
                encoding="gbk" if sys.platform == "win32" else "utf-8",
                timeout=timeout
            )
            
            # 更新结果
            result["returncode"] = proc_result.returncode
            result["stdout"] = proc_result.stdout.strip()
            result["stderr"] = proc_result.stderr.strip()
        
        # 判断是否成功（通常返回码为0表示成功，具体以CONVSP.exe文档为准）
        result["success"] = result["returncode"] == 0
        
    except FileNotFoundError:
        result["stderr"] = f"错误：未找到文件 '{exe_path}'（请检查路径是否正确）"
    except subprocess.TimeoutExpired:
        result["stderr"] = f"错误：调用超时（超过 {timeout} 秒）"
    except PermissionError:
        result["stderr"] = f"错误：权限不足，无法执行 '{exe_path}'（请检查文件权限）"
    except Exception as e:
        result["stderr"] = f"错误：{str(e)}"
    
    return result


if __name__ == "__main__":
    # 3. 实时输出模式：实时查看转换进度（假设CONVSP.exe会输出进度）
    #D:\WeldRobotWeldRobot1.0\ptom\publish
    convsp_path = "D:\\WeldRobotWeldRobot1.0\\ptom\\publish\\CONVSP.EXE"
    status = call_convsp(convsp_path, ["234.txt","111111.s"])
    
    #params = ["-batch", str("D:/WeldRobotWeldRobot1.0/ptom/publish/234.txt")]  # 假设批量转换参数
    #status = call_convsp(convsp_path, args=params, realtime_output=True)
    
    print("\n=== 实时输出调用结果 ===")
    print(f"最终结果:")
    if status['success']:
        print("successful！！！转换成功！！！")
    else:
        print('转换失败: ' + status['stderr'])
    #print(f"返回码：{status['returncode']}")
