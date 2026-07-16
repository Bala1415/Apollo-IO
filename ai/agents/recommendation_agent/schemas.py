from pydantic import BaseModel, Field

class Recommendation(BaseModel):
    priority: str = Field(
        description="The priority of the lead, e.g., 'HOT', 'WARM', 'COLD'."
    )
    next_action: str = Field(
        description="Suggested next action for the sales team, e.g., 'Contact within 24 Hours'."
    )
    sales_pitch: str = Field(
        description="A tailored sales pitch or angle for the prospect based on their profile and research."
    )
    summary: str = Field(
        description="An executive summary describing the overall opportunity."
    )
