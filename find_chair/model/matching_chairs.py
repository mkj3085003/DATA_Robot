import openai

# 设置你的 OpenAI API 密钥,1$
api_key = "sk-0DTIEOCIY1D6XoafRo8wqBWcqZMf4rmCIxMRKtij8LcQJ3h1"
# 初始化 OpenAI 客户端
openai.api_key = api_key
# 用户输入的问题
user_input=input("Welcome! How many people are dining with you today?")
user_input = "we have 3 people and we would like to sit next to the windows."

# 使用 GPT 模型生成对话
response = openai.Completion.create(
    engine="davinci",
    prompt=f"User: {user_input}\nAI:",
    max_tokens=50  # 设置生成文本的最大长度
)

# 提取 GPT 的回答
gpt_response = response.choices[0].text