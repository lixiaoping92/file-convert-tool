import json
import os
from xmindparser import xmind_to_file

def generate_test_cases_local(function_desc, requirements):
    """
    本地生成测试用例（模拟 AI 生成）
    
    参数:
        function_desc: 功能描述
        requirements: 需求列表
    
    返回:
        str: 生成的测试用例
    """
    # 模拟生成测试用例
    test_cases = f"""
1. 测试场景：正常登录
2. 测试步骤：
   1. 打开登录页面
   2. 输入正确的用户名：testuser
   3. 输入正确的密码：password123
   4. 点击登录按钮
3. 预期结果：成功登录，跳转到首页
4. 测试数据：用户名：testuser，密码：password123
5. 优先级：高

1. 测试场景：空用户名登录
2. 测试步骤：
   1. 打开登录页面
   2. 留空用户名
   3. 输入正确的密码：password123
   4. 点击登录按钮
3. 预期结果：提示“请输入用户名”
4. 测试数据：用户名为空，密码：password123
5. 优先级：高

1. 测试场景：空密码登录
2. 测试步骤：
   1. 打开登录页面
   2. 输入正确的用户名：testuser
   3. 留空密码
   4. 点击登录按钮
3. 预期结果：提示“请输入密码”
4. 测试数据：用户名：testuser，密码为空
5. 优先级：高

1. 测试场景：错误用户名登录
2. 测试步骤：
   1. 打开登录页面
   2. 输入错误的用户名：wronguser
   3. 输入正确的密码：password123
   4. 点击登录按钮
3. 预期结果：提示“用户名或密码错误”
4. 测试数据：用户名：wronguser，密码：password123
5. 优先级：高

1. 测试场景：错误密码登录
2. 测试步骤：
   1. 打开登录页面
   2. 输入正确的用户名：testuser
   3. 输入错误的密码：wrongpassword
   4. 点击登录按钮
3. 预期结果：提示“用户名或密码错误”
4. 测试数据：用户名：testuser，密码：wrongpassword
5. 优先级：高

1. 测试场景：连续3次密码错误锁定账户
2. 测试步骤：
   1. 打开登录页面
   2. 输入正确的用户名：testuser
   3. 连续输入错误密码3次
   4. 再次尝试登录
3. 预期结果：提示“账户已锁定，请联系管理员”
4. 测试数据：用户名：testuser，密码：wrong1, wrong2, wrong3
5. 优先级：高

1. 测试场景：忘记密码功能
2. 测试步骤：
   1. 打开登录页面
   2. 点击“忘记密码”链接
   3. 输入注册邮箱：test@example.com
   4. 点击“发送重置链接”按钮
3. 预期结果：提示“重置密码链接已发送到邮箱”
4. 测试数据：邮箱：test@example.com
5. 优先级：中
    """
    
    return test_cases

def parse_test_cases(test_cases_text):
    """
    解析生成的测试用例文本
    
    参数:
        test_cases_text: 生成的测试用例文本
    
    返回:
        list: 解析后的测试用例列表
    """
    test_cases = []
    lines = test_cases_text.strip().split('\n')
    
    current_case = {}
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 检查是否是新的测试场景
        if line.startswith('1. 测试场景'):
            if current_case:
                test_cases.append(current_case)
            current_case = {"测试场景": line.replace('1. 测试场景', '').strip(), "测试步骤": [], "预期结果": "", "测试数据": "", "优先级": ""}
            current_section = None
        elif line.startswith('2. 测试步骤'):
            current_section = "测试步骤"
        elif line.startswith('3. 预期结果'):
            current_section = "预期结果"
            current_case["预期结果"] = line.replace('3. 预期结果', '').strip()
        elif line.startswith('4. 测试数据'):
            current_section = "测试数据"
            current_case["测试数据"] = line.replace('4. 测试数据', '').strip()
        elif line.startswith('5. 优先级'):
            current_section = "优先级"
            current_case["优先级"] = line.replace('5. 优先级', '').strip()
        elif current_section == "测试步骤" and line:
            current_case["测试步骤"].append(line)
    
    # 添加最后一个测试用例
    if current_case:
        test_cases.append(current_case)
    
    return test_cases

def create_xmind_structure(test_cases, output_file):
    """
    创建 XMind 结构并保存
    
    参数:
        test_cases: 测试用例列表
        output_file: 输出 XMind 文件路径
    """
    # 创建 XMind 基本结构（符合 xmind_to_file 的格式）
    xmind_structure = {
        "title": "测试用例",
        "structure": "org.xmind.ui.logic.right",
        "rootTopic": {
            "title": "测试用例",
            "topics": []
        }
    }
    
    # 添加测试用例
    for case in test_cases:
        case_topic = {
            "title": case.get("测试场景", "未命名场景"),
            "topics": []
        }
        
        # 添加测试步骤
        if case.get("测试步骤"):
            steps_topic = {
                "title": "测试步骤",
                "topics": [{"title": step} for step in case["测试步骤"]]
            }
            case_topic["topics"].append(steps_topic)
        
        # 添加预期结果
        if case.get("预期结果"):
            case_topic["topics"].append({"title": f"预期结果: {case['预期结果']}"})
        
        # 添加测试数据
        if case.get("测试数据"):
            case_topic["topics"].append({"title": f"测试数据: {case['测试数据']}"})
        
        # 添加优先级
        if case.get("优先级"):
            case_topic["topics"].append({"title": f"优先级: {case['优先级']}"})
        
        xmind_structure["rootTopic"]["topics"].append(case_topic)
    
    # 保存为 JSON 文件
    json_file = output_file.replace('.xmind', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(xmind_structure, f, ensure_ascii=False, indent=2)
    
    # 转换 JSON 为 XMind 文件
    try:
        xmind_to_file(json_file, output_file)
        # 删除临时 JSON 文件
        if os.path.exists(json_file):
            os.remove(json_file)
        print(f"测试用例已成功保存到: {output_file}")
    except Exception as e:
        print(f"创建 XMind 文件失败: {e}")
        # 保留 JSON 文件以便调试
        print(f"JSON 结构已保存到: {json_file}")

def main():
    # 配置
    function_desc = "用户登录系统"
    requirements = [
        "支持用户名和密码登录",
        "支持忘记密码功能",
        "连续3次密码错误锁定账户",
        "登录成功后跳转到首页"
    ]
    output_file = "test_cases.xmind"
    
    try:
        # 生成测试用例
        print("正在生成测试用例...")
        test_cases_text = generate_test_cases_local(function_desc, requirements)
        print("测试用例生成成功！")
        print("\n生成的测试用例：")
        print(test_cases_text)
        
        # 解析测试用例
        print("\n正在解析测试用例...")
        test_cases = parse_test_cases(test_cases_text)
        print(f"成功解析 {len(test_cases)} 个测试用例")
        
        # 创建 XMind 文件
        print("正在创建 XMind 文件...")
        create_xmind_structure(test_cases, output_file)
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()
