/**
 * API client for making requests to the DevSEO backend.
 * Handles authentication, error handling, request/response formatting, and retry logic.
 */

import type {
  Website,
  CrawlJob,
  CrawlReport,
  AIRecommendation,
  DashboardStats,
  WebsiteVerificationResult,
  RecommendationSummary,
  ScoreHistoryPoint,
} from "@/types";

// Use Next.js proxy to avoid CORS issues in development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api/backend";

export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public details?: unknown
  ) {
    super(message);
    this.name = "APIError";
  }
}

/**
 * Retry configuration
 */
const RETRY_CONFIG = {
  maxRetries: 3,
  initialDelay: 1000, // 1 second
  maxDelay: 10000, // 10 seconds
  backoffMultiplier: 2,
  retryableStatusCodes: [408, 429, 500, 502, 503, 504],
};

/**
 * Sleep utility for retry delays
 */
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Check if an error is retryable
 */
function isRetryable(error: APIError | Error): boolean {
  if (error instanceof APIError) {
    return RETRY_CONFIG.retryableStatusCodes.includes(error.statusCode);
  }
  // Network errors are retryable
  return true;
}

/**
 * Make an authenticated API request with retry logic.
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  retryCount = 0
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const config: RequestInit = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    // Try to parse response as JSON, fallback to text if it fails
    let data;
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      data = await response.json();
    } else {
      const text = await response.text();
      data = text ? { detail: text } : {};
    }

    if (!response.ok) {
      const error = new APIError(
        data.detail || `Request failed with status ${response.status}`,
        response.status,
        data
      );

      // Retry if the error is retryable and we haven't exceeded max retries
      if (retryCount < RETRY_CONFIG.maxRetries && isRetryable(error)) {
        const delay = Math.min(
          RETRY_CONFIG.initialDelay * Math.pow(RETRY_CONFIG.backoffMultiplier, retryCount),
          RETRY_CONFIG.maxDelay
        );

        console.log(`Retrying request to ${endpoint} after ${delay}ms (attempt ${retryCount + 1}/${RETRY_CONFIG.maxRetries})`);
        await sleep(delay);
        return apiRequest<T>(endpoint, options, retryCount + 1);
      }

      throw error;
    }

    return data;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    // Network errors - retry if we haven't exceeded max retries
    if (retryCount < RETRY_CONFIG.maxRetries) {
      const delay = Math.min(
        RETRY_CONFIG.initialDelay * Math.pow(RETRY_CONFIG.backoffMultiplier, retryCount),
        RETRY_CONFIG.maxDelay
      );

      console.log(`Retrying request to ${endpoint} after network error (attempt ${retryCount + 1}/${RETRY_CONFIG.maxRetries})`);
      await sleep(delay);
      return apiRequest<T>(endpoint, options, retryCount + 1);
    }

    throw new APIError("Network error - please check your connection", 0);
  }
}

/**
 * Make an authenticated API request with a token.
 */
