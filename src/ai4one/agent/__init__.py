import copy
from typing import Callable, List
from dataclasses import dataclass


@dataclass
class AgentContext:
    session_id: str
    agent_name: str = "base"


class AttachmentRegistry:
    def __init__(self) -> None:
        self._factories: List[Callable[..., str]] = []

    def add(self, factory: Callable[..., str]) -> None:
        self._factories.append(factory)

    def build(self, ctx: AgentContext) -> str:
        """ctx = agent_name / user_id / session_id"""
        return "\n".join(f(ctx) for f in self._factories)


class Agent:
    _registry = AttachmentRegistry()
    name = "base"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry = AttachmentRegistry()

    @classmethod
    def system_attachment(cls, ctx: AgentContext) -> str:
        ctx.agent_name = cls.name
        return cls._registry.build(ctx)

    @classmethod
    def attach(cls):
        """
        用法：
            @attach(SomeAgent._registry)
            def my_info(agent_name: str, user_id: str, session_id: str) -> str:
                ...
        """

        def decorator(fn: Callable[..., str]):
            cls._registry.add(fn)  # 直接把函数放进去，运行时统一注入参数
            return fn

        return decorator

    def wrap_user_input(self, messages: list, ctx: AgentContext) -> str:
        """
        装饰LLM消息, 在用户输入的最后添加一附件信息.
        Args:
            messages (list): LLM消息列表.
        Returns:
            list: 装饰后的LLM消息列表.
        """
        sys_info = self.system_attachment(ctx)
        messages = copy.deepcopy(messages)
        system_info = (
            "\n<system_only>\n⚠️ 以下内容用户不可见，"
            f"""仅作为系统补充信息：\n{sys_info}\n</system_only>"""
        )
        messages[-1]["content"] = messages[-1]["content"] + system_info
        return messages
