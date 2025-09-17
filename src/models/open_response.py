import pandas as pd
import re
from tqdm import tqdm
from openpyxl import Workbook
from src.models.model_loader import ModelLoader

class OpenResponseAnalyzer:
    def __init__(self, config):
        self.config = config
        self.model_loader = ModelLoader(config)
        self.model_name = "qwen"

    def generate_response(self, scene, d1, d2, prompt_template):
        prompt = prompt_template.format(scene=scene, option1=d1, option2=d2)
        return self.model_loader.generate_response(self.model_name, prompt, max_new_tokens=100, do_sample=True, top_p=0.9, temperature=0.6)
    
    def process_file(self, input_file, output_file, prompt_template, round_number=1):
        df = pd.read_excel(input_file)
        wb = Workbook()
        ws = wb.active
        ws.title = f"Results Round {round_number}"
        ws.append(["Scene", "D1", "D2", "Model Response"])
        for _, row in tqdm(df.iterrows(), desc=f"Processing Round {round_number}"):
            scene, d1, d2 = row['scene'], row['D1'], row['D2']
            try:
                resp = self.generate_response(scene, d1, d2, prompt_template)
                response = resp[len(prompt_template.format(scene=scene, option1=d1, option2=d2)):].strip()
                sentences = re.split(r'[.!?]', response)
                complete_sentences = [s.strip() for s in sentences if s.strip()]
                if complete_sentences:
                    response = ' '.join(complete_sentences[:5]) + '.'
                else:
                    response = "No complete sentences generated."
            except Exception as e:
                response = f"Error generating response: {e}"
            ws.append([scene, d1, d2, response])
        wb.save(output_file)

    def run(self):
        prompt_template = self.config.load_prompt('open_response')
        input_files = self.config.get_input_files('open_response')
        output_dir = self.config.get_output_dir('open_response')
        for input_file in input_files:
            output_base = output_dir + "/" + input_file.split('/')[-1].replace('.xlsx','')
            for r in range(1, 11):
                self.process_file(input_file, f"{output_base}_Round_{r}.xlsx", prompt_template, r)