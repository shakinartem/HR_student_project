import { ShieldX } from "lucide-react";

import { HrShell } from "@/components/hr-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export function AdminAccessDeniedScreen({
  onBackToFeed,
}: {
  onBackToFeed: () => void;
}) {
  return (
    <HrShell
      title="Admin access"
      subtitle="Only users with backend-confirmed admin role can open operational screens."
    >
      <Card className="border-red-500/30 bg-red-500/10 text-red-100">
        <div className="flex items-start gap-3">
          <ShieldX className="mt-0.5 h-5 w-5 text-red-300" />
          <div>
            <h2 className="m-0 text-base font-bold">Access denied</h2>
            <p className="mb-0 mt-2 text-sm text-red-100/80">
              Local role changes are ignored. If you expected access, verify the backend user role and token.
            </p>
          </div>
        </div>
      </Card>
      <Button className="w-full" onClick={onBackToFeed} size="lg">
        Back to feed
      </Button>
    </HrShell>
  );
}
