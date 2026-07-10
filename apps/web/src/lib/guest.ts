const GUEST_ID_KEY = "hr-student-mini-app.guest-id";
const GUEST_VIEWS_KEY = "hr-student-mini-app.guest-views";

function canUseStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function readGuestId() {
  if (!canUseStorage()) {
    return null;
  }
  return window.localStorage.getItem(GUEST_ID_KEY);
}

export function createGuestId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `guest-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function ensureGuestId() {
  const existing = readGuestId();
  if (existing) {
    return existing;
  }
  const next = createGuestId();
  if (canUseStorage()) {
    window.localStorage.setItem(GUEST_ID_KEY, next);
  }
  return next;
}

export function regenerateGuestId() {
  const next = createGuestId();
  if (canUseStorage()) {
    window.localStorage.setItem(GUEST_ID_KEY, next);
  }
  return next;
}

export function readViewedVacancyCount() {
  if (!canUseStorage()) {
    return 0;
  }
  const views = window.localStorage.getItem(GUEST_VIEWS_KEY);
  if (!views) {
    return 0;
  }
  try {
    const parsed = JSON.parse(views);
    if (Array.isArray(parsed)) {
      return parsed.length;
    }
    return 0;
  } catch {
    return 0;
  }
}

export function recordViewedVacancy(vacancyId: string | number) {
  if (!canUseStorage()) {
    return 0;
  }
  const existing = window.localStorage.getItem(GUEST_VIEWS_KEY);
  let views: string[] = [];
  if (existing) {
    try {
      views = JSON.parse(existing);
    } catch {
      views = [];
    }
  }
  const idStr = String(vacancyId);
  if (!views.includes(idStr)) {
    views.push(idStr);
    window.localStorage.setItem(GUEST_VIEWS_KEY, JSON.stringify(views));
  }
  return views.length;
}
