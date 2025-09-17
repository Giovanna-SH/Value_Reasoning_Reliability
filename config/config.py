import yaml
import os
from pathlib import Path

class Config:
    def __init__(self, model_config_path='config/model_config.yaml', data_config_path='config/data_config.yaml'):
        """
        初始化配置类
        
        参数:
            model_config_path (str): 模型配置文件路径
            data_config_path (str): 数据配置文件路径
        """
        self.root_dir = Path(__file__).parent.parent.parent
        
        # 加载模型配置
        model_config_full_path = self.root_dir / model_config_path
        with open(model_config_full_path, 'r') as f:
            self.model_config = yaml.safe_load(f)
            
        # 加载数据配置
        data_config_full_path = self.root_dir / data_config_path
        with open(data_config_full_path, 'r') as f:
            self.data_config = yaml.safe_load(f)
            
        # 创建输出目录
        self.create_output_dirs()
            
    def get_model_config(self, model_name):
        """获取指定模型的配置"""
        if model_name not in self.model_config['models']:
            raise ValueError(f"Model '{model_name}' not found in configuration")
        return self.model_config['models'][model_name]
    
    def get_model_path(self, model_name):
        """获取指定模型的路径"""
        model_config = self.get_model_config(model_name)
        path = model_config['path']
        # 如果路径是相对路径，转换为绝对路径
        if not os.path.isabs(path):
            path = os.path.join(self.root_dir, path)
        return path
    
    def get_input_files(self, module_name):
        """获取指定模块的输入文件列表"""
        if module_name not in self.data_config['input']:
            raise ValueError(f"Input files for '{module_name}' not found in configuration")
        
        files = self.data_config['input'][module_name]
        # 转换为绝对路径
        abs_files = []
        for file_path in files:
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.root_dir, file_path)
            abs_files.append(file_path)
        return abs_files
    
    def get_output_dir(self, module_name):
        """获取指定模块的输出目录"""
        if module_name not in self.data_config['output']:
            raise ValueError(f"Output directory for '{module_name}' not found in configuration")
        
        output_dir = self.data_config['output'][module_name]
        # 转换为绝对路径
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(self.root_dir, output_dir)
        return output_dir
    
    def create_output_dirs(self):
        """创建输出目录"""
        for module_name, output_dir in self.data_config['output'].items():
            if not os.path.isabs(output_dir):
                output_dir = os.path.join(self.root_dir, output_dir)
            os.makedirs(output_dir, exist_ok=True)
            
    def load_prompt(self, prompt_name):
        """加载提示词模板"""
        prompt_path = os.path.join(self.root_dir, 'prompts', f"{prompt_name}.txt")
        if not os.path.exists(prompt_path):
            raise ValueError(f"Prompt file '{prompt_path}' not found")
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        return prompt_template