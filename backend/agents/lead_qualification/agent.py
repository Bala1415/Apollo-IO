"""
backend.agents.lead_qualification.agent

Implements the Lead Qualification Agent, responsible for evaluating companies
against the Ideal Customer Profile (ICP) and business rules.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import asdict
from datetime import datetime, timezone

from backend.graph.state import GraphState, deep_copy_state, update_state
from backend.graph.constants import QualificationStatus
from backend.agents.lead_qualification.providers import (
    ICPProvider,
    QualificationRulesProvider,
    QualificationResult
)

logger = logging.getLogger(__name__)

class LeadQualificationAgent:
    """
    Evaluates whether a company is a qualified lead based on ICP and business rules.
    """
    
    def __init__(
        self,
        icp_provider: Optional[ICPProvider] = None,
        rules_provider: Optional[QualificationRulesProvider] = None
    ):
        self.icp_provider = icp_provider
        self.rules_provider = rules_provider
        self.name = "LeadQualificationAgent"

    def execute(self, state: GraphState) -> GraphState:
        """
        Executes the lead qualification workflow.
        """
        start_time = time.time()
        logger.info(f"[{self.name}] Agent started.")
        
        if not self.validate_input(state):
            logger.warning(f"[{self.name}] Input validation failed. Missing required profile/industry data.")
            return self._record_failure(state, "Missing required company profile or industry data.")
            
        profile, industry, interests, browser_signals = self._extract_inputs(state)
        
        # 1. Evaluate ICP Match
        icp_result = self.evaluate_icp_match(profile, industry, interests)
        
        # 2. Apply Business Qualification Rules
        final_result = self.determine_qualification(icp_result, browser_signals)
        
        # 3. Post-process and calculations
        final_result.qualification_confidence = self.calculate_confidence(final_result)
        final_result.qualification_reason = self.generate_reasoning(final_result)
        
        logger.info(f"[{self.name}] Qualification Decision: {final_result.qualification_status}")
        
        # 4. Finalize Output
        normalized_output = self.normalize_output(final_result)
        
        if not self.validate_output(normalized_output):
            logger.warning(f"[{self.name}] Output validation failed. Insufficient qualification data.")
            return self._record_failure(state, "Failed to qualify lead.")
            
        # 5. Update State
        final_state = self.update_graph_state(state, normalized_output)
        
        duration = time.time() - start_time
        logger.info(f"[{self.name}] GraphState updated. Execution duration: {duration:.2f}s.")
        
        return final_state

    def validate_input(self, state: GraphState) -> bool:
        """Validates minimum inputs required to qualify."""
        has_profile = bool(state.get("company_profile")) or bool(state.get("business_model"))
        has_industry = bool(state.get("industry"))
        return has_profile or has_industry

    def _extract_inputs(self, state: GraphState) -> tuple:
        """Extracts inputs from GraphState for evaluation."""
        profile = {
            "business_model": state.get("business_model"),
            "company_size": state.get("company_size"),
            "growth_stage": state.get("growth_stage"),
            "technology_stack": state.get("technology_stack", []),
            "company_profile": state.get("company_profile", {})
        }
        industry = {
            "industry": state.get("industry"),
            "sector": state.get("sector"),
            "sub_industry": state.get("sub_industry"),
            "naics": state.get("naics"),
            "sic": state.get("sic")
        }
        interests = {
            "interest_categories": state.get("interest_categories", []),
            "interest_profile": state.get("interest_profile", {})
        }
        browser_signals = state.get("browser_history", []) + state.get("visited_domains", [])
        
        return profile, industry, interests, browser_signals

    def extract_company_profile(self, state: GraphState) -> Dict[str, Any]:
        """Public helper to extract profile."""
        profile, _, _, _ = self._extract_inputs(state)
        return profile

    def extract_industry(self, state: GraphState) -> Dict[str, Any]:
        """Public helper to extract industry."""
        _, industry, _, _ = self._extract_inputs(state)
        return industry
        
    def extract_interest_profile(self, state: GraphState) -> Dict[str, Any]:
        """Public helper to extract interests."""
        _, _, interests, _ = self._extract_inputs(state)
        return interests

    def evaluate_icp_match(
        self, 
        profile: Dict[str, Any], 
        industry: Dict[str, Any], 
        interests: Dict[str, Any]
    ) -> QualificationResult:
        """
        Delegates ICP matching to the provider.
        """
        logger.info(f"[{self.name}] Evaluating ICP match.")
        if self.icp_provider:
            try:
                return self.icp_provider.evaluate_icp_match(profile, industry, interests)
            except Exception as e:
                logger.error(f"[{self.name}] ICPProvider error: {e}")
        
        # Fallback empty result
        return QualificationResult()

    def evaluate_company_size(self, icp_result: QualificationResult) -> Optional[str]:
        return icp_result.company_size_fit
        
    def evaluate_technology_fit(self, icp_result: QualificationResult) -> Optional[str]:
        return icp_result.technology_fit
        
    def evaluate_growth_stage(self, icp_result: QualificationResult) -> Optional[str]:
        return icp_result.growth_fit
        
    def evaluate_budget_fit(self, icp_result: QualificationResult) -> Optional[str]:
        return icp_result.budget_fit
        
    def evaluate_business_need(self, icp_result: QualificationResult) -> Optional[str]:
        return icp_result.need_analysis
        
    def evaluate_industry_fit(self, icp_result: QualificationResult) -> Optional[str]:
        return icp_result.industry_fit
        
    def evaluate_risk_flags(self, icp_result: QualificationResult) -> List[str]:
        return icp_result.risk_flags

    def determine_qualification(
        self, 
        icp_result: QualificationResult, 
        browser_signals: List[str]
    ) -> QualificationResult:
        """
        Delegates final business qualification rules.
        """
        logger.info(f"[{self.name}] Executing qualification rules.")
        if self.rules_provider:
            try:
                return self.rules_provider.evaluate_qualification(icp_result, browser_signals)
            except Exception as e:
                logger.error(f"[{self.name}] QualificationRulesProvider error: {e}")
        
        # Fallback logic if no provider
        icp_result.qualification_status = QualificationStatus.NEEDS_REVIEW.value
        icp_result.qualification = QualificationStatus.NEEDS_REVIEW.value
        return icp_result

    def calculate_confidence(self, final_result: QualificationResult) -> float:
        """Calculates internal confidence."""
        if final_result.qualification_confidence is not None:
            return final_result.qualification_confidence
        
        # Fallback basic heuristic
        score = 0.5
        if final_result.icp_match: score += 0.3
        if final_result.industry_fit: score += 0.1
        if final_result.company_size_fit: score += 0.1
        return min(score, 1.0)

    def generate_reasoning(self, final_result: QualificationResult) -> str:
        """Generates fallback reasoning if not provided."""
        if final_result.qualification_reason:
            return final_result.qualification_reason
        
        factors = ", ".join(final_result.decision_factors) if final_result.decision_factors else "None"
        return f"Qualified based on automated heuristics. Key factors: {factors}."

    def normalize_output(self, result: QualificationResult) -> Dict[str, Any]:
        """Normalizes the output dataclass."""
        data = asdict(result)
        # Drop completely empty/None keys but keep empty lists if initialized
        return {k: v for k, v in data.items() if v is not None}

    def validate_output(self, normalized_data: Dict[str, Any]) -> bool:
        """Ensures a valid status was reached."""
        return "qualification_status" in normalized_data or "qualification" in normalized_data

    def update_graph_state(self, state: GraphState, normalized_data: Dict[str, Any]) -> GraphState:
        """
        Safely updates GraphState, utilizing dynamic properties for fields that are
        not strictly modeled in state.py (allowed via TypedDict total=False).
        """
        new_state = deep_copy_state(state)
        
        update = {}
        
        # Fields explicitly defined in GraphState
        if "qualification" in normalized_data:
            update["qualification"] = normalized_data["qualification"]
        if "qualification_reason" in normalized_data:
            update["qualification_reason"] = normalized_data["qualification_reason"]
        if "icp_match" in normalized_data:
            update["icp_match"] = normalized_data["icp_match"]
        if "budget_fit" in normalized_data:
            update["budget_fit"] = normalized_data["budget_fit"]
        if "technology_fit" in normalized_data:
            update["technology_fit"] = normalized_data["technology_fit"]
        if "need_analysis" in normalized_data:
            update["need_analysis"] = normalized_data["need_analysis"]

        # Dynamically inject extra fields requested to avoid altering state.py
        extra_fields = [
            "qualification_status",
            "qualification_confidence",
            "industry_fit",
            "company_size_fit",
            "growth_fit",
            "decision_factors",
            "risk_flags"
        ]
        for field in extra_fields:
            if field in normalized_data:
                update[field] = normalized_data[field]
                
        # Add timestamp
        update["qualification_timestamp"] = datetime.now(timezone.utc).isoformat()
        
        return update_state(new_state, update, agent_name=self.name)

    def _record_failure(self, state: GraphState, message: str) -> GraphState:
        """Records a non-crashing failure."""
        new_state = deep_copy_state(state)
        if "warnings" not in new_state:
            new_state["warnings"] = []
        new_state["warnings"].append(f"[{self.name}] {message}")
        return new_state
