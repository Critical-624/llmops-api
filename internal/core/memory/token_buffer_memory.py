#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/10/01 13:51
@Author  : thezehui@gmail.com
@File    : token_buffer_memory.py
"""
from dataclasses import dataclass
from typing import List
import tiktoken

from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, trim_messages, get_buffer_string
from sqlalchemy import desc

from internal.entity.conversation_entity import MessageStatus
from internal.model import Conversation, Message
from pkg.sqlalchemy import SQLAlchemy


@dataclass
class TokenBufferMemory:
    """基于token计数的缓冲记忆组件"""
    db: SQLAlchemy  # 数据库实例
    conversation: Conversation  # 会话模型
    model_instance: BaseLanguageModel  # LLM大语言模型

    def count_message_tokens(self, messages: List[AnyMessage]) -> int:
        """计算消息列表的token数量"""
        try:
            # 首先尝试使用模型自带的token计数方法
            return self.model_instance.get_num_tokens_from_messages(messages)
        except (NotImplementedError, AttributeError):
            # 如果模型不支持，使用tiktoken进行计算
            encoding = tiktoken.get_encoding("cl100k_base")
            num_tokens = 0
            
            for message in messages:
                # 每条消息的基础token（根据OpenAI的计算方式）
                num_tokens += 4  # 每条消息的元数据开销
                
                # 计算内容的token
                if isinstance(message, (HumanMessage, AIMessage)):
                    num_tokens += len(encoding.encode(str(message.content)))
                    num_tokens += len(encoding.encode(message.type))  # 消息类型
                    
                # 如果消息有额外的key
                if hasattr(message, "additional_kwargs"):
                    for key, value in message.additional_kwargs.items():
                        num_tokens += len(encoding.encode(str(key)))
                        num_tokens += len(encoding.encode(str(value)))
            
            return num_tokens

    def get_history_prompt_messages(
            self,
            max_token_limit: int = 2000,
            message_limit: int = 10,
    ) -> list[AnyMessage]:
        """根据传递的token限制+消息条数限制获取指定会话模型的历史消息列表"""
        # 1.判断会话模型是否存在，如果不存在则直接返回空列表
        if self.conversation is None:
            return []

        # 2.查询该会话的消息列表
        messages = self.db.session.query(Message).filter(
            Message.conversation_id == self.conversation.id,
            Message.answer != "",
            Message.is_deleted == False,
            Message.status.in_([MessageStatus.NORMAL, MessageStatus.STOP, MessageStatus.TIMEOUT]),
        ).order_by(desc("created_at")).limit(message_limit).all()
        messages = list(reversed(messages))

        # 3.将messages转换成LangChain消息列表
        prompt_messages = []
        current_tokens = 0
        
        for message in messages:
            new_messages = [
                HumanMessage(content=message.query),
                AIMessage(content=message.answer),
            ]
            
            # 计算新消息的token数量
            new_tokens = self.count_message_tokens(new_messages)
            
            # 如果添加新消息会超过token限制，就停止添加
            if current_tokens + new_tokens > max_token_limit:
                break
                
            prompt_messages.extend(new_messages)
            current_tokens += new_tokens

        return prompt_messages

    def get_history_prompt_text(
            self,
            human_prefix: str = "Human",
            ai_prefix: str = "AI",
            max_token_limit: int = 2000,
            message_limit: int = 10,
    ) -> str:
        """根据传递的数据获取指定会话历史消息提示文本(短期记忆的文本形式，用于文本生成模型)"""
        # 1.根据传递的信息获取历史消息列表
        messages = self.get_history_prompt_messages(max_token_limit, message_limit)

        # 2.调用LangChain集成的get_buffer_string()函数将消息列表转换成文本
        return get_buffer_string(messages, human_prefix, ai_prefix)
