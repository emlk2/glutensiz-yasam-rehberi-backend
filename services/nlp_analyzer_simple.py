"""
NLP Analyzer - Rule-based Gluten Detection (No ML Dependencies)
"""
from typing import Dict, List
import re

class NLPAnalyzer:
    """Simple rule-based NLP for gluten detection"""
    
    def __init__(self):
        """Initialize analyzer with keyword lists"""
        self.dangerous_keywords = [
            "buğday", "wheat", "arpa", "barley", "çavdar", "rye", "malt", "gluten",
            "durum", "emmer", "spelt", "einkorn", "kamut", "triticale",
            "un", "flour", "kepek", "bran", "irmik", "semolina", "germ"
        ]
        
        self.risky_keywords = [
            "aynı tesiste", "same facility", "çapraz", "cross", 
            "izi", "trace", "may contain", "içerebilir", "olabilir"
        ]
    
    def analyze_ingredients(self, ingredients: str) -> Dict:
        """Analyze ingredient list for gluten risk"""
        text = ingredients.lower().strip()
        
        # Check dangerous keywords
        dangerous_found = []
        for keyword in self.dangerous_keywords:
            if re.search(r'\b' + keyword + r'\b', text):
                dangerous_found.append(keyword)
        
        # Check risky keywords
        risky_found = []
        for keyword in self.risky_keywords:
            if keyword in text:
                risky_found.append(keyword)
        
        # Determine risk level
        if dangerous_found:
            risk_level = "dangerous"
            risk_score = 0.95
        elif risky_found:
            risk_level = "risky"
            risk_score = 0.50
        else:
            risk_level = "safe"
            risk_score = 0.0
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "dangerous_ingredients": dangerous_found,
            "risky_indicators": risky_found,
            "confidence": 0.85
        }
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze text for gluten mentions"""
        return self.analyze_ingredients(text)
    
    def calculate_risk_score(self, ingredients: List[str]) -> float:
        """Calculate risk score from ingredient list"""
        analysis = self.analyze_ingredients(" ".join(ingredients))
        return analysis["risk_score"]
