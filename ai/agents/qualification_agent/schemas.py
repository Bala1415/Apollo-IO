from typing import List
from pydantic import BaseModel, Field

class LeadQualification(BaseModel):
    qualified: bool = Field(
        description="Whether the company is a qualified sales lead based on the criteria."
    )
    qualification_reason: str = Field(
        description="A detailed explanation of why the company is or is not qualified."
    )
    matching_features: List[str] = Field(
        description="List of ICP matches or positive signals (e.g., matching industry, AI adoption potential)."
    )
    missing_features: List[str] = Field(
        description="List of missing criteria or negative signals that detract from qualification."
    )
    confidence: float = Field(
        description="Confidence score for this qualification assessment, ranging from 0.0 to 1.0."
    )
