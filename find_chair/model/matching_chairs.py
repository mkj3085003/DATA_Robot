import openai

# 设置你的 OpenAI API 密钥,1$
api_key = "sk-0DTIEOCIY1D6XoafRo8wqBWcqZMf4rmCIxMRKtij8LcQJ3h1"
openai.api_base = "https://openkey.cloud/v1" 
#记录一些可用的1$的apikey
#sk-buhXFrwePhTBLpJNdgDz1EavrFpqmViAgZ9cYhDI4TsWK7o5
#sk-z2ztez3nzdjRerVojn5LcTSsE5JzXxuDWk3oRHvigO0RzPHV
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
    num1="one"
    num2="3"
    num3="1"
    feature1="I came alone, but I was a little sad and don't want others to disturb me. The best seats have a better view."
    feature2="We have a child who may be noisy and would like to sit further away from the crowd, and it would be better if the seat is softer and lower."
    feature3="I'm looking for a girl named Lily"
    messages =[  
    context,#system
    {'role':'assistant', 'content': "Hello, I am the intelligent service robot of TJark Cafe. I am very happy to serve you. How many of you are dining together? "},
    {'role':'user', 'content':num1},
    {'role':'assistant', 'content':'Do you have any seat preference? Such as position, height, material,or avoid the crowd etc.?'},
    {'role':'user', 'content': feature1},
    {'role':'system', 'content':"Create a json summary of the previous talks. \
    To itemize chair requirements, the fields should be 1)Capacity, 2)Location,3)Share,4)Material,5)Height.\
     it is important that each value in json selects the most similar content from the given Chair's features.\
     Chair's features include:\
        Location: 'dont mind';'Near the window';'near the bar'(which means close to the crowd and easy to take an order);'center of the caffe'\
        Share:'dont mind sharing a table';'alone'(which means need a quite enviroment or dont want too be bothered oor bother others)\
        Height: 'high';'low';'dont mind'\
        Material: 'wood';'metal';'sofa';'dont mind'\
        Capacity is of type int which the value is found from the first user's answer of the number of people, and the others are of type str you can find from  the second user's answer .if not mentioned in the talk ,filled the value 'dont mind'"}#system
    ]
    
    response = get_completion_from_messages(messages, temperature=1)
    print('temperature=1:\n',response)
    response = get_completion_from_messages(messages, temperature=0.5)
    print('temperature=0.5:\n',response)
    response = get_completion_from_messages(messages, temperature=0)
    print('temperature=0:\n',response)

    messages1 =[  
    context,#system
    {'role':'assistant', 'content': "Hello, I am the intelligent service robot of TJark Cafe. I am very happy to serve you. How many of you are dining together? "},
    {'role':'user', 'content':num2},
    {'role':'assistant', 'content':'Do you have any seat preference? Such as position, height, material,or avoid the crowd etc.?'},
    {'role':'user', 'content': feature2},
    {'role':'system', 'content':"Create a json summary of the previous talks. \
    To itemize chair requirements, the fields should be 1)Capacity, 2)Location,3)Share,4)Material,5)Height.\
     it is important that each value in json selects the most similar content from the given Chair's features.\
     Chair's features include:\
        Location: 'dont mind';'Near the window';'near the bar';'center of the caffe'\
        Share:'dont mind sharing a table';'alone'\
        Height: 'high';'low';'dont mind'\
        Material: 'wood';'metal';'sofa';'dont mind'\
        Capacity is of type int which the value is found from the first user's answer of the number of people, and the others are of type str you can find from  the second user's answer .if not mentioned in the talk ,filled the value 'dont mind'"}#system
    ]
    response = get_completion_from_messages(messages1, temperature=1)
    print('temperature=1:\n',response)
    response = get_completion_from_messages(messages1, temperature=0.5)
    print('temperature=0.5:\n',response)
    response = get_completion_from_messages(messages1, temperature=0)
    print('temperature=0:\n',response)
    messages2 =[  
    context,#system
    {'role':'assistant', 'content': "Hello, I am the intelligent service robot of TJark Cafe. I am very happy to serve you. How many of you are dining together? "},
    {'role':'user', 'content':num3},
    {'role':'assistant', 'content':'Do you have any seat preference? Such as position, height, material,or avoid the crowd etc.?'},
    {'role':'user', 'content': feature3},
    {'role':'system', 'content':"\
     At the very beginning, you have to determine his intention during the conversation. \
     If he is not here for dinner, please return an ERROR and politely reject his request.\
    else,\
     Create a json summary of the previous talks. \
    To itemize chair requirements, the fields should be 1)Capacity, 2)Location,3)Share,4)Material,5)Height.\
     it is important that each value in json selects the most similar content from the given Chair's features.\
     Chair's features include:\
        Location: 'dont mind';'Near the window';'near the bar';'center of the caffe'\
        Share:'dont mind sharing a table';'alone'\
        Height: 'high';'low';'dont mind'\
        Material: 'wood';'metal';'sofa';'dont mind'\
        Capacity is of type int which the value is found from the first user's answer of the number of people, and the others are of type str you can find from  the second user's answer .if not mentioned in the talk ,filled the value 'dont mind'.and you should judge the intention "}#system
    ]
    response = get_completion_from_messages(messages2, temperature=1)
    print('temperature=1:\n',response)
    response = get_completion_from_messages(messages2, temperature=0.5)
    print('temperature=0.5:\n',response)
    response = get_completion_from_messages(messages2, temperature=0)
    print('temperature=0:\n',response)