import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import dotenv
dotenv.load_dotenv()

from backend.database.session import SessionLocal
from backend.models.raw_lead import RawLead
from backend.models.lead_score import LeadScore
from backend.models.lead_qualification import LeadQualification
from backend.models.company_profile import CompanyProfile
from backend.models.industry_classification import IndustryClassification
from backend.models.recommendation import Recommendation
from backend.models.company_research import CompanyResearch
from backend.services.langgraph_service import run_lead_analysis

def reprocess_leads():
    db = SessionLocal()
    leads = db.query(RawLead).all()
    
    for lead in leads:
        print(f"Reprocessing AI pipeline for {lead.email}...")
        
        # Run AI
        ai_result = run_lead_analysis(
            company_domain=lead.company_domain,
            email=lead.email,
            browser_history=lead.browser_history
        )
        
        # Clear old data if exists
        db.query(LeadScore).filter(LeadScore.lead_id == lead.lead_id).delete()
        db.query(LeadQualification).filter(LeadQualification.lead_id == lead.lead_id).delete()
        db.query(CompanyProfile).filter(CompanyProfile.lead_id == lead.lead_id).delete()
        db.query(IndustryClassification).filter(IndustryClassification.lead_id == lead.lead_id).delete()
        db.query(CompanyResearch).filter(CompanyResearch.lead_id == lead.lead_id).delete()
        db.query(Recommendation).filter(Recommendation.lead_id == lead.lead_id).delete()
        
        # Persist Agent Outputs
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
        print(f"Successfully generated and saved AI results for {lead.email}!")

if __name__ == "__main__":
    reprocess_leads()
