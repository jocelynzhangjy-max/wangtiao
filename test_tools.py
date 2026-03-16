from agentgateway.tools.weather_tool import WeatherTool
from agentgateway.tools.translate_tool import TranslationTool
from agentgateway.tools.calculator_tool import CalculatorTool

# 测试天气工具
print("=== 测试天气工具 ===")
weather_tool = WeatherTool()
weather_tool.set_parameters({"location": "北京,中国"})
result = weather_tool.execute()
print(result)

# 测试翻译工具
print("\n=== 测试翻译工具 ===")
translate_tool = TranslationTool()
translate_tool.set_parameters({"text": "Hello, how are you?", "source_lang": "en", "target_lang": "zh"})
result = translate_tool.execute()
print(f"翻译结果: {result}")

# 测试计算器工具
print("\n=== 测试计算器工具 ===")
calculator_tool = CalculatorTool()
calculator_tool.set_parameters({"expression": "15 * 24"})
result = calculator_tool.execute()
print(f"计算结果: {result}")
