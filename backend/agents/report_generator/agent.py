"""
backend.agents.report_generator.agent

Implements the AI Report Generator Agent, responsible for compiling all collected
intelligence into a comprehensive, readable business report.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import asdict
from datetime import datetime, timezone

from backend.graph.state import GraphState, deep_copy_state, update_state
from backend.agents.report_generator.providers import (
    ReportFormatterProvider,
    ReportTemplateProvider,
    ReportData
)

logger = logging.getLogger(__name__)

class AIReportGenerator:
    """
    Compiles a comprehensive lead intelligence report from all previous agent outputs.
    
    This agent performs no orchestration or new analysis; it solely formats and 
    structures existing data.
    """
    
    def __init__(
        self,
        formatter_provider: Optional[ReportFormatterProvider] = None,
        template_provider: Optional[ReportTemplateProvider] = None
    ):
        self.formatter_provider = formatter_provider
        self.template_provider = template_provider
        self.name = "AIReportGenerator"

    def execute(self, state: GraphState) -> GraphState:
        """
        Executes the report generation workflow.
        """
        start_time = time.time()
        logger.info(f"[{self.name}] Agent started.")
        
        if not self.validate_input(state):
            logger.warning(f"[{self.name}] Input validation failed. Missing critical data components.")
            return self._record_failure(state, "Missing critical state components to generate a report.")
            
        # 1. Extract all contexts
        research, profile, industry, qualification, score, recommendation = self._extract_inputs(state)
        
        # 2. Get Template
        template = self._get_template()
        
        # 3. Assemble Report
        report_data = self.assemble_report(
            research, profile, industry, qualification, score, recommendation, template
        )
        
        logger.info(f"[{self.name}] Sections Generated. Metadata Generated.")
        
        # 4. Finalize Output
        normalized_output = self.normalize_output(report_data)
        
        if not self.validate_report(normalized_output):
            logger.warning(f"[{self.name}] Report validation failed.")
            return self._record_failure(state, "Failed to assemble a valid report.")
            
        # 5. Update State
        final_state = self.update_graph_state(state, normalized_output)
        
        duration = time.time() - start_time
        logger.info(f"[{self.name}] GraphState updated. Execution duration: {duration:.2f}s.")
        
        return final_state

    def validate_input(self, state: GraphState) -> bool:
        """Validates minimum inputs required to build a report."""
        has_profile = bool(state.get("company_profile")) or bool(state.get("business_model"))
        has_recommendation = bool(state.get("recommendation")) or bool(state.get("priority"))
        return has_profile or has_recommendation

    def _extract_inputs(self, state: GraphState) -> tuple:
        """Extracts all intelligence blocks from GraphState."""
        research = state.get("company_research", {})
        
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
        
        recommendation = {
            "priority": state.get("priority"),
            "recommendation": state.get("recommendation"),
            "recommendation_reason": state.get("recommendation_reason"),
            "next_steps": state.get("next_steps", []),
            "next_action": state.get("next_action"),
            "executive_summary": state.get("executive_summary")
        }
        
        return research, profile, industry, qualification, score, recommendation

    def extract_research(self, state: GraphState) -> Dict[str, Any]:
        research, _, _, _, _, _ = self._extract_inputs(state)
        return research

    def extract_company_profile(self, state: GraphState) -> Dict[str, Any]:
        _, profile, _, _, _, _ = self._extract_inputs(state)
        return profile

    def extract_industry(self, state: GraphState) -> Dict[str, Any]:
        _, _, industry, _, _, _ = self._extract_inputs(state)
        return industry

    def extract_qualification(self, state: GraphState) -> Dict[str, Any]:
        _, _, _, qualification, _, _ = self._extract_inputs(state)
        return qualification

    def extract_lead_score(self, state: GraphState) -> Dict[str, Any]:
        _, _, _, _, score, _ = self._extract_inputs(state)
        return score

    def extract_recommendation(self, state: GraphState) -> Dict[str, Any]:
        _, _, _, _, _, recommendation = self._extract_inputs(state)
        return recommendation

    def _get_template(self) -> str:
        if self.template_provider:
            try:
                return self.template_provider.get_template()
            except Exception as e:
                logger.error(f"[{self.name}] TemplateProvider error: {e}")
        return "DEFAULT_TEMPLATE"

    def assemble_report(
        self,
        research: Dict[str, Any],
        profile: Dict[str, Any],
        industry: Dict[str, Any],
        qualification: Dict[str, Any],
        score: Dict[str, Any],
        recommendation: Dict[str, Any],
        template: str
    ) -> ReportData:
        """Assembles the report using the provider."""
        if self.formatter_provider:
            try:
                return self.formatter_provider.assemble_report(
                    research, profile, industry, qualification, score, recommendation, template
                )
            except Exception as e:
                logger.error(f"[{self.name}] FormatterProvider error: {e}")
                
        # Fallback automated summary
        return self._generate_fallback_report(recommendation, score, profile)

    def build_executive_summary(self, recommendation: Dict[str, Any]) -> str:
        """Internal builder if provider is missing."""
        return recommendation.get("executive_summary") or "Executive summary pending."

    def build_metadata(self, report: ReportData) -> Dict[str, Any]:
        """Internal builder if provider is missing."""
        if not report.report_metadata:
            report.report_metadata = {
                "generated_by": self.name,
                "version": report.report_version
            }
        return report.report_metadata

    def _generate_fallback_report(self, rec: Dict[str, Any], score: Dict[str, Any], profile: Dict[str, Any]) -> ReportData:
        """Creates a minimal readable report if the provider is unavailable."""
        priority = rec.get("priority", "UNKNOWN")
        lead_score = score.get("lead_score", 0.0)
        summary = self.build_executive_summary(rec)
        
        final_text = f"# Lead Intelligence Report\n\n**Priority**: {priority}\n**Score**: {lead_score}\n\n## Executive Summary\n{summary}"
        
        result = ReportData(
            final_report=final_text,
            report_summary=summary,
            report_sections=["Executive Summary", "Scores"],
            report_generated_at=datetime.now(timezone.utc).isoformat()
        )
        self.build_metadata(result)
        return result

    def normalize_output(self, result: ReportData) -> Dict[str, Any]:
        """Normalizes dataclass to dict."""
        data = asdict(result)
        # Ensure timestamp is set
        if not data.get("report_generated_at"):
            data["report_generated_at"] = datetime.now(timezone.utc).isoformat()
        return {k: v for k, v in data.items() if v is not None}

    def validate_report(self, normalized_data: Dict[str, Any]) -> bool:
        """Ensures the report contains text."""
        return bool(normalized_data.get("final_report"))

    def update_graph_state(self, state: GraphState, normalized_data: Dict[str, Any]) -> GraphState:
        """
        Safely updates GraphState. As approved, dynamically injects metadata 
        fields to preserve state.py schema.
        """
        new_state = deep_copy_state(state)
        update = {}
        
        # Standard defined fields in GraphState
        if "final_report" in normalized_data:
            update["final_report"] = normalized_data["final_report"]
            
        # Dynamically inject the rest of the metadata
        extra_fields = [
            "report_metadata",
            "report_version",
            "report_generated_at",
            "report_summary",
            "report_sections",
            "report_status",
            "report_format"
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
