const GUEST_ID_KEY = "hr-student-mini-app.guest-id";

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