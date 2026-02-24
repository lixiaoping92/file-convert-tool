import subprocess
from pathlib import Path
import convert as tos
import windows_status as ws

def call_convsp_with_sentinel_check(convsp_path, args=list)->dict:
    """调用CONVSP.EXE并检测Sentinel弹窗"""
    # 调用CONVSP.EXE（异步）
    exe_path = str(Path(convsp_path).absolute())
    cmd = [exe_path] + (args)
    
    proc = subprocess.Popen(
        cmd,
        shell=False,
        capture_output=True,
        text=True,
        encoding="gbk"
    )
    
    # 检测Sentinel弹窗
    sentinel_info = ws.find_sentinel_popup()
    
    # 等待CONVSP结束
    stdout, stderr = proc.communicate()
    
    result = {
        "success": proc.returncode == 0,
        "sentinel": sentinel_info,
        "no_key": sentinel_info["is_no_key"],
        "stdout": stdout,
        "stderr": stderr,
    }
    return result

# 调用示例
convsp_path = "D:/WeldRobotWeldRobot1.0/ptom/publish/CONVSP.EXE"
# status = tos.call_convsp(convsp_path, ["D:/WeldRobotWeldRobot1.0/ptom/publish/123.PKT","D:/WeldRobotWeldRobot1.0/ptom/publish/111111.p"])
status = call_convsp_with_sentinel_check(convsp_path, ["D:/WeldRobotWeldRobot1.0/ptom/publish/123.PKT","D:/WeldRobotWeldRobot1.0/ptom/publish/111111.p"])
if result["no_key"]:
    print("转换失败：未插入Sentinel KEY！")
else:
    print("转换结果：", "成功" if result["success"] else "失败")