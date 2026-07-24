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

export interface CompanyProfileData {
  description?: string;
  company_size?: string;
  tech_stack?: string[];
  locations?: string[];
}

export interface IndustryClassificationData {
  industry?: string;
  vertical?: string;
  tags?: string[];
}

export interface RecommendationData {
  priority?: 'High' | 'Medium' | 'Low';
  reason?: string;
  next_action?: string;
}

export interface CompanyResearchData {
  recent_news?: string[];
  sentiment_score?: number;
  key_executives?: string[];
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
  company_profile: CompanyProfileData | null;
  industry_classification: IndustryClassificationData | null;
  recommendation: RecommendationData | null;
  company_research: CompanyResearchData | null;
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
