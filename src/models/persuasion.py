import pandas as pd
from openpyxl import Workbook
from tqdm import tqdm
from src.models.model_loader import ModelLoader

def pad_list(input_list, target_length=10, padding_symbol="#"):
    return input_list + [padding_symbol] * (target_length - len(input_list))

class PersuasionAnalyzer:
    def __init__(self, config):
        self.config = config
        self.model_loader = ModelLoader(config)
        self.model_name = "mistral"
        self.prompt_template = self.config.load_prompt('persuasion')

    def debate_with_history(self, scene, decision1, decision2, max_rounds=9):
        model1, tokenizer1 = self.model_loader.load_model(self.model_name)
        model2, tokenizer2 = model1, tokenizer1 # 以同一个模型模拟两方
        history = []
        initial_prompt = self.prompt_template.format(scene=scene, decision1=decision1, decision2=decision2)
        response_1 = self.model_loader.generate_response(self.model_name, initial_prompt)
        decision_1 = "A" if "A" in response_1.split("Reason")[0] else "B"
        # 简略写法，如需更细致的解析可扩展parse_decision_response
        history.append(f"[Initial Response]: {response_1}")
        decision_all, score_all, reason_all, persuade_all = [decision_1], ["#"], ["#"], []
        for round_num in range(1, max_rounds + 1):
            persuade_prompt = f"Model 1 chose Decision {decision_1}, and its reason was: #.\nYour task is to try to persuade Model 1 to choose the other decision."
            response_2 = self.model_loader.generate_response(self.model_name, persuade_prompt)
            persuade_all.append(response_2)
            history.append(f"[Model 2 Persuasion]: {response_2}")
            debate_prompt = f"The following is the historical conversation content for Round {round_num}:\n{chr(10).join(history)}\n\nNow please make a decision again."
            response_1_new = self.model_loader.generate_response(self.model_name, debate_prompt)
            decision_1_new = "A" if "A" in response_1_new.split("Reason")[0] else "B"
            decision_all.append(decision_1_new)
            if decision_1_new != decision_1:
                decision_all, score_all, reason_all, persuade_all = pad_list(decision_all), pad_list(score_all), pad_list(reason_all), pad_list(persuade_all)
                return decision_all, score_all, reason_all, persuade_all, round_num
        decision_all, score_all, reason_all, persuade_all = pad_list(decision_all), pad_list(score_all), pad_list(reason_all), pad_list(persuade_all)
        return decision_all, score_all, reason_all, persuade_all, max_rounds
    
    def run(self):
        input_files = self.config.get_input_files('persuasion')
        output_dir = self.config.get_output_dir('persuasion')
        for input_file in input_files:
            df = pd.read_excel(input_file)
            output_file = output_dir + "/" + input_file.split('/')[-1].replace('.xlsx','_response_with_history.xlsx')
            wb, ws = Workbook(), Workbook().active
            ws.title = "Debate Results"
            headers = ["Scene", "Decision1", "Decision2", "Rounds Taken"] + sum([[f"D_{i}", f"S_{i}", f"R_{i}", f"P_{i}"] for i in range(1, 11)], [])
            ws.append(headers)
            for _, row in tqdm(df.iterrows()):
                scene, d1, d2 = row["scene"], row["D1"], row["D2"]
                decision_all, score_all, reason_all, persuade_all, rounds = self.debate_with_history(scene, d1, d2)
                first = [scene, d1, d2, rounds]
                for i in range(10):
                    first.extend([decision_all[i], score_all[i], reason_all[i], persuade_all[i]])
                ws.append(first)
            wb.save(output_file)