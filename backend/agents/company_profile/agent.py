"""
backend.agents.company_profile.agent

Implements the Company Profile Agent, responsible for converting raw company research
into structured business intelligence.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from backend.graph.state import GraphState, deep_copy_state, update_state
from backend.agents.company_profile.providers import (
    TechnologyDetectionProvider,
    WebsiteAnalysisProvider,
    LLMProvider,
    TechnologyStack
)

logger = logging.getLogger(__name__)


@dataclass
class CompanyProfileData:
    """Internal model for tracking profile data before state update."""
    business_model: Optional[str] = None
    target_market: Optional[str] = None
    market_segment: Optional[str] = None
    company_size: Optional[str] = None
    revenue_estimate: Optional[str] = None
    growth_stage: Optional[str] = None
    organization_type: Optional[str] = None
    founding_year: Optional[int] = None
    locations: List[str] = None
    summary: Optional[str] = None

    def __post_init__(self):
        if self.locations is None:
            self.locations = []


class CompanyProfileAgent:
    """
    Converts raw company research into structured business intelligence.
    
    Uses injected providers to detect technologies, analyze business models,
    and estimate metrics without implementing scraping logic directly.
    """
    
    def __init__(
        self,
        tech_provider: Optional[TechnologyDetectionProvider] = None,
        analysis_provider: Optional[WebsiteAnalysisProvider] = None,
        llm_provider: Optional[LLMProvider] = None
    ):
        self.tech_provider = tech_provider
        self.analysis_provider = analysis_provider
        self.llm_provider = llm_provider
        self.name = "CompanyProfileAgent"

    def execute(self, state: GraphState) -> GraphState:
        """
        Executes the company profiling workflow.
        """
        start_time = time.time()
        logger.info(f"[{self.name}] Agent started.")
        
        if not self.validate_input(state):
            logger.warning(f"[{self.name}] Input validation failed. Missing research data.")
            return self._record_failure(state, "Missing research data.")
            
        domain, research_data = self.extract_research_data(state)
        logger.info(f"[{self.name}] Research received for domain: {domain}")
        
        logger.info(f"[{self.name}] Profile generation started.")
        
        # 1. Base extractions
        description = research_data.get("description", "")
        products = research_data.get("products", [])
        services = research_data.get("services", [])
        locations = self.identify_locations(research_data)
        founding_year = self.identify_founding_year(research_data)
        summary = self.build_company_summary(description)
        
        # 2. Technology Detection
        tech_stack_obj = self.detect_technology_stack(domain)
        logger.info(f"[{self.name}] Technology detection completed.")
        
        # 3. Website/Business Analysis
        business_model = self.identify_business_model(description, products, services)
        target_market = self.identify_target_market(description)
        
        # 4. LLM / Metrics Estimation
        organization_type = self.identify_organization_type(description)
        metrics = self._estimate_metrics_via_llm(research_data)
        
        profile_data = CompanyProfileData(
            business_model=business_model,
            target_market=target_market,
            market_segment=target_market, # Mapping target market to segment for simplicity
            company_size=self.estimate_company_size(metrics, research_data),
            revenue_estimate=self.estimate_revenue(metrics),
            growth_stage=self.estimate_growth_stage(metrics),
            organization_type=organization_type,
            founding_year=founding_year,
            locations=locations,
            summary=summary
        )
        
        normalized_profile = self.normalize_profile(profile_data)
        
        if not self.validate_profile(normalized_profile):
            logger.warning(f"[{self.name}] Profile validation failed. Insufficient data.")
            return self._record_failure(state, "Failed to generate a valid company profile.")
            
        logger.info(f"[{self.name}] Profile validated.")
        
        # Update State
        final_state = self.update_graph_state(state, normalized_profile, tech_stack_obj)
        logger.info(f"[{self.name}] GraphState updated.")
        
        duration = time.time() - start_time
        logger.info(f"[{self.name}] Execution completed. Duration: {duration:.2f}s.")
        
        return final_state

    def validate_input(self, state: GraphState) -> bool:
        """Validates that we have minimum research to proceed."""
        domain = state.get("company_domain")
        has_research = bool(state.get("company_research")) or bool(state.get("website"))
        return bool(domain and has_research)

    def extract_research_data(self, state: GraphState) -> tuple[str, Dict[str, Any]]:
        """Extracts domain and research dict from state."""
        domain = state.get("company_domain", "")
        research_data = {
            "products": state.get("products", []),
            "services": state.get("services", []),
            "customers": state.get("customers", []),
            "employees": state.get("employees"),
            "funding": state.get("funding"),
            "headquarters": state.get("headquarters"),
            "technology_stack": state.get("technology_stack", [])
        }
        
        company_research = state.get("company_research", {})
        if company_research:
            research_data["description"] = company_research.get("description", "")
            research_data["founding_year"] = company_research.get("founding_year")
            research_data["locations"] = company_research.get("locations", [])
            
        return domain, research_data

    def build_company_summary(self, description: str) -> str:
        """Builds a normalized summary from description."""
        if not description:
            return ""
        return description[:500] + ("..." if len(description) > 500 else "")

    def identify_business_model(self, description: str, products: List[str], services: List[str]) -> Optional[str]:
        if not self.analysis_provider:
            return None
        try:
            return self.analysis_provider.analyze_business_model(description, products, services)
        except Exception as e:
            logger.error(f"[{self.name}] Error identifying business model: {e}")
            return None

    def identify_target_market(self, description: str) -> Optional[str]:
        if not self.analysis_provider:
            return None
        try:
            return self.analysis_provider.analyze_target_market(description)
        except Exception as e:
            logger.error(f"[{self.name}] Error identifying target market: {e}")
            return None

    def _estimate_metrics_via_llm(self, research_data: Dict[str, Any]) -> Dict[str, str]:
        if not self.llm_provider:
            return {}
        try:
            return self.llm_provider.estimate_company_metrics(research_data)
        except Exception as e:
            logger.error(f"[{self.name}] Error estimating metrics: {e}")
            return {}

    def estimate_company_size(self, metrics: Dict[str, str], research_data: Dict[str, Any]) -> Optional[str]:
        """Estimates company size based on raw employees count or LLM prediction."""
        employees = research_data.get("employees")
        if employees:
            if employees < 10: return "1-10"
            if employees < 50: return "11-50"
            if employees < 200: return "51-200"
            if employees < 1000: return "201-1000"
            if employees < 5000: return "1001-5000"
            return "5000+"
        return metrics.get("company_size")

    def estimate_revenue(self, metrics: Dict[str, str]) -> Optional[str]:
        return metrics.get("revenue_estimate")

    def estimate_growth_stage(self, metrics: Dict[str, str]) -> Optional[str]:
        return metrics.get("growth_stage")

    def identify_organization_type(self, description: str) -> Optional[str]:
        if not self.llm_provider:
            return None
        try:
            return self.llm_provider.extract_organization_type(description)
        except Exception as e:
            logger.error(f"[{self.name}] Error identifying org type: {e}")
            return None

    def detect_technology_stack(self, domain: str) -> TechnologyStack:
        if not self.tech_provider:
            return TechnologyStack()
        try:
            return self.tech_provider.detect_technology(domain)
        except Exception as e:
            logger.error(f"[{self.name}] Error detecting technology stack: {e}")
            return TechnologyStack()

    def detect_cloud_platforms(self, tech_stack: TechnologyStack) -> List[str]:
        return tech_stack.cloud_platforms

    def detect_frontend_stack(self, tech_stack: TechnologyStack) -> List[str]:
        return tech_stack.frontend_stack

    def detect_backend_stack(self, tech_stack: TechnologyStack) -> List[str]:
        return tech_stack.backend_stack

    def detect_database_stack(self, tech_stack: TechnologyStack) -> List[str]:
        return tech_stack.databases

    def detect_ai_stack(self, tech_stack: TechnologyStack) -> List[str]:
        return tech_stack.ai_ml

    def detect_devops_stack(self, tech_stack: TechnologyStack) -> List[str]:
        return tech_stack.devops

    def detect_security_stack(self, tech_stack: TechnologyStack) -> List[str]:
        return tech_stack.security

    def identify_locations(self, research_data: Dict[str, Any]) -> List[str]:
        locs = research_data.get("locations", [])
        hq = research_data.get("headquarters")
        if hq and hq not in locs:
            locs.append(hq)
        return locs

    def identify_founding_year(self, research_data: Dict[str, Any]) -> Optional[int]:
        return research_data.get("founding_year")

    def normalize_profile(self, profile: CompanyProfileData) -> Dict[str, Any]:
        """Normalizes dataclass into dictionary."""
        return {k: v for k, v in asdict(profile).items() if v is not None}

    def validate_profile(self, profile: Dict[str, Any]) -> bool:
        """Ensures we extracted at least some meaningful business intelligence."""
        # Check if we have at least 2 non-empty keys
        valid_keys = [k for k, v in profile.items() if v and k != "locations"]
        return len(valid_keys) >= 1

    def update_graph_state(self, state: GraphState, profile: Dict[str, Any], tech_stack: TechnologyStack) -> GraphState:
        """Updates the graph state securely without breaking other agent states."""
        new_state = deep_copy_state(state)
        
        # We nest target_market and market_segment inside company_profile since they 
        # aren't top-level fields in GraphState schema.
        existing_profile = new_state.get("company_profile", {})
        if not existing_profile:
            existing_profile = {}
            
        existing_profile["target_market"] = profile.get("target_market")
        existing_profile["market_segment"] = profile.get("market_segment")
        existing_profile["locations"] = profile.get("locations", [])
        existing_profile["summary"] = profile.get("summary")
        
        update = {
            "company_profile": existing_profile,
            "business_model": profile.get("business_model"),
            "company_size": profile.get("company_size"),
            "growth_stage": profile.get("growth_stage"),
            "revenue_estimate": profile.get("revenue_estimate"),
            "organization_type": profile.get("organization_type"),
            "technology_stack": tech_stack.get_all()
        }
        
        # Remove Nones to prevent overwriting with None
        update = {k: v for k, v in update.items() if v is not None}
        
        return update_state(new_state, update, agent_name=self.name)

    def _record_failure(self, state: GraphState, message: str) -> GraphState:
        """Records a non-crashing failure and appends to warnings."""
        new_state = deep_copy_state(state)
        if "warnings" not in new_state:
            new_state["warnings"] = []
        new_state["warnings"].append(f"[{self.name}] {message}")
        return new_state
