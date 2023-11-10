import openai
import json
import time

api_key = "sk-z2ztez3nzdjRerVojn5LcTSsE5JzXxuDWk3oRHvigO0RzPHV"
openai.api_key = api_key
openai.api_base = "https://openkey.cloud/v1"

class ChatBot():
    def __init__(self) -> None:
        self.conversation = []
        self.start_prompt = {'role': 'system', 'content':
 """You are a cafe waiter that collects the customer needs and order information for a Starbucks.the user will plays the role of a customer.
If you judge that the customer has finished ordering:

    first,Please confirm with the customer after you judge that the order is over use the following sentence :
    "Do you have any other needs?" 
                             
    then,use the following sentence as the first sentence of your reply:
    'Ordering is over, I will repeat your order.'
                             
Now, start a conversation.""",\
'role':'assistant','content':"""
welcome to starbucks!How can I assist you today?
"""}
        self.conversation.append(self.start_prompt)
        # user_input = """'"""
        # self.conversation.append({'role': 'user', 'content': user_input})
        self.end_prompt = {'role': 'system', 'content': """The conversation is over.
                         Please process the talk and return the guest's needs in JSON format."""}
        self.final_return = []

    def if_end(self, end_response):
        if end_response.startswith("Ordering is over"):
            return True
        else:
            return False

    def get_message_completion(self, messages, model="gpt-3.5-turbo", temperature=0):
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,  # 控制模型输出的随机程度
        )
        return response.choices[0].message['content']

    def chat(self):
        print('chat bot:',"welcome to starbucks!How can I assist you today?")
        while True:
            # 用户输入
            input_from_user = str(input("user:"))
            
            # 添加新的用户输入
            self.conversation.append({'role': 'user', 'content': input_from_user})

            # 模型回复
            reply = self.get_message_completion(self.conversation, temperature=0.3)
            print('chat bot:', reply)
            
            # 判断是否结束对话
            if self.if_end(reply):
                # 输出最终回复
                print(reply)
                
                # 结束对话
                self.conversation.append({'role': 'assistant', 'content': reply})
                self.final_return = self.get_message_completion(self.conversation, temperature=0.1)
                self.conversation.append(self.end_prompt)
                
                # 返回整个对话历史
                return self.conversation


    def get_json(self):
        reply = self.get_message_completion(self.conversation, temperature=0)
        print("response from gpt:\n", reply)

        # Check if the content starts with '{' to identify JSON output
        if str(reply).strip().startswith('{'):
            try:
                # Attempt to parse the content as JSON
                order = json.loads(str(reply))
                # If successful, return the JSON content
                self.final_return = order
            except json.JSONDecodeError:
                # If parsing as JSON fails, let the model's response second time
                try_again_prompt = f" Please provide valid JSON format.\n Response from the model: {str(reply)}"
                self.final_return = json.loads(self.get_message_completion(try_again_prompt))

        # Check if the content is an error message
        else:
            self.final_return = str(reply)

        return self.final_return


if __name__ == '__main__':
    chatbot = ChatBot()
    chatbot.chat()
    print(chatbot.get_json())
