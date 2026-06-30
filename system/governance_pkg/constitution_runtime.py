from pathlib import Path 
import yaml
DATA=yaml.safe_load(Path(__file__).parent.parent.joinpath('constitution.yaml').read_text(encoding='utf-8'))
class Constitution:
    def snapshot(self): return DATA
    def protected_domains(self): return ['identity','mission','constitution']
constitution=Constitution()
