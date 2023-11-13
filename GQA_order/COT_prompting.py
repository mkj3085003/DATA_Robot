import openai
import json
import sys 
sys.path.append("../")
from ChatBot import ChatBot#,API_KEY
# api_key = "sk-z2ztez3nzdjRerVojn5LcTSsE5JzXxuDWk3oRHvigO0RzPHV"
API_KEY = "sk-z2ztez3nzdjRerVojn5LcTSsE5JzXxuDWk3oRHvigO0RzPHV"
#22:00领取可用：
#sk-Nqaedek5GkD6fC9SVyMwVTCEVeSIh5WB9EhQjAFWqjNdOZ0R
#sk-qoXUG1ZD6BI2Lkfov8fOir8bI1dJkTd9hgEZhrHskejp15eM
#sk-GTM6iyTPm0ALZaUUZL5Dq2LuKTHv6Qm01s4TNBAh6ACAsUM2
#sk-eQcx5qelSmgk6DhEKPGgNJ5IZvaWfPrF8mat2QWRomcPLGls
#sk-BCZt1tS0b1Q0bCIN1SPLpBNyFKLggQwkEfdhizw5iolDXywJ
#sk-72xe4WItoRtddjKK2Vjl0SD06c1OQ3ee1ZbHKTXKj4n5CrpS

openai.api_key = API_KEY
openai.api_base = "https://openkey.cloud/v1"
# openai.api_base = "https://openkey.cloud/v1"
prompt_start={'role':'system','content':"""
You are a cafe waiter robot. Please follow the steps below to assist customers in ordering until the customer indicates that they no longer need the service and returns the collected order information:
1. After the customer places an order, tell the customer the menu information
2. Talk to the customer and ask about their ordering preferences and preferences until the customer says they no longer need the service.
3. Collect information and process it, and output the order information in JSON format.
The JSON format should contain the following fields: "object", "num", "prefrence"
The menu is as follows:

"""}
class OrderAgent(ChatBot):
    def __init__(self,menu_path="data_object.json") -> None:
        super().__init__()
        with open(menu_path, 'r') as json_file:
            MENU_FILE = json_file.read()
            MENU = json.loads(MENU_FILE)
        self.menu=MENU['food']
        self.conversation = []
        self.final_return = []
                            #角色+任务+注意事项/实现细节+
        self.start_prompt={'role': 'system', 'content':
                            f"""You are an ordering robot that automatically collects order information for cafe.The user is a customer.
                            the menu from cafe includes:\
                                {self.menu}

                            there are three things you need to do:
                            First, greet with the customerand offer him the menu.
                            Second, ask him for the item and number he want to order.
                            Last,return a json file of the order.
                            
                            Please make sure to specify all options, quantities, so that the item is uniquely identifiable from the menu.
                            The ordering conversation should end within 4 inquiries. 
                            
                            there are also three things you need pay attentions to:
                            1. Your response should be presented in a brief, very casual and friendly style.
                            2. If you judge that the customer has finished ordering,use the following sentence as the first sentence of your reply:
                            'Ordering is over, I will repeat your order.' 
                            3. The order item should be selected from the menu.
                            4. The ordering conversation should end within 4 inquiries
                            
                            """,
                            'role': 'assistant', 'content': """It's my pleasure to serve you. What would you like to order? here is the menu \n {self.menu}"""
                            }
        self.conversation.append(self.start_prompt)
        self.end_prompt = {'role': 'system', 'content': """The conversation is over.
                         Please process the talk and return the guest's needs in JSON format.
                           Format:
                           {
                           'object': item in the menu
                           'num':num of ordering
                           }
                           """}
    

    
if __name__  == '__main__':
    ORDER_LIST=[]
    order_agent =  OrderAgent()
    print(f"order bot: It's my pleasure to serve you. What would you like to order? Here is our menu \n{order_agent.menu}")
    order_agent.chat(temp=0)
    print(order_agent.get_json())