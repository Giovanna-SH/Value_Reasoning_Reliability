import json
import re
import torch
import torch.nn.functional as F
from openpyxl import Workbook
from tqdm import tqdm
from src.models.model_loader import ModelLoader

class BinaryDecisionAnalyzer:
    def __init__(self, config):
        self.config = config
        self.model_loader = ModelLoader(config)
        self.model_name = "qwen"

    def calculate_option_probabilities(self, model, tokenizer, model_inputs):
        options = ["A", "B"]
        option_tokens = [tokenizer.encode(option, return_tensors="pt")[0][0] for option in options]
        with torch.no_grad():
            output = model(model_inputs['input_ids'], output_hidden_states=True, return_dict=True)
            logits = output.logits[:, -1, :]
            probs = F.softmax(logits, dim=-1)[0]
        option_probs = {option: probs[token.item()].item() for option, token in zip(options, option_tokens)}
        total_prob = sum(option_probs.values())
        option_probs = {option: prob / total_prob for option, prob in option_probs.items()}
        return option_probs

    def response_to_list(self, response_content, option_probs):
        pattern = r"I choose (\d); my confidence score is ([\d\.]+) points; I choose Option (1|2), my confidence score is ([\d\.]+) points; My reason is (.+)"
        match = re.search(pattern, response_content)
        if match:
            value_choice = match.group(1)
            value_confidence_score = match.group(2)
            option_choice = match.group(3)
            option_confidence_score = match.group(4)
            reason = match.group(5)
            return [
                value_choice, value_confidence_score, option_choice, option_confidence_score, reason,
                option_probs.get(option_choice, "#"), str(option_probs)
            ]
        else:
            return ["#", "#", "#", "#", response_content, "#", str(option_probs)]

    def process_file(self, input_file, output_file, prompt_template, round_number=1):
        model, tokenizer = self.model_loader.load_model(self.model_name)
        device = self.model_loader.get_device(self.model_name)
        with open(input_file, 'r') as f:
            data_list = json.load(f)
        wb = Workbook()
        ws = wb.active
        ws.title = "Results"
        headers = [
            "Value Choice", "Value Confidence Score", "Option Choice", "Option Confidence Score",
            "Reason", "Option_choose Probability", "Option_all Probability"
        ]
        ws.append(headers)
        for _, message in tqdm(data_list.items(), desc=f"Processing Round {round_number}"):
            try:
                text = tokenizer.apply_chat_template(
                    message, tokenize=False, add_generation_prompt=False
                )
                model_inputs = tokenizer([text], return_tensors="pt").to(device)
                generated_ids = model.generate(**model_inputs, max_new_tokens=512)
                generated_ids = [
                    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
                ]
                option_probs = self.calculate_option_probabilities(model, tokenizer, model_inputs)
                response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                row_data = self.response_to_list(response, option_probs)
            except Exception as e:
                row_data = ["#", "#", "#", "#", f"Error:{e}", "#", "#"]
            ws.append(row_data)
        wb.save(output_file)

    def run(self):
        prompt_template = self.config.load_prompt('binary_decision')
        input_files = self.config.get_input_files('binary_decision')
        output_dir = self.config.get_output_dir('binary_decision')
        for input_file in input_files:
            output_base = output_dir + "/" + input_file.split('/')[-1].replace('.json','')
            for r in range(1, 11):
                self.process_file(input_file, f"{output_base}_Round_{r}.xlsx", prompt_template, r)