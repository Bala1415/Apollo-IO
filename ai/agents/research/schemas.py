"""
schemas.py — Pydantic models for the Research Agent.

Defines both the intermediate FactExtractionResult (Stage 1)
and the final CompanyResearch output (Stage 2).
"""
from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Stage 1 — Intermediate fact extraction schema
# ---------------------------------------------------------------------------

class ProductInfo(BaseModel):
    name: Optional[str] = Field(default=None, description="Product name")
    category: Optional[str] = Field(default=None, description="Product category (e.g. SaaS, API, Hardware)")
    description: Optional[str] = Field(default=None, description="Short factual description of the product")
    target_users: Optional[str] = Field(default=None, description="Who this product is built for")


class ServiceInfo(BaseModel):
    name: Optional[str] = Field(default=None, description="Service name")
    description: Optional[str] = Field(default=None, description="Short factual description of the service")
    target_customer: Optional[str] = Field(default=None, description="Target customer type for this service")


class SocialLinks(BaseModel):
    linkedin: Optional[str] = Field(default=None, description="LinkedIn company page URL")
    twitter: Optional[str] = Field(default=None, description="Twitter/X company profile URL")
    github: Optional[str] = Field(default=None, description="GitHub organization URL")
    youtube: Optional[str] = Field(default=None, description="YouTube channel URL")


class TechnologyStack(BaseModel):
    cloud: Optional[List[str]] = Field(default_factory=list, description="Cloud platforms (AWS, GCP, Azure, etc.)")
    ai_ml: Optional[List[str]] = Field(default_factory=list, description="AI/ML tools (OpenAI, Anthropic, etc.)")
    frontend: Optional[List[str]] = Field(default_factory=list, description="Frontend technologies (React, Next.js, etc.)")
    backend: Optional[List[str]] = Field(default_factory=list, description="Backend technologies (Node.js, FastAPI, etc.)")
    crm: Optional[List[str]] = Field(default_factory=list, description="CRM tools (HubSpot, Salesforce, etc.)")
    payments: Optional[List[str]] = Field(default_factory=list, description="Payment platforms (Stripe, PayPal, etc.)")
    devops: Optional[List[str]] = Field(default_factory=list, description="DevOps tools (Docker, Kubernetes, etc.)")
    databases: Optional[List[str]] = Field(default_factory=list, description="Databases (PostgreSQL, MongoDB, etc.)")


class FactExtractionResult(BaseModel):
    """
    Intermediate schema produced by Stage 1 LLM.
    Contains only verifiable facts extracted from raw web content.
    """
    company_name: Optional[str] = Field(default=None, description="Official company name")
    website: Optional[str] = Field(default=None, description="Official website URL")
    description: Optional[str] = Field(default=None, description="Factual description of what the company does")
    founded_year: Optional[str] = Field(default=None, description="Year the company was founded")
    headquarters: Optional[str] = Field(default=None, description="Headquarters location")
    employee_count: Optional[str] = Field(default=None, description="Number of employees or range")
    funding: Optional[str] = Field(default=None, description="Funding information if mentioned")
    products: Optional[List[ProductInfo]] = Field(default_factory=list, description="List of products")
    services: Optional[List[ServiceInfo]] = Field(default_factory=list, description="List of services")
    technology: Optional[TechnologyStack] = Field(default=None, description="Technologies detected")
    social_links: Optional[SocialLinks] = Field(default=None, description="Social media links")
    raw_contact_info: Optional[str] = Field(default=None, description="Any contact email or phone found")
    pages_crawled: Optional[List[str]] = Field(default_factory=list, description="List of pages that were crawled")


# ---------------------------------------------------------------------------
# Stage 2 — Final enriched output schema
# ---------------------------------------------------------------------------

