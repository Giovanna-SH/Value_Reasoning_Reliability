import pandas as pd
from openpyxl import Workbook
from tqdm import tqdm
from src.models.model_loader import ModelLoader

def pad_list(input_list, target_length=10, padding_symbol="#"):
    return input_list + [padding_symbol] * (target_length - len(input_list))

class PersuasionQuestionnaireAnalyzer:
    def __init__(self, config):
        self.config = config
        self.model_loader = ModelLoader(config)
        self.model_name = "mistral"
        self.prompt_template = self.config.load_prompt('persuasion_questionnaire')

    def debate_with_history(self, q, op, max_rounds=9):
        model1, _ = self.model_loader.load_model(self.model_name)
        history = [f"[Question]: {self.prompt_template.format(question=q, options=op)}"]
        response_1 = self.model_loader.generate_response(self.model_name, history[0])
        decision_1 = response_1 if "Option" in response_1 else "#"
        decision_all = [decision_1]; score_all = ["#"]; reason_all = ["#"]; persuade_all = []
        for round_num in range(1, max_rounds + 1):
            persuade_prompt = f"Model 1 chose: {decision_1}. Try to persuade Model 1 to change."
            response_2 = self.model_loader.generate_response(self.model_name, persuade_prompt)
            persuade_all.append(response_2)
            history.append(f"Round {round_num} Persuasion: {response_2}")
            debate_prompt = f"The following conversation history:\n{chr(10).join(history)}\nPlease make a decision again."
            response_1_new = self.model_loader.generate_response(self.model_name, debate_prompt)
            decision_all.append(response_1_new)
            if response_1_new != decision_1:
                return pad_list(decision_all), pad_list(score_all), pad_list(reason_all), pad_list(persuade_all), round_num
        return pad_list(decision_all), pad_list(score_all), pad_list(reason_all), pad_list(persuade_all), max_rounds

    def run(self):
        input_files = self.config.get_input_files('persuasion_questionnaire')
        output_dir = self.config.get_output_dir('persuasion_questionnaire')
        for input_file in input_files:
            df = pd.read_excel(input_file)
            output_file = output_dir + "/" + input_file.split('/')[-1].replace('.xlsx','_response_with_history.xlsx')
            wb, ws = Workbook(), Workbook().active
            ws.title = "Debate Results"
            headers = ["Q","A", "Rounds Taken"] + sum([[f"D_{i}", f"S_{i}", f"R_{i}", f"P_{i}"] for i in range(1, 11)], [])
            ws.append(headers)
            for _, row in tqdm(df.iterrows()):
                qes, options = row.iloc[0], row.iloc[1]
                decision_all, score_all, reason_all, persuade_all, rounds = self.debate_with_history(qes, options)
                first = [qes, options, rounds]
                for i in range(10):
                    first.extend([decision_all[i], score_all[i], reason_all[i], persuade_all[i]])
                ws.append(first)
            wb.save(output_file)