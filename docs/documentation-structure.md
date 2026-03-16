# 文档结构

本文档描述了 AI Agent Gateway 项目的文档结构，帮助您快速找到所需的信息。

## 📚 文档结构概览

```
docs/
├── getting-started/     # 入门指南
├── core-concepts/       # 核心概念
├── api-reference/       # API 参考
├── tools/               # 工具相关
├── adapters/            # 适配器相关
├── examples/            # 示例代码
├── testing/             # 测试指南
├── contributing.md      # 贡献指南
├── documentation-structure.md  # 本文档
└── index.md             # 文档首页
```

## 🎯 文档导航

### 1. 入门指南 (getting-started/)

适合初学者的指南，帮助您快速上手 AI Agent Gateway。

- **quick-start.md**: 快速开始指南，包含基本安装和使用步骤
- **installation.md**: 详细的安装说明，包括依赖项和环境配置
- **configuration.md**: 配置选项和环境变量说明

### 2. 核心概念 (core-concepts/)

深入了解 AI Agent Gateway 的核心概念和设计理念。

- **agent-gateway.md**: Agent Gateway 概述和架构
- **agents.md**: AI 代理的概念、创建和管理
- **tools.md**: 工具的概念、使用和集成
- **responses.md**: 响应处理和格式化

### 3. API 参考 (api-reference/)

详细的 API 接口文档，包括请求参数和响应格式。

- **agent-gateway.md**: Agent Gateway 主 API
- **agent.md**: 代理相关 API
- **tool.md**: 工具相关 API
- **prompt.md**: 提示相关 API
- **response.md**: 响应相关 API

### 4. 工具 (tools/)

关于工具的详细信息，包括内置工具和自定义工具开发。

- **tools-overview.md**: 工具概述
- **built-in-tools.md**: 内置工具列表和使用方法
- **building-custom-tools.md**: 开发自定义工具的指南
- **tool-authentication.md**: 工具认证和安全

### 5. 适配器 (adapters/)

关于适配器的信息，用于集成不同的 AI 模型。

- **adapters-overview.md**: 适配器概述
- **integrating-adapters.md**: 集成现有适配器
- **writing-custom-adapters.md**: 开发自定义适配器

### 6. 示例 (examples/)

实际使用示例，帮助您理解如何使用 AI Agent Gateway。

- **basic-usage-examples.md**: 基本使用示例
- **advanced-scenarios-examples.md**: 高级场景示例
- **real-world-applications-examples.md**: 真实世界应用示例

### 7. 测试 (testing/)

关于测试的指南，确保您的代码质量。

- **running-tests.md**: 运行测试的方法
- **writing-tests.md**: 编写测试的指南

### 8. 贡献指南 (contributing.md)

如何为 AI Agent Gateway 项目贡献代码和文档。

## 🔍 查找帮助

- **入门问题**: 查看 `getting-started/` 目录
- **概念理解**: 查看 `core-concepts/` 目录
- **API 使用**: 查看 `api-reference/` 目录
- **工具开发**: 查看 `tools/` 目录
- **适配器集成**: 查看 `adapters/` 目录
- **实际示例**: 查看 `examples/` 目录
- **测试相关**: 查看 `testing/` 目录
- **贡献代码**: 查看 `contributing.md` 文件

## 📝 文档约定

- **代码块**: 使用 ``` 包围的代码示例
- **命令行**: 使用 `$` 前缀表示命令行输入
- **文件路径**: 使用 `path/to/file` 表示文件路径
- **API 端点**: 使用 `GET /api/endpoint` 格式表示 API 端点
- **重要概念**: 使用 **加粗文本** 强调重要概念

## 🤝 改进文档

如果您发现文档中的错误或有改进建议，请参考 `contributing.md` 文件了解如何贡献。
