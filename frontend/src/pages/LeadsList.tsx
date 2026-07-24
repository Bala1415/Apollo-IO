import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardService } from '../services/api';
import { LeadListResponse } from '../services/types';
import './LeadsList.css';

const LeadsList = () => {
  const [data, setData] = useState<LeadListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchLeads = async () => {
      setLoading(true);
      try {
        const response = await dashboardService.getLeads({ page, size: 20 });
        setData(response);
      } catch (error) {
        console.error("Failed to load leads:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchLeads();
  }, [page]);

  return (
    <div className="leads-list-container">
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold">Leads Directory</h1>
          <p className="text-secondary">Browse and filter all processed leads.</p>
        </div>
      </div>

      <div className="card glass leads-table-wrapper mt-6">
        {loading && <div className="loading-overlay">Loading...</div>}
        
        <table className="leads-table interactive">
          <thead>
            <tr>
              <th>Lead Email</th>
              <th>Domain</th>
              <th>Status</th>
              <th>AI Score</th>
              <th>Confidence</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map(lead => (
              <tr key={lead.lead_id} onClick={() => navigate(`/leads/${lead.lead_id}`)}>
                <td className="font-medium">{lead.email}</td>
                <td className="text-secondary">{lead.company_domain}</td>
                <td>
                  <span className={`badge ${lead.qualified ? 'badge-success' : 'badge-warning'}`}>
                    {lead.qualified ? 'Qualified' : (lead.status || 'Pending')}
                  </span>
                </td>
                <td>
                  <span className={`score-badge ${lead.score && lead.score > 70 ? 'high' : ''}`}>
                    {lead.score || 'N/A'}
                  </span>
                </td>
                <td>{lead.confidence ? `${(lead.confidence * 100).toFixed(0)}%` : '-'}</td>
                <td className="text-muted">{new Date(lead.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
        
        <div className="pagination">
          <button 
            disabled={page === 1} 
            onClick={() => setPage(p => p - 1)}
            className="btn-outline"
          >
            Previous
          </button>
          <span className="page-info">Page {page}</span>
          <button 
            disabled={data ? data.items.length < 20 : true} 
            onClick={() => setPage(p => p + 1)}
            className="btn-outline"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default LeadsList;
