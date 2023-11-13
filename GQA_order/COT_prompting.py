import openai
import json
import sys 
sys.path.append("../")
from ChatBot import ChatBot#,API_KEY
# api_key = "sk-z2ztez3nzdjRerVojn5LcTSsE5JzXxuDWk3oRHvigO0RzPHV"

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
        self.start_prompt={'role': 'system', 'content':
                            f"""You are a cafe waiter that collects the customer needs and order information for a Starbucks.
                            The user will play the role of a customer.
                            Menu includes:\
                                {self.menu}
                            Please make sure to specify all options, quantities, so that the item is uniquely identifiable from the menu.
                            The ordering conversation should end within 4 inquiries. 
                            
                            Your response should be presented in a brief, very casual and friendly style.
  
                             If you judge that the customer has finished ordering,
                             use the following sentence as the first sentence of your reply:
                             'Ordering is over, I will repeat your order.'
                             The order content should be selected from the menu, and the customer should be asked how many portions are served, hot or cold
                             Now, start a conversation.""",
                             'role': 'assistant', 'content': """Welcome to Starbucks! How can I assist you today?"""
                            }
        self.end_prompt = {'role': 'system', 'content': """The conversation is over.
                         Please process the talk and return the guest's needs in JSON format.
                           Format:
                           {
                           'object': object in the menu
                           'num':num of ordering
                           }
                           """}
    

    
if __name__  == '__main__':
    ORDER_LIST=[]
    order_agent =  OrderAgent()
    order_agent.chat()
    print(order_agent.get_json())