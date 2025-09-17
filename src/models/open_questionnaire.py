import pandas as pd
import re
from tqdm import tqdm
from openpyxl import Workbook
from src.models.model_loader import ModelLoader

class OpenQuestionnaireAnalyzer:
    def __init__(self, config):
        self.config = config
        self.model_loader = ModelLoader(config)
        self.model_name = "mistral"
        self.prompt_template = self.config.load_prompt('open_questionnaire')

    def run(self):
        input_files = self.config.get_input_files('open_questionnaire')
        output_dir = self.config.get_output_dir('open_questionnaire')
        for input_file in input_files:
            output_base = output_dir + "/" + input_file.split('/')[-1].replace('.xlsx','')
            df = pd.read_excel(input_file)
            for round_number in range(1, 11):
                wb, ws = Workbook(), Workbook().active
                ws.title = f"Results Round {round_number}"
                ws.append(["Scene", "Model Response"])
                for _, row in tqdm(df.iterrows(), desc=f"Processing Round {round_number}"):
                    scene = row['Q']
                    try:
                        prompt = self.prompt_template.format(scene=scene)
                        resp = self.model_loader.generate_response(self.model_name, prompt, max_new_tokens=100, do_sample=True, top_p=0.9, temperature=0.6)
                        response = resp[len(prompt):].strip()
                        sentences = re.split(r'[.!?]', response)
                        complete_sentences = [s.strip() for s in sentences if s.strip()]
                        if complete_sentences:
                            response = ' '.join(complete_sentences[:5]) + '.'
                        else:
                            response = "No complete sentences generated."
                    except Exception as e:
                        response = f"Error: {e}"
                    ws.append([scene, response])
                wb.save(f"{output_base}_Round_{round_number}.xlsx")