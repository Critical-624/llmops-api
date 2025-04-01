#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/19 21:11
@Author  : thezehui@gmail.com
@File    : dalle3.py
"""
from typing import Type
import requests

from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from internal.lib.helper import add_attribute


# class Dalle3ArgsSchema(BaseModel):
#     query: str = Field(description="输入应该是生成图像的文本提示(prompt)")
#
#
# @add_attribute("args_schema", Dalle3ArgsSchema)
# def dalle3(**kwargs) -> BaseTool:
#     """返回dalle3绘图的LangChain工具"""
#     return OpenAIDALLEImageGenerationTool(
#         api_wrapper=DallEAPIWrapper(model="dall-e-3", **kwargs),
#         args_schema=Dalle3ArgsSchema,
#     )
class Dalle3ArgsSchema(BaseModel):
    query: str = Field(description="输入应该是生成图像的文本提示(prompt)")


class SiliconFlowKuaishouTool(BaseTool):
    name: str = "dalle3"
    description: str = "用于生成图像的硅基流动平台上的快手模型"
    args_schema: Type[BaseModel] = Dalle3ArgsSchema

    def _run(self, query: str) -> str:
        # 调用硅基流动API的逻辑
        api_url = "https://api.siliconflow.cn/v1/images/generations"

        try:
            response = requests.post(
                api_url,
                json={"prompt": query},
                headers={"Authorization": "Bearer sk-phhrxiymzriebrcmsrlnlyacgesmqcklretubdbuobwkbejs"}  # 需要替换为实际的API密钥
            )
            response.raise_for_status()
            result = response.json()
            return result.get("image_url", "图像生成失败")
        except Exception as e:
            return f"调用硅基流动API失败: {str(e)}"

    def _arun(self, query: str) -> str:
        return self._run(query)


@add_attribute("args_schema", Dalle3ArgsSchema)
def dalle3(**kwargs) -> BaseTool:
    """返回dalle3绘图的LangChain工具"""
    return SiliconFlowKuaishouTool()
