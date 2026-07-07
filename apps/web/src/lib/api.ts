import type {
  AdminComplaint,
  AdminComplaintListResponse,
  AdminHRProfile,
  AdminHRProfileListResponse,
  AdminModerationVacancy,
  AdminModerationVacancyListResponse,
  AdminPaymentListResponse,
  AdminStats,
  AdminUser,
  AdminUserListResponse,
  AdminUserUpdateRequest,
  HRApplication,
  HRApplicationListResponse,
  HRVacancy,
  HRVacancyCreateRequest,
  HRVacancyListResponse,
  PaymentCreateRequest,
  PaymentCreateResponse,
  PaymentHistoryResponse,
  StudentApplication,
  StudentApplicationListResponse,
  StudentBalanceResponse,
  StudentProfile,
  StudentProfileUpdateRequest,
  StudentSubscription,
  TelegramAuthResponse,
  User,
  UserUpdateRequest,
  VacancyDetail,
  VacancyListResponse,
  VacancyViewResponse,
} from "@/types/api";

export class ApiError extends Error {
  status: number;
  code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const AUTH_TOKEN_KEY = "hr-student-mini-app.auth-token";
let unauthorizedHandler: (() => void) | null = null;

export function getAuthToken() {
  if (typeof window === "undefined") {
    return null;
  }
  return window.sessionStorage.getItem(AUTH_TOKEN_KEY);
}

export function setAuthToken(token: string) {
  if (typeof window === "undefined") {
    return;
  }
  window.sessionStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function clearAuthToken() {
  if (typeof window === "undefined") {
    return;
  }
  window.sessionStorage.removeItem(AUTH_TOKEN_KEY);
}

export function setUnauthorizedHandler(handler: (() => void) | null) {
  unauthorizedHandler = handler;
}

function normalizeApiError(status: number, detail: unknown) {
  if (typeof detail === "string") {
    if (detail.includes("X-Guest-Id")) {
      return new ApiError("Guest id is required", status, "MISSING_GUEST_ID");
    }
    return new ApiError(detail, status);
  }

  if (detail && typeof detail === "object") {
    const code = "code" in detail && typeof detail.code === "string" ? detail.code : undefined;
    const message = "message" in detail && typeof detail.message === "string" ? detail.message : "Request failed";
    return new ApiError(message, status, code);
  }

  return new ApiError("Request failed", status);
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("Accept", "application/json");
  if (init?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const token = getAuthToken();
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }
    if (response.status === 401) {
      clearAuthToken();
      unauthorizedHandler?.();
    }
    const detail = payload && typeof payload === "object" && "detail" in payload ? payload.detail : payload;
    throw normalizeApiError(response.status, detail);
  }

  return (await response.json()) as T;
}

export const apiClient = {
  listVacancies() {
    return request<VacancyListResponse>("/api/vacancies");
  },

  getVacancyDetail(vacancyId: string, guestId?: string) {
    const headers = guestId ? { "X-Guest-Id": guestId } : undefined;
    return request<VacancyDetail>(`/api/vacancies/${vacancyId}`, { headers });
  },

  recordVacancyView(vacancyId: string, guestId?: string) {
    const headers = guestId ? { "X-Guest-Id": guestId } : undefined;
    return request<VacancyViewResponse>(`/api/vacancies/${vacancyId}/view`, {
      method: "POST",
      headers,
    });
  },

  authenticateTelegram(initData: string) {
    return request<TelegramAuthResponse>("/api/auth/telegram", {
      method: "POST",
      body: JSON.stringify({ init_data: initData }),
    });
  },

  getMe() {
    return request<User>("/api/me");
  },

  updateMe(payload: UserUpdateRequest) {
    return request<User>("/api/me", {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  getStudentProfile() {
    return request<StudentProfile>("/api/student/profile");
  },

  updateStudentProfile(payload: StudentProfileUpdateRequest) {
    return request<StudentProfile>("/api/student/profile", {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  getStudentBalance() {
    return request<StudentBalanceResponse>("/api/student/balance");
  },

  getStudentSubscription() {
    return request<StudentSubscription>("/api/student/subscription");
  },

  getStudentApplications() {
    return request<StudentApplicationListResponse>("/api/student/applications");
  },

  createPayment(payload: PaymentCreateRequest) {
    return request<PaymentCreateResponse>("/api/payments/create", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  getHrVacancies() {
    return request<HRVacancyListResponse>("/api/hr/vacancies");
  },

  createHrVacancy(payload: HRVacancyCreateRequest) {
    return request<HRVacancy>("/api/hr/vacancies", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  getHrVacancy(vacancyId: string) {
    return request<HRVacancy>(`/api/hr/vacancies/${vacancyId}`);
  },

  createHrVacancyPublishPayment(vacancyId: string) {
    return request<PaymentCreateResponse>(`/api/hr/vacancies/${vacancyId}/publish-payment`, {
      method: "POST",
    });
  },

  getHrApplications() {
    return request<HRApplicationListResponse>("/api/hr/applications");
  },

  getHrApplication(applicationId: string) {
    return request<HRApplication>(`/api/hr/applications/${applicationId}`);
  },

  acceptHrApplication(applicationId: string) {
    return request<HRApplication>(`/api/hr/applications/${applicationId}/accept`, {
      method: "POST",
    });
  },

  rejectHrApplication(applicationId: string) {
    return request<HRApplication>(`/api/hr/applications/${applicationId}/reject`, {
      method: "POST",
    });
  },

  confirmMockPayment(paymentId: string) {
    return request<{ payment_id: string; status: string }>("/api/payments/mock-confirm", {
      method: "POST",
      body: JSON.stringify({ payment_id: paymentId }),
    });
  },

  getPaymentHistory() {
    return request<PaymentHistoryResponse>("/api/payments/history");
  },

  applyToVacancy(vacancyId: string, studentComment?: string) {
    return request<StudentApplication>(`/api/vacancies/${vacancyId}/apply`, {
      method: "POST",
      body: JSON.stringify({ student_comment: studentComment?.trim() || null }),
    });
  },

  getAdminUsers() {
    return request<AdminUserListResponse>("/api/admin/users");
  },

  getAdminUser(userId: string) {
    return request<AdminUser>(`/api/admin/users/${userId}`);
  },

  updateAdminUser(userId: string, payload: AdminUserUpdateRequest) {
    return request<AdminUser>(`/api/admin/users/${userId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  getAdminHrProfiles() {
    return request<AdminHRProfileListResponse>("/api/admin/hr-profiles");
  },

  updateAdminHrProfileStatus(profileId: string, verifiedStatus: string) {
    return request<AdminHRProfile>(`/api/admin/hr-profiles/${profileId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ verified_status: verifiedStatus }),
    });
  },

  getAdminModerationVacancies() {
    return request<AdminModerationVacancyListResponse>("/api/admin/moderation/vacancies");
  },

  approveAdminModerationVacancy(vacancyId: string) {
    return request<AdminModerationVacancy>(`/api/admin/moderation/vacancies/${vacancyId}/approve`, {
      method: "POST",
    });
  },

  rejectAdminModerationVacancy(vacancyId: string, reason?: string) {
    return request<AdminModerationVacancy>(`/api/admin/moderation/vacancies/${vacancyId}/reject`, {
      method: "POST",
      body: JSON.stringify({ reason: reason ?? null }),
    });
  },

  getAdminComplaints() {
    return request<AdminComplaintListResponse>("/api/admin/complaints");
  },

  updateAdminComplaintStatus(complaintId: string, statusValue: string, adminComment?: string) {
    return request<AdminComplaint>(`/api/admin/complaints/${complaintId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status: statusValue, admin_comment: adminComment ?? null }),
    });
  },

  getAdminPayments() {
    return request<AdminPaymentListResponse>("/api/admin/payments");
  },

  getAdminStats() {
    return request<AdminStats>("/api/admin/stats");
  },
};
