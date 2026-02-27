import sys
import os
from pathlib import Path
import windows_status as ws
import watch_file as wf


# 配置CONVSP.EXE的路径来源
CONVSP_CONFIG = {
    "env_var": "CONVSP_PATH",  # 环境变量名
    "default_path": r"D:\LXPmyAPP\publish"    # 默认路径
}
number = 0
"""统计指定目录中的文件数量（仅当前目录，不包含子目录）"""
def count_files_current_dir(directory):
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

def setup_convsp_path()->dict:
    """设置CONVSP.EXE的路径"""
    paths = {
        "convsp_exe":None,
        "convsp_path":None
    }
    # 1. 尝试从环境变量读取
    convsp_path = os.environ.get(CONVSP_CONFIG["env_var"], CONVSP_CONFIG["default_path"])
    
    # 2. 验证路径存在
    if not os.path.exists(convsp_path):
        print(f"警告：路径 {convsp_path} 不存在，使用默认路径")
        convsp_path = CONVSP_CONFIG["default_path"]
    
    # 3. 添加到sys.path（如果需要导入相关模块）
    if convsp_path not in sys.path:
        sys.path.insert(0, convsp_path)
    paths = {
        "convsp_exe":os.path.join(convsp_path, "CONVSP.EXE"),
        "convsp_path":convsp_path + "\\C9110011"
    }
    # 4. 返回CONVSP.EXE的完整路径以及遍历的目录
    return paths

def find_files_and_extract_names(directory, extensions=None, recursive=False, include_extension=True):
    """
    查找目录中的指定扩展名文件并提取文件名
    
    参数:
        directory: 要搜索的目录路径
        extensions: 要查找的扩展名列表（默认：['txt', 'p', 'pkt', 's']，不区分大小写）
        recursive: 是否递归查找子目录（默认 False）
        include_extension: 提取的文件名是否包含扩展名（默认 True）
    
    返回:
        包含提取文件名的列表
    """
    # 默认扩展名
    if extensions is None:
        extensions = ['.TXT', '.P', '.PKT', '.S']   
    # 统一转换为小写，以实现不区分大小写
    # extensions_lower = [ext.lower() for ext in extensions]
    found_files = []
    
    try:
        # 转换为 Path 对象
        dir_path = Path(directory)
        # 构建搜索模式
        pattern = "**/*" if recursive else "*"
        # 查找所有文件
        for file_path in dir_path.glob(pattern):
            # 只处理文件
            if file_path.is_file():
                # 获取文件扩展名（小写）
                # file_ext = file_path.suffix.lower().lstrip('.')  # 移除点号并转为小写 
                file_ext = file_path.suffix   
                # 检查扩展名是否在列表中
                if file_ext in extensions:
                    # 提取文件名
                    if include_extension:
                        file_name = file_path.name  # 包含扩展名的完整文件名
                    else:
                        file_name = file_path.stem   # 不包含扩展名的基本文件名           
                    found_files.append(file_name)               
    except Exception as e:
        print(f"错误: {e}")
    return found_files


"文件分类"
def file_type(file_type:str)->list:
    file_results = find_files_and_extract_names(convsp_path,file_type)
    files = []
    for file in file_results:
        if file.endswith(file_type):
            files.append(file)
    return files

"文件转换状态窗口捕捉"
def file_convert_status(convsp_path,convsp_exe,file,to_file_type,call_convsp)->dict:
    detect_result = {
        "found": False,
        "title": None,
        "content": None
    }
    
    init_number = count_files_current_dir(convsp_path)
    temp_name = Path(file).stem       
    result = call_convsp.call_convsp(
            convsp_exe,
            [convsp_path + "\\" + file, convsp_path + "\\" + temp_name + to_file_type]    #input_file: 输入文件路径，output_file: 输出文件路径
        ) 
    isNew = wf.monitor_file_with_watchdog(convsp_path + "\\" + temp_name + to_file_type)
    content_lower = result["status_window"]["content"].lower()
    if r"Sentinel LDK Protection System".lower() in content_lower:
        result["status_window"]["content"] = r"Sentinel key not found(H0007)"
    elif r"CONVSP".lower() in content_lower:
        addnumber = count_files_current_dir(convsp_path)
        if addnumber > init_number:
            result["status_window"]["content"] = r"Conversion successful" 
        elif addnumber == init_number and isNew:
            result["status_window"]["content"] = r"Conversion successful"
        elif addnumber == init_number and not isNew:
            result["status_window"]["content"] = r"Different No. of Axis" 
    print("文件名称：",file)
    print("窗口标题：",result["status_window"]["title"])  
    print("窗口内容：",result["status_window"]["content"]) 
    detect_result["found"] = True
    detect_result["title"] = result["status_window"]["title"]
    detect_result["content"] = result["status_window"]["content"]
    return detect_result

