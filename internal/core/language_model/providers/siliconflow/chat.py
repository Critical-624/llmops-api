#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/14 18:10
@Author  : thezehui@gmail.com
@File    : chat.py
"""
import os

from langchain_openai import ChatOpenAI

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(ChatOpenAI, BaseLanguageModel):
    """硅基流动聊天模型"""

    def __init__(self, **kwargs):
        super().__init__(
            openai_api_key=os.getenv("SILICONE_FLOW_API_KEY"),
            openai_api_base=os.getenv("SILICONE_FLOW_BASE_URL"),
            **kwargs
        )
