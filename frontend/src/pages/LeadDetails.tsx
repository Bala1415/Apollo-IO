import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { dashboardService } from '../services/api';
import { LeadDetails as LeadDetailsType } from '../services/types';
import { ArrowLeft, Building2, Briefcase, Zap } from 'lucide-react';
import './LeadDetails.css';

const LeadDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [lead, setLead] = useState<LeadDetailsType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const fetchLead = async () => {
      try {
        const data = await dashboardService.getLeadDetails(id);
        setLead(data);
      } catch (error) {
        console.error("Failed to load lead details", error);
      } finally {
        setLoading(false);
      }
    };
    fetchLead();
  }, [id]);

  if (loading) return <div className="loading">Loading details...</div>;
  if (!lead) return <div className="error">Lead not found</div>;

  return (
    <div className="lead-details-container">
      <div className="back-nav" onClick={() => navigate('/leads')}>
        <ArrowLeft size={18} />
        <span>Back to Leads</span>
      </div>

      <div className="details-header card glass">
        <div className="header-main">
          <div className="profile-icon">
            <Building2 size={32} />
          </div>
          <div>
            <h1 className="text-2xl font-semibold mb-1">{lead.company_domain}</h1>
            <p className="text-secondary">{lead.email}</p>
          </div>
        </div>
        <div className="header-stats">
          <div className="stat-box">
            <span className="stat-title">AI Score</span>
            <span className={`stat-big ${lead.score && lead.score > 70 ? 'text-green' : ''}`}>
              {lead.score || 'N/A'}
            </span>
          </div>
          <div className="stat-box">
            <span className="stat-title">Status</span>
            <span className={`badge ${lead.qualification_status ? 'badge-success' : 'badge-warning'}`}>
              {lead.qualification_status ? 'Qualified' : 'Pending'}
            </span>
          </div>
        </div>
      </div>

      <div className="details-grid">
        <div className="card glass">
          <h3 className="section-title"><Briefcase size={18}/> Company Profile</h3>
          <div className="json-display">
            {lead.company_profile ? (
              <pre>{JSON.stringify(lead.company_profile, null, 2)}</pre>
            ) : (
              <p className="text-muted">No profile data available.</p>
            )}
          </div>
        </div>

        <div className="card glass">
          <h3 className="section-title"><Zap size={18}/> AI Recommendation</h3>
          <div className="json-display">
             {lead.recommendation ? (
              <pre>{JSON.stringify(lead.recommendation, null, 2)}</pre>
            ) : (
              <p className="text-muted">No recommendation generated yet.</p>
            )}
          </div>
          {lead.qualification_reason && (
             <div className="reason-box">
               <strong>Reasoning:</strong> {lead.qualification_reason}
             </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LeadDetails;