# 使用示例
if __name__ == "__main__":
    convsp_exe = setup_convsp_path()["convsp_exe"]
    convsp_path = setup_convsp_path()["convsp_path"]
    # 调用CONVSP.EXE
    # 创建检测器实例
    detector = ws.ConvspStatusDetector(
        window_keywords=["CONVSP", "Sentinel LDK Protection System"],
        timeout=3  # 15秒超时
    )

    if os.path.exists(convsp_exe):
        PKTfiles = file_type(".PKT")
        for PKTfile in PKTfiles: 
            number += 1
            print("排序：",number) 
            file_convert_status(convsp_path,convsp_exe,PKTfile,".P",detector)
        TXTfiles = file_type(".TXT")
        for TXTfile in TXTfiles:
            number += 1
            print("排序：",number) 
            file_convert_status(convsp_path,convsp_exe,TXTfile,".S",detector)
        Pfiles = file_type(".P")
        for Pfile in Pfiles:
            number += 1
            print("排序：",number) 
            file_convert_status(convsp_path,convsp_exe,Pfile,".PKT",detector)
        Sfiles = file_type(".S")
        for Sfile in Sfiles:
            number += 1
            print("排序：",number) 
            file_convert_status(convsp_path,convsp_exe,Sfile,".TXT",detector)

    # convsp_exe = setup_convsp_path()["convsp_exe"]
    # convsp_path = setup_convsp_path()["convsp_path"]
    # print(f"CONVSP.EXE路径：{convsp_exe}")
    
    # print("=== 示例 1: 基本用法（默认设置）===")
    # file_results = find_files_and_extract_names(convsp_path)
    # pkt_files = []
    # txt_files = []
    # p_files = []
    # s_files = []
    # for file in file_results:
    #     if file.endswith(".PKT"):
    #         pkt_files.append(file)
    #     elif file.endswith(".TXT"):
    #         txt_files.append(file)
    #     elif file.endswith(".P"):
    #         p_files.append(file)
    #     elif file.endswith(".S"):
    #         s_files.append(file)

    # # convsp_path = r"D:\LXPmyAPP\publish\C9110011"
    # # 调用CONVSP.EXE
    # # 创建检测器实例
    # detector = ws.ConvspStatusDetector(
    #     window_keywords=["CONVSP", "Sentinel LDK Protection System"],
    #     timeout=3  # 15秒超时
    # )

    
    # init_number = count_files_current_dir(convsp_path)
    # if os.path.exists(convsp_exe):
    #     number = 0
    #     for file in pkt_files:
    #         # 调用CONVSP.exe并检测状态窗口 convsp_path: CONVSP.EXE的路径,args: 传递给CONVSP.EXE的参数列表
    #         temp_name = Path(file).stem
            
    #         result = detector.call_convsp(
    #                 convsp_exe,
    #                 [convsp_path + "\\" + file, convsp_path + "\\" + temp_name + ".P"]    #input_file: 输入文件路径，output_file: 输出文件路径
    #             ) 
    #         isNew = wf.monitor_file_with_watchdog(convsp_path + "\\" + temp_name + ".P")
    #         content_lower = result["status_window"]["content"].lower()
    #         if r"Sentinel LDK Protection System".lower() in content_lower:
    #             result["status_window"]["content"] = r"Sentinel key not found(H0007)"
    #         elif r"CONVSP".lower() in content_lower:
    #             addnumber = count_files_current_dir(convsp_path)
    #             if addnumber > init_number:
    #                 result["status_window"]["content"] = r"Conversion successful" 
    #             elif addnumber == init_number and isNew:
    #                 result["status_window"]["content"] = r"Conversion successful"
    #             elif addnumber == init_number and not isNew:
    #                 result["status_window"]["content"] = r"Different No. of Axis" 
    #         number += 1
    #         print("排序：",number) 
    #         print("文件名称：",file)
    #         print("窗口标题：",result["status_window"]["title"])  
    #         print("窗口内容：",result["status_window"]["content"]) 


    #     for file in txt_files:
    #         temp_name = Path(file).stem
            
    #         result = detector.call_convsp(
    #             convsp_exe,
    #             [convsp_path + "\\" + file, convsp_path + "\\" + temp_name + ".S"]    #input_file: 输入文件路径，output_file: 输出文件路径
    #         )
    #         isNew = wf.monitor_file_with_watchdog(convsp_path + "\\" + temp_name + ".S")
            
    #         content_lower = result["status_window"]["content"].lower()
    #         if r"Sentinel LDK Protection System".lower() in content_lower:
    #             result["status_window"]["content"] = r"Sentinel key not found(H0007)"
    #         elif r"CONVSP".lower() in content_lower:
    #             addnumber = count_files_current_dir(convsp_path)
    #             if addnumber > init_number:
    #                 result["status_window"]["content"] = r"Conversion successful" 
    #             elif addnumber == init_number and isNew:
    #                 result["status_window"]["content"] = r"Conversion successful"
    #             elif addnumber == init_number and not isNew:
    #                 result["status_window"]["content"] = r"Different No. of Axis"
    #                 number += 1
    #         print("排序：",number) 
    #         print("文件名称：",file)
    #         print("窗口标题：",result["status_window"]["title"])  
    #         print("窗口内容：",result["status_window"]["content"]) 

    #     for file in p_files:
    #         temp_name = Path(file).stem
            
    #         result = detector.call_convsp(
    #             convsp_exe,
    #             [convsp_path + "\\" + file, convsp_path + "\\" + temp_name + ".PKT"]    #input_file: 输入文件路径，output_file: 输出文件路径
    #         )
    #         isNew = wf.monitor_file_with_watchdog(convsp_path + "\\" + temp_name + ".PKT")
    #         content_lower = result["status_window"]["content"].lower()
    #         if r"Sentinel LDK Protection System".lower() in content_lower:
    #             result["status_window"]["content"] = r"Sentinel key not found(H0007)"
    #         elif r"CONVSP".lower() in content_lower:
    #             addnumber = count_files_current_dir(convsp_path)
    #             if addnumber > init_number :
    #                 result["status_window"]["content"] = r"Conversion successful" 
    #             elif addnumber == init_number and isNew:
    #                 result["status_window"]["content"] = r"Conversion successful" 
    #             elif addnumber == init_number and not isNew:
    #                 result["status_window"]["content"] = r"Different No. of Axis"
    #                 number += 1
    #         print("排序：",number) 
    #         print("文件名称：",file)
    #         print("窗口标题：",result["status_window"]["title"])  
    #         print("窗口内容：",result["status_window"]["content"]) 
                
    #     for file in s_files:
    #         temp_name = Path(file).stem
    #         result = detector.call_convsp(
    #             convsp_exe,
    #             [convsp_path + "\\" + file, convsp_path + "\\" + temp_name + ".TXT"]    #input_file: 输入文件路径，output_file: 输出文件路径
    #         )
    #         isNew = wf.monitor_file_with_watchdog(convsp_path + "\\" + temp_name + ".TXT")
    #         content_lower = result["status_window"]["content"].lower()
    #         if r"Sentinel LDK Protection System".lower() in content_lower:
    #             result["status_window"]["content"] = r"Sentinel key not found(H0007)"
    #         elif r"CONVSP".lower() in content_lower:
    #             addnumber = count_files_current_dir(convsp_path)
    #             if addnumber > init_number:
    #                 result["status_window"]["content"] = r"Conversion successful" 
    #             elif addnumber == init_number and isNew:
    #                 result["status_window"]["content"] = r"Conversion successful"
    #             elif addnumber == init_number and not isNew:
    #                 result["status_window"]["content"] = r"Different No. of Axis"
    #                 number += 1
    #         print("排序：",number) 
    #         print("文件名称：",file)
    #         print("窗口标题：",result["status_window"]["title"])  
    #         print("窗口内容：",result["status_window"]["content"]) 