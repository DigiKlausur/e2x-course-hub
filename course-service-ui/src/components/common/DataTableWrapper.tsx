import { type ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface DataTableWrapperProps {
  children: ReactNode;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  loadingMessage?: string;
  errorTitle?: string;
  className?: string;
}

export function DataTableWrapper({
  children,
  loading = false,
  error = null,
  onRetry,
  loadingMessage = "Loading...",
  errorTitle = "Error loading data",
  className,
}: DataTableWrapperProps) {
  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="p-10 text-center text-muted-foreground">
          {loadingMessage}
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardContent className="p-10 text-center">
          <h3 className="text-destructive mb-2.5 font-semibold">
            {errorTitle}
          </h3>
          <p className="text-muted-foreground mb-4">{error}</p>
          {onRetry && <Button onClick={onRetry}>Retry</Button>}
        </CardContent>
      </Card>
    );
  }

  return <>{children}</>;
}
