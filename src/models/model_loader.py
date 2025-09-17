import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import yaml
import os

class ModelLoader:
    def __init__(self, config):
        """
        初始化模型加载器
        
        参数:
            config: 配置对象
        """
        self.config = config
        self.models = {}
        self.tokenizers = {}
        
    def get_device(self, model_name):
        """获取指定模型的设备配置"""
        device_name = self.config.get_model_config(model_name).get('device', 'cuda')
        if device_name == 'cuda' and not torch.cuda.is_available():
            device_name = 'cpu'
        return torch.device(device_name)
    
    def load_model(self, model_name):
        """
        加载指定的模型和分词器
        
        参数:
            model_name (str): 模型名称，必须在配置文件中定义
            
        返回:
            tuple: (model, tokenizer)
        """
        if model_name in self.models and model_name in self.tokenizers:
            return self.models[model_name], self.tokenizers[model_name]
        
        model_config = self.config.get_model_config(model_name)
        model_path = self.config.get_model_path(model_name)
        device = self.get_device(model_name)
        trust_remote_code = model_config.get('trust_remote_code', False)
        
        print(f"Loading model {model_name} from {model_path} to {device}")
        
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype="auto",
            device_map=device.type,
            trust_remote_code=trust_remote_code
        )
        
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Cache models and tokenizers
        self.models[model_name] = model
        self.tokenizers[model_name] = tokenizer
        
        return model, tokenizer
        
    def generate_response(self, model_name, prompt, max_new_tokens=512, **kwargs):
        """
        使用指定模型生成回答
        
        参数:
            model_name (str): 模型名称
            prompt (str): 提示词
            max_new_tokens (int): 生成的最大token数量
            
        返回:
            str: 生成的回答
        """
        model, tokenizer = self.load_model(model_name)
        device = self.get_device(model_name)
        
        message = [{"role": 'user', 'content': prompt}]
        
        text = tokenizer.apply_chat_template(
            message,
            tokenize=False,
            add_generation_prompt=False
        )
        
        model_inputs = tokenizer([text], return_tensors="pt").to(device)
        
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=max_new_tokens,
            **kwargs
        )
        
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        # 清理GPU缓存
        if device.type == 'cuda':
            torch.cuda.empty_cache()
            
        return response.strip()