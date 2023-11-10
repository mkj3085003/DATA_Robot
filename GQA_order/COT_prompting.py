import openai
import json

api_key = "sk-z2ztez3nzdjRerVojn5LcTSsE5JzXxuDWk3oRHvigO0RzPHV"
#加入chain of thought 激发大模型的推理能力。
openai.api_base = "https://openkey.cloud/v1"
prompt_start={'role':'system','content':"""
You are a cafe waiter robot. Please follow the steps below to assist customers in ordering until the customer indicates that they no longer need the service and returns the collected order information:
1. After the customer places an order, tell the customer the menu information
2. Talk to the customer and ask about their ordering preferences and preferences until the customer says they no longer need the service.
3. Collect information and process it, and output the order information in JSON format.
The JSON format should contain the following fields: "object", "num", "prefrence"
The menu is as follows:

"""}
class OrderAgent():
    def __init__(self,menu_path="../VLN_find_chair/data/data_object.json") -> None:
        with open(menu_path, 'r') as json_file:
            MENU_FILE = json_file.read()
            MENU = json.loads(MENU_FILE)
        self.menu=MENU['food']
    

    
if __name__  == '__main__':
    ORDER_LIST=[]
    

    run()