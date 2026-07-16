from typing import List, Optional
from pydantic import BaseModel, Field

class CompanyResearch(BaseModel):
    """
    Structured information about a company gathered by the Research Agent.
    """
    company_name: Optional[str] = Field(default=None, description="The official name of the company")
    website: Optional[str] = Field(default=None, description="The official website URL of the company")
    description: Optional[str] = Field(default=None, description="A brief, factual description of what the company does")
    products: Optional[List[str]] = Field(default_factory=list, description="List of main products offered by the company")
    services: Optional[List[str]] = Field(default_factory=list, description="List of services provided by the company")
    employee_count: Optional[str] = Field(default=None, description="Estimated number of employees")
    headquarters: Optional[str] = Field(default=None, description="Location of the company headquarters")
    funding: Optional[str] = Field(default=None, description="Information about company funding, if available")
    social_links: Optional[List[str]] = Field(default_factory=list, description="List of social media URLs (LinkedIn, Twitter, etc.)")
    recent_news: Optional[List[str]] = Field(default_factory=list, description="List of recent news headlines or summaries related to the company")
    sources: Optional[List[str]] = Field(default_factory=list, description="URLs of the sources used to gather this information")
