import { CheckCircle, XCircle, AlertCircle, Loader2 } from "lucide-react";

interface StatusIndicatorProps {
  status: "success" | "error" | "warning" | "loading";
  message?: string;
  size?: "sm" | "md" | "lg";
}

export function StatusIndicator({
  status,
  message,
  size = "md",
}: StatusIndicatorProps) {
  const icons = {
    success: CheckCircle,
    error: XCircle,
    warning: AlertCircle,
    loading: Loader2,
  };

  const colors = {
    success: "text-green-600",
    error: "text-red-600",
    warning: "text-yellow-600",
    loading: "text-blue-600",
  };

  const sizes = {
    sm: "h-4 w-4",
    md: "h-5 w-5",
    lg: "h-6 w-6",
  };

  const Icon = icons[status];

  return (
    <div className="flex items-center space-x-2">
      <Icon
        className={`${sizes[size]} ${colors[status]} ${
          status === "loading" ? "animate-spin" : ""
        }`}
      />
      {message && (
        <span className={`text-sm ${colors[status]}`}>{message}</span>
      )}
    </div>
  );
}
