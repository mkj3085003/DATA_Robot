import openai
import json
# 设置你的 OpenAI API 密钥,1$
api_key = "sk-z2ztez3nzdjRerVojn5LcTSsE5JzXxuDWk3oRHvigO0RzPHV"
openai.api_base = "https://openkey.cloud/v1"
openai.api_key = api_key 
#记录一些可用的1$的apikey

#4. Finally reply to the location of the best matching chair retrieved by the customer, ask the customer if they are satisfied, and indicate that you will lead them to the chair and ask them to follow you.
prompt_front = {'role':'system', 'content':"""
You are a cafe waiter robot that automatically collects seat order information for a Starbucks. Follow these steps to collect and format the seat order:

1. Start by greeting the customers and asking how many people are dining together.
2. Wait for the user to reply with the number of diners and their seating preferences, including details such as location, sharing, height, material, and any special requests.
3. After collecting the information, you need to process it and output the seat order in JSON format. The JSON format should include the following fields:
   - Capacity (An integer value, conclude from the first user's reply)
   - Location (options: 'dont mind', 'Near the window', 'near the bar', 'center of the cafe')
   - Share (options: 'dont mind sharing a table', 'alone')
   - Height (options: 'high', 'low', 'dont mind')
   - Material (options: 'wood', 'metal', 'sofa', 'dont mind')

4. If any of the information is missing in the user's response, fill it with 'dont mind'.

Please ensure that each value in the JSON is selected from the most similar content given in the customer's response. You can find these values in the customer's reply.

When the customer's answer does not match the available options or is unclear, respond with a statement starting with "ERROR:" and politely request clarifications.

Your response should be in one of two formats:
1. A JSON file containing the seat order.without other words.
    for example:
        {'Capacity': 1, 'Location': 'Near the window', 'Share': 'alone', 'Height': 'dont mind', 'Material': 'dont mind'}
2. An error message when the customer's response cannot be understood.
    for example:
        "ERROR: we don't have hotpot"

"""}  # accumulate messages 
#Capacity (An integer value, inferred from the first user's reply)，inferred 会增加回复的时间

first_ask={'role':'assistant', 'content': "Hello, I am the intelligent service robot of TJark Cafe. I am very happy to serve you. How many of you are dining together? "}
second_ask={'role':'assistant', 'content':'Do you have any seat preference? Such as position, height, material,or avoid the crowd etc.?'}
prompt_end={'role':'system', 'content':"conversation is end.please return the json"}


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # 控制模型输出的随机程度
    )
    return response.choices[0].message["content"]

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature  # Control the randomness of model output
    )
    content = response.choices[0].message['content']
    print("first response:\n",content)
    # Check if the content starts with '{' to identify JSON output
    if content.strip().startswith('{'):
        try:
            # Attempt to parse the content as JSON
            seat_order = json.loads(content)
            # If successful, return the JSON content
            return seat_order
        except json.JSONDecodeError:
            # If parsing as JSON fails,let the model's response escond time
            error_message = f" Please provide valid JSON format.\n Response from the model: {content}"
            second_reply=json.loads(get_completion(error_message))
            return second_reply
    
    # Check if the content is an error message
    else:   return content

    # If the content doesn't match either format, return an error message
    # return "Error: Unable to process the request. Please provide valid information."
    # return content
    

if __name__ == '__main__':
    
    ORDER_LIST=[]
    with open("data_order.json", 'r') as json_file:
        ORDER_DATA_FILE = json_file.read()
        ORDER_LIST = json.loads(ORDER_DATA_FILE)
    # 打开JSON文件并加载数据
    
    for i in range(len(ORDER_LIST)): #慎用GPTkey余额有限
    # for i in range(5):
        message =[  
        prompt_front,first_ask,
        {'role':'user', 'content':ORDER_LIST[i]["num"]},
        second_ask,
        {'role':'user', 'content': ORDER_LIST[i]["need"]},
        prompt_front #system
        ]
        # print(ORDER_LIST[i])
        print('Iterate',i )
        response = get_completion_from_messages(message, temperature=0.3)
        print('proceed resopnse:\n',response)
