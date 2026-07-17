"""
backend.agents.industry_classification.agent

Implements the Industry Classification Agent, responsible for categorizing
the company into standard business categories based on its profile.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import asdict

from backend.graph.state import GraphState, deep_copy_state, update_state
from backend.agents.industry_classification.providers import (
    IndustryClassificationProvider,
    NAICSLookupProvider,
    SICLookupProvider,
    LLMClassificationProvider,
    IndustryData
)

logger = logging.getLogger(__name__)

class IndustryClassificationAgent:
    """
    Classifies the company into standard business categories.
    
    Uses injected providers to infer taxonomy and lookup standard codes without
    hardcoding rules or implementing scoring engines.
    """
    
    def __init__(
        self,
        classification_provider: Optional[IndustryClassificationProvider] = None,
        naics_provider: Optional[NAICSLookupProvider] = None,
        sic_provider: Optional[SICLookupProvider] = None,
        llm_provider: Optional[LLMClassificationProvider] = None
    ):
        self.classification_provider = classification_provider
        self.naics_provider = naics_provider
        self.sic_provider = sic_provider
        self.llm_provider = llm_provider
        self.name = "IndustryClassificationAgent"

    def execute(self, state: GraphState) -> GraphState:
        """
        Executes the industry classification workflow.
        """
        start_time = time.time()
        logger.info(f"[{self.name}] Agent started.")
        
        if not self.validate_input(state):
            logger.warning(f"[{self.name}] Input validation failed. Missing company profile.")
            return self._record_failure(state, "Missing company profile data.")
            
        profile_data = self.extract_company_profile(state)
        logger.info(f"[{self.name}] Company profile received.")
        
        # 1. Analyze inputs (can be used by internal methods or providers)
        self.analyze_business_model(profile_data)
        self.analyze_products(profile_data)
        self.analyze_services(profile_data)
        self.analyze_technology(profile_data)
        
        # 2. Identify Taxonomy
        industry_data = self.identify_taxonomy(profile_data)
        
        # 3. Lookup standard codes
        naics = self.assign_naics(industry_data, profile_data)
        sic = self.assign_sic(industry_data, profile_data)
        if naics: industry_data.naics = naics
        if sic: industry_data.sic = sic
        
        # 4. Calculate Confidence and Reasoning
        industry_data.confidence = self.calculate_confidence(industry_data)
        industry_data.reasoning = self.generate_reasoning(profile_data, industry_data)
        
        logger.info(f"[{self.name}] Classification completed. Industry: {industry_data.industry}, Confidence: {industry_data.confidence}")
        
        # 5. Output processing
        normalized_output = self.normalize_output(industry_data)
        
        if not self.validate_output(normalized_output):
            logger.warning(f"[{self.name}] Output validation failed. Insufficient classification data.")
            return self._record_failure(state, "Failed to determine a valid industry classification.")
            
        # 6. Update state
        final_state = self.update_graph_state(state, normalized_output)
        
        duration = time.time() - start_time
        logger.info(f"[{self.name}] GraphState updated. Execution duration: {duration:.2f}s.")
        
        return final_state

    def validate_input(self, state: GraphState) -> bool:
        """Validates that a company profile exists."""
        return bool(state.get("company_profile"))

    def extract_company_profile(self, state: GraphState) -> Dict[str, Any]:
        """Extracts the structured profile data."""
        return {
            "business_model": state.get("business_model"),
            "products": state.get("products", []),
            "services": state.get("services", []),
            "technology_stack": state.get("technology_stack", []),
            "company_size": state.get("company_size"),
            "company_profile": state.get("company_profile", {}),
            "company_research": state.get("company_research", {})
        }

    def analyze_business_model(self, profile_data: Dict[str, Any]) -> None:
        """Pre-analysis hook for business model."""
        pass # Can be extended if internal logic is required before passing to provider

    def analyze_products(self, profile_data: Dict[str, Any]) -> None:
        """Pre-analysis hook for products."""
        pass

    def analyze_services(self, profile_data: Dict[str, Any]) -> None:
        """Pre-analysis hook for services."""
        pass

    def analyze_technology(self, profile_data: Dict[str, Any]) -> None:
        """Pre-analysis hook for technology."""
        pass

    def identify_taxonomy(self, profile_data: Dict[str, Any]) -> IndustryData:
        """Identifies primary industry, sector, and sub-industry."""
        # Try direct classification provider first
        if self.classification_provider:
            try:
                data = self.classification_provider.classify(profile_data)
                if data and data.industry:
                    return data
            except Exception as e:
                logger.error(f"[{self.name}] ClassificationProvider error: {e}")
                
        # Fallback to LLM
        if self.llm_provider:
            try:
                data = self.llm_provider.infer_taxonomy(profile_data)
                if data and data.industry:
                    return data
            except Exception as e:
                logger.error(f"[{self.name}] LLMProvider taxonomy error: {e}")
                
        return IndustryData()

    def identify_primary_industry(self, industry_data: IndustryData) -> Optional[str]:
        return industry_data.industry

    def identify_sector(self, industry_data: IndustryData) -> Optional[str]:
        return industry_data.sector

    def identify_sub_industry(self, industry_data: IndustryData) -> Optional[str]:
        return industry_data.sub_industry

    def assign_naics(self, industry_data: IndustryData, profile_data: Dict[str, Any]) -> Optional[str]:
        if not self.naics_provider or not industry_data.industry:
            return industry_data.naics
            
        description = profile_data.get("company_research", {}).get("description", "")
        try:
            return self.naics_provider.get_naics_code(
                industry_data.industry, 
                industry_data.sub_industry or "", 
                description
            ) or industry_data.naics
        except Exception as e:
            logger.error(f"[{self.name}] NAICS Provider error: {e}")
            return industry_data.naics

    def assign_sic(self, industry_data: IndustryData, profile_data: Dict[str, Any]) -> Optional[str]:
        if not self.sic_provider or not industry_data.industry:
            return industry_data.sic
            
        description = profile_data.get("company_research", {}).get("description", "")
        try:
            return self.sic_provider.get_sic_code(
                industry_data.industry, 
                industry_data.sub_industry or "", 
                description
            ) or industry_data.sic
        except Exception as e:
            logger.error(f"[{self.name}] SIC Provider error: {e}")
            return industry_data.sic

    def calculate_confidence(self, industry_data: IndustryData) -> float:
        """Calculates or extracts confidence score."""
        if industry_data.confidence is not None:
            return industry_data.confidence
        # Simple heuristic if no confidence provided by provider
        score = 0.0
        if industry_data.industry: score += 0.5
        if industry_data.sector: score += 0.2
        if industry_data.sub_industry: score += 0.1
        if industry_data.naics: score += 0.1
        if industry_data.sic: score += 0.1
        return min(score, 1.0)

    def generate_reasoning(self, profile_data: Dict[str, Any], industry_data: IndustryData) -> Optional[str]:
        if not self.llm_provider or not industry_data.industry:
            return industry_data.reasoning
        try:
            return self.llm_provider.generate_reasoning(profile_data, industry_data)
        except Exception as e:
            logger.error(f"[{self.name}] LLMProvider reasoning error: {e}")
            return industry_data.reasoning

    def normalize_output(self, data: IndustryData) -> Dict[str, Any]:
        """Converts internal dataclass to dict and drops empty values."""
        return {k: v for k, v in asdict(data).items() if v is not None}

    def validate_output(self, normalized_data: Dict[str, Any]) -> bool:
        """Must at least have an industry identified."""
        return "industry" in normalized_data

    def update_graph_state(self, state: GraphState, normalized_data: Dict[str, Any]) -> GraphState:
        """
        Updates the graph state securely without modifying unauthorized fields.
        """
        new_state = deep_copy_state(state)
        
        update = {}
        for key in ["industry", "sector", "sub_industry", "naics", "sic"]:
            if key in normalized_data:
                update[key] = normalized_data[key]
                
        # Handle 'confidence' key from the dataclass if present
        if "confidence" in normalized_data:
            update["industry_confidence"] = normalized_data["confidence"]
            
        # Dynamically inject reasoning to avoid state.py changes
        if "reasoning" in normalized_data:
            update["industry_reasoning"] = normalized_data["reasoning"]
            
        return update_state(new_state, update, agent_name=self.name)

    def _record_failure(self, state: GraphState, message: str) -> GraphState:
        """Records a non-crashing failure and appends to warnings."""
        new_state = deep_copy_state(state)
        if "warnings" not in new_state:
            new_state["warnings"] = []
        new_state["warnings"].append(f"[{self.name}] {message}")
        return new_state
