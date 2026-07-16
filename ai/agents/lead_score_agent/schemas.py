from pydantic import BaseModel, Field

class LeadScore(BaseModel):
    lead_score: int = Field(
        description="The final calculated lead score from 0 to 100 based on the weighted criteria.",
        ge=0,
        le=100
    )
    confidence: int = Field(
        description="Confidence level in the calculated score from 0 to 100.",
        ge=0,
        le=100
    )
