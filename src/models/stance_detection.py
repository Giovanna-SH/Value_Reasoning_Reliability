import pandas as pd
from openpyxl import Workbook
from src.models.model_loader import ModelLoader

class StanceDetectionAnalyzer:
    def __init__(self, config):
        self.config = config
        self.model_loader = ModelLoader(config)
        self.model_name = "qwen"
        self.prompt_template = self.config.load_prompt('stance_detection')

    def judge(self, scene, d1, d2, response_text):
        prompt = self.prompt_template.format(option1=d1, option2=d2, text=response_text)
        result = self.model_loader.generate_response(self.model_name, prompt, max_new_tokens=20, do_sample=True, top_p=0.9, temperature=0.7)
        # 简化版提取
        if "A" in result:
            return "A"
        elif "B" in result:
            return "B"
        elif "C" in result:
            return "C"
        else:
            return "C"

    def run(self):
        input_files = self.config.get_input_files('stance_detection')
        output_dir = self.config.get_output_dir('stance_detection')
        for input_file in input_files:
            df = pd.read_excel(input_file)
            output_file = output_dir + "/" + input_file.split('/')[-1].replace('.xlsx','_with_preference.xlsx')
            wb = Workbook()
            ws = wb.active
            ws.title = "Results"
            ws.append(["Scene", "D1", "D2", "Model Response", "Preference"])
            for _, row in df.iterrows():
                scene,row_d1,row_d2,resp = row['Scene'], row['D1'], row['D2'], row['Model Response']
                try:
                    pref = self.judge(scene, row_d1, row_d2, resp)
                except Exception as e:
                    pref = "Error"
                ws.append([scene, row_d1, row_d2, resp, pref])
            wb.save(output_file)