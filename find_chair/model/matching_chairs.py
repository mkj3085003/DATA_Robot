import openai

# 设置你的 OpenAI API 密钥,1$
api_key = "sk-0DTIEOCIY1D6XoafRo8wqBWcqZMf4rmCIxMRKtij8LcQJ3h1"
openai.api_base = "https://openkey.cloud/v1" 
#sk-buhXFrwePhTBLpJNdgDz1EavrFpqmViAgZ9cYhDI4TsWK7o5
#https://openkey.cloud
# 初始化 OpenAI 客户端
openai.api_key = api_key

context = {'role':'system', 'content':"""
You are a cafe waiter robot that automatically collects order information for a pizza restaurant.
you want:
     1. First, greet the customers and how many people are dining there.
     2. Then, wait for the user to reply to collect the number of diners and the customer's seating tendency and preferences.
     3. After collecting the information, you need to streamline and process the information, and output the num+feature-description of the chair in json format.
     4. Finally reply to the location of the best matching chair retrieved by the customer, ask the customer if they are satisfied, and indicate that you will lead them to the chair and ask them to follow you.

Please make sure to identify all chair characteristics and location information so that the match can be identified from existing chairs in the cafe.
Your response should be presented in a brief, very casual and friendly style.

When the customer's answer fails to match the content, please return an error and politely reject the customer's request.
"""}  # accumulate messages

promt=""
# 用户输入的问题
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
        temperature=temperature, # 控制模型输出的随机程度
    )
    return response.choices[0].message["content"]

if __name__ == '__main__':
    messages =[  
    context,#system
    {'role':'assistant', 'content': "Hello, I am the intelligent service robot of TJark Cafe. I am very happy to serve you. How many of you are dining together? "},
    {'role':'user', 'content':'There are 3 of us'},
    {'role':'assistant', 'content':'Do you have any seat preference? Such as position, height, material, etc.?'},
    {'role':'user', 'content': "We have a child who may be noisy and would like to sit further away from the crowd, and it would be better if the seat is softer and lower."},
    {'role':'user', 'content':"Create a json summary of the previous talks. \
    To itemize chair requirements, the fields should be 1) Capacity, 2) location ,3) material, 4) height.\
     it is important that each value in json selects the most similar content from the given Chair's features.\
     Chair's features include:\
        Location: Near the window, near the bar\
        Material: wood, metal, sofa\
        Capacity: num of people\
        Height: high, low\
        Capacity is of type int which the value is found from the first user's answer of the number of people, and the others are of type str you can faind from  the second user's answer .\
        for example\
        "}#system
    ]
    response = get_completion_from_messages(messages, temperature=1)
    print('temperature=1:\n',response)
    response = get_completion_from_messages(messages, temperature=0)
    print('temperature=0:\n',response)