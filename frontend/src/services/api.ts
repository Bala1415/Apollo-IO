import axios from 'axios';
import { 
  OverviewResponse, 
  StatisticsResponse, 
  AnalyticsResponse, 
  LeadListResponse, 
  LeadDetails 
} from './types';

// Create axios instance pointing to the backend API
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Since the backend uses `current_user: User = Security(...)` which might require auth,
// For now we might need to pass a mock token or the backend might have auth disabled in dev mode.
// We'll attach a basic placeholder auth header if needed.
apiClient.interceptors.request.use((config) => {
  // config.headers.Authorization = `Bearer test-token`;
  return config;
});

export const dashboardService = {
  getOverview: async (): Promise<OverviewResponse> => {
    const { data } = await apiClient.get('/dashboard/overview');
    return data;
  },

  getStatistics: async (): Promise<StatisticsResponse> => {
    const { data } = await apiClient.get('/dashboard/statistics');
    return data;
  },

  getAnalytics: async (): Promise<AnalyticsResponse> => {
    const { data } = await apiClient.get('/dashboard/analytics');
    return data;
  },

  getLeads: async (params?: Record<string, any>): Promise<LeadListResponse> => {
    const { data } = await apiClient.get('/dashboard/leads', { params });
    return data;
  },

  getLeadDetails: async (leadId: string): Promise<LeadDetails> => {
    const { data } = await apiClient.get(`/dashboard/leads/${leadId}`);
    return data;
  },
  
  searchLeads: async (q: string, page = 1, size = 20): Promise<LeadListResponse> => {
    const { data } = await apiClient.get('/dashboard/search', { params: { q, page, size } });
    return data;
  }
};
