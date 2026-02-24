import sys
import os
import convert as tos
import uuid

# 配置CONVSP.EXE的路径来源
CONVSP_CONFIG = {
    "env_var": "CONVSP_PATH",  # 环境变量名
    "default_path": r"D:\WeldRobotWeldRobot1.0\ptom\publish"  # 默认路径
}

def setup_convsp_path():
    """设置CONVSP.EXE的路径"""
    # 1. 尝试从环境变量读取
    convsp_path = os.environ.get(CONVSP_CONFIG["env_var"], CONVSP_CONFIG["default_path"])
    
    # 2. 验证路径存在
    if not os.path.exists(convsp_path):
        print(f"警告：路径 {convsp_path} 不存在，使用默认路径")
        convsp_path = CONVSP_CONFIG["default_path"]
    
    # 3. 添加到sys.path（如果需要导入相关模块）
    if convsp_path not in sys.path:
        sys.path.insert(0, convsp_path)
    
    # 4. 返回CONVSP.EXE的完整路径
    return os.path.join(convsp_path, "CONVSP.EXE")

# 使用示例
if __name__ == "__main__":
    convsp_exe = setup_convsp_path()
    print(f"CONVSP.EXE路径：{convsp_exe}")
    convsp_path = r"D:\WeldRobotWeldRobot1.0\ptom\publish"
    # 调用CONVSP.EXE
    if os.path.exists(convsp_exe):
        result = tos.call_convsp(convsp_exe, [os.path.join(convsp_path,"*.txt"), os.path.join(convsp_path,"uuid.uuid4().s")])
        result = tos.call_convsp(convsp_exe, [os.path.join(convsp_path,"*.s"), os.path.join(convsp_path,"uuid.uuid4().txt")])
        result = tos.call_convsp(convsp_exe, [os.path.join(convsp_path,"*.p"), os.path.join(convsp_path,"uuid.uuid4().PKT")])
        result = tos.call_convsp(convsp_exe, [os.path.join(convsp_path,"*.PKT"), os.path.join(convsp_path,"uuid.uuid4().p")])