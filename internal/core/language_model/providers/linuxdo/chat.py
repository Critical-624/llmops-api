#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/14 22:57
@Author  : thezehui@gmail.com
@File    : chat.py
"""
import os

from langchain_openai import ChatOpenAI

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(ChatOpenAI, BaseLanguageModel):
    """LinuxDO聊天模型"""

    def __init__(self, **kwargs):
        super().__init__(
            openai_api_key=os.getenv("LINUXDO_API_KEY"),
            openai_api_base=os.getenv("LINUXDO_API_BASE"),
            **kwargs
        )
