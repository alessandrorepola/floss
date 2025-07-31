"""
Fault Localization Engine.
"""

import json
from ..formulas import *
from .data import CoverageData
from .config import FLConfig


class FLEngine:
    """Engine for calculating fault localization suspiciousness scores."""
    
    AVAILABLE_FORMULAS = {
        "ochiai": OchiaiFormula(),
        "tarantula": TarantulaFormula(),
        "jaccard": JaccardFormula(),
        "dstar2": DStarFormula(star=2),
        "dstar3": DStarFormula(star=3),
        "kulczynski2": Kulczynski2Formula(),
        "naish1": Naish1Formula(),
        "russellrao": RussellRaoFormula(),
        "sorensendice": SorensenDiceFormula(),
        "sbi": SBIFormula(),
    }
    
    def __init__(self, config: FLConfig):
        self.config = config
        formulas_to_use = config.formulas or ["ochiai", "tarantula", "jaccard", "dstar2"]
        self.formulas = {
            name: self.AVAILABLE_FORMULAS[name] 
            for name in formulas_to_use 
            if name in self.AVAILABLE_FORMULAS
        }
    
    def calculate_suspiciousness(self, input_file: str, output_file: str) -> None:
        """Calculate suspiciousness scores and generate report."""
        # Load coverage data
        with open(input_file, 'r') as f:
            coverage_json = json.load(f)
        
        coverage_data = CoverageData.from_json(coverage_json)
        
        # Calculate suspiciousness for each line
        suspiciousness_scores = {}
        
        for line_key in coverage_data.line_coverage:
            n_cf, n_nf, n_cp, n_np = coverage_data.get_sbfl_params(line_key)
            
            line_scores = {}
            for formula_name, formula in self.formulas.items():
                score = formula.calculate(n_cf, n_nf, n_cp, n_np)
                line_scores[formula_name] = score
            
            suspiciousness_scores[line_key] = line_scores
        
        # Create report
        report = coverage_json.copy()
        
        # Add suspiciousness scores to each file's lines
        for file_path, file_data in report.get("files", {}).items():
            contexts = file_data.get("contexts", {})
            
            # Add suspiciousness section to file
            file_data["suspiciousness"] = {}
            
            for line_num in contexts:
                line_key = f"{file_path}:{line_num}"
                if line_key in suspiciousness_scores:
                    file_data["suspiciousness"][line_num] = suspiciousness_scores[line_key]
        
        # Add metadata about FL calculation
        report["fl_metadata"] = {
            "formulas_used": list(self.formulas.keys()),
            "total_lines_analyzed": len(suspiciousness_scores)
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
