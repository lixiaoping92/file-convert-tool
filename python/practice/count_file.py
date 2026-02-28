import os

def count_files_current_dir(directory):
    """统计指定目录中的文件数量（仅当前目录，不包含子目录）"""
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

def count_files_recursive(directory):
    """递归统计目录及其所有子目录中的文件数量"""
    try:
        file_count = 0
        # 递归遍历目录树
        for root, dirs, files in os.walk(directory):
            file_count += len(files)
        return file_count
    except FileNotFoundError:
        print(f"错误：目录 '{directory}' 不存在")
        return -1
    except PermissionError:
        print(f"错误：没有访问目录 '{directory}' 的权限")
        return -1
    except Exception as e:
        print(f"错误：{e}")
        return -1

def main():
    """主函数：处理用户输入并执行统计"""
    print("文件数量统计工具")
    print("=" * 40)
    
    # 选择统计模式
    print("请选择统计模式：")
    print("1. 仅统计当前目录中的文件")
    print("2. 递归统计所有子目录中的文件")
    
    mode = input("请输入选项编号 (1/2)：").strip()
    
    if mode not in ["1", "2"]:
        print("无效的选项，请重新运行程序")
        return
    
    # 输入目录路径
    directory = input("请输入要统计的目录路径：").strip()
    
    # 规范化路径（处理相对路径）
    directory = os.path.abspath(directory)
    
    print(f"\n正在统计目录 '{directory}' 中的文件数量...")
    
    # 执行统计
    if mode == "1":
        count = count_files_current_dir(directory)
        mode_name = "当前目录"
    else:
        count = count_files_recursive(directory)
        mode_name = "所有子目录"
    
    # 输出结果
    if count >= 0:
        print(f"\n统计完成！")
        print(f"在 {mode_name} 中找到的文件数量：{count}")
    else:
        print("\n统计失败，请检查错误信息")

if __name__ == "__main__":
    main()