import openai
import json
import time


API_KEY = "sk-eQcx5qelSmgk6DhEKPGgNJ5IZvaWfPrF8mat2QWRomcPLGls"
#22:00领取可用：
#sk-Nqaedek5GkD6fC9SVyMwVTCEVeSIh5WB9EhQjAFWqjNdOZ0R
#sk-qoXUG1ZD6BI2Lkfov8fOir8bI1dJkTd9hgEZhrHskejp15eM
#sk-GTM6iyTPm0ALZaUUZL5Dq2LuKTHv6Qm01s4TNBAh6ACAsUM2
#sk-eQcx5qelSmgk6DhEKPGgNJ5IZvaWfPrF8mat2QWRomcPLGls
#sk-BCZt1tS0b1Q0bCIN1SPLpBNyFKLggQwkEfdhizw5iolDXywJ
#sk-72xe4WItoRtddjKK2Vjl0SD06c1OQ3ee1ZbHKTXKj4n5CrpS

openai.api_key = API_KEY
openai.api_base = "https://openkey.cloud/v1"
    
    
API_KEY = "sk-eQcx5qelSmgk6DhEKPGgNJ5IZvaWfPrF8mat2QWRomcPLGls"
#22:00领取可用：
#sk-Nqaedek5GkD6fC9SVyMwVTCEVeSIh5WB9EhQjAFWqjNdOZ0R
#sk-qoXUG1ZD6BI2Lkfov8fOir8bI1dJkTd9hgEZhrHskejp15eM
#sk-GTM6iyTPm0ALZaUUZL5Dq2LuKTHv6Qm01s4TNBAh6ACAsUM2
#sk-eQcx5qelSmgk6DhEKPGgNJ5IZvaWfPrF8mat2QWRomcPLGls
#sk-BCZt1tS0b1Q0bCIN1SPLpBNyFKLggQwkEfdhizw5iolDXywJ
#sk-72xe4WItoRtddjKK2Vjl0SD06c1OQ3ee1ZbHKTXKj4n5CrpS

openai.api_key = API_KEY
openai.api_base = "https://openkey.cloud/v1"
    
class ChatBot():
    def __init__(self) -> None:
        self.conversation = []
        self.start_prompt = {'role': 'system', 'content':
                             f"""You are a cafe waiter that collects the customer needs and order information for a Starbucks.The user will play the role of a customer.
                            The ordering conversation should end within 4 inquiries. Please use as few conversations as possible to ask clearly the user's needs.
                             If you judge that the customer has finished ordering,
                             use the following sentence as the first sentence of your reply:
                             'Ordering is over, I will repeat your order.'
                             
                             Now, start a conversation.""",
                             'role': 'assistant', 'content': """It's a pleasure to serve you. What would you like to order?"""
                            }
        self.conversation.append(self.start_prompt)
        self.end_prompt = {'role': 'system', 'content': """The conversation is over.
                         Please process the talk and return the guest's needs in JSON format."""}
        self.final_return = []

    def if_end(self):
        prompt={'role':"user","content":f"""{str(self.conversation)}\n
                Please judge whether the ordering in the above conversation is over. 
                When it is over, answer me a BOOL type variable: True, otherwise reply False."""
                }
        ifend = self.get_message_completion(prompt)
        print(ifend)
        if ifend =="True":
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

    def chat(self,temp):
        count=0
        while True:
            # 用户输入
            count += 1
            input_from_user = str(input("user:"))
            self.conversation.append({'role': 'user', 'content': input_from_user})

            # 模型回复
            reply = self.get_message_completion(self.conversation, temperature=temp)
            print('chat bot:', reply)

            # 判断是否结束对话
            if self.if_end(reply) or count > 5:#限制对话强制小于5轮 不然说个没完没了.
                # 输出最终回复
                print("===============coversation is over===============")
                # print(reply)
                # 结束对话
                self.conversation.append({'role': 'assistant', 'content': reply})
                self.final_return = self.get_message_completion(self.conversation, temperature=0)
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
    chatbot.chat(temp=0)
    print(chatbot.get_json())
