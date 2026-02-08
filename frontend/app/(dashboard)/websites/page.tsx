"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth, useUser } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Globe, CheckCircle2, XCircle, Trash2, ExternalLink } from "lucide-react";
import toast from "react-hot-toast";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AddWebsiteDialog } from "@/components/dashboard/AddWebsiteDialog";
import { WebsitesSkeleton } from "@/components/dashboard/WebsitesSkeleton";
import { websitesAPI } from "@/lib/api";
import { cache, CacheKeys } from "@/lib/cache";
import type { Website } from "@/types";

function getScoreColor(score: number): string {
  if (score >= 80) return "text-green-600 bg-green-50 dark:bg-green-900/20";
  if (score >= 60) return "text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20";
  return "text-red-600 bg-red-50 dark:bg-red-900/20";
}

export default function WebsitesPage() {
  const { getToken, isLoaded } = useAuth();
  const { user } = useUser();
  const router = useRouter();
  const [websites, setWebsites] = useState<Website[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadWebsites = useCallback(async () => {
    try {
      const token = await getToken();
      if (!token) return;

      const data = await websitesAPI.list(token);
      setWebsites(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load websites");
    } finally {
      setIsLoading(false);
    }
  }, [getToken]);

  useEffect(() => {
    if (isLoaded) {
      loadWebsites();
    }
  }, [isLoaded, loadWebsites]);

  const handleDelete = async (websiteId: string) => {
    if (!confirm("Are you sure you want to delete this website? All crawl data will be lost.")) {
      return;
    }

    try {
      const token = await getToken();
      if (!token) return;

      await websitesAPI.delete(token, websiteId);
      setWebsites(websites.filter((w) => w.id !== websiteId));
      toast.success("Website deleted successfully");

      // Invalidate dashboard stats cache since website count changed
      if (user) {
        cache.invalidate(CacheKeys.dashboardStats(user.id));
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to delete website";
      toast.error(errorMessage);
    }
  };

  if (isLoading) {
    return <WebsitesSkeleton />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Websites</h2>
          <p className="text-muted-foreground">
            Manage and monitor your websites
          </p>
        </div>
        <AddWebsiteDialog onWebsiteAdded={loadWebsites} />
      </div>

      {error && (
        <div className="p-4 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 rounded-md">
          {error}
        </div>
      )}

      {websites.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <Globe className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No websites yet</h3>
            <p className="text-muted-foreground mb-6 text-center max-w-sm">
              Get started by adding your first website to monitor its SEO performance.
            </p>
            <AddWebsiteDialog onWebsiteAdded={loadWebsites} />
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {websites.map((website) => (
            <Card key={website.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-lg truncate">
                      {website.name || website.domain}
                    </CardTitle>
                    <CardDescription className="flex items-center gap-2 mt-1">
                      <span className="truncate">{website.domain}</span>
                      <a
                        href={`https://${website.domain}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Verification Status */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {website.verified ? (
                        <>
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                          <span className="text-sm text-green-600 font-medium">
                            Verified
                          </span>
                        </>
                      ) : (
                        <>
                          <XCircle className="h-4 w-4 text-orange-600" />
                          <span className="text-sm text-orange-600 font-medium">
                            Not Verified
                          </span>
                        </>
                      )}
                    </div>

                    {/* SEO Score Badge */}
                    {website.last_scan_score !== null && website.last_scan_score !== undefined && (
                      <div className={`px-2 py-1 rounded-md text-sm font-semibold ${getScoreColor(website.last_scan_score)}`}>
                        {website.last_scan_score}/100
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button
                      variant="default"
                      size="sm"
                      className="flex-1"
                      onClick={() => router.push(`/websites/${website.id}`)}
                    >
                      View Details
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(website.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
