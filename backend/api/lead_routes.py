from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.raw_lead import RawLead
from backend.models.lead_score import LeadScore
from backend.models.lead_qualification import LeadQualification
from backend.models.company_profile import CompanyProfile
from backend.models.industry_classification import IndustryClassification
from backend.models.recommendation import Recommendation
from backend.models.company_research import CompanyResearch
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
        
        # Trigger AI analysis synchronously
        ai_result = run_lead_analysis(
            company_domain=new_lead.company_domain,
            email=new_lead.email,
            browser_history=new_lead.browser_history
        )
        
        # Persist Agent Outputs to Database
        if ai_result.get("lead_score"):
            ls_data = ai_result["lead_score"]
            db.add(LeadScore(lead_id=new_lead.lead_id, score=ls_data.get("score"), confidence=ls_data.get("confidence")))
            
        if ai_result.get("qualification"):
            q_data = ai_result["qualification"]
            db.add(LeadQualification(lead_id=new_lead.lead_id, qualified=q_data.get("qualified", False), reason=q_data.get("reason")))
            
        if ai_result.get("company_fit"):
            cf_data = ai_result["company_fit"]
            db.add(CompanyProfile(lead_id=new_lead.lead_id, description=cf_data.get("description"), company_size=cf_data.get("company_size"), tech_stack=cf_data.get("tech_stack", []), locations=cf_data.get("locations", [])))
            db.add(IndustryClassification(lead_id=new_lead.lead_id, industry=cf_data.get("industry"), sector=cf_data.get("vertical")))
            
        if ai_result.get("research"):
            r_data = ai_result["research"]
            db.add(CompanyResearch(lead_id=new_lead.lead_id, news=r_data.get("recent_news", [])))
            
        if ai_result.get("recommendation"):
            rec_data = ai_result["recommendation"]
            db.add(Recommendation(lead_id=new_lead.lead_id, priority=rec_data.get("priority"), reason=rec_data.get("reason"), next_action=rec_data.get("next_action")))
        
        # Update status
        new_lead.status = "processed"
        db.commit()
        
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

@router.put("/{lead_id}")
def update_lead(lead_id: str, update_data: dict, db: Session = Depends(get_db)):
    lead = db.query(RawLead).filter(RawLead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    if "company_domain" in update_data:
        lead.company_domain = update_data["company_domain"]
    if "email" in update_data:
        lead.email = update_data["email"]
        
    db.commit()
    db.refresh(lead)
    return {"status": "success", "message": "Lead updated successfully"}

@router.post("/{lead_id}/analyze")
def analyze_lead(lead_id: str, db: Session = Depends(get_db)):
    lead = db.query(RawLead).filter(RawLead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    try:
        # 1. Run AI analysis
        ai_result = run_lead_analysis(
            company_domain=lead.company_domain,
            email=lead.email,
            browser_history=lead.browser_history
        )
        
        # 2. Clear old data if exists
        db.query(LeadScore).filter(LeadScore.lead_id == lead.lead_id).delete()
        db.query(LeadQualification).filter(LeadQualification.lead_id == lead.lead_id).delete()
        db.query(CompanyProfile).filter(CompanyProfile.lead_id == lead.lead_id).delete()
        db.query(IndustryClassification).filter(IndustryClassification.lead_id == lead.lead_id).delete()
        db.query(CompanyResearch).filter(CompanyResearch.lead_id == lead.lead_id).delete()
        db.query(Recommendation).filter(Recommendation.lead_id == lead.lead_id).delete()
        
        # 3. Persist new Agent Outputs
        if ai_result.get("lead_score"):
            ls_data = ai_result["lead_score"]
            db.add(LeadScore(lead_id=lead.lead_id, score=ls_data.get("score"), confidence=ls_data.get("confidence")))
            
        if ai_result.get("qualification"):
            q_data = ai_result["qualification"]
            db.add(LeadQualification(lead_id=lead.lead_id, qualified=q_data.get("qualified", False), reason=q_data.get("reason")))
            
        if ai_result.get("company_fit"):
            cf_data = ai_result["company_fit"]
            db.add(CompanyProfile(lead_id=lead.lead_id, description=cf_data.get("description"), company_size=cf_data.get("company_size"), tech_stack=cf_data.get("tech_stack", []), locations=cf_data.get("locations", [])))
            db.add(IndustryClassification(lead_id=lead.lead_id, industry=cf_data.get("industry"), sector=cf_data.get("vertical")))
            
        if ai_result.get("research"):
            r_data = ai_result["research"]
            db.add(CompanyResearch(lead_id=lead.lead_id, news=r_data.get("recent_news", [])))
            
        if ai_result.get("recommendation"):
            rec_data = ai_result["recommendation"]
            db.add(Recommendation(lead_id=lead.lead_id, priority=rec_data.get("priority"), reason=rec_data.get("reason"), next_action=rec_data.get("next_action")))
        
        lead.status = "processed"
        db.commit()
        
        return {"status": "success", "message": "AI Analysis complete"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
