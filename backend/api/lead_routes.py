from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.raw_lead import RawLead
from backend.services.langgraph_service import run_lead_analysis

router = APIRouter()

@router.post("/")
def create_lead(lead_data: dict, db: Session = Depends(get_db)):
    try:
        new_lead = RawLead(
            email=lead_data.get("email"),
            company_domain=lead_data.get("company_domain"),
            browser_history=lead_data.get("browser_history", {}),
            interest_summary=lead_data.get("interest_summary", {}),
            status="new"
        )
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        
        # Trigger AI analysis asynchronously or synchronously
        # For now we do it synchronously to return the results
        ai_result = run_lead_analysis(
            company_domain=new_lead.company_domain,
            email=new_lead.email,
            browser_history=new_lead.browser_history
        )
        
        return {
            "status": "success", 
            "lead_id": new_lead.lead_id,
            "ai_analysis": ai_result
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
def get_leads(db: Session = Depends(get_db)):
    leads = db.query(RawLead).all()
    return {"leads": leads}
