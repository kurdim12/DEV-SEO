/**
 * Circular gauge component for displaying SEO scores.
 */
interface ScoreGaugeProps {
  score: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

export function ScoreGauge({ score, size = "md", showLabel = true }: ScoreGaugeProps) {
  // Determine size dimensions
  const dimensions = {
    sm: { size: 80, strokeWidth: 8, fontSize: "text-lg" },
    md: { size: 120, strokeWidth: 12, fontSize: "text-3xl" },
    lg: { size: 160, strokeWidth: 16, fontSize: "text-4xl" },
  };

  const { size: svgSize, strokeWidth, fontSize } = dimensions[size];
  const radius = (svgSize - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  // Determine color based on score
  const getColor = (score: number) => {
    if (score >= 80) return { stroke: "#10b981", text: "text-green-600" }; // Good
    if (score >= 60) return { stroke: "#f59e0b", text: "text-orange-600" }; // Warning
    return { stroke: "#ef4444", text: "text-red-600" }; // Poor
  };

  const { stroke, text } = getColor(score);

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: svgSize, height: svgSize }}>
        <svg
          width={svgSize}
          height={svgSize}
          className="transform -rotate-90"
        >
          {/* Background circle */}
          <circle
            cx={svgSize / 2}
            cy={svgSize / 2}
            r={radius}
            stroke="#e5e7eb"
            strokeWidth={strokeWidth}
            fill="none"
          />
          {/* Progress circle */}
          <circle
            cx={svgSize / 2}
            cy={svgSize / 2}
            r={radius}
            stroke={stroke}
            strokeWidth={strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-500 ease-out"
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`font-bold ${fontSize} ${text}`}>{score}</span>
        </div>
      </div>
      {showLabel && (
        <span className="text-sm text-muted-foreground font-medium">
          SEO Score
        </span>
      )}
    </div>
  );
}
