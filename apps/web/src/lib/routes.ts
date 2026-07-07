export type AppRoute =
  | { kind: "feed" }
  | { kind: "vacancy"; vacancyId: string }
  | { kind: "paywall"; reason?: "guest-limit" | "guest-apply" | "inactive-subscription" }
  | { kind: "profile" }
  | { kind: "balance" }
  | { kind: "applications" }
  | { kind: "hr-dashboard" }
  | { kind: "hr-create-vacancy" }
  | { kind: "hr-vacancy"; vacancyId: string }
  | { kind: "hr-application"; applicationId: string }
  | { kind: "admin-dashboard" }
  | { kind: "admin-users" }
  | { kind: "admin-hr" }
  | { kind: "admin-moderation" }
  | { kind: "admin-complaints" }
  | { kind: "admin-payments" }
  | { kind: "admin-stats" };

const ROUTE_QUERY_PARAM = "route";

export function routeToPath(route: AppRoute) {
  if (route.kind === "feed") {
    return "/feed";
  }
  if (route.kind === "vacancy") {
    return `/vacancies/${route.vacancyId}`;
  }
  if (route.kind === "paywall") {
    const params = new URLSearchParams();
    if (route.reason) {
      params.set("reason", route.reason);
    }
    const query = params.toString();
    return query ? `/paywall?${query}` : "/paywall";
  }
  if (route.kind === "profile") {
    return "/profile";
  }
  if (route.kind === "balance") {
    return "/balance";
  }
  if (route.kind === "applications") {
    return "/applications";
  }
  if (route.kind === "hr-dashboard") {
    return "/hr";
  }
  if (route.kind === "hr-create-vacancy") {
    return "/hr/vacancies/new";
  }
  if (route.kind === "hr-vacancy") {
    return `/hr/vacancies/${route.vacancyId}`;
  }
  if (route.kind === "hr-application") {
    return `/hr/applications/${route.applicationId}`;
  }
  if (route.kind === "admin-dashboard") {
    return "/admin";
  }
  if (route.kind === "admin-users") {
    return "/admin/users";
  }
  if (route.kind === "admin-hr") {
    return "/admin/hr";
  }
  if (route.kind === "admin-moderation") {
    return "/admin/moderation";
  }
  if (route.kind === "admin-complaints") {
    return "/admin/complaints";
  }
  if (route.kind === "admin-payments") {
    return "/admin/payments";
  }
  return "/admin/stats";
}

export function parseRouteString(routeString: string | null | undefined): AppRoute {
  if (!routeString || routeString === "/" || routeString === "/feed") {
    return { kind: "feed" };
  }
  const [pathname, queryString] = routeString.split("?");
  if (routeString.startsWith("/vacancies/")) {
    const vacancyId = routeString.replace("/vacancies/", "").trim();
    if (vacancyId) {
      return { kind: "vacancy", vacancyId };
    }
  }
  if (pathname === "/paywall") {
    const params = new URLSearchParams(queryString);
    const reason = params.get("reason");
    if (reason === "guest-limit" || reason === "guest-apply" || reason === "inactive-subscription") {
      return { kind: "paywall", reason };
    }
    return { kind: "paywall" };
  }
  if (pathname === "/profile") {
    return { kind: "profile" };
  }
  if (pathname === "/balance") {
    return { kind: "balance" };
  }
  if (pathname === "/applications") {
    return { kind: "applications" };
  }
  if (pathname === "/hr") {
    return { kind: "hr-dashboard" };
  }
  if (pathname === "/hr/create") {
    return { kind: "hr-create-vacancy" };
  }
  if (pathname === "/hr/vacancies/new") {
    return { kind: "hr-create-vacancy" };
  }
  if (pathname === "/hr/vacancies" || pathname === "/hr/applications" || pathname === "/hr/company") {
    return { kind: "hr-dashboard" };
  }
  if (pathname.startsWith("/hr/vacancies/")) {
    const vacancyId = pathname.replace("/hr/vacancies/", "").trim();
    if (vacancyId) {
      return { kind: "hr-vacancy", vacancyId };
    }
  }
  if (pathname.startsWith("/hr/applications/")) {
    const applicationId = pathname.replace("/hr/applications/", "").trim();
    if (applicationId) {
      return { kind: "hr-application", applicationId };
    }
  }
  if (pathname === "/admin") {
    return { kind: "admin-dashboard" };
  }
  if (pathname === "/admin/users") {
    return { kind: "admin-users" };
  }
  if (pathname === "/admin/hr" || pathname === "/admin/hr-access") {
    return { kind: "admin-hr" };
  }
  if (pathname === "/admin/moderation") {
    return { kind: "admin-moderation" };
  }
  if (pathname === "/admin/complaints") {
    return { kind: "admin-complaints" };
  }
  if (pathname === "/admin/payments") {
    return { kind: "admin-payments" };
  }
  if (pathname === "/admin/stats") {
    return { kind: "admin-stats" };
  }
  return { kind: "feed" };
}

export function getRouteFromLocation(locationLike: Pick<Location, "search" | "pathname">) {
  const base = typeof window !== "undefined" ? window.location.origin : "https://mini-app.local";
  const url = new URL(`${base}${locationLike.pathname}${locationLike.search}`);
  const routeParam = url.searchParams.get(ROUTE_QUERY_PARAM);
  return parseRouteString(routeParam ?? locationLike.pathname);
}

export function navigateToRoute(route: AppRoute, options?: { replace?: boolean }) {
  const url = new URL(window.location.href);
  url.searchParams.set(ROUTE_QUERY_PARAM, routeToPath(route));
  const state = { route };
  if (options?.replace) {
    window.history.replaceState(state, "", url.toString());
  } else {
    window.history.pushState(state, "", url.toString());
  }
  window.dispatchEvent(new PopStateEvent("popstate", { state }));
}
