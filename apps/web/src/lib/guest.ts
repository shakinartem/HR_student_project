const GUEST_ID_KEY = "hr-student-mini-app.guest-id";
const VIEWED_VACANCIES_KEY = "hr-student-mini-app.viewed-vacancies";

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

export function readViewedVacancyIds() {
  if (!canUseStorage()) {
    return [];
  }
  const raw = window.localStorage.getItem(VIEWED_VACANCIES_KEY);
  if (!raw) {
    return [];
  }

  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.filter((value): value is string => typeof value === "string") : [];
  } catch {
    return [];
  }
}

export function recordViewedVacancy(vacancyId: string) {
  const nextSet = new Set(readViewedVacancyIds());
  nextSet.add(vacancyId);
  if (canUseStorage()) {
    window.localStorage.setItem(VIEWED_VACANCIES_KEY, JSON.stringify([...nextSet]));
  }
  return nextSet.size;
}

export function readViewedVacancyCount() {
  return readViewedVacancyIds().length;
}