async function authenticatedRequest<T>(
  endpoint: string,
  token: string,
  options: RequestInit = {}
): Promise<T> {
  return apiRequest<T>(endpoint, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * Get a user-friendly error message from an APIError
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof APIError) {
    // Map common status codes to user-friendly messages
    switch (error.statusCode) {
      case 401:
        return "Please sign in to continue";
      case 403:
        return "You don't have permission to perform this action";
      case 404:
        return "The requested resource was not found";
      case 429:
        return "Too many requests. Please try again in a moment";
      case 500:
        return "Server error. Our team has been notified";
      case 502:
      case 503:
      case 504:
        return "Service temporarily unavailable. Please try again";
      default:
        return error.message || "An unexpected error occurred";
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred";
}

// Auth API
export const authAPI = {
  register: async (data: {
    email: string;
    password: string;
    name?: string;
    locale?: string;
    timezone?: string;
  }) => {
    return apiRequest<{
      access_token: string;
      refresh_token: string;
      token_type: string;
      expires_in: number;
    }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  login: async (data: { email: string; password: string }) => {
    return apiRequest<{
      access_token: string;
      refresh_token: string;
      token_type: string;
      expires_in: number;
    }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  refreshToken: async (refreshToken: string) => {
    return apiRequest<{
      access_token: string;
      refresh_token: string;
      token_type: string;
      expires_in: number;
    }>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  },

  getMe: async (token: string) => {
    return authenticatedRequest<{
      id: string;
      email: string;
      name: string | null;
      avatar_url: string | null;
      locale: string;
      timezone: string;
      created_at: string;
      updated_at: string;
    }>("/auth/me", token);
  },
};

// Websites API
export const websitesAPI = {
  list: async (token: string) => {
    return authenticatedRequest<Website[]>("/websites", token);
  },

  create: async (token: string, data: { domain: string; name?: string }) => {
    return authenticatedRequest<Website>("/websites", token, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  get: async (token: string, websiteId: string) => {
    return authenticatedRequest<Website>(`/websites/${websiteId}`, token);
  },

  update: async (
    token: string,
    websiteId: string,
    data: { name?: string; settings?: Record<string, unknown> }
  ) => {
    return authenticatedRequest<Website>(`/websites/${websiteId}`, token, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  delete: async (token: string, websiteId: string) => {
    return authenticatedRequest<void>(`/websites/${websiteId}`, token, {
      method: "DELETE",
    });
  },

  verify: async (token: string, websiteId: string, method: string) => {
    return authenticatedRequest<WebsiteVerificationResult>(`/websites/${websiteId}/verify`, token, {
      method: "POST",
      body: JSON.stringify({ method }),
    });
  },
};

// Crawls API
export const crawlsAPI = {
  start: async (token: string, websiteId: string) => {
    return authenticatedRequest<CrawlJob>(
      `/crawls/websites/${websiteId}/crawl`,
      token,
      {
        method: "POST",
      }
    );
  },

  getStatus: async (token: string, crawlId: string) => {
    return authenticatedRequest<CrawlJob>(`/crawls/${crawlId}`, token);
  },

  getReport: async (token: string, crawlId: string) => {
    return authenticatedRequest<CrawlReport>(`/crawls/${crawlId}/report`, token);
  },

  getHistory: async (token: string, websiteId: string) => {
    return authenticatedRequest<CrawlJob[]>(
      `/crawls/websites/${websiteId}/history`,
      token
    );
  },

  cancel: async (token: string, crawlId: string) => {
    return authenticatedRequest<CrawlJob>(`/crawls/${crawlId}/cancel`, token, {
      method: "POST",
    });
  },

  getScoreHistory: async (token: string, websiteId: string) => {
    return authenticatedRequest<ScoreHistoryPoint[]>(
      `/crawls/websites/${websiteId}/score-history`,
      token
    );
  },

  exportCsv: async (token: string, crawlId: string) => {
    const response = await fetch(`${API_BASE_URL}/crawls/${crawlId}/export/csv`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new APIError(
        "Failed to export CSV",
        response.status
      );
    }

    // Get the blob and trigger download
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `seo-report-${crawlId}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  },
};

// Dashboard API
export const dashboardAPI = {
  getStats: async (token: string) => {
    return authenticatedRequest<DashboardStats>("/dashboard/stats", token);
  },
};

// Recommendations API
export const recommendationsAPI = {
  generate: async (
    token: string,
    crawlId: string,
    useAiAnalysis: boolean = false
  ) => {
    return authenticatedRequest<AIRecommendation[]>(
      `/crawls/${crawlId}/recommendations`,
      token,
      {
        method: "POST",
        body: JSON.stringify({ use_ai_analysis: useAiAnalysis }),
      }
    );
  },

  list: async (
    token: string,
    crawlId: string,
    priority?: string,
    status?: string
  ) => {
    const params = new URLSearchParams();
    if (priority) params.append("priority", priority);
    if (status) params.append("status_filter", status);

    const query = params.toString();
    const endpoint = `/crawls/${crawlId}/recommendations${
      query ? `?${query}` : ""
    }`;

    return authenticatedRequest<AIRecommendation[]>(endpoint, token);
  },

  getSummary: async (token: string, crawlId: string) => {
    return authenticatedRequest<RecommendationSummary>(
      `/crawls/${crawlId}/recommendations/summary`,
      token
    );
  },

  updateStatus: async (
    token: string,
    recommendationId: string,
    status: string
  ) => {
    return authenticatedRequest<AIRecommendation>(
      `/crawls/recommendations/${recommendationId}`,
      token,
      {
        method: "PATCH",
        body: JSON.stringify({ implementation_status: status }),
      }
    );
  },
};

export default apiRequest;
