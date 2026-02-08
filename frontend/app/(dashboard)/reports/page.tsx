"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { FileText, Download, Calendar, Globe, AlertCircle } from "lucide-react";
import toast from "react-hot-toast";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { websitesAPI, crawlsAPI } from "@/lib/api";
import type { Website, CrawlJob } from "@/types";

interface ReportItem {
  crawlId: string;
  websiteId: string;
  websiteName: string;
  websiteDomain: string;
  date: string;
  pagesCount: number;
  status: string;
}

export default function ReportsPage() {
  const router = useRouter();
  const { getToken, isLoaded } = useAuth();
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadReports = useCallback(async () => {
    try {
      const token = await getToken();
      if (!token) return;

      // Fetch all websites
      const websites = await websitesAPI.list(token);

      // Fetch crawl history for each website in parallel
      const crawlHistories = await Promise.all(
        websites.map((website) =>
          crawlsAPI.getHistory(token, website.id).catch(() => [] as CrawlJob[])
        )
      );

      // Flatten and transform into report items
      const allReports: ReportItem[] = [];
      websites.forEach((website, index) => {
        const crawls = crawlHistories[index];
        const completedCrawls = crawls.filter(
          (crawl) => crawl.status === "completed"
        );

        completedCrawls.forEach((crawl) => {
          allReports.push({
            crawlId: crawl.id,
            websiteId: website.id,
            websiteName: website.name || website.domain,
            websiteDomain: website.domain,
            date: crawl.completed_at || crawl.created_at,
            pagesCount: crawl.pages_crawled,
            status: crawl.status,
          });
        });
      });

      // Sort by date (newest first)
      allReports.sort((a, b) =>
        new Date(b.date).getTime() - new Date(a.date).getTime()
      );

      setReports(allReports);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load reports");
    } finally {
      setIsLoading(false);
    }
  }, [getToken]);

  useEffect(() => {
    if (isLoaded) {
      loadReports();
    }
  }, [isLoaded, loadReports]);

  const handleDownloadCSV = async (crawlId: string, websiteName: string) => {
    try {
      const token = await getToken();
      if (!token) return;

      const loadingToast = toast.loading("Preparing CSV export...");

      await crawlsAPI.exportCsv(token, crawlId);

      toast.success("CSV downloaded successfully", { id: loadingToast });
    } catch (err) {
      toast.error("Failed to download CSV");
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Reports</h2>
          <p className="text-muted-foreground">
            View all your SEO analysis reports
          </p>
        </div>
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-muted-foreground">Loading reports...</div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Reports</h2>
          <p className="text-muted-foreground">
            View all your SEO analysis reports
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 rounded-md flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>All Reports</CardTitle>
          <CardDescription>
            {reports.length} completed SEO scan{reports.length !== 1 ? "s" : ""}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {reports.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <FileText className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No Reports Yet</h3>
              <p className="text-muted-foreground mb-6 text-center max-w-sm">
                Run your first SEO scan to generate reports
              </p>
              <Button onClick={() => router.push("/websites")}>
                <Globe className="h-4 w-4 mr-2" />
                Go to Websites
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {reports.map((report) => (
                <div
                  key={report.crawlId}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <Globe className="h-4 w-4 text-muted-foreground" />
                      <h3 className="font-semibold">{report.websiteName}</h3>
                    </div>
                    <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3.5 w-3.5" />
                        {new Date(report.date).toLocaleString()}
                      </div>
                      <div className="flex items-center gap-1">
                        <FileText className="h-3.5 w-3.5" />
                        {report.pagesCount} pages
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDownloadCSV(report.crawlId, report.websiteName)}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      CSV
                    </Button>
                    <Button
                      variant="default"
                      size="sm"
                      onClick={() => router.push(`/reports/${report.crawlId}`)}
                    >
                      View Report
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
