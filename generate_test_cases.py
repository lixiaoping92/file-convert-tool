import json
import requests
import os
from xmindparser import xmind_to_dict, xmind_to_file

# 配置
API_KEY = "YOUR_API_KEY"  # 替换为您的 API Key
API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

def generate_test_cases_with_aliyun(function_desc, requirements):
    """
    使用通义千问生成测试用例
    
    参数:
        function_desc: 功能描述
        requirements: 需求列表
    
    返回:
        str: 生成的测试用例
    """
    # 构建提示词
    prompt = f"""请为以下功能生成详细的测试用例，包括测试场景、测试步骤、预期结果、测试数据和优先级：

功能描述：{function_desc}

需求：
{chr(10).join([f"{i+1}. {req}" for i, req in enumerate(requirements)])}

请按照以下格式输出：
1. 测试场景
2. 测试步骤
3. 预期结果
4. 测试数据
5. 优先级
"""
    
    # 构建请求数据
    payload = {
        "model": "qwen-plus",
        "input": {
            "prompt": prompt
        },
        "parameters": {
            "max_new_tokens": 2048,
            "temperature": 0.7
        }
    }
    
    # 设置请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # 发送请求
    response = requests.post(API_URL, json=payload, headers=headers)
    
    # 解析响应
    if response.status_code == 200:
        result = response.json()
        if "output" in result and "text" in result["output"]:
            return result["output"]["text"]
        else:
            raise Exception(f"API 响应格式错误: {result}")
    else:
        raise Exception(f"API 调用失败: {response.status_code} - {response.text}")

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
        elif current_section == "测试步骤":
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
        print("正在调用 AI 生成测试用例...")
        test_cases_text = generate_test_cases_with_aliyun(function_desc, requirements)
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
