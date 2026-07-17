"""
backend.agents.research.agent

Implements the Research Agent, responsible solely for gathering company intelligence.
It orchestrates research via injected providers without implementing business logic, scoring,
or concrete scraping logic.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from backend.graph.state import GraphState, deep_copy_state, update_state
from backend.agents.research.providers import (
    CompanyInfoProvider,
    ProductServiceProvider,
    CustomerProvider,
    NewsProvider,
    SocialMediaProvider,
    TechnologyStackProvider,
    CompanyInfo
)

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    Orchestrates the gathering of company intelligence.
    
    Depends on injected providers to collect data about the company domain.
    """
    
    def __init__(
        self,
        company_info_provider: Optional[CompanyInfoProvider] = None,
        product_service_provider: Optional[ProductServiceProvider] = None,
        customer_provider: Optional[CustomerProvider] = None,
        news_provider: Optional[NewsProvider] = None,
        social_media_provider: Optional[SocialMediaProvider] = None,
        technology_stack_provider: Optional[TechnologyStackProvider] = None
    ):
        """
        Initializes the ResearchAgent with optional injected providers.
        """
        self.company_info_provider = company_info_provider
        self.product_service_provider = product_service_provider
        self.customer_provider = customer_provider
        self.news_provider = news_provider
        self.social_media_provider = social_media_provider
        self.technology_stack_provider = technology_stack_provider
        self.name = "ResearchAgent"

    def execute(self, state: GraphState) -> GraphState:
        """
        Executes the research gathering workflow.
        
        Args:
            state (GraphState): The current state of the execution graph.
            
        Returns:
            GraphState: The updated graph state containing the gathered research.
        """
        start_time = time.time()
        logger.info(f"[{self.name}] Agent started.")
        
        if not self.validate_input(state):
            logger.warning(f"[{self.name}] Input validation failed. Missing required fields.")
            return self._record_failure(state, "Missing company_domain in GraphState.")
            
        domain = self.extract_company_domain(state)
        logger.info(f"[{self.name}] Domain received: {domain}")
        
        # Collect individual data points
        company_info = self.collect_company_profile(domain)
        products = self.collect_products(domain)
        services = self.collect_services(domain)
        customers = self.collect_customers(domain)
        news = self.collect_news(domain)
        social_links = self.collect_social_links(domain)
        tech_stack = self.collect_technology(domain)
        
        # Merge and normalize
        raw_results = self.merge_results(
            company_info=company_info,
            products=products,
            services=services,
            customers=customers,
            news=news,
            social_links=social_links,
            tech_stack=tech_stack
        )
        normalized_data = self.normalize_results(raw_results)
        
        # Output validation
        if not self.validate_output(normalized_data):
            logger.warning(f"[{self.name}] Output validation failed. Insufficient data collected.")
            return self._record_failure(state, "Insufficient research data gathered.")
            
        # Update state
        final_state = self.update_graph_state(state, normalized_data)
        
        duration = time.time() - start_time
        logger.info(f"[{self.name}] Completion. Execution duration: {duration:.2f}s.")
        
        return final_state

    def validate_input(self, state: GraphState) -> bool:
        """
        Validates the input state to ensure minimum required fields are present.
        """
        return bool(state.get("company_domain"))

    def extract_company_domain(self, state: GraphState) -> str:
        """
        Extracts the company domain from the GraphState.
        """
        return state.get("company_domain", "").strip()

    def _safe_execute_provider(self, provider: Any, method_name: str, domain: str, default_value: Any) -> Any:
        """
        Safely executes a provider method, handling unavailability and exceptions.
        """
        if not provider:
            return default_value
            
        try:
            method = getattr(provider, method_name)
            provider_name = provider.get_name() if hasattr(provider, "get_name") else provider.__class__.__name__
            logger.info(f"[{self.name}] Provider called: {provider_name}.{method_name}")
            
            result = method(domain)
            
            logger.info(f"[{self.name}] Provider completed: {provider_name}.{method_name}")
            return result
        except Exception as e:
            logger.error(f"[{self.name}] Provider failure ({method_name}): {e}")
            return default_value

    def collect_company_profile(self, domain: str) -> Optional[CompanyInfo]:
        """Collects core company information."""
        return self._safe_execute_provider(self.company_info_provider, "fetch_company_info", domain, None)

    def collect_products(self, domain: str) -> List[str]:
        """Collects company products."""
        return self._safe_execute_provider(self.product_service_provider, "fetch_products", domain, [])

    def collect_services(self, domain: str) -> List[str]:
        """Collects company services."""
        return self._safe_execute_provider(self.product_service_provider, "fetch_services", domain, [])

    def collect_customers(self, domain: str) -> List[str]:
        """Collects company customers."""
        return self._safe_execute_provider(self.customer_provider, "fetch_customers", domain, [])

    def collect_headquarters(self, info: Optional[CompanyInfo]) -> Optional[str]:
        """Extracts headquarters from gathered info."""
        return info.headquarters if info else None

    def collect_employees(self, info: Optional[CompanyInfo]) -> Optional[int]:
        """Extracts employee count from gathered info."""
        return info.employees if info else None

    def collect_funding(self, info: Optional[CompanyInfo]) -> Optional[str]:
        """Extracts funding information from gathered info."""
        return info.funding if info else None

    def collect_news(self, domain: str) -> List[str]:
        """Collects latest news about the company."""
        return self._safe_execute_provider(self.news_provider, "fetch_latest_news", domain, [])

    def collect_social_links(self, domain: str) -> Dict[str, str]:
        """Collects social media links."""
        return self._safe_execute_provider(self.social_media_provider, "fetch_social_links", domain, {})

    def collect_technology(self, domain: str) -> List[str]:
        """Collects the technology stack used by the company."""
        return self._safe_execute_provider(self.technology_stack_provider, "fetch_technology_stack", domain, [])

    def merge_results(
        self,
        company_info: Optional[CompanyInfo],
        products: List[str],
        services: List[str],
        customers: List[str],
        news: List[str],
        social_links: Dict[str, str],
        tech_stack: List[str]
    ) -> Dict[str, Any]:
        """
        Merges all gathered data points into a single dictionary.
        """
        return {
            "company_info": company_info,
            "products": products,
            "services": services,
            "customers": customers,
            "news": news,
            "social_links": social_links,
            "technology_stack": tech_stack
        }

    def normalize_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes the merged results into the structure expected by GraphState.
        """
        normalized = {
            "products": list(set(raw_results.get("products", []))),
            "services": list(set(raw_results.get("services", []))),
            "customers": list(set(raw_results.get("customers", []))),
            "news": list(set(raw_results.get("news", []))),
            "social_links": raw_results.get("social_links", {}),
            "technology_stack": list(set(raw_results.get("technology_stack", [])))
        }
        
        info = raw_results.get("company_info")
        if info:
            normalized["website"] = info.website
            normalized["employees"] = info.employees
            normalized["funding"] = info.funding
            normalized["headquarters"] = info.headquarters
            normalized["company_research"] = {
                "description": info.description,
                "founding_year": info.founding_year,
                "locations": info.locations
            }
            
        logger.info(f"[{self.name}] Fields collected: {list(normalized.keys())}")
        return normalized

    def validate_output(self, normalized_data: Dict[str, Any]) -> bool:
        """
        Validates the final output before updating the state.
        Ensures we didn't just fail to gather everything.
        """
        # If at least one non-empty field was collected, it's valid.
        for value in normalized_data.values():
            if value:
                return True
        return False

    def update_graph_state(self, state: GraphState, normalized_data: Dict[str, Any]) -> GraphState:
        """
        Updates the GraphState with the gathered and normalized research fields.
        Only updates research-related fields.
        """
        new_state = deep_copy_state(state)
        
        update = {}
        for key in ["website", "products", "services", "customers", "employees", 
                    "funding", "headquarters", "news", "social_links", "technology_stack"]:
            if key in normalized_data:
                update[key] = normalized_data[key]
                
        if "company_research" in normalized_data:
            update["company_research"] = normalized_data["company_research"]
            
        # Ensure we do not overwrite fields belonging to later agents
        return update_state(new_state, update, agent_name=self.name)

    def _record_failure(self, state: GraphState, message: str) -> GraphState:
        """
        Records a non-crashing failure and appends to warnings.
        """
        new_state = deep_copy_state(state)
        if "warnings" not in new_state:
            new_state["warnings"] = []
        new_state["warnings"].append(f"[{self.name}] {message}")
        return new_state
