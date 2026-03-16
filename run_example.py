from agentgateway.tools.weather_tool import WeatherTool
from agentgateway.tools.translate_tool import TranslationTool
from agentgateway.tools.calculator_tool import CalculatorTool

print("🎉 AI Agent Gateway 工具测试成功！")
print("=" * 50)

# 1. 测试天气工具
print("1. 测试天气工具")
weather_tool = WeatherTool()
weather_tool.set_parameters({"location": "北京,中国"})
result = weather_tool.execute()
print(result)

# 2. 测试翻译工具
print("\n2. 测试翻译工具")
translate_tool = TranslationTool()
translate_tool.set_parameters({"text": "Hello, how are you?", "source_lang": "en", "target_lang": "zh"})
result = translate_tool.execute()
print(f"英文 → 中文: Hello, how are you? → {result}")

translate_tool.set_parameters({"text": "Hello, how are you?", "source_lang": "en", "target_lang": "es"})
result = translate_tool.execute()
print(f"英文 → 西班牙语: Hello, how are you? → {result}")

# 3. 测试计算器工具
print("\n3. 测试计算器工具")
calculator_tool = CalculatorTool()
calculator_tool.set_parameters({"expression": "15 * 24"})
result = calculator_tool.execute()
print(f"计算: 15 * 24 = {result['result']}")

calculator_tool.set_parameters({"expression": "(10 + 5) * 2"})
result = calculator_tool.execute()
print(f"计算: (10 + 5) * 2 = {result['result']}")

print("\n" + "=" * 50)
print("✅ 所有工具测试完成！")
print("\n项目已经成功运行，可以使用以下工具：")
print("- WeatherTool: 获取天气信息")
print("- TranslationTool: 翻译文本")
print("- CalculatorTool: 执行计算")
print("- 以及其他内置工具...")
