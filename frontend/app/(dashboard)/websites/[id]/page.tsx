"use client";

import { useCallback, useEffect, useState, useRef } from "react";
import { useAuth } from "@clerk/nextjs";
import { useParams, useRouter } from "next/navigation";
import { Play, Clock, CheckCircle, XCircle, ArrowLeft, ExternalLink, RefreshCw, X } from "lucide-react";
import toast from "react-hot-toast";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { WebsiteDetailSkeleton } from "@/components/dashboard/WebsiteDetailSkeleton";
import { ScoreHistoryChart } from "@/components/dashboard/ScoreHistoryChart";
import { websitesAPI, crawlsAPI } from "@/lib/api";
import type { Website, CrawlJob, ScoreHistoryPoint } from "@/types";

export default function WebsiteDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { getToken, isLoaded } = useAuth();
  const [website, setWebsite] = useState<Website | null>(null);
  const [crawls, setCrawls] = useState<CrawlJob[]>([]);
  const [scoreHistory, setScoreHistory] = useState<ScoreHistoryPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCrawling, setIsCrawling] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);
  const [error, setError] = useState("");
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const previousCrawlStatusRef = useRef<string | null>(null);

  const websiteId = params.id as string;

  const loadData = useCallback(async (silent = false) => {
    try {
      const token = await getToken();
      if (!token) return;

      const [websiteData, crawlsData, scoreHistoryData] = await Promise.all([
        websitesAPI.get(token, websiteId),
        crawlsAPI.getHistory(token, websiteId),
        crawlsAPI.getScoreHistory(token, websiteId),
      ]);

      setWebsite(websiteData);
      setCrawls(crawlsData);
      setScoreHistory(scoreHistoryData);
    } catch (err) {
      if (!silent) {
        setError(err instanceof Error ? err.message : "Failed to load website");
      }
    } finally {
      setIsLoading(false);
    }
  }, [getToken, websiteId]);

  // Poll for crawl updates when there's an active crawl
  useEffect(() => {
    const latestCrawl = crawls[0];
    const hasActiveCrawl = crawls.some(
      (crawl) => crawl.status === "pending" || crawl.status === "running"
    );

    // Detect status changes and show notifications
    if (latestCrawl && previousCrawlStatusRef.current) {
      const previousStatus = previousCrawlStatusRef.current;
      const currentStatus = latestCrawl.status;

      if (previousStatus !== currentStatus) {
        if (currentStatus === "completed") {
          toast.success(`Scan completed! ${latestCrawl.pages_crawled} pages analyzed`);
        } else if (currentStatus === "failed") {
          toast.error("Scan failed. Please try again");
        } else if (currentStatus === "cancelled") {
          toast("Scan cancelled", { icon: "🛑" });
        }
      }
    }

    // Update previous status
    if (latestCrawl) {
      previousCrawlStatusRef.current = latestCrawl.status;
    }

    if (hasActiveCrawl && !pollingIntervalRef.current) {
      // Start polling every 3 seconds
      pollingIntervalRef.current = setInterval(() => {
        loadData(true); // Silent reload to avoid showing errors during polling
      }, 3000);
    } else if (!hasActiveCrawl && pollingIntervalRef.current) {
      // Stop polling when no active crawls
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }

    // Cleanup on unmount
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [crawls, loadData]);

  useEffect(() => {
    if (isLoaded && websiteId) {
      loadData();
    }
  }, [isLoaded, websiteId, loadData]);

  const handleStartCrawl = async () => {
    if (isCrawling) return;

    setIsCrawling(true);
    setError("");

    try {
      const token = await getToken();
      if (!token) return;

      await crawlsAPI.start(token, websiteId);

      // Reload crawl history
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start crawl");
    } finally {
      setIsCrawling(false);
    }
  };

  const handleCancelCrawl = async () => {
    if (!latestCrawl || isCancelling) return;

    setIsCancelling(true);
    setError("");

    try {
      const token = await getToken();
      if (!token) return;

      await crawlsAPI.cancel(token, latestCrawl.id);
      toast("Cancellation requested", { icon: "⏸️" });

      // Reload crawl history
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to cancel crawl");
      toast.error("Failed to cancel crawl");
    } finally {
      setIsCancelling(false);
    }
  };

  if (isLoading) {
    return <WebsiteDetailSkeleton />;
  }

  if (!website) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold mb-2">Website not found</h2>
        <Button onClick={() => router.push("/websites")}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Websites
        </Button>
      </div>
    );
  }

  const latestCrawl = crawls[0];
  const isRunning = latestCrawl?.status === "pending" || latestCrawl?.status === "running";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push("/websites")}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h2 className="text-3xl font-bold tracking-tight">
              {website.name || website.domain}
            </h2>
            <div className="flex items-center gap-2 mt-1">
              <p className="text-muted-foreground">{website.domain}</p>
              <a
                href={`https://${website.domain}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          {isRunning && (
            <Button
              onClick={handleCancelCrawl}
              disabled={isCancelling}
              variant="outline"
            >
              <X className="h-4 w-4 mr-2" />
              {isCancelling ? "Cancelling..." : "Cancel"}
            </Button>
          )}
          <Button
            onClick={handleStartCrawl}
            disabled={isRunning || isCrawling}
          >
            {isRunning || isCrawling ? (
              <>
                <Clock className="h-4 w-4 mr-2 animate-spin" />
                Crawling...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Run SEO Scan
              </>
            )}
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-4 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 rounded-md">
          {error}
        </div>
      )}

      {/* Verification Status */}
      <Card>
        <CardHeader>
          <CardTitle>Domain Verification</CardTitle>
          <CardDescription>
            Verify ownership of your domain
          </CardDescription>
        </CardHeader>
        <CardContent>
          {website.verified ? (
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle className="h-5 w-5" />
              <span className="font-medium">Domain verified</span>
            </div>
          ) : (
            <div>
              <div className="flex items-center gap-2 text-orange-600 mb-4">
                <XCircle className="h-5 w-5" />
                <span className="font-medium">Domain not verified</span>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                You can still run scans, but verification is recommended for full access.
              </p>
              {website.verification_token && (
                <div className="p-3 bg-muted rounded-md">
                  <p className="text-sm font-medium mb-2">Verification Token:</p>
                  <code className="text-xs bg-background px-2 py-1 rounded">
                    {website.verification_token}
                  </code>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Latest Crawl */}
      {latestCrawl && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Latest Scan</CardTitle>
                <CardDescription>
                  Most recent SEO analysis results
                </CardDescription>
              </div>
              {isRunning && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                  <span>Auto-refreshing</span>
                </div>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <div className="flex items-center gap-2 mt-1">
                    {latestCrawl.status === "completed" && (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    )}
                    {latestCrawl.status === "running" && (
                      <Clock className="h-4 w-4 text-blue-600 animate-spin" />
                    )}
                    {latestCrawl.status === "failed" && (
                      <XCircle className="h-4 w-4 text-red-600" />
                    )}
                    {latestCrawl.status === "cancelled" && (
                      <XCircle className="h-4 w-4 text-orange-600" />
                    )}
                    <span className="font-medium capitalize">{latestCrawl.status}</span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Pages Crawled</p>
                  <p className="text-2xl font-bold mt-1">
                    {latestCrawl.pages_crawled}
                    {latestCrawl.pages_total && ` / ${latestCrawl.pages_total}`}
                  </p>
                </div>
              </div>

              {/* Progress bar when running */}
              {isRunning && latestCrawl.pages_total && latestCrawl.pages_total > 0 && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>Progress</span>
                    <span>
                      {Math.round((latestCrawl.pages_crawled / latestCrawl.pages_total) * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-primary h-2 transition-all duration-300"
                      style={{
                        width: `${Math.min((latestCrawl.pages_crawled / latestCrawl.pages_total) * 100, 100)}%`,
                      }}
                    />
                  </div>
                </div>
              )}

              {latestCrawl.status === "completed" && (
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => router.push(`/reports/${latestCrawl.id}`)}
                >
                  View Full Report
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Score History Chart */}
      {scoreHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>SEO Score Trend</CardTitle>
            <CardDescription>
              Track your website&apos;s SEO score improvement over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScoreHistoryChart data={scoreHistory} />
          </CardContent>
        </Card>
      )}

      {/* Crawl History */}
      <Card>
        <CardHeader>
          <CardTitle>Scan History</CardTitle>
          <CardDescription>
            All SEO scans for this website
          </CardDescription>
        </CardHeader>
        <CardContent>
          {crawls.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No scans yet. Click &quot;Run SEO Scan&quot; to get started.
            </p>
          ) : (
            <div className="space-y-3">
              {crawls.map((crawl) => (
                <div
                  key={crawl.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      {crawl.status === "completed" && (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      )}
                      {crawl.status === "running" && (
                        <Clock className="h-4 w-4 text-blue-600 animate-spin" />
                      )}
                      {crawl.status === "failed" && (
                        <XCircle className="h-4 w-4 text-red-600" />
                      )}
                      {crawl.status === "cancelled" && (
                        <XCircle className="h-4 w-4 text-orange-600" />
                      )}
                      <span className="font-medium capitalize">{crawl.status}</span>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {new Date(crawl.created_at).toLocaleString()} • {crawl.pages_crawled} pages
                    </p>
                  </div>
                  {crawl.status === "completed" && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => router.push(`/reports/${crawl.id}`)}
                    >
                      View Report
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
