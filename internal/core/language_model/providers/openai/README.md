# OpenAI Provider

## 多API密钥支持

本项目支持使用多个OpenAI API密钥，实现自动轮询和失效密钥排除功能。

### 配置方法

在`.env`文件中，您可以通过以下两种方式配置OpenAI API密钥：

1. 单个API密钥（向后兼容）：
```
OPENAI_API_KEY=sk-your-api-key
```

2. 多个API密钥（新功能）：
```
OPENAI_API_KEYS=sk-your-first-key,sk-your-second-key,sk-your-third-key
```

多个API密钥之间使用逗号分隔。系统会自动轮询这些密钥，并在遇到无效密钥时自动排除。

### 特性

- **自动轮询**：系统会随机选择可用的API密钥，避免单个密钥的使用频率过高
- **失效密钥排除**：当遇到认证错误或速率限制错误时，系统会自动标记该密钥为无效，并使用其他可用密钥
- **自动重试**：当API调用失败时，系统会自动使用其他密钥重试
- **向后兼容**：如果只配置了`OPENAI_API_KEY`，系统仍然可以正常工作

### 支持的模型

- gpt-4o
- gpt-4o-mini
- gpt-4.1（新增）

## GPT-4.1 模型

GPT-4.1是OpenAI最新发布的模型，本项目已添加对该模型的支持。您可以在应用配置中选择使用该模型。
