import requests
import json
import traceback

# 登录获取token
login_url = "http://localhost:8000/api/auth/login"
login_data = {
    "username": "1057438016@qq.com",
    "password": "123456"
}

print("Logging in...")
try:
    response = requests.post(login_url, data=login_data)
    print(f"Login status: {response.status_code}")
    print(f"Login response: {response.text}")

    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"Got token: {token[:20]}...")
        
        # 先获取用户代理列表
        list_url = "http://localhost:8000/api/agents/"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        print("\nGetting agents list...")
        response = requests.get(list_url, headers=headers)
        print(f"List agents status: {response.status_code}")
        print(f"List agents response: {response.text[:200]}")
        
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
        print(f"Data: {json.dumps(agent_data, ensure_ascii=False)}")
        
        response = requests.post(create_url, headers=headers, json=agent_data)
        print(f"\nCreate agent status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
    else:
        print(f"Login failed: {response.text}")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
