/**
 * Component for displaying SEO issues categorized by severity.
 */
import { AlertCircle, AlertTriangle, Info } from "lucide-react";
import { SEOIssue } from "@/types";

interface IssuesListProps {
  issues: SEOIssue[];
  showSuggestions?: boolean;
}

export function IssuesList({ issues, showSuggestions = true }: IssuesListProps) {
  // Group issues by severity
  const grouped = {
    critical: issues.filter((i) => i.severity === "critical"),
    warning: issues.filter((i) => i.severity === "warning"),
    info: issues.filter((i) => i.severity === "info"),
  };

  if (issues.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="h-16 w-16 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center mb-4">
          <svg
            className="h-8 w-8 text-green-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <h3 className="text-lg font-semibold mb-2">All Good!</h3>
        <p className="text-muted-foreground">No SEO issues found on this page.</p>
      </div>
    );
  }

  const SeverityBadge = ({ severity }: { severity: "critical" | "warning" | "info" }) => {
    const styles = {
      critical: {
        bg: "bg-red-100 dark:bg-red-900/20",
        text: "text-red-700 dark:text-red-400",
        icon: AlertCircle,
      },
      warning: {
        bg: "bg-orange-100 dark:bg-orange-900/20",
        text: "text-orange-700 dark:text-orange-400",
        icon: AlertTriangle,
      },
      info: {
        bg: "bg-blue-100 dark:bg-blue-900/20",
        text: "text-blue-700 dark:text-blue-400",
        icon: Info,
      },
    };

    const style = styles[severity];
    const Icon = style.icon;

    return (
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${style.bg} ${style.text}`}
      >
        <Icon className="h-3.5 w-3.5" />
        {severity.charAt(0).toUpperCase() + severity.slice(1)}
      </span>
    );
  };

  const IssueItem = ({ issue }: { issue: SEOIssue }) => (
    <div className="border-l-4 border-current pl-4 py-2">
      <div className="flex items-start gap-3">
        <div className="flex-1">
          <p className="font-medium text-sm mb-1">{issue.message}</p>
          {showSuggestions && issue.suggestion && (
            <p className="text-sm text-muted-foreground">{issue.suggestion}</p>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Critical Issues */}
      {grouped.critical.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <SeverityBadge severity="critical" />
            <span className="text-sm text-muted-foreground">
              {grouped.critical.length} issue{grouped.critical.length > 1 ? "s" : ""}
            </span>
          </div>
          <div className="space-y-3 border-l-red-500">
            {grouped.critical.map((issue, index) => (
              <IssueItem key={`critical-${index}`} issue={issue} />
            ))}
          </div>
        </div>
      )}

      {/* Warning Issues */}
      {grouped.warning.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <SeverityBadge severity="warning" />
            <span className="text-sm text-muted-foreground">
              {grouped.warning.length} issue{grouped.warning.length > 1 ? "s" : ""}
            </span>
          </div>
          <div className="space-y-3 border-l-orange-500">
            {grouped.warning.map((issue, index) => (
              <IssueItem key={`warning-${index}`} issue={issue} />
            ))}
          </div>
        </div>
      )}

      {/* Info Issues */}
      {grouped.info.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <SeverityBadge severity="info" />
            <span className="text-sm text-muted-foreground">
              {grouped.info.length} item{grouped.info.length > 1 ? "s" : ""}
            </span>
          </div>
          <div className="space-y-3 border-l-blue-500">
            {grouped.info.map((issue, index) => (
              <IssueItem key={`info-${index}`} issue={issue} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
