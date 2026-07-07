import { Ban, Clock3, LoaderCircle, ShieldAlert, ShieldCheck, UserRound } from "lucide-react";

import { AdminNav } from "@/components/admin-nav";
import { HrShell } from "@/components/hr-shell";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { AppRoute } from "@/lib/routes";
import type { AdminUser, User } from "@/types/api";

function formatDate(value: string | null) {
  if (!value) {
    return "No date";
  }

  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function userStatus(user: AdminUser) {
  if (user.is_blocked) {
    return { label: "blocked", tone: "danger" as const };
  }
  if (user.mute_until) {
    return { label: "muted", tone: "warning" as const };
  }
  return { label: "active", tone: "success" as const };
}

export function AdminUsersScreen({
  currentRoute,
  currentUser,
  errorMessage,
  isLoading,
  isMutating,
  onNavigate,
  onSelectUser,
  onToggleBlock,
  onToggleMute,
  selectedUser,
  users,
}: {
  currentRoute: AppRoute["kind"];
  currentUser: User;
  errorMessage: string | null;
  isLoading: boolean;
  isMutating: boolean;
  onNavigate: (
    route: Extract<
      AppRoute,
      {
        kind:
          | "admin-dashboard"
          | "admin-users"
          | "admin-hr"
          | "admin-moderation"
          | "admin-complaints"
          | "admin-payments"
          | "admin-stats";
      }
    >,
  ) => void;
  onSelectUser: (userId: string) => void;
  onToggleBlock: (user: AdminUser) => void;
  onToggleMute: (user: AdminUser) => void;
  selectedUser: AdminUser | null;
  users: AdminUser[];
}) {
  return (
    <HrShell title="Users" subtitle="Inspect user role and account status without exposing or editing sensitive data." headerBadge={<StatusBadge label={currentUser.role} tone="danger" />}>
      <AdminNav currentRoute={currentRoute} onNavigate={onNavigate} />

      {errorMessage ? (
        <Card className="border-red-500/30 bg-red-500/10 text-red-100">
          <p className="m-0 text-sm">{errorMessage}</p>
        </Card>
      ) : null}

      {selectedUser ? (
        <Card className="border-hub-orange/30 bg-hub-panel text-hub-text">
          <div className="flex items-start justify-between gap-3">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <UserRound className="h-4 w-4 text-hub-orange" />
                <h2 className="m-0 text-base font-bold">
                  {selectedUser.first_name} {selectedUser.last_name ?? ""}
                </h2>
              </div>
              <p className="m-0 text-sm text-hub-muted">
                Role: {selectedUser.role} | Telegram ID: {selectedUser.telegram_id ?? "n/a"}
              </p>
              <p className="m-0 text-sm text-hub-muted">
                Username: {selectedUser.username ?? "n/a"} | Created: {formatDate(selectedUser.created_at)}
              </p>
            </div>
            <StatusBadge {...userStatus(selectedUser)} />
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <Button disabled={isMutating} onClick={() => onToggleBlock(selectedUser)} variant={selectedUser.is_blocked ? "secondary" : "primary"}>
              <Ban className="mr-2 h-4 w-4" />
              {selectedUser.is_blocked ? "Unblock" : "Block"}
            </Button>
            <Button disabled={isMutating} onClick={() => onToggleMute(selectedUser)} variant="secondary">
              <Clock3 className="mr-2 h-4 w-4" />
              {selectedUser.mute_until ? "Unmute" : "Mute 24h"}
            </Button>
          </div>
        </Card>
      ) : null}

      {isLoading ? (
        <Card className="flex items-center gap-3 border-hub-border bg-hub-panel text-hub-text">
          <LoaderCircle className="h-5 w-5 animate-spin text-hub-orange" />
          <p className="m-0 text-sm text-hub-muted">Loading users...</p>
        </Card>
      ) : null}

      {!isLoading && users.length === 0 ? (
        <Card className="border-hub-border bg-hub-panel text-hub-text">
          <p className="m-0 text-sm text-hub-muted">No users found.</p>
        </Card>
      ) : null}

      {!isLoading ? (
        <section className="space-y-3">
          {users.map((user) => {
            const status = userStatus(user);
            return (
              <button
                className="w-full rounded-[28px] border border-hub-border bg-hub-panel p-4 text-left text-hub-text transition hover:border-hub-orange/40"
                key={user.id}
                onClick={() => onSelectUser(user.id)}
                type="button"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      {user.is_blocked ? <ShieldAlert className="h-4 w-4 text-red-300" /> : <ShieldCheck className="h-4 w-4 text-hub-orange" />}
                      <h2 className="m-0 text-base font-bold">
                        {user.first_name} {user.last_name ?? ""}
                      </h2>
                    </div>
                    <p className="m-0 text-sm text-hub-muted">
                      @{user.username ?? "no_username"} | {user.role}
                    </p>
                    <p className="m-0 text-xs text-hub-muted">Created {formatDate(user.created_at)}</p>
                  </div>
                  <StatusBadge label={status.label} tone={status.tone} />
                </div>
              </button>
            );
          })}
        </section>
      ) : null}
    </HrShell>
  );
}
