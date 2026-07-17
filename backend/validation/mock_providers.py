"""
backend.validation.mock_providers

Provides deterministic mock implementations of all abstract providers
across the Apollo-IO backend agents for pipeline validation without side-effects.
"""

from typing import Dict, Any, List

from backend.agents.research.providers import (
    CompanyInfoProvider, ProductServiceProvider, CustomerProvider, 
    NewsProvider, SocialMediaProvider, TechnologyStackProvider, CompanyInfo
)
from backend.agents.company_profile.providers import (
    TechnologyDetectionProvider, WebsiteAnalysisProvider, LLMProvider, TechnologyStack
)
from backend.agents.industry_classification.providers import (
    IndustryClassificationProvider, NAICSLookupProvider, SICLookupProvider, LLMClassificationProvider, IndustryData
)
from backend.agents.lead_qualification.providers import QualificationRulesProvider, ICPProvider, QualificationResult
from backend.agents.lead_score.providers import ScoringStrategyProvider, WeightConfigurationProvider, ScoreResult
from backend.agents.recommendation.providers import RecommendationStrategyProvider, RecommendationResult
from backend.agents.report_generator.providers import ReportFormatterProvider, ReportTemplateProvider, ReportData
from backend.services.notifications.providers import NotificationProvider, NotificationPayload, NotificationResult, NotificationTemplateProvider, DeliveryTracker

class MockCompanyInfoProvider(CompanyInfoProvider):
    def get_name(self) -> str: return "MockCompanyInfo"
    def fetch_company_info(self, domain: str) -> CompanyInfo:
        return CompanyInfo(website=f"http://{domain}", headquarters="San Francisco", employees=500, funding="Series B")

class MockProductServiceProvider(ProductServiceProvider):
    def get_name(self) -> str: return "MockProductService"
    def fetch_products(self, domain: str) -> List[str]: return ["Product A", "Product B"]
    def fetch_services(self, domain: str) -> List[str]: return ["Service A"]

class MockCustomerProvider(CustomerProvider):
    def get_name(self) -> str: return "MockCustomer"
    def fetch_customers(self, domain: str) -> List[str]: return ["Customer A", "Customer B"]

class MockNewsProvider(NewsProvider):
    def get_name(self) -> str: return "MockNews"
    def fetch_latest_news(self, domain: str) -> List[str]: return ["Great news 1", "Great news 2"]

class MockSocialMediaProvider(SocialMediaProvider):
    def get_name(self) -> str: return "MockSocial"
    def fetch_social_links(self, domain: str) -> Dict[str, str]: return {"linkedin": "link", "twitter": "link"}

class MockTechnologyStackProvider(TechnologyStackProvider):
    def get_name(self) -> str: return "MockTech"
    def fetch_technology_stack(self, domain: str) -> List[str]: return ["Python", "React"]

class MockTechnologyDetectionProvider(TechnologyDetectionProvider):
    def get_name(self) -> str: return "MockTechDetect"
    def detect_technology(self, domain: str) -> TechnologyStack:
        return TechnologyStack(cloud_platforms=["AWS"], frontend_stack=["React"])

class MockWebsiteAnalysisProvider(WebsiteAnalysisProvider):
    def get_name(self) -> str: return "MockWebAnalysis"
    def analyze_business_model(self, description: str, products: List[str], services: List[str]) -> str: return "B2B SaaS"
    def analyze_target_market(self, description: str) -> str: return "Enterprise"

class MockLLMProvider(LLMProvider):
    def get_name(self) -> str: return "MockLLM"
    def extract_organization_type(self, description: str) -> str: return "Private"
    def estimate_company_metrics(self, data: Dict[str, Any]) -> Dict[str, str]:
        return {"revenue_estimate": "$10M-$50M", "growth_stage": "Series B", "company_size": "100-500"}

