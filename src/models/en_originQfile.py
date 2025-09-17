'''
程序会把excel文件表格中的所有数据，形成要输入大模型的对应的所有prompt，输出到一个json文件中
使用时替换main函数中的两个文件名即可。
注意运行成功后，要打开json文件大体看下每条prompt内容是否正确。
这个程序运行成功后，且内容正确后，就不需要运行这个程序了。
后续调用大模型的程序即可。
'''

import pandas as pd
import re
from tqdm import tqdm
from openpyxl import Workbook
import json

def xlsx_to_prompt(file_name_input,file_json):
    # 读取 Excel 文件
    df = pd.read_excel(file_name_input)

    # 初始化一个空的字典来存储 prompts
    prompts_dict = {}

    # 遍历每一行，生成对应的 prompt
    for index, row in df.iterrows():
        context = row['Q']  
        option = row['A'] 
        
        prompt=f'''Input："Question":{context} "Option":{option}
                Output：?
                Note: '1.You must select only one option!You only need to answer with numbers! '2.give your reason why you choose this option which should be less than two sentences. '3.You must answer in English.'4.Please answer in the following format: "I choose Option ...; My confidence score is ... points; My reason is ...".'5.For examples:I choose Option 1; My confidence score is 0.5 points; My reason is that family is the fundamental unit of society.'''
            #code时候将示例进行了修改    

            # 使用部属模型生成回答
        messages = [
                {"role": "system", "content": "You need to select one option from the choices based on the question described,and indicate your confidence scores which are how firm you are in choosing this option, which ranging from 0 to 1, where 0 represents complete uncertainty and 1 represents complete certainty."},
                {"role": "user", "content": prompt}
            ]
        # 将 messages 添加到字典中
        prompts_dict[f'message_{index}'] = messages

    # 将字典转换为 JSON 格式并保存到文件
    with open(file_json, 'w', encoding='utf-8') as f:
        json.dump(prompts_dict, f,ensure_ascii=False,indent=4)


def main():
     # 读取Excel文件
    file_name_input = r''  # 替换为你的Excel文件名
    file_json=r''
    xlsx_to_prompt(file_name_input,file_json)
    print("The prompt file is formed!")

if __name__ == "__main__":
    main()