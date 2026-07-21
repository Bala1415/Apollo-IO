import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import uuid

from backend.database.session import get_db
from backend.models.raw_lead import RawLead

router = APIRouter(prefix="/extension", tags=["Extension Ingestion"])
logger = logging.getLogger("apollo.api.extension")

# Pydantic schemas for the incoming Chrome extension payload
class PayloadUser(BaseModel):
    googleId: Optional[str] = None
    email: str
    companyDomain: Optional[str] = None
    displayName: Optional[str] = None

class BrowserPayload(BaseModel):
    id: str
    version: str
    timestamp: str
    user: PayloadUser
    device: Dict[str, Any] = Field(default_factory=dict)
    currentSession: Dict[str, Any] = Field(default_factory=dict)
    browsingSummary: Dict[str, Any] = Field(default_factory=dict)
    signals: Dict[str, Any] = Field(default_factory=dict)

@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_extension_data(payload: BrowserPayload, db: Session = Depends(get_db)):
    """
    Ingests AI insights collected locally by the Chrome Extension.
    Creates or updates a RawLead in the database.
    """
    logger.info(f"Received extension payload for {payload.user.email}")
    
    # Check if lead already exists
    existing_lead = db.query(RawLead).filter(RawLead.email == payload.user.email).first()
    
    if existing_lead:
        # Update existing lead's history and intent
        existing_lead.browser_history = payload.browsingSummary
        existing_lead.interest_summary = payload.signals
        existing_lead.company_domain = payload.user.companyDomain or existing_lead.company_domain
        logger.info(f"Updated existing lead {existing_lead.lead_id}")
    else:
        # Create new RawLead
        new_lead = RawLead(
            email=payload.user.email,
            company_domain=payload.user.companyDomain or "unknown.com",
            browser_history=payload.browsingSummary,
            interest_summary=payload.signals,
            status="new"
        )
        db.add(new_lead)
        logger.info(f"Created new RawLead for {payload.user.email}")
        
    db.commit()
    
    return {"status": "success", "message": "Payload ingested successfully"}
