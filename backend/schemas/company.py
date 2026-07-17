from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import uuid

class CompanyResponse(BaseModel):
    """Schema representing a company profile."""
    id: uuid.UUID
    domain: str
    name: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    estimated_revenue: Optional[str] = None
    technologies: List[str] = []

class CompanySearchResponse(BaseModel):
    """Schema for company search results."""
    companies: List[CompanyResponse]
    total_count: int
