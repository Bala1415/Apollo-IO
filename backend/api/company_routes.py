import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, Query, Request, Security
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.User import User
from backend.security.dependencies import require_permissions
from backend.schemas.response import StandardResponse, success_response
from backend.schemas.company import CompanyResponse, CompanySearchResponse

router = APIRouter(prefix="/companies", tags=["Companies"])
logger = logging.getLogger(__name__)

@router.get("/search", response_model=StandardResponse[CompanySearchResponse])
async def search_companies(
    request: Request,
    q: str = Query(..., description="Search query for domain or company name"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Security(require_permissions(["company:read"])),
    db: Session = Depends(get_db)
):
    """
    Searches the companies repository.
    """
    correlation_id = getattr(request.state, "correlation_id", None)
    
    # Stub for searching companies logic
    results = CompanySearchResponse(
        companies=[
            CompanyResponse(
                id=uuid.uuid4(),
                domain=f"{q}.com",
                name=q.capitalize(),
                industry="Software",
                technologies=["React", "Python"]
            )
        ],
        total_count=1
    )
    
    return success_response(
        data=results, 
        trace_id=correlation_id,
        metadata={"page": page, "size": size}
    )

@router.get("/{company_id}", response_model=StandardResponse[CompanyResponse])
async def get_company(
    company_id: uuid.UUID,
    request: Request,
    current_user: User = Security(require_permissions(["company:read"])),
    db: Session = Depends(get_db)
):
    """
    Retrieves a specific company profile by ID.
    """
    correlation_id = getattr(request.state, "correlation_id", None)
    
    # Stub for fetching company
    company = CompanyResponse(
        id=company_id,
        domain="example.com",
        name="Example Corp",
        industry="Enterprise Software",
        employee_count=500,
        estimated_revenue="$10M-$50M",
        technologies=["AWS", "FastAPI"]
    )
    
    return success_response(data=company, trace_id=correlation_id)
