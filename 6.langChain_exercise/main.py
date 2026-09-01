from httpx import stream
from langchain.chat_models import init_chat_model
from src.config.model import config_chat_model
from langchain_community.chat_models.tongyi import ChatTongyi


# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。


# 模型测试1
chat_model = init_chat_model(model_name="anthropic")
# print("anthropic", chat_model)

# 模型测试2
# model2 = ChatTongyi(
#     model="qianwen-max"
# )


# 调用方式2
from langchain.agents import create_agent
agent = create_agent(
    model=config_chat_model,
    system_prompt="你是一个 helpful 的助手，回答尽量简洁。",
)


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':

    # 1.通过模型类的凡是调用
    # print("config_chat_model", config_chat_model.stream("你是谁？"))
    # print("config_chat_model", config_chat_model.invoke("你是谁？"))
    # print(type(model2))  # model2 暂未启用，启用前请先取消上方 ChatTongyi 注释


    # 2.通过agent 智能体的方式调用
    # result = agent.invoke(
    #     {"messages": [{"role": "user", "content": "你是谁？"}]}
    # )
    # print(result)
    # print(result["messages"][-1].content)


    result = agent.stream(
        {"messages": [{"role": "user", "content": "你是谁？"}]},
        stream_mode="messages"
    )
    for token, metadata in result:
        if token.content == "":
            continue
        print(token.content, end="", flush=True)
      
