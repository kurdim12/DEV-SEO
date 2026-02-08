"use client";

/**
 * Dashboard overview page - shows SEO score, websites, and recent activity.
 */
import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, AlertCircle } from "lucide-react";
import { AddWebsiteDialog } from "@/components/dashboard/AddWebsiteDialog";
import { dashboardAPI } from "@/lib/api";
import type { DashboardStats } from "@/types";

export default function DashboardPage() {
  const router = useRouter();
  const { getToken, isLoaded } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadStats = useCallback(async () => {
    try {
      const token = await getToken();
      if (!token) return;

      const data = await dashboardAPI.getStats(token);
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard stats");
    } finally {
      setIsLoading(false);
    }
  }, [getToken]);

  useEffect(() => {
    if (isLoaded) {
      loadStats();
    }
  }, [isLoaded, loadStats]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
            <p className="text-muted-foreground">
              Monitor your website SEO performance at a glance
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Loading...
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold animate-pulse">--</div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <p className="text-muted-foreground">
            Monitor your website SEO performance at a glance
          </p>
        </div>
        <AddWebsiteDialog onWebsiteAdded={loadStats} />
      </div>

      {error && (
        <div className="p-4 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 rounded-md flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Websites
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.website_count || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {stats?.website_count === 0 ? "No websites added yet" : "Total websites"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Scans This Month
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.scans_this_month || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Total scans completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Average SEO Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.avg_seo_score !== null && stats?.avg_seo_score !== undefined
                ? `${Math.round(stats.avg_seo_score)}/100`
                : "--"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {stats?.avg_seo_score !== null && stats?.avg_seo_score !== undefined
                ? "Across all scanned pages"
                : "Run a scan to get started"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Scans */}
      {stats && stats.recent_scans && stats.recent_scans.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Scans</CardTitle>
            <CardDescription>
              Latest SEO analysis results
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats.recent_scans.map((scan) => (
                <div
                  key={scan.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                  onClick={() => router.push(`/reports/${scan.id}`)}
                >
                  <div>
                    <h3 className="font-medium">{scan.website_name || scan.website_domain}</h3>
                    <p className="text-sm text-muted-foreground">
                      {new Date(scan.completed_at).toLocaleString()} • {scan.pages_crawled} pages
                    </p>
                  </div>
                  <Button variant="ghost" size="sm">
                    View Report
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Getting Started Card - only show if no websites */}
      {stats && stats.website_count === 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
            <CardDescription>
              Follow these steps to start analyzing your website
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start space-x-4">
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <span className="text-sm font-bold text-primary">1</span>
              </div>
              <div className="flex-1">
                <h3 className="font-medium">Add your first website</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Click the &quot;Add Website&quot; button to add your website domain
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <span className="text-sm font-bold text-primary">2</span>
              </div>
              <div className="flex-1">
                <h3 className="font-medium">Verify domain ownership</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Add a DNS TXT record to verify you own the domain (optional)
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <span className="text-sm font-bold text-primary">3</span>
              </div>
              <div className="flex-1">
                <h3 className="font-medium">Run your first SEO scan</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Get comprehensive SEO analysis with actionable insights
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
