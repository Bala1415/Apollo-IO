import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { dashboardService, leadsService } from '../services/api';
import { LeadDetails as LeadDetailsType } from '../services/types';
import { ArrowLeft, Building2, Briefcase, Zap, Globe, TrendingUp, ShieldAlert, CheckCircle } from 'lucide-react';
import './LeadDetails.css';

const LeadDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [lead, setLead] = useState<LeadDetailsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [editDomain, setEditDomain] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const fetchLead = async () => {
    try {
      const data = await dashboardService.getLeadDetails(id!);
      setLead(data);
      setEditDomain(data.company_domain || '');
      setEditEmail(data.email || '');
    } catch (error) {
      console.error("Failed to load lead details", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!id) return;
    fetchLead();
  }, [id]);

  const handleSave = async () => {
    try {
      setLoading(true);
      await leadsService.updateLead(id!, { company_domain: editDomain, email: editEmail });
      await fetchLead();
      setIsEditing(false);
    } catch (error) {
      alert("Failed to update lead");
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    try {
      setIsAnalyzing(true);
      await leadsService.analyzeLead(id!);
      await fetchLead();
    } catch (error) {
      alert("Failed to run analysis");
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (loading) return <div className="loading">Loading details...</div>;
  if (!lead) return <div className="error">Lead not found</div>;

  const scoreClass = lead.score && lead.score > 70 ? 'text-green' : (lead.score && lead.score > 40 ? 'text-yellow' : 'text-red');
  const qualificationClass = lead.qualification_status ? 'badge-success' : 'badge-danger';

  return (
    <div className="lead-details-container">
      <div className="back-nav flex justify-between items-center">
        <div className="flex items-center gap-2 cursor-pointer text-muted hover:text-white" onClick={() => navigate('/leads')}>
          <ArrowLeft size={18} />
          <span>Back to Leads</span>
        </div>
        <div className="flex gap-3">
          {isEditing ? (
            <button onClick={handleSave} className="btn-primary bg-emerald-600 hover:bg-emerald-700 px-4 py-2 rounded text-sm font-medium">Save Details</button>
          ) : (
            <button onClick={() => setIsEditing(true)} className="btn-outline px-4 py-2 rounded text-sm font-medium border border-gray-600">Edit Details</button>
          )}
          <button onClick={handleAnalyze} disabled={isAnalyzing} className="btn-primary bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium flex items-center gap-2">
            <Zap size={16} />
            {isAnalyzing ? "Analyzing..." : "Run AI Agents"}
          </button>
        </div>
      </div>

      <div className="details-header card glass">
        <div className="header-main">
          <div className="profile-icon">
            <Building2 size={32} />
          </div>
          <div>
            {isEditing ? (
              <div className="flex flex-col gap-2">
                <input 
                  type="text" 
                  value={editDomain} 
                  onChange={e => setEditDomain(e.target.value)} 
                  className="bg-[rgba(0,0,0,0.2)] border border-[rgba(255,255,255,0.1)] rounded px-2 py-1 text-lg font-semibold text-white focus:outline-none"
                  placeholder="Company Domain (e.g. stripe.com)"
                />
                <input 
                  type="email" 
                  value={editEmail} 
                  onChange={e => setEditEmail(e.target.value)} 
                  className="bg-[rgba(0,0,0,0.2)] border border-[rgba(255,255,255,0.1)] rounded px-2 py-1 text-sm text-secondary focus:outline-none"
                  placeholder="Lead Email"
                />
              </div>
            ) : (
              <>
                <h1 className="text-2xl font-semibold mb-1 text-gradient">
                  {lead.company_domain ? (
                    <a href={`https://${lead.company_domain}`} target="_blank" rel="noopener noreferrer" className="hover:underline">
                      {lead.company_domain}
                    </a>
                  ) : (
                    lead.email
                  )}
                </h1>
                <p className="text-secondary">{lead.email}</p>
              </>
            )}
          </div>
        </div>
        <div className="header-stats">
          <div className="stat-box text-center">
            <span className="stat-title block text-sm text-muted uppercase tracking-wider mb-1">Lead Score Agent</span>
            <span className={`stat-big text-3xl font-bold ${scoreClass}`}>
              {lead.score || 'N/A'}
            </span>
          </div>
          <div className="stat-box text-center">
            <span className="stat-title block text-sm text-muted uppercase tracking-wider mb-2">Qualification Agent</span>
            <span className={`badge ${qualificationClass}`}>
              {lead.qualification_status ? 'Qualified' : 'Unqualified'}
            </span>
          </div>
        </div>
      </div>

      <div className="details-grid grid gap-6" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))' }}>
        
        {/* Company Fit Agent Card */}
        <div className="card glass">
          <h3 className="section-title flex items-center gap-2 text-lg font-semibold mb-4 text-gradient">
            <Briefcase size={20}/> Company Fit Agent
          </h3>
          {lead.company_profile ? (
            <div className="space-y-4">
              <p className="text-sm leading-relaxed">{lead.company_profile.description || "No description available."}</p>
              
              {lead.company_profile.company_size && (
                <div className="mt-4">
                  <span className="text-xs text-muted uppercase">Company Size</span>
                  <p className="font-medium">{lead.company_profile.company_size}</p>
                </div>
              )}

              {lead.industry_classification && (
                <div className="mt-4">
                  <span className="text-xs text-muted uppercase">Industry & Vertical</span>
                  <p className="font-medium">{lead.industry_classification.industry} - {lead.industry_classification.vertical}</p>
                </div>
              )}
              
              {lead.company_profile.tech_stack && lead.company_profile.tech_stack.length > 0 && (
                <div className="mt-4">
                  <span className="text-xs text-muted uppercase block mb-2">Tech Stack</span>
                  <div className="flex flex-wrap gap-2">
                    {lead.company_profile.tech_stack.map((tech, i) => (
                      <span key={i} className="badge badge-info">{tech}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-muted text-sm italic">No profile data available.</p>
          )}
        </div>

        {/* Research Agent Card */}
        <div className="card glass">
          <h3 className="section-title flex items-center gap-2 text-lg font-semibold mb-4 text-gradient">
            <Globe size={20}/> Research Agent
          </h3>
          
          {lead.company_research ? (
            <div className="space-y-4">
              {lead.company_research.sentiment_score !== undefined && lead.company_research.sentiment_score !== null && (
                <div>
                  <span className="text-xs text-muted uppercase">Market Sentiment</span>
                  <div className="w-full bg-slate-800 rounded-full h-2 mt-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${Math.min(Math.max((lead.company_research.sentiment_score + 1) * 50, 0), 100)}%` }}></div>
                  </div>
                </div>
              )}
              
              {lead.company_research.recent_news && lead.company_research.recent_news.length > 0 && (
                <div className="mt-4">
                  <span className="text-xs text-muted uppercase block mb-2">Recent News Signals</span>
                  <ul className="list-disc pl-4 text-sm text-secondary space-y-1">
                    {lead.company_research.recent_news.slice(0, 3).map((news, i) => (
                      <li key={i}>{news}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <p className="text-muted text-sm italic">No research data available.</p>
          )}
        </div>

        {/* Qualification Agent Card */}
        <div className="card glass">
          <h3 className="section-title flex items-center gap-2 text-lg font-semibold mb-4 text-gradient">
            <ShieldAlert size={20}/> Qualification Agent
          </h3>
          
          <div>
            <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
              <span className={lead.qualification_status ? 'text-emerald-500' : 'text-rose-500'}>
                Decision Rationale
              </span>
            </h4>
            <p className="text-sm text-secondary bg-[rgba(0,0,0,0.2)] p-4 rounded-lg leading-relaxed">
              {lead.qualification_reason || "No rationale provided."}
            </p>
          </div>
        </div>

        {/* Recommendation Agent Card */}
        <div className="card glass">
          <h3 className="section-title flex items-center gap-2 text-lg font-semibold mb-4 text-gradient">
            <CheckCircle size={20}/> Recommendation Agent
          </h3>
          
          {lead.recommendation ? (
            <div>
              <div className="bg-[rgba(0,0,0,0.2)] p-4 rounded-lg">
                <div className="mb-3">
                  <span className="text-xs text-muted uppercase mr-2">Priority:</span>
                  <span className={`badge ${lead.recommendation.priority === 'High' ? 'badge-danger' : 'badge-info'}`}>
                    {lead.recommendation.priority}
                  </span>
                </div>
                <p className="text-sm text-secondary leading-relaxed mb-3">
                  <strong>Why:</strong> {lead.recommendation.reason}
                </p>
                <p className="text-sm text-primary font-medium p-3 bg-[rgba(59,130,246,0.1)] border border-[rgba(59,130,246,0.2)] rounded">
                  <strong>Next Action:</strong> {lead.recommendation.next_action}
                </p>
              </div>
            </div>
          ) : (
            <p className="text-muted text-sm italic">No recommendation generated yet.</p>
          )}
        </div>

      </div>
    </div>
  );
};

export default LeadDetails;
