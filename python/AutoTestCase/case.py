import json
import os

def generate_test_cases(function_desc, requirements):
    """
    生成测试用例
    
    参数:
        function_desc: 功能描述
        requirements: 需求列表
    
    返回:
        str: 生成的测试用例
    """
    # 生成测试用例
    test_cases = f"""# 测试用例

## 功能描述
{function_desc}

## 需求
{chr(10).join([f"- {req}" for req in requirements])}

## 测试用例列表

### 1. 正常登录
- **测试步骤**:
  1. 打开登录页面
  2. 输入正确的用户名：testuser
  3. 输入正确的密码：password123
  4. 点击登录按钮
- **预期结果**: 成功登录，跳转到首页
- **测试数据**: 用户名：testuser，密码：password123
- **优先级**: 高

### 2. 空用户名登录
- **测试步骤**:
  1. 打开登录页面
  2. 留空用户名
  3. 输入正确的密码：password123
  4. 点击登录按钮
- **预期结果**: 提示"请输入用户名"
- **测试数据**: 用户名为空，密码：password123
- **优先级**: 高

### 3. 空密码登录
- **测试步骤**:
  1. 打开登录页面
  2. 输入正确的用户名：testuser
  3. 留空密码
  4. 点击登录按钮
- **预期结果**: 提示"请输入密码"
- **测试数据**: 用户名：testuser，密码为空
- **优先级**: 高

### 4. 错误用户名登录
- **测试步骤**:
  1. 打开登录页面
  2. 输入错误的用户名：wronguser
  3. 输入正确的密码：password123
  4. 点击登录按钮
- **预期结果**: 提示"用户名或密码错误"
- **测试数据**: 用户名：wronguser，密码：password123
- **优先级**: 高

### 5. 错误密码登录
- **测试步骤**:
  1. 打开登录页面
  2. 输入正确的用户名：testuser
  3. 输入错误的密码：wrongpassword
  4. 点击登录按钮
- **预期结果**: 提示"用户名或密码错误"
- **测试数据**: 用户名：testuser，密码：wrongpassword
- **优先级**: 高

### 6. 连续3次密码错误锁定账户
- **测试步骤**:
  1. 打开登录页面
  2. 输入正确的用户名：testuser
  3. 连续输入错误密码3次
  4. 再次尝试登录
- **预期结果**: 提示"账户已锁定，请联系管理员"
- **测试数据**: 用户名：testuser，密码：wrong1, wrong2, wrong3
- **优先级**: 高

### 7. 忘记密码功能
- **测试步骤**:
  1. 打开登录页面
  2. 点击"忘记密码"链接
  3. 输入注册邮箱：test@example.com
  4. 点击"发送重置链接"按钮
- **预期结果**: 提示"重置密码链接已发送到邮箱"
- **测试数据**: 邮箱：test@example.com
- **优先级**: 中

### 8. 记住密码功能
- **测试步骤**:
  1. 打开登录页面
  2. 输入正确的用户名：testuser
  3. 输入正确的密码：password123
  4. 勾选"记住密码"
  5. 点击登录按钮
  6. 关闭浏览器后重新打开
- **预期结果**: 自动填充用户名和密码
- **测试数据**: 用户名：testuser，密码：password123
- **优先级**: 中

### 9. 自动登录功能
- **测试步骤**:
  1. 打开登录页面
  2. 输入正确的用户名：testuser
  3. 输入正确的密码：password123
  4. 勾选"自动登录"
  5. 点击登录按钮
  6. 关闭浏览器后重新打开
- **预期结果**: 直接登录进入系统，无需输入凭证
- **测试数据**: 用户名：testuser，密码：password123
- **优先级**: 中

### 10. 登出功能
- **测试步骤**:
  1. 成功登录
  2. 点击登出按钮
- **预期结果**: 退出系统，返回登录页
- **测试数据**: 无
- **优先级**: 高
"""
    
    return test_cases

def save_test_cases(test_cases, output_file):
    """
    保存测试用例到文件
    
    参数:
        test_cases: 测试用例文本
        output_file: 输出文件路径
    """
    # 保存为 Markdown 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(test_cases)
    print(f"测试用例已成功保存到: {output_file}")

def main():
    # 配置
    function_desc = "用户登录系统"
    requirements = [
        "支持用户名和密码登录",
        "支持忘记密码功能",
        "连续3次密码错误锁定账户",
        "登录成功后跳转到首页"
    ]
    output_file = "test_cases.md"
    
    try:
        # 生成测试用例
        print("正在生成测试用例...")
        test_cases = generate_test_cases(function_desc, requirements)
        print("测试用例生成成功！")
        
        # 保存测试用例
        print("正在保存测试用例...")
        save_test_cases(test_cases, output_file)
        
        # 显示生成的测试用例
        print("\n生成的测试用例预览：")
        print(test_cases[:500] + "...")  # 显示前 500 个字符
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()
cd D:\LXPMyPython
git add python
