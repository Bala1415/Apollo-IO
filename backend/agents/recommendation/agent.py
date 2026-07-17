"""
backend.agents.recommendation.agent

Implements the Recommendation Agent, responsible for determining the final
business priority and generating sales strategies.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import asdict
from datetime import datetime, timezone

from backend.graph.state import GraphState, deep_copy_state, update_state
from backend.agents.recommendation.providers import (
    RecommendationStrategyProvider,
    RecommendationResult
)

logger = logging.getLogger(__name__)

class RecommendationAgent:
    """
    Generates final business recommendations, priorities, and sales notes based on
    aggregated intelligence from previous agents.
    
    This agent never recalculates lead scores or changes qualification status.
    """
    
    def __init__(
        self,
        strategy_provider: Optional[RecommendationStrategyProvider] = None
    ):
        self.strategy_provider = strategy_provider
        self.name = "RecommendationAgent"

    def execute(self, state: GraphState) -> GraphState:
        """
        Executes the recommendation workflow.
        """
        start_time = time.time()
        logger.info(f"[{self.name}] Agent started.")
        
        if not self.validate_input(state):
            logger.warning(f"[{self.name}] Input validation failed. Missing score or qualification.")
            return self._record_failure(state, "Missing required lead score or qualification data.")
            
        profile, industry, qualification, score, interests, browser_signals = self._extract_inputs(state)
        
        # 1. Load Strategy and Generate Recommendation
        result = self.load_strategy(profile, industry, qualification, score, interests, browser_signals)
        logger.info(f"[{self.name}] Recommendation strategy executed.")
        
        # 2. Individual internal calculations if provider fallback is needed
        result.priority = self.determine_priority(result, score, qualification)
        result.executive_summary = self.generate_executive_summary(result)
        result.sales_notes = self.generate_sales_notes(result)
        result.sales_pitch = self.generate_sales_pitch(result)
        result.next_action = self.recommend_next_action(result)
        result.estimated_conversion_probability = self.estimate_conversion_probability(result, score)
        result.estimated_business_value = self.estimate_business_value(result)
        result.business_reasoning = self.generate_business_reasoning(result)
        
        logger.info(f"[{self.name}] Priority Assigned: {result.priority}")
        
        # 3. Finalize Output
        normalized_output = self.normalize_output(result)
        
        if not self.validate_output(normalized_output):
            logger.warning(f"[{self.name}] Output validation failed.")
            return self._record_failure(state, "Failed to generate valid recommendation.")
            
        # 4. Update State
        final_state = self.update_graph_state(state, normalized_output)
        
        duration = time.time() - start_time
        logger.info(f"[{self.name}] GraphState updated. Execution duration: {duration:.2f}s.")
        
        return final_state

    def validate_input(self, state: GraphState) -> bool:
        """Validates minimum inputs required to recommend."""
        has_score = bool(state.get("lead_score") is not None)
        has_qualification = bool(state.get("qualification")) or bool(state.get("qualification_status"))
        return has_score and has_qualification

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
        qualification = {
            "qualification": state.get("qualification"),
            "qualification_status": state.get("qualification_status"),
            "icp_match": state.get("icp_match"),
            "need_analysis": state.get("need_analysis")
        }
        score = {
            "lead_score": state.get("lead_score"),
            "score_breakdown": state.get("score_breakdown", {})
        }
        interests = {
            "interest_categories": state.get("interest_categories", []),
            "interest_profile": state.get("interest_profile", {})
        }
        browser_signals = state.get("browser_history", []) + state.get("visited_domains", [])
        
        return profile, industry, qualification, score, interests, browser_signals

    def extract_lead_score(self, state: GraphState) -> Dict[str, Any]:
        _, _, _, score, _, _ = self._extract_inputs(state)
        return score

    def extract_qualification(self, state: GraphState) -> Dict[str, Any]:
        _, _, qual, _, _, _ = self._extract_inputs(state)
        return qual

    def extract_company_profile(self, state: GraphState) -> Dict[str, Any]:
        profile, _, _, _, _, _ = self._extract_inputs(state)
        return profile

    def extract_industry(self, state: GraphState) -> Dict[str, Any]:
        _, industry, _, _, _, _ = self._extract_inputs(state)
        return industry

    def load_strategy(
        self,
        profile: Dict[str, Any],
        industry: Dict[str, Any],
        qualification: Dict[str, Any],
        score: Dict[str, Any],
        interests: Dict[str, Any],
        browser_signals: List[str]
    ) -> RecommendationResult:
        """Loads and executes the recommendation strategy."""
        if self.strategy_provider:
            try:
                return self.strategy_provider.generate_recommendation(
                    profile, industry, qualification, score, interests, browser_signals
                )
            except Exception as e:
                logger.error(f"[{self.name}] RecommendationStrategyProvider error: {e}")
                
        return RecommendationResult()

    def determine_priority(self, result: RecommendationResult, score: Dict[str, Any], qualification: Dict[str, Any]) -> str:
        if result.priority:
            return result.priority
            
        qual_status = qualification.get("qualification_status") or qualification.get("qualification", "")
        lead_score = score.get("lead_score") or 0.0
        
        if "QUALIFIED" in str(qual_status).upper() or lead_score > 0.8:
            return "HOT"
        elif lead_score > 0.5:
            return "WARM"
        return "REVIEW"

    def generate_executive_summary(self, result: RecommendationResult) -> str:
        return result.executive_summary or "Pending manual review."

    def generate_sales_notes(self, result: RecommendationResult) -> str:
        return result.sales_notes or "No specific sales notes generated."

    def generate_sales_pitch(self, result: RecommendationResult) -> str:
        return result.sales_pitch or ""

    def recommend_next_action(self, result: RecommendationResult) -> str:
        return result.next_action or "Review lead details."

    def estimate_conversion_probability(self, result: RecommendationResult, score: Dict[str, Any]) -> float:
        if result.estimated_conversion_probability is not None:
            return result.estimated_conversion_probability
        return min((score.get("lead_score") or 0.0) * 0.9, 1.0)

    def estimate_business_value(self, result: RecommendationResult) -> float:
        return result.estimated_business_value or 0.0

    def generate_business_reasoning(self, result: RecommendationResult) -> str:
        return result.business_reasoning or result.recommendation_reason or "Automated priority assignment based on lead score."

    def normalize_output(self, result: RecommendationResult) -> Dict[str, Any]:
        data = asdict(result)
        return {k: v for k, v in data.items() if v is not None}

    def validate_output(self, normalized_data: Dict[str, Any]) -> bool:
        return "priority" in normalized_data

    def update_graph_state(self, state: GraphState, normalized_data: Dict[str, Any]) -> GraphState:
        """
        Safely updates GraphState, dynamically injecting extra requested fields to 
        preserve state.py without modification.
        """
        new_state = deep_copy_state(state)
        update = {}
        
        # Standard defined fields in GraphState
        if "priority" in normalized_data:
            update["priority"] = normalized_data["priority"]
        if "recommendation" in normalized_data:
            update["recommendation"] = normalized_data["recommendation"]
        if "recommendation_reason" in normalized_data:
            update["recommendation_reason"] = normalized_data["recommendation_reason"]
            
        # Map next_action to next_steps if we want to follow the schema closely, 
        # but also inject next_action natively since it was requested.
        if "next_action" in normalized_data:
            update["next_steps"] = [normalized_data["next_action"]]
            update["next_action"] = normalized_data["next_action"]

        # Dynamically inject the rest of the metadata
        extra_fields = [
            "sales_pitch",
            "sales_notes",
            "executive_summary",
            "business_reasoning",
            "recommended_followup",
            "estimated_business_value",
            "estimated_conversion_probability"
        ]
        
        for field in extra_fields:
            if field in normalized_data:
                update[field] = normalized_data[field]
                
        update["recommendation_timestamp"] = datetime.now(timezone.utc).isoformat()
        
        return update_state(new_state, update, agent_name=self.name)

    def _record_failure(self, state: GraphState, message: str) -> GraphState:
        """Records a non-crashing failure."""
        new_state = deep_copy_state(state)
        if "warnings" not in new_state:
            new_state["warnings"] = []
        new_state["warnings"].append(f"[{self.name}] {message}")
        return new_state
