import argparse
import os
import sys
from pathlib import Path

# 将项目根目录添加到系统路径
sys.path.append(str(Path(__file__).parent.parent))

from src.config.config import Config
from src.models.binary_decision import BinaryDecisionAnalyzer
from src.models.open_response import OpenResponseAnalyzer
from src.models.persuasion import PersuasionAnalyzer
from src.models.questionnaire import QuestionnaireAnalyzer
from src.models.open_questionnaire import OpenQuestionnaireAnalyzer
from src.models.persuasion_questionnaire import PersuasionQuestionnaireAnalyzer
from src.models.stance_detection import StanceDetectionAnalyzer

def main():
    parser = argparse.ArgumentParser(description='价值决策分析系统')
    parser.add_argument('--mode', type=str, required=True, 
                        choices=['binary', 'open', 'persuasion', 'questionnaire', 
                                'open_questionnaire', 'persuasion_questionnaire', 'stance'],
                        help='分析模式')
    parser.add_argument('--config', type=str, default='config/model_config.yaml',
                        help='模型配置文件路径')
    parser.add_argument('--data', type=str, default='config/data_config.yaml',
                        help='数据配置文件路径')
    parser.add_argument('--rounds', type=int, default=10,
                        help='运行轮数')
    parser.add_argument('--input', type=str, default=None,
                        help='输入文件路径(覆盖配置文件设置)')
    parser.add_argument('--output', type=str, default=None,
                        help='输出目录(覆盖配置文件设置)')
    args = parser.parse_args()
    
    # 加载配置
    config = Config(args.config, args.data)
    
    # 选择分析模式
    if args.mode == 'binary':
        analyzer = BinaryDecisionAnalyzer(config)
    elif args.mode == 'open':
        analyzer = OpenResponseAnalyzer(config)
    elif args.mode == 'persuasion':
        analyzer = PersuasionAnalyzer(config)
    elif args.mode == 'questionnaire':
        analyzer = QuestionnaireAnalyzer(config)
    elif args.mode == 'open_questionnaire':
        analyzer = OpenQuestionnaireAnalyzer(config)
    elif args.mode == 'persuasion_questionnaire':
        analyzer = PersuasionQuestionnaireAnalyzer(config)
    elif args.mode == 'stance':
        analyzer = StanceDetectionAnalyzer(config)
    
    # 运行分析
    input_files = [args.input] if args.input else None
    output_dir = args.output if args.output else None
    analyzer.run(input_files=input_files, output_dir=output_dir, rounds=args.rounds)

if __name__ == "__main__":
    main()