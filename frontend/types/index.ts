export interface Website {
  id: string;
  domain: string;
  name?: string | null;
  verified: boolean;
  verification_token?: string | null;
  created_at?: string;
  updated_at?: string;
  last_scan_score?: number | null;
}

export interface CrawlJob {
  id: string;
  website_id: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  pages_crawled: number;
  pages_total?: number | null;
  cancellation_requested?: boolean;
  cancelled_at?: string | null;
  created_at: string;
  completed_at?: string | null;
}

export interface SEOIssue {
  severity: "critical" | "warning" | "info";
  message: string;
  suggestion?: string;
}

export interface PageResult {
  id: string;
  url: string;
  title: string | null;
  seo_score: number | null;
  word_count: number | null;
  issues: SEOIssue[];
}

export interface CrawlReport {
  crawl_job: {
    id: string;
    status: string;
    created_at: string;
    completed_at?: string | null;
  };
  summary: {
    avg_score: number;
    total_issues: number;
    critical_issues: number;
    pages_analyzed: number;
  };
  pages: PageResult[];
}

export type ImplementationStatus = "pending" | "in_progress" | "completed" | "dismissed";

export interface AIRecommendation {
  id: string;
  priority: "high" | "medium" | "low";
  implementation_status: ImplementationStatus;
  title: string;
  description: string;
  recommendation_type: string;
}

export interface DashboardStats {
  website_count: number;
  scans_this_month: number;
  avg_seo_score: number | null;
  total_pages_scanned: number;
  recent_scans: Array<{
    id: string;
    website_id: string;
    website_name: string;
    website_domain: string;
    pages_crawled: number;
    completed_at: string;
  }>;
}

export interface WebsiteVerificationResult {
  verified: boolean;
  message?: string;
}

export interface RecommendationSummary {
  total: number;
  by_priority: Record<string, number>;
  by_status: Record<string, number>;
}

export interface ScoreHistoryPoint {
  crawl_id: string;
  date: string;
  avg_score: number;
  pages_count: number;
}
