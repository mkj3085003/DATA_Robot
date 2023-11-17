import json

import openai


class InquireTempNeeds:
    def __init__(self):
        # 设置你的 OpenAI API 密钥
        api_key = "sk-z2ztez3nzdjRerVojn5LcTSsE5JzXxuDWk3oRHvigO0RzPHV"
        openai.api_base = "https://openkey.cloud/v1"
        openai.api_key = api_key

        self.conversation = []
        self.final_return = []
        # 询问座椅需求的对话流程
        self.prompt_front = {'role': 'system', 'content': """
               You are a cafe waiter robot that automatically collects seat order information for a Starbucks. 
               Please let me know if the room temperature is suitable. Does it need to be adjusted? 
               If so, do you want it higher or lower?

              Format:
               {
                   "option": (options:'no', 'higher', 'lower','set')
                   "temp": "A numerical value representing the temperature change in degrees"
               }
               
               Please respond using the corresponding option along with the desired temperature change.
           """}

        self.conversation.append(self.prompt_front)
        self.first_ask = {'role': 'assistant',
                          'content': "Is the room temperature suitable? Does it need to be adjusted? "
                                     "Does it need to be adjusted higher or lower? "}
        self.conversation.append(self.prompt_front)
        self.prompt_end = {'role': 'user',
                           'content': """
                           Conversation is finished. Please provide the Option and Temp number in JSON format.

                           Format:
                           {
                               "option": (options:'no', 'higher', 'lower','set')
                               "temp": "A numerical value representing the temperature change in degrees"
                           }


                           Example:
                           User: It is ok.
                           Return JSON: 
                           {
                               "option": "no",
                               "temp": 0
                           }
                           User: I want to increase the temperature by 2 degrees.
                           Return JSON: 
                           {
                               "option": "higher",
                               "temp": 2
                           }
                           User: I want to decrease the temperature by 5 degrees.
                           Return JSON: 
                           {
                               "option": "lower",
                               "temp": 5
                           }
                           User: I want to set the temperature at 25 degrees.
                           Return JSON: 
                           {
                               "option": "set",
                               "temp": 25
                           }
                           """
                           }

    def get_message_completion(self, messages, model="gpt-3.5-turbo", temperature=0):
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,  # 控制模型输出的随机程度
        )
        return response.choices[0].message['content']

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


    def chat(self, temp):
        count = 0
        while True:
            # 用户输入
            if  count > 1:
                print("===============corversation is over===============")
                # 结束对话
                self.conversation.append(self.prompt_end)
                return self.conversation
            else:
                input_from_user = str(input("user:"))
                # self.user.append({'role': 'user', 'content': input_from_user})
                self.conversation.append({'role': 'user', 'content': input_from_user})

                # 模型回复
                reply = self.get_message_completion(self.conversation, temperature=temp)
                self.conversation.append({'role': 'assistant', 'content': reply})
                count += 1
                print('robot:', reply)
                # 判断是否结束对话
