import openai
import json


class InquireChairNeeds:
    def __init__(self):
        # 设置你的 OpenAI API 密钥
        api_key = "sk-z2ztez3nzdjRerVojn5LcTSsE5JzXxuDWk3oRHvigO0RzPHV"
        openai.api_base = "https://openkey.cloud/v1"
        openai.api_key = api_key

        # 询问座椅需求的对话流程
        self.prompt_front = {'role': 'system', 'content': """
            You are a cafe waiter robot that automatically collects seat order information for a Starbucks...
            [此处为提供的对话流程文本，具体内容请填充到这里]
        """}

        self.first_ask = {'role': 'assistant',
                          'content': "Hello, I am the intelligent service robot of TJark Cafe. I am very happy to serve you. How many of you are dining together? "}
        self.second_ask = {'role': 'assistant',
                           'content': 'Do you have any seat preference? Such as position, height, material, or avoiding the crowd, etc.?'}
        self.prompt_end = {'role': 'user', 'content': "Conversation is finished. Please return the JSON."}
        self.prompt_json = {'role': 'assistant', 'content': "{\n  \"seat_preference\": \"near window\",\n  \"number_of_people\": 4\n }"}

    def get_completion(self, prompt, model="gpt-3.5-turbo"):
        a = 1
        mymessage = [
            self.prompt_front, self.first_ask,  # 进行首次问候及问题提问
            {'role': 'user', 'content': "4"},  # 模拟用户回答第一个问题
            self.second_ask,  # 向用户提出第二个问题
            {'role': 'user', 'content': "Prefer a table near the window."},  # 模拟用户回答第二个问题
            self.prompt_end,  # 结束对话
            self.prompt_json,
            {"role": "user", "content": prompt},
            self.prompt_end,
        ]
        response = openai.get_completion_from_messages(mymessage, temperature=0.3)
        return response.choices[0].message["content"]

    def get_completion_from_messages(self, messages, model="gpt-3.5-turbo", temperature=0):
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature  # 控制模型输出的随机程度
        )
        content = response.choices[0].message['content']
        # ...
        # 剩余的处理逻辑，用于解析对话内容和生成回复
        # ...
        return content

    def initiate_conversation(self):
        # 调用对话方法，开始和用户交互
        # 在这些函数的中间，调用robot和人的冒泡
        message = [
            self.prompt_front, self.first_ask,  # 进行首次问候及问题提问
            {'role': 'user', 'content': "4"},  # 模拟用户回答第一个问题
            self.second_ask,  # 向用户提出第二个问题
            {'role': 'user', 'content': "Prefer a table near the window."},  # 模拟用户回答第二个问题
            self.prompt_end  # 结束对话
        ]
        response = self.get_completion_from_messages(message, temperature=0.3)
        return response


if __name__ == '__main__':
    inquirer = InquireChairNeeds()  # 初始化对话类
    response = inquirer.initiate_conversation()  # 调用对话函数
    print('Proceed response:\n', response)
