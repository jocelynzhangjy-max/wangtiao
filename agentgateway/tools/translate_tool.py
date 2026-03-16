from typing import Dict, Any
from agentgateway.core.abstract_tool import Tool
import os
from dotenv import load_dotenv

class TranslationTool(Tool):
    def __init__(self):
        super().__init__("translate", "Translate text from one language to another")
        load_dotenv()

    def is_auth_setup(self):
        return True

    def execute(self) -> Any:
        parameters = self.get_parameters()
        text = parameters.get('text')
        source_lang = parameters.get('source_lang')
        target_lang = parameters.get('target_lang')

        # 简单的翻译实现（使用硬编码的示例）
        translated_text = self.translate_text(text, source_lang, target_lang)
        return translated_text

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to translate"
                },
                "source_lang": {
                    "type": "string",
                    "description": "The source language code (e.g., 'en' for English)"
                },
                "target_lang": {
                    "type": "string",
                    "description": "The target language code (e.g., 'es' for Spanish)"
                }
            },
            "required": ["text", "source_lang", "target_lang"]
        }

    def translate_text(self, text, source_lang, target_lang):
        # 简单的翻译实现（示例）
        translations = {
            'en_zh': {
                'Hello, how are you?': '你好，你怎么样？',
                'Hello': '你好',
                'Thank you': '谢谢'
            },
            'en_es': {
                'Hello, how are you?': '¡Hola, ¿cómo estás?',
                'Hello': 'Hola',
                'Thank you': 'Gracias'
            },
            'en_de': {
                'Hello, how are you?': 'Hallo, wie geht es dir?',
                'Hello': 'Hallo',
                'Thank you': 'Danke'
            },
            'en_hi': {
                'Hello, how are you?': 'नमस्ते, आप कैसे हैं?',
                'Hello': 'नमस्ते',
                'Thank you': 'धन्यवाद'
            }
        }
        
        key = f"{source_lang}_{target_lang}"
        if key in translations:
            if text in translations[key]:
                return translations[key][text]
            else:
                return f"[Translation: {text} from {source_lang} to {target_lang}]"
        else:
            return f"Translation not supported for {source_lang} to {target_lang}"