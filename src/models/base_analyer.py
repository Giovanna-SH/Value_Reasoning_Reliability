from abc import ABC, abstractmethod
import os
import pandas as pd
from openpyxl import Workbook
from tqdm import tqdm

class BaseAnalyzer(ABC):
    """分析器基类，定义了所有分析器的通用接口和方法"""
    
    def __init__(self, config):
        """
        初始化分析器
        
        参数:
            config: 配置对象
        """
        self.config = config
        self.model_name = self.get_model_name()
        self.input_type = self.get_input_type()
        self.output_type = self.get_output_type()
        
    @abstractmethod
    def get_model_name(self):
        """返回此分析器使用的模型名称"""
        pass
    
    @abstractmethod
    def get_input_type(self):
        """返回此分析器的输入类型标识"""
        pass
    
    @abstractmethod
    def get_output_type(self):
        """返回此分析器的输出类型标识"""
        pass
    
    @abstractmethod
    def process_file(self, input_file, output_file, round_number=1):
        """
        处理单个文件
        
        参数:
            input_file (str): 输入文件路径
            output_file (str): 输出文件路径
            round_number (int): 当前轮次
        """
        pass
    
    def run(self, input_files=None, output_dir=None, rounds=10):
        """
        运行分析器
        
        参数:
            input_files (list): 输入文件路径列表，如果为None则使用配置文件中的设置
            output_dir (str): 输出目录，如果为None则使用配置文件中的设置
            rounds (int): 运行轮数
        """
        if input_files is None:
            input_files = self.config.get_input_files(self.input_type)
        
        if output_dir is None:
            output_dir = self.config.get_output_dir(self.output_type)
        
        os.makedirs(output_dir, exist_ok=True)
        
        for input_file in input_files:
            file_name = os.path.basename(input_file)
            base_name = os.path.splitext(file_name)[0]
            
            for round_num in range(1, rounds + 1):
                output_file = os.path.join(output_dir, f"{base_name}_Round_{round_num}.xlsx")
                print(f"Processing {input_file}, round {round_num}/{rounds}")
                self.process_file(input_file, output_file, round_num)