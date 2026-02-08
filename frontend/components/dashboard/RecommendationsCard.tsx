"use client";

import { useState } from "react";
import { Lightbulb, CheckCircle2, XCircle, Clock, Sparkles } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { AIRecommendation } from "@/types";

interface RecommendationsCardProps {
  recommendations: AIRecommendation[];
  onStatusChange?: (recommendationId: string, status: string) => void;
}

export function RecommendationsCard({
  recommendations,
  onStatusChange,
}: RecommendationsCardProps) {
  const [filter, setFilter] = useState<"all" | "high" | "medium" | "low">("all");

  // Filter recommendations
  const filteredRecommendations = recommendations.filter(
    (rec) => filter === "all" || rec.priority === filter
  );

  // Group by priority
  const highPriority = filteredRecommendations.filter((r) => r.priority === "high");
  const mediumPriority = filteredRecommendations.filter((r) => r.priority === "medium");
  const lowPriority = filteredRecommendations.filter((r) => r.priority === "low");

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-green-600" />;
      case "in_progress":
        return <Clock className="h-4 w-4 text-blue-600" />;
      case "dismissed":
        return <XCircle className="h-4 w-4 text-gray-400" />;
      default:
        return <Lightbulb className="h-4 w-4 text-orange-500" />;
    }
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      title: "Title",
      meta_description: "Meta Description",
      headings: "Headings",
      content_quality: "Content Quality",
      content_length: "Content Length",
      technical: "Technical SEO",
      performance: "Performance",
      images: "Images",
      overall: "Site-wide",
    };
    return labels[type] || type;
  };

  if (recommendations.length === 0) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <CardTitle>AI Recommendations</CardTitle>
          </div>
          <CardDescription>
            Smart SEO recommendations powered by our hybrid AI system
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Lightbulb className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">
              No recommendations yet. They will be generated automatically after the scan completes.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <CardTitle>AI Recommendations</CardTitle>
          </div>
          <Badge variant="secondary" className="text-xs">
            {recommendations.length} total
          </Badge>
        </div>
        <CardDescription>
          Smart SEO recommendations powered by our hybrid AI system (95% rule-based + optional AI analysis)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Filters */}
        <div className="flex flex-wrap gap-2">
          <div className="flex gap-2">
            <Button
              variant={filter === "all" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter("all")}
            >
              All
            </Button>
            <Button
              variant={filter === "high" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter("high")}
            >
              High ({recommendations.filter((r) => r.priority === "high").length})
            </Button>
            <Button
              variant={filter === "medium" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter("medium")}
            >
              Medium ({recommendations.filter((r) => r.priority === "medium").length})
            </Button>
            <Button
              variant={filter === "low" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter("low")}
            >
              Low ({recommendations.filter((r) => r.priority === "low").length})
            </Button>
          </div>
        </div>

        {/* High Priority Recommendations */}
        {highPriority.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-red-600 dark:text-red-400">
              High Priority ({highPriority.length})
            </h4>
            {highPriority.map((rec) => (
              <div
                key={rec.id}
                className="p-4 border border-red-200 dark:border-red-800 rounded-lg bg-red-50/50 dark:bg-red-900/10"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      {getStatusIcon(rec.implementation_status)}
                      <h5 className="font-semibold">{rec.title}</h5>
                      <Badge variant="outline" className="text-xs">
                        {getTypeLabel(rec.recommendation_type)}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{rec.description}</p>
                  </div>
                  {onStatusChange && rec.implementation_status === "pending" && (
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onStatusChange(rec.id, "completed")}
                        title="Mark as completed"
                      >
                        <CheckCircle2 className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onStatusChange(rec.id, "dismissed")}
                        title="Dismiss"
                      >
                        <XCircle className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Medium Priority Recommendations */}
        {mediumPriority.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-orange-600 dark:text-orange-400">
              Medium Priority ({mediumPriority.length})
            </h4>
            {mediumPriority.map((rec) => (
              <div
                key={rec.id}
                className="p-4 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      {getStatusIcon(rec.implementation_status)}
                      <h5 className="font-medium">{rec.title}</h5>
                      <Badge variant="outline" className="text-xs">
                        {getTypeLabel(rec.recommendation_type)}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{rec.description}</p>
                  </div>
                  {onStatusChange && rec.implementation_status === "pending" && (
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onStatusChange(rec.id, "completed")}
                        title="Mark as completed"
                      >
                        <CheckCircle2 className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onStatusChange(rec.id, "dismissed")}
                        title="Dismiss"
                      >
                        <XCircle className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Low Priority Recommendations */}
        {lowPriority.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-blue-600 dark:text-blue-400">
              Low Priority ({lowPriority.length})
            </h4>
            {lowPriority.map((rec) => (
              <div
                key={rec.id}
                className="p-3 border rounded-lg hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      {getStatusIcon(rec.implementation_status)}
                      <h5 className="text-sm font-medium">{rec.title}</h5>
                      <Badge variant="outline" className="text-xs">
                        {getTypeLabel(rec.recommendation_type)}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">{rec.description}</p>
                  </div>
                  {onStatusChange && rec.implementation_status === "pending" && (
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onStatusChange(rec.id, "completed")}
                        title="Mark as completed"
                      >
                        <CheckCircle2 className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onStatusChange(rec.id, "dismissed")}
                        title="Dismiss"
                      >
                        <XCircle className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {filteredRecommendations.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            No recommendations match the current filters
          </div>
        )}
      </CardContent>
    </Card>
  );
}
