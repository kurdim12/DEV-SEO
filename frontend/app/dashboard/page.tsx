"use client";

/**
 * Dashboard overview page - shows SEO score, websites, and recent activity.
 */
import { useCallback, useEffect, useState } from "react";
import { useAuth, useUser } from "@clerk/nextjs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, TrendingUp, Globe, FileText, AlertCircle } from "lucide-react";
import Link from "next/link";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { dashboardAPI, getErrorMessage } from "@/lib/api";
import { cache, CacheKeys, CacheTTL } from "@/lib/cache";
import toast from "react-hot-toast";

interface DashboardStats {
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

export default function DashboardPage() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const { user } = useUser();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardStats = useCallback(async (skipCache = false) => {
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      const cacheKey = CacheKeys.dashboardStats(user.id);

      // Check cache first if not explicitly skipping
      if (!skipCache) {
        const cachedData = cache.get<DashboardStats>(cacheKey);
        if (cachedData) {
          setStats(cachedData);
          setLoading(false);
          return;
        }
      }

      const token = await getToken();
      if (!token) {
        throw new Error("No access token available");
      }

      const data = await dashboardAPI.getStats(token);
      setStats(data);

      // Cache the data for 2 minutes
      cache.set(cacheKey, data, CacheTTL.MEDIUM);
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [user, getToken]);

  useEffect(() => {
    if (isLoaded && isSignedIn && user) {
      fetchDashboardStats();
    }
  }, [isLoaded, isSignedIn, user, fetchDashboardStats]);

  if (loading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="w-full max-w-md">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-destructive/10 flex items-center justify-center">
                <AlertCircle className="h-5 w-5 text-destructive" />
              </div>
              <div>
                <CardTitle className="text-destructive">Unable to Load Dashboard</CardTitle>
                <CardDescription>Something went wrong</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">{error}</p>
            <Button onClick={() => fetchDashboardStats(true)} className="w-full">
              Try Again
            </Button>
          </CardContent>
        </Card>
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
        <Link href="/websites">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Website
          </Button>
        </Link>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-2">
              <Globe className="h-4 w-4 text-muted-foreground" />
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Websites
              </CardTitle>
            </div>
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
            <div className="flex items-center space-x-2">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Scans This Month
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.scans_this_month || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              1 scan available (Free plan)
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Average SEO Score
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.avg_seo_score !== null && stats?.avg_seo_score !== undefined
                ? Number(stats.avg_seo_score).toFixed(1)
                : "--"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {stats?.avg_seo_score ? "Across all scans" : "Run a scan to see your score"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Pages Scanned
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_pages_scanned || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Total pages analyzed
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      {stats?.recent_scans && stats.recent_scans.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Your latest completed scans
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.recent_scans.map((scan) => (
                <div
                  key={scan.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-1">
                    <Link href={`/websites/${scan.website_id}`} className="hover:underline">
                      <p className="font-medium">{scan.website_name}</p>
                    </Link>
                    <p className="text-sm text-muted-foreground">{scan.website_domain}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{scan.pages_crawled} pages</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(scan.completed_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Link href={`/reports/${scan.id}`}>
                    <Button variant="ghost" size="sm" className="ml-4">
                      View Report
                    </Button>
                  </Link>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
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
                <h3 className="font-medium">Run your first SEO scan</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Get comprehensive SEO analysis with actionable insights
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <span className="text-sm font-bold text-primary">3</span>
              </div>
              <div className="flex-1">
                <h3 className="font-medium">Review your report</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  See detailed SEO scores and recommendations
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
