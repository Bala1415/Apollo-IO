"""
backend.agents.lead_score.agent

Implements the Lead Score Agent, responsible for calculating numerical scores
based on configurable strategies.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import asdict
from datetime import datetime, timezone

from backend.graph.state import GraphState, deep_copy_state, update_state
from backend.agents.lead_score.providers import (
    ScoringStrategyProvider,
    WeightConfigurationProvider,
    ScoreResult
)

logger = logging.getLogger(__name__)

class LeadScoreAgent:
    """
    Calculates a numerical lead score and confidence score using configurable strategies.
    
    This agent never qualifies leads; it only computes a score.
    """
    
    def __init__(
        self,
        strategy_provider: Optional[ScoringStrategyProvider] = None,
        weight_provider: Optional[WeightConfigurationProvider] = None
    ):
        self.strategy_provider = strategy_provider
        self.weight_provider = weight_provider
        self.name = "LeadScoreAgent"

    def execute(self, state: GraphState) -> GraphState:
        """
        Executes the lead scoring workflow.
        """
        start_time = time.time()
        logger.info(f"[{self.name}] Agent started.")
        
        if not self.validate_input(state):
            logger.warning(f"[{self.name}] Input validation failed. Missing qualification or profile data.")
            return self._record_failure(state, "Missing required qualification or company profile data.")
            
        qualification, profile, industry, interests, browser_signals = self._extract_inputs(state)
        logger.info(f"[{self.name}] Input validated.")
        
        # 1. Load weights
        weights = self.load_weight_configuration()
        logger.info(f"[{self.name}] Weights loaded.")
        
        # 2. Calculate scores
        score_result = self.apply_weighted_scoring(
            qualification, profile, industry, interests, browser_signals, weights
        )
        logger.info(f"[{self.name}] Scores calculated. Overall: {score_result.overall_score}")
        
        # 3. Post-process (Confidence and Reasoning inherently handled in Strategy or via fallbacks here)
        confidence = self.calculate_confidence(score_result)
        reasoning = self.generate_reasoning(score_result)
        logger.info(f"[{self.name}] Confidence calculated. Reasoning generated.")
        
        # 4. Finalize Output
        normalized_output = self.normalize_output(score_result, confidence, reasoning)
        
        if not self.validate_output(normalized_output):
            logger.warning(f"[{self.name}] Output validation failed. Invalid scores generated.")
            return self._record_failure(state, "Failed to compute valid lead scores.")
            
        # 5. Update State
        final_state = self.update_graph_state(state, normalized_output)
        
        duration = time.time() - start_time
        logger.info(f"[{self.name}] GraphState updated. Execution duration: {duration:.2f}s.")
        
        return final_state

    def validate_input(self, state: GraphState) -> bool:
        """Validates minimum inputs required to score."""
        has_profile = bool(state.get("company_profile")) or bool(state.get("business_model"))
        has_qualification = bool(state.get("qualification")) or bool(state.get("qualification_status"))
        return has_profile and has_qualification

    def _extract_inputs(self, state: GraphState) -> tuple:
        """Extracts inputs from GraphState for evaluation."""
        qualification = {
            "qualification": state.get("qualification"),
            "icp_match": state.get("icp_match"),
            "budget_fit": state.get("budget_fit"),
            "technology_fit": state.get("technology_fit"),
            "need_analysis": state.get("need_analysis")
        }
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
        
        return qualification, profile, industry, interests, browser_signals

    def extract_qualification(self, state: GraphState) -> Dict[str, Any]:
        """Public helper to extract qualification."""
        qual, _, _, _, _ = self._extract_inputs(state)
        return qual

    def extract_company_profile(self, state: GraphState) -> Dict[str, Any]:
        """Public helper to extract profile."""
        _, profile, _, _, _ = self._extract_inputs(state)
        return profile

    def extract_industry(self, state: GraphState) -> Dict[str, Any]:
        """Public helper to extract industry."""
        _, _, industry, _, _ = self._extract_inputs(state)
        return industry
        
    def extract_interest_profile(self, state: GraphState) -> Dict[str, Any]:
        """Public helper to extract interests."""
        _, _, _, interests, _ = self._extract_inputs(state)
        return interests

    def load_weight_configuration(self) -> Dict[str, float]:
        """Retrieves weights from the provider or uses defaults."""
        if self.weight_provider:
            try:
                return self.weight_provider.get_weights()
            except Exception as e:
                logger.error(f"[{self.name}] WeightProvider error: {e}")
                
        # Default Weights
        return {
            "intent": 0.30,
            "industry": 0.20,
            "company_size": 0.15,
            "technology": 0.15,
            "growth": 0.10,
            "icp": 0.10
        }

    def calculate_intent_score(self, result: ScoreResult) -> float:
        return result.intent_score

    def calculate_industry_score(self, result: ScoreResult) -> float:
        return result.industry_score

    def calculate_company_size_score(self, result: ScoreResult) -> float:
        return result.company_size_score

    def calculate_technology_score(self, result: ScoreResult) -> float:
        return result.technology_score

    def calculate_growth_score(self, result: ScoreResult) -> float:
        return result.growth_score

    def calculate_icp_score(self, result: ScoreResult) -> float:
        return result.icp_score

    def apply_weighted_scoring(
        self,
        qualification: Dict[str, Any],
        profile: Dict[str, Any],
        industry: Dict[str, Any],
        interests: Dict[str, Any],
        browser_signals: list[str],
        weights: Dict[str, float]
    ) -> ScoreResult:
        """
        Delegates scoring calculation to the configured strategy provider.
        """
        if self.strategy_provider:
            try:
                return self.strategy_provider.calculate_scores(
                    qualification, profile, industry, interests, browser_signals, weights
                )
            except Exception as e:
                logger.error(f"[{self.name}] ScoringStrategyProvider error: {e}")
                
        # Fallback empty logic if no provider (returns 0s)
        return ScoreResult()

    def calculate_confidence(self, result: ScoreResult) -> float:
        if result.confidence > 0:
            return result.confidence
        # Default fallback confidence if strategy provider omitted it
        return 0.5 if result.overall_score > 0 else 0.0

    def generate_reasoning(self, result: ScoreResult) -> str:
        if result.reasoning:
            return result.reasoning
        return "Calculated via fallback heuristic."

    def generate_score_breakdown(self, result: ScoreResult) -> Dict[str, float]:
        """Constructs the breakdown dictionary."""
        return {
            "intent_score": result.intent_score,
            "industry_score": result.industry_score,
            "company_size_score": result.company_size_score,
            "technology_score": result.technology_score,
            "growth_score": result.growth_score,
            "icp_score": result.icp_score
        }

    def normalize_output(self, result: ScoreResult, confidence: float, reasoning: str) -> Dict[str, Any]:
        """Consolidates output mapping."""
        breakdown = self.generate_score_breakdown(result)
        return {
            "lead_score": result.overall_score,
            "score_breakdown": breakdown,
            "confidence": confidence,
            "score_reasoning": reasoning,
            "score_timestamp": datetime.now(timezone.utc).isoformat()
        }

    def validate_output(self, normalized_data: Dict[str, Any]) -> bool:
        """Ensures valid scoring logic produced a number."""
        return "lead_score" in normalized_data and isinstance(normalized_data["lead_score"], (int, float))

    def update_graph_state(self, state: GraphState, normalized_data: Dict[str, Any]) -> GraphState:
        """
        Safely updates GraphState. Sub-scores are stored inside 'score_breakdown'
        to respect state.py schema. Untracked metadata like reasoning and timestamps
        are injected dynamically.
        """
        new_state = deep_copy_state(state)
        update = {}
        
        # Standard defined fields
        if "lead_score" in normalized_data:
            update["lead_score"] = normalized_data["lead_score"]
            
        if "score_breakdown" in normalized_data:
            existing_breakdown = new_state.get("score_breakdown", {})
            if not existing_breakdown:
                existing_breakdown = {}
            # Merge with any existing breakdown data if needed
            existing_breakdown.update(normalized_data["score_breakdown"])
            update["score_breakdown"] = existing_breakdown

        # Dynamically inject metadata missing from state.py
        extra_fields = [
            "confidence",
            "score_reasoning",
            "score_timestamp"
        ]
        for field in extra_fields:
            if field in normalized_data:
                update[field] = normalized_data[field]
                
        return update_state(new_state, update, agent_name=self.name)

    def _record_failure(self, state: GraphState, message: str) -> GraphState:
        """Records a non-crashing failure."""
        new_state = deep_copy_state(state)
        if "warnings" not in new_state:
            new_state["warnings"] = []
        new_state["warnings"].append(f"[{self.name}] {message}")
        return new_state
