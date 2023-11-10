import openai
import json
import time
api_key = "sk-z2ztez3nzdjRerVojn5LcTSsE5JzXxuDWk3oRHvigO0RzPHV"
openai.api_key = api_key
openai.api_base = "https://openkey.cloud/v1"
class ChatBot():
    def __init__(self) -> None:
       
        
        self.conversation=[None]
        self.start_prompt={"role":"system","content":\
                           "You are a cafe waiter robot that\
                          s  automatically collects the guest need and order information\
                            for a Starbucks.\
                            If you judge that the customer has finished ordering. \
                            Please return in the following sentence: \
                                'Ordering is over, I will repeat your order.'\
                            Now,please start the conversation with the guest."}
        self.conversation.append(self.start_prompt)
        self.end_prompt={"role":'system','content':"The conversation is over.\
                         please process the talk and return the need from the guest in json format"}
        self.final_return=None
    
    def if_end(self,end_response):
        if end_response.startswith("Ordering is over"):
            return True
        else :
            return False
        
    def get_message_completion(messages,model="gpt-3.5-turbo",temperature=0):
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature, # 控制模型输出的随机程度
        )
        return response.choices[0].message["content"]
    
    def chat(self):
        response=self.get_message_completion(self.conversation)
        print('chat bot:',response)
        while True:
            input_from_user=str(input("user :"))
            time.sleep(3)
            self.conversation.append({'role':'user','content':input_from_user})
            reply=self.get_message_completion(self.conversation,temperature=0.3)
            print('chat bot :',reply)
            self.conversation.append({'role':'assistant','content':reply})
            if self.if_end(reply):
                self.final_return=self.get_message_completion(self.conversation,temperature=0.1)
                self.conversation.append(self.end_prompt)
                return self.conversation
            else:continue

    def get_json(self):
        reply=self.get_message_completion(self.conversation,temperature=0)
        print("first response:\n",reply)
        # Check if the content starts with '{' to identify JSON output
        if reply.strip().startswith('{'):
            try:
                # Attempt to parse the content as JSON
                order = json.loads(reply)
                # If successful, return the JSON content
                self.final_return= order
            except json.JSONDecodeError:
                # If parsing as JSON fails,let the model's response escond time
                try_again_promt= f" Please provide valid JSON format.\n Response from the model: {reply}"
                self.final_return=json.dumps(self.get_message_completion(try_again_promt))
        
        # Check if the content is an error message
        else:
            self.final_return=reply   
            
        return self.final_return

if __name__ =='__main__':
    chatbot=ChatBot()
    chatbot.chat()
    print(chatbot.get_json())