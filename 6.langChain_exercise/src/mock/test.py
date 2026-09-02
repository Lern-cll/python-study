# test.py
# 模型与 agent 调用示例，提供阻塞 / 流式两种问答方式

from src.config.model import config_chat_model  # 项目自定义的 chat model 配置
from langchain.agents import create_agent        # langchain 内置 agent 创建函数
from langchain.messages import (                 # langchain 消息类型（多轮对话）
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from pydantic import BaseModel, Field

from langchain_tavily import TavilySearch
# 初始化工具，并设置参数，具体参数设置参考官网
search_tool = TavilySearch(
    max_results=5,
    topic="general",
    # include_answer=False,
    # include_raw_content=False,
    # include_images=False,
    # include_image_descriptions=False,
    # search_depth="basic",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None
)

# Agent回答内容引用的网页信息
class Reference(BaseModel):
    title: str = Field(description="The title of the web page cited in the answer")
    url: str = Field(description="The url of the web page cited in the answer")

# Agent的回答内容
class AnswerInfo (BaseModel):
    answer: str = Field(description="The final answer for user")
    reference: list[Reference] = Field(description="The web pages cited in the answer")




# 提示词工程
system_prompt = """
# 身份
你是一个专业的图片分析助手和专业的摄影专家，能够根据图片内容回答用户问题。

# 示例
user：图片中有什么内容?
assistant: 优美的乡村傍晚—— 图片中展示了一个优美的乡村场景,采用了xxx的摄影技术，给人一种宁静的感觉。

# 指令
- 你只能回答图片相关的问题，不能回答其他问题。
- 需要你对图片中的内容进行详细分析，不能简单回答。
- 返回的时候,使用中文回答。

# 规则
- 你只能回答图片相关的问题，不能回答其他问题。
- 不能捏造图片中的内容，只能根据图片中的内容回答问题。
- 如果碰到模糊的,无法识别的内容，要回答"无法识别"。
"""

# 全局缓存的 agent 实例，用于单例模式
_agent = None


def web_search():
    agent = get_agent('')
    for chunk in agent.stream(
            {"messages": [HumanMessage(content="北京接下来5天天气如何?")]},
            stream_mode="updates"
    ):
        for step, data in chunk.items():
            print(f"step: {step}")
            print(f"content: {data['messages'][-1].content_blocks}")
            print()


# 工具函数：模拟查询天气（agent 会根据用户问题决定是否调用）
def get_weather(location: str):
        """获取指定地点的当前天气"""
        return f"Current weather in {location} is sunny"

def test_get_weather():
    """测试带工具的 agent：让模型自行决定何时调用 get_weather"""
    # 创建带工具的 agent
    agent = create_agent( model=config_chat_model, tools=[get_weather])

    # 多轮对话，最后一条问题是关键触发工具调用的请求
    response = agent.invoke(
        {
            "messages": [
                SystemMessage("请使用工具来获取天气信息。"),
                HumanMessage("你好，我是乐哥,"),
                AIMessage("你好，乐哥，很高兴认识你。"),
                HumanMessage("上海今天天气如何？"),
            ]
        }
    )
    for message in response["messages"]: 
        message.pretty_print()


def image_ask(url: str = '', question: str = "分析一下图片中的内容") -> str:
    """
    多模态问答：根据图片 URL + 问题，返回模型回答。
    :param url: 图片的公网 URL（http/https），必须是模型能访问到的链接
    :param question: 关于图片的问题，默认是"分析一下图片中的内容"
    :return: 模型的文本回答
    """
    IMAGE_URL = "https://img95.699pic.com/photo/50464/9776.jpg_wh860.jpg"
    agent = get_agent(system_prompt)
    response = agent.invoke({
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": question or "分析一下图片中的内容"},
                # Anthropic 多模态格式：source 必须嵌套对象（之前的 source_type 是错误字段）
                {"type": "image", "source": {"type": "url", "url": IMAGE_URL or url}},
            ],
        }]
    })
    response["messages"][-1].pretty_print()
    return response["messages"][-1].content

def stream_ask(question: str):
    """
    流式问答，逐 token 输出
    :param question: 用户问题
    """
    agent = get_agent()
    # stream_mode="messages" 表示按消息片段逐个返回
    result = agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="messages",
    )
    for token, metadata in result:  # token 为单个消息片段，metadata 携带上下文信息
        if token.content == "":      # 跳过空内容片段，避免打印空行
            continue
        token.pretty_print()          # 用 langchain 自带的格式化方式打印

def ask(question: str) -> str:
    """
    阻塞式问答
    :param question: 用户问题
    :return: 模型最终回答内容
    """
    agent = get_agent()
    # invoke 为一次性调用，等待完整结果返回
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    # 取最后一条消息（助手回复）的内容
    return result["messages"][-1].content

def get_agent(system_prompt: str = system_prompt):
    """获取 agent 实例，首次调用时创建，之后复用"""
    global _agent
    if _agent is None:  # 首次调用才初始化，节省资源
        _agent = create_agent(
            tools=[search_tool],
            model=config_chat_model,                       # 使用 config 中配置的模型
            system_prompt= system_prompt or "你是一个 helpful 的助手，回答尽量简洁。",  # 系统提示词
            response_format=AnswerInfo
        )
    return _agent