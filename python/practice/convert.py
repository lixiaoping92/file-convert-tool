import subprocess
import sys
import os
from pathlib import Path
import windows_status as ws

# 调用 CONVSP.exe 并捕捉完整调用状态,参数：exe_path: CONVSP.exe 的完整路径（支持带空格的路径）,args: 传递给 CONVSP.exe 的参数列表，如 ["-input", "file.txt"]
def call_convsp(exe_path: str, args: list = None) -> dict:
    # 初始化返回结果
    result = {
        "success": False,       # 调用是否成功（返回码为0时为True）
        "returncode": -1,       # 程序返回码
        "stdout": "",           # 标准输出内容
        "stderr": "",           # 标准错误内容
        "command": "",          # 完整调用命令
        "exe_path": exe_path    # 执行的EXE路径
    }
    
    # 处理路径：确保是绝对路径，避免因工作目录问题找不到文件
    exe_path = str(Path(exe_path).absolute())
    
    # 构建命令列表（支持带空格的路径）
    cmd = [exe_path]
    if args:
        cmd.extend(args)
    # 记录完整命令
    result["command"] = " ".join(cmd)
    
    try:
        proc = subprocess.Popen(
                cmd,
                shell=False,
                text=True,
                encoding="gbk" if sys.platform == "win32" else "utf-8"
            )
            
        # # 检测Sentinel弹窗
        # sentinel_info = ws.find_sentinel_popup()
        # print("Sentinel弹窗检测结果：")
        # print(f"找到弹窗：{sentinel_info['found']}")
        # print(f"弹窗标题：{sentinel_info['title']}")
        # print(f"弹窗内容：{sentinel_info['content']}")
        # print(f"是否未插入KEY：{sentinel_info['is_no_key']}")
        # print(f"错误代码：{sentinel_info['error_code']}")
        
        # 等待CONVSP结束
        stdout, stderr = proc.communicate()
        
        proc_result = subprocess.run(
                cmd,
                shell=False,
                capture_output=True,
                text=True,
                encoding="gbk" if sys.platform == "win32" else "utf-8"
            )
        
        # 判断是否成功（通常返回码为0表示成功，具体以CONVSP.exe文档为准）
        result["success"] = result["returncode"] == 0

        # 检查是否成功，成功则直接返回
        if result["success"]:
            result["error_type"] = "none"
            result["returncode"] = proc_result.returncode
            result["stdout"] = proc_result.stdout.strip() 
            result["stderr"] = proc_result.stderr.strip()
            return result
        else:  
            # 构建完整结果  
            result = {
                "success": proc_result.returncode == 0,
                "returncode": proc_result.returncode,
                "stdout": proc_result.stdout.strip(),
                "stderr": proc_result.stderr.strip(),
                "command": " ".join(cmd),
                "exe_path": exe_path,
            }
           
    except FileNotFoundError:
        result["stderr"] = f"错误：未找到文件 '{exe_path}'（请检查路径是否正确）"
    except PermissionError:
        result["stderr"] = f"错误：权限不足，无法执行 '{exe_path}'（请检查文件权限）"
    except WindowsError:
         result["stderr"] = f"错误：%1 '{exe_path}'".args(result["sentinel"])
    except Exception as e:
        result["stderr"] = f"错误：{str(e)}"
    return result


if __name__ == "__main__":
    convsp_path = "D:/WeldRobotWeldRobot1.0/ptom/publish/CONVSP.EXE"
    # status = call_convsp(convsp_path, ["D:/WeldRobotWeldRobot1.0/ptom/publish/123.PKT","D:/WeldRobotWeldRobot1.0/ptom/publish/111111.p"])
    status = call_convsp(convsp_path, ["D:/WeldRobotWeldRobot1.0/ptom/publish/234.txt","D:/WeldRobotWeldRobot1.0/ptom/publish/111111.s"])
    print("\n=== 实时输出调用结果 ===")
    print(f"最终结果:")
    if status['success']:
        print("successful！！！转换成功！！！")
    else:
        print('转换失败: ' + status['stderr'])
    #print(f"返回码：{status['returncode']}")
