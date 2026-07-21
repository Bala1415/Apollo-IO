from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
import uuid

class LeadAnalyzeRequest(BaseModel):
    """Schema for requesting a lead analysis/qualification."""
    email: EmailStr = Field(..., description="The lead's email address")
    company_domain: str = Field(..., description="The lead's company domain")
    browser_data: Dict[str, Any] = Field(default_factory=dict, description="Browsing behavior data")
    interest_profile: Dict[str, Any] = Field(default_factory=dict, description="Inferred interest profile")
    first_name: Optional[str] = Field(None, description="The lead's first name")
    last_name: Optional[str] = Field(None, description="The lead's last name")
    company_name: Optional[str] = Field(None, description="The lead's company name")
    website: Optional[str] = Field(None, description="The lead's company website")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional contextual data")

class LeadResponse(BaseModel):
    """Schema representing a single lead."""
    id: uuid.UUID
    email: str
    status: str
    score: Optional[float] = None
    company_id: Optional[uuid.UUID] = None

class LeadPatchRequest(BaseModel):
    """Schema for partially updating a lead."""
    status: Optional[str] = None
    notes: Optional[str] = None
