#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/05/15 11:48
@Author  : thezehui@gmail.com
@File    : multi_key_chat.py
"""
import os
import random
import time
import logging
from pathlib import Path
from typing import List, Any, ClassVar
from pydantic import PrivateAttr
from openai import APIError, AuthenticationError, RateLimitError
from langchain_openai import ChatOpenAI
from internal.core.language_model.entities.model_entity import BaseLanguageModel


class MultiKeyChatOpenAI(ChatOpenAI, BaseLanguageModel):
    """支持多API密钥轮询的OpenAI聊天模型"""
    _api_keys: ClassVar[List[str]] = PrivateAttr()
    _tried_keys: ClassVar[set] = PrivateAttr()

    def __init__(self, **kwargs):
        # 初始化类变量
        self.__class__._api_keys = []
        self.__class__._tried_keys = set()
        
        # 加载API密钥
        keys = self._load_keys_from_file()
        if not keys:
            # 尝试从环境变量获取默认key
            default_key = os.getenv("OPENAI_API_KEY")
            if default_key:
                keys = [default_key]
            else:
                raise ValueError("No API keys found in file or environment")
        
        # 设置类变量和选择初始密钥
        self.__class__._api_keys = keys
        initial_key = random.choice(keys)
        
        # 使用选定的密钥初始化父类
        super().__init__(openai_api_key=initial_key, **kwargs)

    def _load_keys_from_file(self) -> List[str]:
        """从文件加载API密钥"""
        keys = []
        api_keys_file = os.getenv("OPENAI_API_KEYS_FILE")
        if api_keys_file and Path(api_keys_file).exists():
            with open(api_keys_file, 'r', encoding='utf-8') as f:
                keys = [line.strip() for line in f if line.strip()]
        return keys

    def _generate(self, *args, **kwargs) -> Any:
        """简化版的生成方法，支持最多重试10次"""
        max_retries = 10
        errors = []
        
        for attempt in range(max_retries):
            try:
                return super()._generate(*args, **kwargs)
            except (AuthenticationError, RateLimitError, APIError) as e:
                # 记录错误信息
                error_msg = f"Attempt {attempt + 1}/{max_retries} failed with key {self.openai_api_key}: {str(e)}"
                logging.warning(error_msg)
                errors.append(error_msg)
                
                # 记录当前失败的密钥
                self.__class__._tried_keys.add(self.openai_api_key)
                
                # 从未尝试过的密钥中随机选择
                available_keys = [k for k in self.__class__._api_keys 
                                if k not in self.__class__._tried_keys]
                
                if not available_keys:
                    if attempt < max_retries - 1:  # 如果还有重试次数，重置已尝试的密钥集合
                        self.__class__._tried_keys.clear()
                        available_keys = self.__class__._api_keys
                    else:
                        error_details = "\n".join(errors)
                        raise RuntimeError(f"All API keys failed after {max_retries} attempts. "
                                         f"Errors:\n{error_details}")
                
                # 使用新密钥
                new_key = random.choice(available_keys)
                self.openai_api_key = new_key
                self.client.api_key = new_key
                
                # 指数退避重试
                wait_time = min(0.5 * (2 ** attempt), 10)  # 最大等待10秒
                time.sleep(wait_time)
        
        error_details = "\n".join(errors)
        raise RuntimeError(f"Max retries ({max_retries}) reached. Errors:\n{error_details}")
