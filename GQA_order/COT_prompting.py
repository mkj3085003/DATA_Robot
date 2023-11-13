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
#多任务，多轮对话理解与记忆
class OrderAgent(ChatBot):
    def __init__(self,menu_path="data_object.json") -> None:
        super().__init__()
        with open(menu_path, 'r') as json_file:
            MENU_FILE = json_file.read()
            MENU = json.loads(MENU_FILE)
        self.menu=MENU['food']
        self.conversation = []
                            #角色+任务+注意事项/实现细节+
        self.start_prompt={'role': 'system', 'content':
                            f"""You are an ordering robot that automatically collects order information for cafe.The user is a customer.
                            the menu from caffe is:{self.menu}
                            Follow these steps to collect and format the order:
                            1. greet and offer him the menu.
                            2. ask him for the item and number he want to order.options of item must from menu.
                            Please make sure to specify all options, quantities, so that the item is uniquely identifiable from the menu.
                            Your response should be presented in a brief, very casual and friendly style. 
                            """,
                            'role': 'assistant', 'content': """It's my pleasure to serve you. What would you like to order? here is the menu"""
                            }
        self.conversation.append(self.start_prompt)
        self.end_prompt = {'role': 'system', 'content': """The conversation is over.
                         Please process the talk and return all the guest's needs in JSON format.
                           Format:
                           [{
                           'object': (options:'Cake', 'Walnut', 'Mangosteen', 'SourMilkDrink', 'Banana', 'Bernachon', 'Date', 'HamSausage', 'SesameSeedCake', 'Watermelon', 'NFCJuice', 'Dunian', 'StickyNotes', 'Garlic', 'TeaTray', 'Bread', 'SpringWater', 'Softdrink', 'Gum', 'Apple', 'CoconutMilk', 'YogurtDrink', 'Yogurt', 'MilkDrink', 'OrangeJuice', 'Coffee', 'ADMilk', 'CoconutWater', 'Orange', 'CandyCase', 'Chips', 'TennisBall', 'Milk')
                           'num':number of the objects
                           }
                           ]
                           for example:
                            user:I want a glass of milk and a OrangeJuice for my daughter.
                            return json:[{
                            "object" : "Milk",
                            "num" : 1
                            },
                            {
                            "object" : "OrangeJuice"
                            "num" : 1
                            }]
                           Please ensure that each value in the JSON is selected from the most similar content given in the customer's response. You can find these values in the customer's reply.
                           """}
    
    def if_end(self):
        input = str(self.conversation)#判断是否结束对话
        prompt=[{'role':'user','content':f"""{input}
                Please check whether the user's information in the above conversation contains food items and the corresponding quantity. If so, answer me "True", otherwise reply "False"."""
                }]
        ifend = self.get_message_completion(prompt)
        print("if end:",ifend)
        if ifend.lower().strip() == "true":
            return True
        else:
            return False
        
    def if_menu(self):
        input = str(self.conversation)#判断是否结束对话
        prompt=[{'role':'user','content':f"""{input}
                Please check whether the user's information in the above conversation contains food items comes from the options:'Cake', 'Walnut', 'Mangosteen', 'SourMilkDrink', 'Banana', 'Bernachon', 'Date', 'HamSausage', 'SesameSeedCake', 'Watermelon', 'NFCJuice', 'Dunian', 'StickyNotes', 'Garlic', 'TeaTray', 'Bread', 'SpringWater', 'Softdrink', 'Gum', 'Apple', 'CoconutMilk', 'YogurtDrink', 'Yogurt', 'MilkDrink', 'OrangeJuice', 'Coffee', 'ADMilk', 'CoconutWater', 'Orange', 'CandyCase', 'Chips', 'TennisBall', 'Milk'. If so, answer me "True", otherwise reply "False"."""
                }]
        ifmenu = self.get_message_completion(prompt)
        print("if menu:",ifmenu )
        if ifmenu.lower().strip() == "true":
            return True
        else:
            if self.conversation :
                self.conversation.append({'role':'system','content':f"the ordering is not on the menu.offer him the menu again and let him choose from the menu and tell the quantities,menu is {self.menu}."})
                reply = self.get_message_completion(self.conversation, temperature=0.1)
                self.conversation.append({'role': 'assistant', 'content': reply})
                print('order bot:', reply)
            return False

        
    def chat(self,temp):
        count=0
        while True:
            # 用户输入
            if( self.if_end() and self.if_menu() and count>2) or count > 5:#限制对话强制小于5轮不然说个没完没了.
                print("===============Order corversation is over===============")
                # 结束对话
                self.conversation.append(self.end_prompt)
                return self.conversation
            else:
                input_from_user = str(input("user:"))
                # self.user.append({'role': 'user', 'content': input_from_user})
                self.conversation.append({'role': 'user', 'content': input_from_user})

                # 模型回复
                reply = self.get_message_completion(self.conversation, temperature=temp)
                self.conversation.append({'role': 'assistant', 'content': reply})
                count += 1
                print('order bot:', reply)
                # 判断是否结束对话
                
    

    
if __name__  == '__main__':
    ORDER_LIST=[]
    order_agent =  OrderAgent()
    print(f"order bot: It's my pleasure to serve you. What would you like to order? Here is our menu \n{order_agent.menu}")
    order_agent.chat(temp=0)
    print(order_agent.get_json())