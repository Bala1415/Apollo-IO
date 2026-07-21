export interface PaginationParams {
  page: number;
  size: number;
}

export interface LeadSummary {
  lead_id: string;
  email: string;
  company_domain: string;
  status: string | null;
  score: number | null;
  confidence: number | null;
  qualified: boolean | null;
  created_at: string;
}

export interface LeadListResponse {
  total_count: number;
  page: number;
  size: number;
  items: LeadSummary[];
}

export interface LeadDetails {
  lead_id: string;
  email: string;
  company_domain: string;
  status: string | null;
  created_at: string;
  score: number | null;
  confidence: number | null;
  qualification_status: boolean | null;
  qualification_reason: string | null;
  company_profile: any;
  industry_classification: any;
  recommendation: any;
}

export interface StatisticsResponse {
  total_leads: number;
  qualified_leads: number;
  unqualified_leads: number;
  high_score_leads: number;
  average_score: number;
  leads_by_status: Record<string, number>;
}

export interface AnalyticsResponse {
  top_industries: Record<string, number>;
  score_distribution: Record<string, number>;
}

export interface OverviewResponse {
  statistics: StatisticsResponse;
  recent_leads: LeadSummary[];
}
