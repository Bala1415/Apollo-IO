import typing
import sqlalchemy.util.typing
sqlalchemy.util.typing.make_union_type = lambda *types: typing.Union[types]

from .raw_lead import RawLead
from .company_research import CompanyResearch
from .company_profile import CompanyProfile
from .industry_classification import IndustryClassification
from .lead_qualification import LeadQualification
from .lead_score import LeadScore
from .recommendation import Recommendation

__all__ = [
    "RawLead",
    "CompanyResearch",
    "CompanyProfile",
    "IndustryClassification",
    "LeadQualification",
    "LeadScore",
    "Recommendation",
]
