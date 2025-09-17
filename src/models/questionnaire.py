import pandas as pd
import re
import json
from tqdm import tqdm
from openpyxl import Workbook
from src.models.model_loader import ModelLoader

class QuestionnaireAnalyzer:
    def __init__(self, config):
        self.config = config
        self.model_loader = ModelLoader(config)
        self.model_name = "llama"
        self.prompt_template = self.config.load_prompt('questionnaire')

    def response_to_list(self, response_content):
        idx = response_content.find("I choose")
        part_content = response_content[idx:]
        pattern = r"I choose Option (\d+); My confidence score is ([\d\.\-]+)[\s\S]*?My reason is(.+)"
        match = re.search(pattern, part_content)
        if match:
            return [match.group(1), match.group(2), match.group(3), response_content]
        else:
            return ["#", "#", part_content, response_content]

    def run(self):
        input_files = self.config.get_input_files('questionnaire')
        output_dir = self.config.get_output_dir('questionnaire')
        for input_file in input_files:
            output_base = output_dir + "/" + input_file.split('/')[-1].replace('.json','')
            with open(input_file, 'r') as f:
                data_list = json.load(f)
            for round_number in range(1, 11):
                wb, ws = Workbook(), Workbook().active
                ws.title = "Results"
                ws.append(['option_choose', 'option_score', 'Reason', 'Response_content'])
                for _, message in tqdm(data_list.items(), desc=f"Processing Round {round_number}"):
                    prompt = self.prompt_template.format(**message)
                    try:
                        resp = self.model_loader.generate_response(self.model_name, prompt, max_new_tokens=512)
                        row_data = self.response_to_list(resp)
                    except Exception as e:
                        row_data = ["#", "#", "#", str(e)]
                    ws.append(row_data)
                output_file = f"{output_base}_Round_{round_number}.xlsx"
                wb.save(output_file)