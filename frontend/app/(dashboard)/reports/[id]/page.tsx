"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, ExternalLink } from "lucide-react";
import toast from "react-hot-toast";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScoreGauge } from "@/components/dashboard/ScoreGauge";
import { IssuesList } from "@/components/dashboard/IssuesList";
import { ReportSkeleton } from "@/components/dashboard/ReportSkeleton";
import { RecommendationsCard } from "@/components/dashboard/RecommendationsCard";
import { crawlsAPI, recommendationsAPI } from "@/lib/api";
import type { CrawlReport, AIRecommendation } from "@/types";

export default function CrawlReportPage() {
  const params = useParams();
  const router = useRouter();
  const { getToken, isLoaded } = useAuth();
  const [report, setReport] = useState<CrawlReport | null>(null);
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedPage, setExpandedPage] = useState<string | null>(null);

  const crawlId = params.id as string;

  useEffect(() => {
    const loadReport = async () => {
      try {
        const token = await getToken();
        if (!token) return;

        const [reportData, recommendationsData] = await Promise.all([
          crawlsAPI.getReport(token, crawlId),
          recommendationsAPI.list(token, crawlId).catch(() => []), // Fail silently if no recommendations
        ]);

        setReport(reportData);
        setRecommendations(recommendationsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load report");
      } finally {
        setIsLoading(false);
      }
    };

    if (isLoaded && crawlId) {
      loadReport();
    }
  }, [isLoaded, crawlId, getToken]);

  const handleRecommendationStatusChange = async (
    recommendationId: string,
    status: string
  ) => {
    try {
      const token = await getToken();
      if (!token) return;

      await recommendationsAPI.updateStatus(token, recommendationId, status);

      // Update local state
      setRecommendations((prev) =>
        prev.map((rec) =>
          rec.id === recommendationId
            ? { ...rec, implementation_status: status as AIRecommendation["implementation_status"] }
            : rec
        )
      );

      toast.success(
        status === "completed"
          ? "Recommendation marked as completed"
          : "Recommendation dismissed"
      );
    } catch {
      toast.error("Failed to update recommendation status");
    }
  };

  if (isLoading) {
    return <ReportSkeleton />;
  }

  if (error || !report) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold mb-2">
          {error || "Report not found"}
        </h2>
        <Button onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Go Back
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.back()}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h2 className="text-3xl font-bold tracking-tight">SEO Report</h2>
            <p className="text-muted-foreground">
              {new Date(report.crawl_job.created_at).toLocaleDateString()} •{" "}
              {report.pages.length} pages analyzed
            </p>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Average Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center">
              <ScoreGauge score={Math.round(report.summary.avg_score)} size="sm" showLabel={false} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Issues
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{report.summary.total_issues}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Found across all pages
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Critical Issues
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">
              {report.summary.critical_issues}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Require immediate attention
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Pages Analyzed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{report.pages.length}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Successfully crawled
            </p>
          </CardContent>
        </Card>
      </div>

      {/* AI Recommendations */}
      <RecommendationsCard
        recommendations={recommendations}
        onStatusChange={handleRecommendationStatusChange}
      />

      {/* Pages List */}
      <Card>
        <CardHeader>
          <CardTitle>Analyzed Pages</CardTitle>
          <CardDescription>
            Click on a page to view detailed SEO issues
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {report.pages.map((page) => (
              <div key={page.id}>
                <div
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                  onClick={() =>
                    setExpandedPage(expandedPage === page.id ? null : page.id)
                  }
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3">
                      <ScoreGauge
                        score={page.seo_score || 0}
                        size="sm"
                        showLabel={false}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="font-medium truncate">{page.title || "Untitled"}</p>
                          <a
                            href={page.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:underline"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <ExternalLink className="h-3.5 w-3.5" />
                          </a>
                        </div>
                        <p className="text-sm text-muted-foreground truncate">
                          {page.url}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm font-medium">
                        {page.issues.length} issue{page.issues.length !== 1 ? "s" : ""}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {page.word_count || 0} words
                      </p>
                    </div>
                  </div>
                </div>

                {/* Expanded Issues */}
                {expandedPage === page.id && (
                  <div className="mt-3 p-4 border rounded-lg bg-muted/30">
                    <h4 className="font-semibold mb-4">SEO Issues</h4>
                    <IssuesList issues={page.issues} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