class MockIndustryClassificationProvider(IndustryClassificationProvider):
    def get_name(self) -> str: return "MockIndustry"
    def classify(self, profile_data: Dict[str, Any]) -> IndustryData:
        return IndustryData(industry="Technology", sector="SaaS", confidence=0.95)

class MockNAICSLookupProvider(NAICSLookupProvider):
    def get_name(self) -> str: return "MockNAICS"
    def get_naics_code(self, industry: str, sub_industry: str, description: str) -> Optional[str]: return "511210"

class MockSICLookupProvider(SICLookupProvider):
    def get_name(self) -> str: return "MockSIC"
    def get_sic_code(self, industry: str, sub_industry: str, description: str) -> Optional[str]: return "7372"

class MockLLMClassificationProvider(LLMClassificationProvider):
    def get_name(self) -> str: return "MockLLMClass"
    def infer_taxonomy(self, profile_data: Dict[str, Any]) -> IndustryData: return IndustryData(industry="Tech")
    def generate_reasoning(self, profile_data: Dict[str, Any], taxonomy: IndustryData) -> str: return "Because of reasons"

class MockICPProvider(ICPProvider):
    def get_name(self) -> str: return "MockICP"
    def evaluate_icp_match(self, profile: Dict[str, Any], industry: Dict[str, Any], interests: Dict[str, Any]) -> QualificationResult:
        return QualificationResult(icp_match=True, industry_fit="High")

class MockQualificationRulesProvider(QualificationRulesProvider):
    def get_name(self) -> str: return "MockQual"
    def evaluate_qualification(self, icp_result: QualificationResult, browser_signals: List[str]) -> QualificationResult:
        return QualificationResult(qualification="QUALIFIED", qualification_status="QUALIFIED", qualification_reason="High ICP fit")

class MockWeightConfigurationProvider(WeightConfigurationProvider):
    def get_name(self) -> str: return "MockWeights"
    def get_weights(self) -> Dict[str, float]:
        return {"intent": 0.5, "industry": 0.5}

class MockScoringStrategyProvider(ScoringStrategyProvider):
    def get_name(self) -> str: return "MockScoring"
    def calculate_scores(self, qual: Dict, prof: Dict, ind: Dict, ints: Dict, sigs: List, wts: Dict) -> ScoreResult:
        return ScoreResult(overall_score=85.0, confidence=0.9, reasoning="Mock score")

class MockRecommendationStrategyProvider(RecommendationStrategyProvider):
    def get_name(self) -> str: return "MockRec"
    def generate_recommendation(self, prof: Dict, ind: Dict, qual: Dict, score: Dict, ints: Dict, sigs: List) -> RecommendationResult:
        return RecommendationResult(priority="HOT", recommendation="Call immediately", executive_summary="High priority lead.")

class MockReportTemplateProvider(ReportTemplateProvider):
    def get_name(self) -> str: return "MockTemplate"
    def get_template(self, format_type: str = "MARKDOWN") -> str: return "MOCK_TEMPLATE"

class MockReportFormatterProvider(ReportFormatterProvider):
    def get_name(self) -> str: return "MockFormatter"
    def assemble_report(self, res: Dict, prof: Dict, ind: Dict, qual: Dict, score: Dict, rec: Dict, tpl: str) -> ReportData:
        return ReportData(final_report="MOCK FINAL REPORT MARKDOWN", report_version="1.0", report_status="COMPLETED")

class MockNotificationProvider(NotificationProvider):
    def get_name(self) -> str: return "MockNotification"
    def dispatch(self, payload: NotificationPayload) -> bool: return True

class MockNotificationTemplateProvider(NotificationTemplateProvider):
    def get_name(self) -> str: return "MockNotifTpl"
    def build_payload(self, report: Dict, rec: Dict, channel: str) -> NotificationPayload:
        return NotificationPayload(target_channel=channel, recipient="admin", subject="Mock", body="Mock")

class MockDeliveryTracker(DeliveryTracker):
    def get_name(self) -> str: return "MockTracker"
    def record_delivery(self, result: NotificationResult) -> None: pass
