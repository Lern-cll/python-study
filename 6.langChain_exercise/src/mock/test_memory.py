# langchain提供的checkpointer的默认实现，基于内存存储
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from langchain.messages import HumanMessage, AIMessage

from src.config.model import config_chat_model  # 复用 test.py 中的模型配置


# 设定thread_id，作为会话标识
config = {"configurable": {"thread_id": "thread_1"}}

# 创建带 checkpointer 的 agent，保存对话历史到内存
checkpointer = InMemorySaver()
agent = create_agent(
    model=config_chat_model,
    tools=[],                                  # 暂不绑定工具，按需添加
    system_prompt="你是一个 helpful 的助手，回答尽量简洁。",
    checkpointer=checkpointer,                 # 关键：启用记忆
)


def test_memory1():
    # 第一次调用，告知AI我的信息
    response = agent.invoke(
        {"messages": [HumanMessage(content="你好，我叫虎哥，我最喜欢猫猫。")]},
        config # 调用时添加thread_id，区分不同会话
    )
    for message in response["messages"]:
        message.pretty_print()


def test_memory2():
    # 第二次调用，验证 agent 是否记住上一轮的内容
    response = agent.invoke(
        {"messages": [HumanMessage(content="你知道我叫什么名字吗？我喜欢什么动物？")]},
        config
    )
    for message in response["messages"]:
        message.pretty_print()