class CompanyProfile(BaseModel):
    name: Optional[str] = Field(default=None, description="Official company name")
    website: Optional[str] = Field(default=None, description="Official website URL")
    domain: Optional[str] = Field(default=None, description="Company domain")
    description: Optional[str] = Field(default=None, description="Factual description of what the company does")
    founded_year: Optional[str] = Field(default=None, description="Year founded")
    headquarters: Optional[str] = Field(default=None, description="Headquarters location")
    employee_count: Optional[str] = Field(default=None, description="Employee count or range")
    funding: Optional[str] = Field(default=None, description="Funding details")


class BusinessIntelligence(BaseModel):
    industry: Optional[str] = Field(default=None, description="Primary industry (e.g. Software, Healthcare)")
    sector: Optional[str] = Field(default=None, description="Sector (e.g. B2B SaaS, Consumer Tech)")
    business_model: Optional[str] = Field(default=None, description="Business model (e.g. SaaS, Marketplace, Consulting)")
    revenue_model: Optional[str] = Field(default=None, description="Revenue model (e.g. Subscription, Usage-based, One-time)")
    pricing_model: Optional[str] = Field(default=None, description="Pricing approach (e.g. Freemium, Enterprise, Self-serve)")
    target_market: Optional[str] = Field(default=None, description="Primary target market (e.g. Enterprise, SMB, Developer)")
    customer_segment: Optional[str] = Field(default=None, description="Customer segment (e.g. Developers, HR Teams, CFOs)")
    sales_strategy: Optional[str] = Field(default=None, description="Sales motion (e.g. PLG, SLG, Channel)")


class CustomerIntelligence(BaseModel):
    target_customers: Optional[List[str]] = Field(default_factory=list, description="Types of target customers")
    customer_segments: Optional[List[str]] = Field(default_factory=list, description="Customer segments served")
    industries_served: Optional[List[str]] = Field(default_factory=list, description="Industries the company serves")


class GrowthSignals(BaseModel):
    hiring: Optional[bool] = Field(default=None, description="Is the company actively hiring?")
    funding_raised: Optional[str] = Field(default=None, description="Recent funding details if any")
    new_products: Optional[List[str]] = Field(default_factory=list, description="Recently launched products")
    expansions: Optional[List[str]] = Field(default_factory=list, description="Geographic or market expansions")
    partnerships: Optional[List[str]] = Field(default_factory=list, description="Strategic partnerships announced")
    acquisitions: Optional[List[str]] = Field(default_factory=list, description="Recent acquisitions")


class CompetitorInfo(BaseModel):
    name: Optional[str] = Field(default=None, description="Competitor company name")
    positioning: Optional[str] = Field(default=None, description="How the company positions against this competitor")


class NewsItem(BaseModel):
    headline: Optional[str] = Field(default=None, description="News headline")
    summary: Optional[str] = Field(default=None, description="Brief summary of the news")
    category: Optional[str] = Field(default=None, description="Category: Funding, Product, Expansion, Hiring, Partnership")
    date: Optional[str] = Field(default=None, description="Date of the news item if available")


class CompanyResearch(BaseModel):
    """
    Final structured output produced by the Research Agent.
    Contains full company intelligence organized into nested sections.
    """
    company: Optional[CompanyProfile] = Field(default=None, description="Core company profile")
    business: Optional[BusinessIntelligence] = Field(default=None, description="Business intelligence")
    products: Optional[List[ProductInfo]] = Field(default_factory=list, description="Product intelligence")
    services: Optional[List[ServiceInfo]] = Field(default_factory=list, description="Service intelligence")
    technology: Optional[TechnologyStack] = Field(default=None, description="Technology stack")
    customers: Optional[CustomerIntelligence] = Field(default=None, description="Customer intelligence")
    competitors: Optional[List[CompetitorInfo]] = Field(default_factory=list, description="Known competitors")
    growth_signals: Optional[GrowthSignals] = Field(default=None, description="Growth signals")
    recent_news: Optional[List[NewsItem]] = Field(default_factory=list, description="Recent news items")
    social_links: Optional[SocialLinks] = Field(default=None, description="Social media links")
    sources: Optional[List[str]] = Field(default_factory=list, description="Source URLs used")
    executive_summary: Optional[str] = Field(default=None, description="High-quality executive summary of the company")
