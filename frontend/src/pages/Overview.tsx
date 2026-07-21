import { useEffect, useState } from 'react';
import { dashboardService } from '../services/api';
import { OverviewResponse } from '../services/types';
import { Target, Users, TrendingUp, ShieldCheck } from 'lucide-react';
import './Overview.css';

const Overview = () => {
  const [data, setData] = useState<OverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOverview = async () => {
      try {
        const response = await dashboardService.getOverview();
        setData(response);
      } catch (error) {
        console.error("Failed to load overview data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchOverview();
  }, []);

  if (loading) return <div className="loading">Loading dashboard...</div>;
  if (!data) return <div className="error">Failed to load data. Make sure backend is running.</div>;

  const { statistics, recent_leads } = data;

  return (
    <div className="overview-container">
      <div className="page-header">
        <h1 className="text-2xl font-semibold">Dashboard Overview</h1>
        <p className="text-secondary">Welcome back. Here is what's happening with your leads today.</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card card">
          <div className="stat-icon bg-blue"><Users size={24} /></div>
          <div className="stat-content">
            <span className="stat-label">Total Leads</span>
            <span className="stat-value">{statistics.total_leads}</span>
          </div>
        </div>
        <div className="stat-card card">
          <div className="stat-icon bg-green"><ShieldCheck size={24} /></div>
          <div className="stat-content">
            <span className="stat-label">Qualified</span>
            <span className="stat-value">{statistics.qualified_leads}</span>
          </div>
        </div>
        <div className="stat-card card">
          <div className="stat-icon bg-purple"><TrendingUp size={24} /></div>
          <div className="stat-content">
            <span className="stat-label">High Score Leads</span>
            <span className="stat-value">{statistics.high_score_leads}</span>
          </div>
        </div>
        <div className="stat-card card">
          <div className="stat-icon bg-orange"><Target size={24} /></div>
          <div className="stat-content">
            <span className="stat-label">Avg. Lead Score</span>
            <span className="stat-value">{statistics.average_score.toFixed(1)}</span>
          </div>
        </div>
      </div>

      <div className="recent-leads section-card glass">
        <h2 className="text-lg font-semibold mb-4">Recently Processed Leads</h2>
        <div className="table-responsive">
          <table className="leads-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Company</th>
                <th>Score</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {recent_leads.map(lead => (
                <tr key={lead.lead_id}>
                  <td>{lead.email}</td>
                  <td>{lead.company_domain}</td>
                  <td>
                    <span className={`score-badge ${lead.score && lead.score > 70 ? 'high' : 'medium'}`}>
                      {lead.score || 'N/A'}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${lead.qualified ? 'badge-success' : 'badge-warning'}`}>
                      {lead.qualified ? 'Qualified' : 'Pending'}
                    </span>
                  </td>
                </tr>
              ))}
              {recent_leads.length === 0 && (
                <tr>
                  <td colSpan={4} className="text-center text-muted">No recent leads found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Overview;
