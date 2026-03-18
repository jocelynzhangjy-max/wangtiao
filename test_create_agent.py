import requests
import json

# 登录获取token
login_url = "http://localhost:8000/api/auth/login"
login_data = {
    "username": "1057438016@qq.com",
    "password": "123456"
}

print("Logging in...")
response = requests.post(login_url, data=login_data)
print(f"Login status: {response.status_code}")

if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"Got token: {token[:20]}...")
    
    # 创建代理
    create_url = "http://localhost:8000/api/agents/"
    agent_data = {
        "name": "测试代理",
        "description": "测试描述",
        "agent_type": "DeepSeek",
        "model_id": "deepseek-chat",
        "config_json": {"temperature": 0.7}
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\nCreating agent...")
    print(f"URL: {create_url}")
    print(f"Headers: {headers}")
    print(f"Data: {agent_data}")
    
    response = requests.post(create_url, headers=headers, json=agent_data)
    print(f"\nCreate agent status: {response.status_code}")
    print(f"Response: {response.text}")
else:
    print(f"Login failed: {response.text}")
