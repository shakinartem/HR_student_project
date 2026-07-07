import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";

import {
  apiClient,
  ApiError,
  clearAuthToken,
  getAuthToken,
  setAuthToken,
  setUnauthorizedHandler,
} from "@/lib/api";
import { ensureGuestId, readViewedVacancyCount, recordViewedVacancy, regenerateGuestId } from "@/lib/guest";
import { type AppRoute, getRouteFromLocation, navigateToRoute } from "@/lib/routes";
import { getRawInitDataSafe, setTelegramBackButtonVisible, setupTelegramMiniApp } from "@/lib/telegram";
import { ApplicationsScreen } from "@/screens/applications-screen";
import { AdminAccessDeniedScreen } from "@/screens/admin-access-denied-screen";
import { AdminComplaintsScreen } from "@/screens/admin-complaints-screen";
import { AdminDashboardScreen } from "@/screens/admin-dashboard-screen";
import { AdminHrScreen } from "@/screens/admin-hr-screen";
import { AdminModerationScreen } from "@/screens/admin-moderation-screen";
import { AdminPaymentsScreen } from "@/screens/admin-payments-screen";
import { AdminStatsScreen } from "@/screens/admin-stats-screen";
import { AdminUsersScreen } from "@/screens/admin-users-screen";
import { BalanceScreen } from "@/screens/balance-screen";
import { FeedScreen } from "@/screens/feed-screen";
import { HrApplicationDetailScreen } from "@/screens/hr-application-detail-screen";
import { HrDashboardScreen } from "@/screens/hr-dashboard-screen";
import { HrVacancyDetailScreen } from "@/screens/hr-vacancy-detail-screen";
import { HrVacancyFormScreen } from "@/screens/hr-vacancy-form-screen";
import { PaywallScreen } from "@/screens/paywall-screen";
import { ProfileScreen } from "@/screens/profile-screen";
import { VacancyDetailScreen } from "@/screens/vacancy-detail-screen";
import type { AdminUser, HRVacancyCreateRequest, User, VacancyDetail } from "@/types/api";

const queryClient = new QueryClient();
const GUEST_VIEW_LIMIT = Number(import.meta.env.VITE_GUEST_FREE_VACANCY_VIEWS ?? "3");
const DEFAULT_TOP_UP_AMOUNT = "350";
const CAN_MOCK_CONFIRM = import.meta.env.DEV || import.meta.env.VITE_ENABLE_MOCK_PAYMENT_CONFIRM === "true";

function getApiErrorMessage(error: unknown, fallback: string) {
  if (error instanceof ApiError) {
    return error.message;
  }

  return fallback;
}

function toNullableTrimmedString(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function toNullableList(values: string[]) {
  return values.length ? values : null;
}

function isAccessDeniedError(error: unknown) {
  return error instanceof ApiError && error.status === 403;
}

function studentOnlyMessage(user: User | null) {
  if (!user) {
    return null;
  }

  return user.role === "student" ? null : "Эта часть Mini App пока доступна только для студента.";
}

function AppContent() {
  const rawInitData = useMemo(() => getRawInitDataSafe(), []);
  const authInitDataRef = useRef<string | null>(null);
  const [route, setRoute] = useState<AppRoute>(() => getRouteFromLocation(window.location));
  const [previewCount, setPreviewCount] = useState(() => readViewedVacancyCount());
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [authStatus, setAuthStatus] = useState<"guest" | "authenticating" | "authenticated">(() =>
    getAuthToken() ? "authenticating" : "guest",
  );
  const [actionError, setActionError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [applyError, setApplyError] = useState<string | null>(null);
  const [isApplying, setIsApplying] = useState(false);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [profileSaveError, setProfileSaveError] = useState<string | null>(null);
  const [profileSaveSuccess, setProfileSaveSuccess] = useState<string | null>(null);
  const [topUpAmount, setTopUpAmount] = useState(DEFAULT_TOP_UP_AMOUNT);
  const [pendingPaymentId, setPendingPaymentId] = useState<string | null>(null);
  const [paymentError, setPaymentError] = useState<string | null>(null);
  const [paymentSuccess, setPaymentSuccess] = useState<string | null>(null);
  const [isCreatingPayment, setIsCreatingPayment] = useState(false);
  const [isConfirmingPayment, setIsConfirmingPayment] = useState(false);

  const [hrSubmitError, setHrSubmitError] = useState<string | null>(null);
  const [hrActionError, setHrActionError] = useState<string | null>(null);
  const [hrActionMessage, setHrActionMessage] = useState<string | null>(null);
  const [isCreatingHrVacancy, setIsCreatingHrVacancy] = useState(false);
  const [pendingHrPaymentId, setPendingHrPaymentId] = useState<string | null>(null);
  const [isCreatingHrPayment, setIsCreatingHrPayment] = useState(false);
  const [isConfirmingHrPayment, setIsConfirmingHrPayment] = useState(false);
  const [isAcceptingHrApplication, setIsAcceptingHrApplication] = useState(false);
  const [isRejectingHrApplication, setIsRejectingHrApplication] = useState(false);
  const [selectedAdminUserId, setSelectedAdminUserId] = useState<string | null>(null);
  const [adminActionError, setAdminActionError] = useState<string | null>(null);
  const [isUpdatingAdminEntity, setIsUpdatingAdminEntity] = useState(false);

  const isAuthenticated = authStatus === "authenticated" && currentUser !== null;
  const isStudent = currentUser?.role === "student";
  const isHr = currentUser?.role === "hr";
  const isAdmin = currentUser?.role === "admin";
  const canAuthenticateInTelegram = Boolean(rawInitData);
  const isHrRoute =
    route.kind === "hr-dashboard" ||
    route.kind === "hr-create-vacancy" ||
    route.kind === "hr-vacancy" ||
    route.kind === "hr-application";
  const isAdminRoute =
    route.kind === "admin-dashboard" ||
    route.kind === "admin-users" ||
    route.kind === "admin-hr" ||
    route.kind === "admin-moderation" ||
    route.kind === "admin-complaints" ||
    route.kind === "admin-payments" ||
    route.kind === "admin-stats";

  useEffect(() => {
    const syncRoute = () => setRoute(getRouteFromLocation(window.location));
    window.addEventListener("popstate", syncRoute);
    return () => window.removeEventListener("popstate", syncRoute);
  }, []);

  useEffect(() => {
    const cleanup = setupTelegramMiniApp(() => {
      if (route.kind === "vacancy" || route.kind === "paywall") {
        navigateToRoute({ kind: "feed" });
      }

      if (route.kind === "hr-vacancy" || route.kind === "hr-application" || route.kind === "hr-create-vacancy") {
        navigateToRoute({ kind: "hr-dashboard" });
      }

      if (isAdminRoute && route.kind !== "admin-dashboard") {
        navigateToRoute({ kind: "admin-dashboard" });
      }
    });

    return cleanup;
  }, [isAdminRoute, route.kind]);

  useEffect(() => {
    setTelegramBackButtonVisible(route.kind !== "feed" && route.kind !== "hr-dashboard" && route.kind !== "admin-dashboard");
  }, [route.kind]);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setCurrentUser(null);
      setAuthStatus("guest");
      setPendingPaymentId(null);
      setPendingHrPaymentId(null);
      setApplyError(null);
      setProfileSaveError(null);
      setPaymentError(null);
      setHrSubmitError(null);
      setHrActionError(null);
      setAdminActionError(null);
      setActionError("Сессия завершилась. Продолжаем в гостевом режиме.");
      queryClient.removeQueries({
        predicate: (query) => {
          const rootKey = Array.isArray(query.queryKey) ? String(query.queryKey[0]) : "";
          return (
            rootKey.startsWith("student") ||
            rootKey.startsWith("payments") ||
            rootKey.startsWith("hr") ||
            rootKey.startsWith("admin")
          );
        },
      });
    });

    return () => setUnauthorizedHandler(null);
  }, []);

  useEffect(() => {
    async function restoreSession() {
      setAuthStatus("authenticating");
      try {
        const me = await apiClient.getMe();
        setCurrentUser(me);
        setAuthStatus("authenticated");
      } catch {
        clearAuthToken();
        setCurrentUser(null);
        setAuthStatus("guest");
      }
    }

    async function bootstrapTelegramAuth(initData: string) {
      setAuthStatus("authenticating");
      try {
        const authResponse = await apiClient.authenticateTelegram(initData);
        setAuthToken(authResponse.access_token);
        const me = await apiClient.getMe();
        setCurrentUser(me);
        setAuthStatus("authenticated");
        setActionError(null);
      } catch {
        clearAuthToken();
        setCurrentUser(null);
        setAuthStatus("guest");
        setActionError("Не удалось выполнить вход через Telegram. Продолжаем в гостевом режиме.");
      }
    }

    if (rawInitData && authInitDataRef.current !== rawInitData) {
      authInitDataRef.current = rawInitData;
      void bootstrapTelegramAuth(rawInitData);
      return;
    }

    if (!rawInitData && getAuthToken() && !currentUser && authStatus !== "authenticated") {
      void restoreSession();
      return;
    }

    if (!getAuthToken() && !rawInitData && !currentUser) {
      setAuthStatus("guest");
    }
  }, [authStatus, currentUser, rawInitData]);

  const feedQuery = useQuery({
    queryKey: ["vacancies", "feed"],
    queryFn: () => apiClient.listVacancies(),
  });

  const studentProfileQuery = useQuery({
    queryKey: ["student-profile"],
    queryFn: () => apiClient.getStudentProfile(),
    enabled: isStudent,
  });

  const studentSubscriptionQuery = useQuery({
    queryKey: ["student-subscription"],
    queryFn: () => apiClient.getStudentSubscription(),
    enabled: isStudent,
  });

  const studentBalanceQuery = useQuery({
    queryKey: ["student-balance"],
    queryFn: () => apiClient.getStudentBalance(),
    enabled: isStudent && route.kind === "balance",
  });

  const paymentHistoryQuery = useQuery({
    queryKey: ["payments-history"],
    queryFn: () => apiClient.getPaymentHistory(),
    enabled: isStudent && route.kind === "balance",
  });

  const studentApplicationsQuery = useQuery({
    queryKey: ["student-applications"],
    queryFn: () => apiClient.getStudentApplications(),
    enabled: isStudent && route.kind === "applications",
  });

  const hrVacanciesQuery = useQuery({
    queryKey: ["hr-vacancies"],
    queryFn: () => apiClient.getHrVacancies(),
    enabled: isHr,
  });

  const hrApplicationsQuery = useQuery({
    queryKey: ["hr-applications"],
    queryFn: () => apiClient.getHrApplications(),
    enabled: isHr,
  });

  const detailQuery = useQuery({
    queryKey: ["vacancy-detail", route.kind === "vacancy" ? route.vacancyId : null, isAuthenticated ? currentUser?.id : "guest"],
    enabled: route.kind === "vacancy",
    queryFn: async () => {
      if (route.kind !== "vacancy") {
        throw new Error("Vacancy route required");
      }

      const guestId = !isAuthenticated ? ensureGuestId() : undefined;

      try {
        const detail = await apiClient.getVacancyDetail(route.vacancyId, guestId);
        if (!isAuthenticated) {
          setPreviewCount(recordViewedVacancy(route.vacancyId));
        }
        return detail;
      } catch (error) {
        if (!isAuthenticated && error instanceof ApiError && error.code === "MISSING_GUEST_ID") {
          const nextGuestId = regenerateGuestId();
          const detail = await apiClient.getVacancyDetail(route.vacancyId, nextGuestId);
          setPreviewCount(recordViewedVacancy(route.vacancyId));
          return detail;
        }

        if (!isAuthenticated && error instanceof ApiError && error.code === "GUEST_VIEW_LIMIT_REACHED") {
          navigateToRoute({ kind: "paywall", reason: "guest-limit" });
        }

        throw error;
      }
    },
    retry: false,
  });

  const hrVacancyDetailQuery = useQuery({
    queryKey: ["hr-vacancy-detail", route.kind === "hr-vacancy" ? route.vacancyId : null],
    enabled: isHr && route.kind === "hr-vacancy",
    queryFn: () => {
      if (route.kind !== "hr-vacancy") {
        throw new Error("HR vacancy route required");
      }

      return apiClient.getHrVacancy(route.vacancyId);
    },
  });

  const hrApplicationDetailQuery = useQuery({
    queryKey: ["hr-application-detail", route.kind === "hr-application" ? route.applicationId : null],
    enabled: isHr && route.kind === "hr-application",
    queryFn: () => {
      if (route.kind !== "hr-application") {
        throw new Error("HR application route required");
      }

      return apiClient.getHrApplication(route.applicationId);
    },
  });

  const adminStatsQuery = useQuery({
    queryKey: ["admin-stats"],
    queryFn: () => apiClient.getAdminStats(),
    enabled: isAdmin && (route.kind === "admin-dashboard" || route.kind === "admin-stats"),
  });

  const adminUsersQuery = useQuery({
    queryKey: ["admin-users"],
    queryFn: () => apiClient.getAdminUsers(),
    enabled: isAdmin && route.kind === "admin-users",
  });

  const selectedAdminUserQuery = useQuery({
    queryKey: ["admin-user", selectedAdminUserId],
    queryFn: () => {
      if (!selectedAdminUserId) {
        throw new Error("Admin user id is required");
      }

      return apiClient.getAdminUser(selectedAdminUserId);
    },
    enabled: isAdmin && route.kind === "admin-users" && selectedAdminUserId !== null,
  });

  const adminHrProfilesQuery = useQuery({
    queryKey: ["admin-hr-profiles"],
    queryFn: () => apiClient.getAdminHrProfiles(),
    enabled: isAdmin && route.kind === "admin-hr",
  });

  const adminModerationQuery = useQuery({
    queryKey: ["admin-moderation-vacancies"],
    queryFn: () => apiClient.getAdminModerationVacancies(),
    enabled: isAdmin && route.kind === "admin-moderation",
  });

  const adminComplaintsQuery = useQuery({
    queryKey: ["admin-complaints"],
    queryFn: () => apiClient.getAdminComplaints(),
    enabled: isAdmin && route.kind === "admin-complaints",
  });

  const adminPaymentsQuery = useQuery({
    queryKey: ["admin-payments"],
    queryFn: () => apiClient.getAdminPayments(),
    enabled: isAdmin && route.kind === "admin-payments",
  });

  const detailErrorMessage = useMemo(() => {
    if (!(detailQuery.error instanceof ApiError)) {
      return detailQuery.error ? "Что-то пошло не так. Попробуй открыть вакансию еще раз." : null;
    }

    if (detailQuery.error.code === "GUEST_VIEW_LIMIT_REACHED") {
      return null;
    }

    if (detailQuery.error.status === 404) {
      return "Эта вакансия уже недоступна.";
    }

    return detailQuery.error.message;
  }, [detailQuery.error]);

  const studentScreenError = studentOnlyMessage(currentUser);

  async function handleOpenVacancy(vacancyId: string) {
    setActionError(null);
    setSuccessMessage(null);
    setApplyError(null);

    if (isAuthenticated) {
      navigateToRoute({ kind: "vacancy", vacancyId });
      return;
    }

    let guestId = ensureGuestId();

    try {
      const viewResult = await apiClient.recordVacancyView(vacancyId, guestId);
      setPreviewCount(viewResult.view_count);
      recordViewedVacancy(vacancyId);
      navigateToRoute({ kind: "vacancy", vacancyId });
    } catch (error) {
      if (error instanceof ApiError && error.code === "MISSING_GUEST_ID") {
        guestId = regenerateGuestId();
        const viewResult = await apiClient.recordVacancyView(vacancyId, guestId);
        setPreviewCount(viewResult.view_count);
        recordViewedVacancy(vacancyId);
        navigateToRoute({ kind: "vacancy", vacancyId });
        return;
      }

      if (error instanceof ApiError && error.code === "GUEST_VIEW_LIMIT_REACHED") {
        navigateToRoute({ kind: "paywall", reason: "guest-limit" });
        return;
      }

      setActionError("Не удалось открыть вакансию. Попробуй еще раз.");
    }
  }

  function handleNavigate(routeToOpen: Extract<AppRoute, { kind: "feed" | "applications" | "balance" | "profile" }>) {
    setActionError(null);
    setSuccessMessage(null);
    navigateToRoute(routeToOpen);
  }

  function handleHrDashboardNavigate() {
    setHrActionError(null);
    setHrActionMessage(null);
    navigateToRoute({ kind: "hr-dashboard" });
  }

  function handleAdminNavigate(
    routeToOpen: Extract<
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
  ) {
    setAdminActionError(null);
    navigateToRoute(routeToOpen);
  }

  async function handleSaveProfile(form: {
    first_name: string;
    last_name: string;
    phone: string;
    email: string;
    university: string;
    course: string;
    speciality: string;
    preferred_job_types: string[];
    preferred_schedule: string[];
    preferred_districts: string[];
    experience_text: string;
  }) {
    if (!isStudent) {
      setProfileSaveError("Сохранение профиля доступно только студенту.");
      return;
    }

    setIsSavingProfile(true);
    setProfileSaveError(null);
    setProfileSaveSuccess(null);

    try {
      const updatedUser = await apiClient.updateMe({
        first_name: form.first_name.trim(),
        last_name: toNullableTrimmedString(form.last_name) ?? undefined,
        phone: toNullableTrimmedString(form.phone) ?? undefined,
        email: toNullableTrimmedString(form.email) ?? undefined,
      });

      const updatedProfile = await apiClient.updateStudentProfile({
        university: toNullableTrimmedString(form.university),
        course: form.course.trim() ? Number(form.course) : null,
        speciality: toNullableTrimmedString(form.speciality),
        preferred_job_types: toNullableList(form.preferred_job_types),
        preferred_schedule: toNullableList(form.preferred_schedule),
        preferred_districts: toNullableList(form.preferred_districts),
        experience_text: toNullableTrimmedString(form.experience_text),
      });

      setCurrentUser(updatedUser);
      queryClient.setQueryData(["student-profile"], updatedProfile);
      setProfileSaveSuccess(
        updatedProfile.profile_completed
          ? "Профиль сохранен. Теперь данные будут использоваться при отклике."
          : "Профиль сохранен. Заполни оставшиеся поля, чтобы завершить регистрацию.",
      );
    } catch (error) {
      setProfileSaveError(getApiErrorMessage(error, "Не удалось сохранить профиль."));
    } finally {
      setIsSavingProfile(false);
    }
  }

  async function handleCreatePayment() {
    if (!isStudent) {
      setPaymentError("Пополнение доступно только студенту.");
      return;
    }

    const numericAmount = Number(topUpAmount.replace(",", "."));
    if (!Number.isFinite(numericAmount) || numericAmount <= 0) {
      setPaymentError("Укажи корректную сумму пополнения.");
      return;
    }

    setIsCreatingPayment(true);
    setPaymentError(null);
    setPaymentSuccess(null);

    try {
      const payment = await apiClient.createPayment({
        amount: numericAmount,
        purpose: "student_balance_topup",
      });
      setPendingPaymentId(payment.payment_id);
      setPaymentSuccess("Платеж создан. Если mock confirm доступен, можно завершить его ниже.");
      queryClient.invalidateQueries({ queryKey: ["payments-history"] });
    } catch (error) {
      setPaymentError(getApiErrorMessage(error, "Не удалось создать платеж."));
    } finally {
      setIsCreatingPayment(false);
    }
  }

  async function handleConfirmPayment() {
    if (!pendingPaymentId) {
      return;
    }

    setIsConfirmingPayment(true);
    setPaymentError(null);

    try {
      await apiClient.confirmMockPayment(pendingPaymentId);
      setPendingPaymentId(null);
      setPaymentSuccess("Платеж подтвержден. Баланс и подписка обновлены.");
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["student-balance"] }),
        queryClient.invalidateQueries({ queryKey: ["student-subscription"] }),
        queryClient.invalidateQueries({ queryKey: ["payments-history"] }),
      ]);
    } catch (error) {
      setPaymentError(getApiErrorMessage(error, "Не удалось подтвердить платеж."));
    } finally {
      setIsConfirmingPayment(false);
    }
  }

  async function handleApply() {
    if (route.kind !== "vacancy") {
      return;
    }

    setApplyError(null);
    setActionError(null);
    setSuccessMessage(null);

    if (!currentUser) {
      navigateToRoute({ kind: "paywall", reason: "guest-apply" });
      return;
    }

    if (currentUser.role !== "student") {
      setApplyError("Отклик доступен только студенту.");
      return;
    }

    if (studentSubscriptionQuery.data?.status !== "active") {
      navigateToRoute({ kind: "paywall", reason: "inactive-subscription" });
      return;
    }

    setIsApplying(true);

    try {
      await apiClient.applyToVacancy(route.vacancyId);
      setSuccessMessage("Отклик отправлен. Если HR заинтересуется, статус появится в разделе «Мои отклики».");
      queryClient.invalidateQueries({ queryKey: ["student-applications"] });
      navigateToRoute({ kind: "feed" });
    } catch (error) {
      if (error instanceof ApiError && error.status === 403 && error.message === "Active subscription required") {
        navigateToRoute({ kind: "paywall", reason: "inactive-subscription" });
      } else {
        setApplyError(getApiErrorMessage(error, "Не удалось отправить отклик."));
      }
    } finally {
      setIsApplying(false);
    }
  }

  async function handleCreateHrVacancy(payload: HRVacancyCreateRequest) {
    setHrSubmitError(null);
    setHrActionError(null);
    setHrActionMessage(null);
    setIsCreatingHrVacancy(true);

    try {
      const vacancy = await apiClient.createHrVacancy(payload);
      setHrActionMessage("Вакансия сохранена как draft. Дальше можно перейти к оплате публикации.");
      await queryClient.invalidateQueries({ queryKey: ["hr-vacancies"] });
      navigateToRoute({ kind: "hr-vacancy", vacancyId: vacancy.id });
    } catch (error) {
      setHrSubmitError(getApiErrorMessage(error, "Не удалось сохранить вакансию."));
    } finally {
      setIsCreatingHrVacancy(false);
    }
  }

  async function handleCreateHrPublishPayment() {
    if (route.kind !== "hr-vacancy") {
      return;
    }

    setHrActionError(null);
    setHrActionMessage(null);
    setIsCreatingHrPayment(true);

    try {
      const payment = await apiClient.createHrVacancyPublishPayment(route.vacancyId);
      setPendingHrPaymentId(payment.payment_id);
      setHrActionMessage("Платеж на публикацию создан. Если mock confirm включен, подтверди его на этом экране.");
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["hr-vacancy-detail", route.vacancyId] }),
        queryClient.invalidateQueries({ queryKey: ["hr-vacancies"] }),
      ]);
    } catch (error) {
      setHrActionError(getApiErrorMessage(error, "Не удалось создать платеж на публикацию."));
    } finally {
      setIsCreatingHrPayment(false);
    }
  }

  async function handleConfirmHrPublishPayment() {
    if (!pendingHrPaymentId || route.kind !== "hr-vacancy") {
      return;
    }

    setHrActionError(null);
    setHrActionMessage(null);
    setIsConfirmingHrPayment(true);

    try {
      await apiClient.confirmMockPayment(pendingHrPaymentId);
      setPendingHrPaymentId(null);
      setHrActionMessage("Оплата подтверждена. Статусы вакансии обновлены по backend-логике.");
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["hr-vacancy-detail", route.vacancyId] }),
        queryClient.invalidateQueries({ queryKey: ["hr-vacancies"] }),
        queryClient.invalidateQueries({ queryKey: ["vacancies", "feed"] }),
      ]);
    } catch (error) {
      setHrActionError(getApiErrorMessage(error, "Не удалось подтвердить платеж на публикацию."));
    } finally {
      setIsConfirmingHrPayment(false);
    }
  }

  async function handleAcceptHrApplication() {
    if (route.kind !== "hr-application") {
      return;
    }

    setHrActionError(null);
    setHrActionMessage(null);
    setIsAcceptingHrApplication(true);

    try {
      const application = await apiClient.acceptHrApplication(route.applicationId);
      queryClient.setQueryData(["hr-application-detail", route.applicationId], application);
      setHrActionMessage("Отклик принят. Контакты появятся только если backend уже вернул их в ответе.");
      await queryClient.invalidateQueries({ queryKey: ["hr-applications"] });
    } catch (error) {
      setHrActionError(getApiErrorMessage(error, "Не удалось принять отклик."));
    } finally {
      setIsAcceptingHrApplication(false);
    }
  }

  async function handleRejectHrApplication() {
    if (route.kind !== "hr-application") {
      return;
    }

    setHrActionError(null);
    setHrActionMessage(null);
    setIsRejectingHrApplication(true);

    try {
      const application = await apiClient.rejectHrApplication(route.applicationId);
      queryClient.setQueryData(["hr-application-detail", route.applicationId], application);
      setHrActionMessage("Отклик отклонен.");
      await queryClient.invalidateQueries({ queryKey: ["hr-applications"] });
    } catch (error) {
      setHrActionError(getApiErrorMessage(error, "Не удалось отклонить отклик."));
    } finally {
      setIsRejectingHrApplication(false);
    }
  }

  async function handleToggleAdminUserBlock(user: AdminUser) {
    setAdminActionError(null);
    setIsUpdatingAdminEntity(true);

    try {
      const updatedUser = await apiClient.updateAdminUser(user.id, { is_blocked: !user.is_blocked });
      queryClient.setQueryData(["admin-user", user.id], updatedUser);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["admin-users"] }),
        queryClient.invalidateQueries({ queryKey: ["admin-stats"] }),
      ]);
    } catch (error) {
      setAdminActionError(getApiErrorMessage(error, "Failed to update user status."));
    } finally {
      setIsUpdatingAdminEntity(false);
    }
  }

  async function handleToggleAdminUserMute(user: AdminUser) {
    setAdminActionError(null);
    setIsUpdatingAdminEntity(true);

    const nextMuteUntil = user.mute_until ? null : new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();

    try {
      const updatedUser = await apiClient.updateAdminUser(user.id, { mute_until: nextMuteUntil });
      queryClient.setQueryData(["admin-user", user.id], updatedUser);
      await queryClient.invalidateQueries({ queryKey: ["admin-users"] });
    } catch (error) {
      setAdminActionError(getApiErrorMessage(error, "Failed to update mute status."));
    } finally {
      setIsUpdatingAdminEntity(false);
    }
  }

  async function handleAdminHrStatus(profileId: string, statusValue: string) {
    setAdminActionError(null);
    setIsUpdatingAdminEntity(true);

    try {
      await apiClient.updateAdminHrProfileStatus(profileId, statusValue);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["admin-hr-profiles"] }),
        queryClient.invalidateQueries({ queryKey: ["admin-stats"] }),
        queryClient.invalidateQueries({ queryKey: ["admin-users"] }),
      ]);
    } catch (error) {
      setAdminActionError(getApiErrorMessage(error, "Failed to update HR status."));
    } finally {
      setIsUpdatingAdminEntity(false);
    }
  }

  async function handleAdminApproveVacancy(vacancyId: string) {
    setAdminActionError(null);
    setIsUpdatingAdminEntity(true);

    try {
      await apiClient.approveAdminModerationVacancy(vacancyId);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["admin-moderation-vacancies"] }),
        queryClient.invalidateQueries({ queryKey: ["admin-stats"] }),
      ]);
    } catch (error) {
      setAdminActionError(getApiErrorMessage(error, "Failed to approve vacancy."));
    } finally {
      setIsUpdatingAdminEntity(false);
    }
  }

  async function handleAdminRejectVacancy(vacancyId: string) {
    setAdminActionError(null);
    setIsUpdatingAdminEntity(true);

    try {
      await apiClient.rejectAdminModerationVacancy(vacancyId, "Rejected by admin");
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["admin-moderation-vacancies"] }),
        queryClient.invalidateQueries({ queryKey: ["admin-stats"] }),
      ]);
    } catch (error) {
      setAdminActionError(getApiErrorMessage(error, "Failed to reject vacancy."));
    } finally {
      setIsUpdatingAdminEntity(false);
    }
  }

  async function handleAdminComplaintStatus(complaintId: string, statusValue: string) {
    setAdminActionError(null);
    setIsUpdatingAdminEntity(true);

    try {
      await apiClient.updateAdminComplaintStatus(complaintId, statusValue, `Updated to ${statusValue}`);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["admin-complaints"] }),
        queryClient.invalidateQueries({ queryKey: ["admin-stats"] }),
      ]);
    } catch (error) {
      setAdminActionError(getApiErrorMessage(error, "Failed to update complaint status."));
    } finally {
      setIsUpdatingAdminEntity(false);
    }
  }

  const authLabel = currentUser?.role === "student" ? "Студент" : currentUser?.role ? currentUser.role : "Гость";
  const selectedAdminUser =
    selectedAdminUserQuery.data ??
    adminUsersQuery.data?.items.find((user) => user.id === selectedAdminUserId) ??
    null;

  if (
    isAdminRoute &&
    (!isAdmin ||
      isAccessDeniedError(adminStatsQuery.error) ||
      isAccessDeniedError(adminUsersQuery.error) ||
      isAccessDeniedError(selectedAdminUserQuery.error) ||
      isAccessDeniedError(adminHrProfilesQuery.error) ||
      isAccessDeniedError(adminModerationQuery.error) ||
      isAccessDeniedError(adminComplaintsQuery.error) ||
      isAccessDeniedError(adminPaymentsQuery.error))
  ) {
    return <AdminAccessDeniedScreen onBackToFeed={() => navigateToRoute({ kind: "feed" })} />;
  }

  if (route.kind === "admin-dashboard" && currentUser && isAdmin) {
    return (
      <AdminDashboardScreen
        currentRoute={route.kind}
        currentUser={currentUser}
        errorMessage={adminActionError ?? (adminStatsQuery.error ? getApiErrorMessage(adminStatsQuery.error, "Failed to load admin stats.") : null)}
        isLoading={adminStatsQuery.isLoading}
        onNavigate={handleAdminNavigate}
        stats={adminStatsQuery.data ?? null}
      />
    );
  }

  if (route.kind === "admin-users" && currentUser && isAdmin) {
    return (
      <AdminUsersScreen
        currentRoute={route.kind}
        currentUser={currentUser}
        errorMessage={
          adminActionError ??
          (adminUsersQuery.error
            ? getApiErrorMessage(adminUsersQuery.error, "Failed to load users.")
            : selectedAdminUserQuery.error
              ? getApiErrorMessage(selectedAdminUserQuery.error, "Failed to load user detail.")
              : null)
        }
        isLoading={adminUsersQuery.isLoading}
        isMutating={isUpdatingAdminEntity}
        onNavigate={handleAdminNavigate}
        onSelectUser={setSelectedAdminUserId}
        onToggleBlock={(user) => void handleToggleAdminUserBlock(user)}
        onToggleMute={(user) => void handleToggleAdminUserMute(user)}
        selectedUser={selectedAdminUser}
        users={adminUsersQuery.data?.items ?? []}
      />
    );
  }

  if (route.kind === "admin-hr" && currentUser && isAdmin) {
    return (
      <AdminHrScreen
        currentRoute={route.kind}
        currentUser={currentUser}
        errorMessage={adminActionError ?? (adminHrProfilesQuery.error ? getApiErrorMessage(adminHrProfilesQuery.error, "Failed to load HR access queue.") : null)}
        isLoading={adminHrProfilesQuery.isLoading}
        isMutating={isUpdatingAdminEntity}
        onNavigate={handleAdminNavigate}
        onUpdateStatus={(profileId, statusValue) => void handleAdminHrStatus(profileId, statusValue)}
        profiles={adminHrProfilesQuery.data?.items ?? []}
      />
    );
  }

  if (route.kind === "admin-moderation" && currentUser && isAdmin) {
    return (
      <AdminModerationScreen
        currentRoute={route.kind}
        currentUser={currentUser}
        errorMessage={adminActionError ?? (adminModerationQuery.error ? getApiErrorMessage(adminModerationQuery.error, "Failed to load moderation queue.") : null)}
        isLoading={adminModerationQuery.isLoading}
        isMutating={isUpdatingAdminEntity}
        onApprove={(vacancyId) => void handleAdminApproveVacancy(vacancyId)}
        onNavigate={handleAdminNavigate}
        onReject={(vacancyId) => void handleAdminRejectVacancy(vacancyId)}
        vacancies={adminModerationQuery.data?.items ?? []}
      />
    );
  }

  if (route.kind === "admin-complaints" && currentUser && isAdmin) {
    return (
      <AdminComplaintsScreen
        complaints={adminComplaintsQuery.data?.items ?? []}
        currentRoute={route.kind}
        currentUser={currentUser}
        errorMessage={adminActionError ?? (adminComplaintsQuery.error ? getApiErrorMessage(adminComplaintsQuery.error, "Failed to load complaints.") : null)}
        isLoading={adminComplaintsQuery.isLoading}
        isMutating={isUpdatingAdminEntity}
        onNavigate={handleAdminNavigate}
        onUpdateStatus={(complaintId, statusValue) => void handleAdminComplaintStatus(complaintId, statusValue)}
      />
    );
  }

  if (route.kind === "admin-payments" && currentUser && isAdmin) {
    return (
      <AdminPaymentsScreen
        currentRoute={route.kind}
        currentUser={currentUser}
        errorMessage={adminActionError ?? (adminPaymentsQuery.error ? getApiErrorMessage(adminPaymentsQuery.error, "Failed to load payments.") : null)}
        isLoading={adminPaymentsQuery.isLoading}
        onNavigate={handleAdminNavigate}
        payments={adminPaymentsQuery.data?.items ?? []}
      />
    );
  }

  if (route.kind === "admin-stats" && currentUser && isAdmin) {
    return (
      <AdminStatsScreen
        currentRoute={route.kind}
        currentUser={currentUser}
        errorMessage={adminActionError ?? (adminStatsQuery.error ? getApiErrorMessage(adminStatsQuery.error, "Failed to load stats.") : null)}
        isLoading={adminStatsQuery.isLoading}
        onNavigate={handleAdminNavigate}
        stats={adminStatsQuery.data ?? null}
      />
    );
  }

  if (isHr && !isHrRoute) {
    return (
      <HrDashboardScreen
        applications={hrApplicationsQuery.data?.items ?? []}
        currentUser={currentUser!}
        errorMessage={
          hrVacanciesQuery.error
            ? getApiErrorMessage(hrVacanciesQuery.error, "Не удалось загрузить HR-вакансии.")
            : hrApplicationsQuery.error
              ? getApiErrorMessage(hrApplicationsQuery.error, "Не удалось загрузить HR-отклики.")
              : null
        }
        isLoading={hrVacanciesQuery.isLoading || hrApplicationsQuery.isLoading}
        onCreateVacancy={() => navigateToRoute({ kind: "hr-create-vacancy" })}
        onOpenApplication={(applicationId) => navigateToRoute({ kind: "hr-application", applicationId })}
        onOpenVacancy={(vacancyId) => navigateToRoute({ kind: "hr-vacancy", vacancyId })}
        vacancies={hrVacanciesQuery.data?.items ?? []}
      />
    );
  }

  if (route.kind === "hr-dashboard" && currentUser && isHr) {
    return (
      <HrDashboardScreen
        applications={hrApplicationsQuery.data?.items ?? []}
        currentUser={currentUser}
        errorMessage={
          hrVacanciesQuery.error
            ? getApiErrorMessage(hrVacanciesQuery.error, "Не удалось загрузить HR-вакансии.")
            : hrApplicationsQuery.error
              ? getApiErrorMessage(hrApplicationsQuery.error, "Не удалось загрузить HR-отклики.")
              : null
        }
        isLoading={hrVacanciesQuery.isLoading || hrApplicationsQuery.isLoading}
        onCreateVacancy={() => navigateToRoute({ kind: "hr-create-vacancy" })}
        onOpenApplication={(applicationId) => navigateToRoute({ kind: "hr-application", applicationId })}
        onOpenVacancy={(vacancyId) => navigateToRoute({ kind: "hr-vacancy", vacancyId })}
        vacancies={hrVacanciesQuery.data?.items ?? []}
      />
    );
  }

  if (route.kind === "hr-create-vacancy" && isHr) {
    return (
      <HrVacancyFormScreen
        isSubmitting={isCreatingHrVacancy}
        onBack={handleHrDashboardNavigate}
        onSubmit={handleCreateHrVacancy}
        submitError={hrSubmitError}
      />
    );
  }

  if (route.kind === "hr-vacancy" && isHr) {
    return (
      <HrVacancyDetailScreen
        actionError={hrActionError}
        actionMessage={hrActionMessage}
        canMockConfirm={CAN_MOCK_CONFIRM}
        errorMessage={hrVacancyDetailQuery.error ? getApiErrorMessage(hrVacancyDetailQuery.error, "Не удалось загрузить вакансию.") : null}
        isConfirmingPayment={isConfirmingHrPayment}
        isCreatingPayment={isCreatingHrPayment}
        isLoading={hrVacancyDetailQuery.isLoading}
        onBack={handleHrDashboardNavigate}
        onConfirmPayment={() => void handleConfirmHrPublishPayment()}
        onCreatePayment={() => void handleCreateHrPublishPayment()}
        pendingPaymentId={pendingHrPaymentId}
        vacancy={hrVacancyDetailQuery.data ?? null}
      />
    );
  }

  if (route.kind === "hr-application" && isHr) {
    return (
      <HrApplicationDetailScreen
        actionError={hrActionError}
        actionMessage={hrActionMessage}
        application={hrApplicationDetailQuery.data ?? null}
        errorMessage={
          hrApplicationDetailQuery.error ? getApiErrorMessage(hrApplicationDetailQuery.error, "Не удалось загрузить отклик.") : null
        }
        isAccepting={isAcceptingHrApplication}
        isLoading={hrApplicationDetailQuery.isLoading}
        isRejecting={isRejectingHrApplication}
        onAccept={() => void handleAcceptHrApplication()}
        onBack={handleHrDashboardNavigate}
        onReject={() => void handleRejectHrApplication()}
      />
    );
  }

  if (route.kind === "vacancy") {
    return (
      <VacancyDetailScreen
        applyError={applyError}
        errorMessage={detailErrorMessage}
        isApplying={isApplying}
        isLoading={detailQuery.isLoading}
        onApply={() => void handleApply()}
        onBack={() => navigateToRoute({ kind: "feed" })}
        vacancy={(detailQuery.data ?? null) as VacancyDetail | null}
      />
    );
  }

  if (route.kind === "paywall") {
    const primaryAction =
      route.reason === "inactive-subscription"
        ? () => navigateToRoute({ kind: "balance" })
        : () => navigateToRoute({ kind: "profile" });

    return (
      <PaywallScreen
        canAuthenticateInTelegram={canAuthenticateInTelegram}
        isAuthenticated={isAuthenticated}
        onBack={() => navigateToRoute({ kind: "feed" })}
        onPrimaryAction={primaryAction}
        primaryLabel={route.reason === "inactive-subscription" ? "Перейти к балансу" : "Открыть профиль"}
        reason={route.reason}
      />
    );
  }

  if (route.kind === "profile") {
    return (
      <ProfileScreen
        canAuthenticateInTelegram={canAuthenticateInTelegram}
        currentUser={currentUser}
        errorMessage={
          studentScreenError ??
          (studentProfileQuery.error ? getApiErrorMessage(studentProfileQuery.error, "Не удалось загрузить профиль.") : null)
        }
        isLoading={authStatus === "authenticating" || studentProfileQuery.isLoading}
        isSaving={isSavingProfile}
        onNavigate={handleNavigate}
        onSave={(payload) => void handleSaveProfile(payload)}
        profile={studentProfileQuery.data ?? null}
        saveError={profileSaveError}
        saveSuccess={profileSaveSuccess}
      />
    );
  }

  if (route.kind === "balance") {
    return (
      <BalanceScreen
        balance={studentBalanceQuery.data ?? null}
        canAuthenticateInTelegram={canAuthenticateInTelegram}
        canMockConfirm={CAN_MOCK_CONFIRM}
        currentUser={currentUser}
        errorMessage={
          studentScreenError ??
          (studentBalanceQuery.error
            ? getApiErrorMessage(studentBalanceQuery.error, "Не удалось загрузить баланс.")
            : paymentHistoryQuery.error
              ? getApiErrorMessage(paymentHistoryQuery.error, "Не удалось загрузить историю платежей.")
              : null)
        }
        isConfirmingPayment={isConfirmingPayment}
        isCreatingPayment={isCreatingPayment}
        isLoading={
          authStatus === "authenticating" ||
          studentBalanceQuery.isLoading ||
          studentSubscriptionQuery.isLoading ||
          paymentHistoryQuery.isLoading
        }
        onConfirmPayment={() => void handleConfirmPayment()}
        onCreatePayment={() => void handleCreatePayment()}
        onNavigate={handleNavigate}
        onQuickAmountPick={(value) => setTopUpAmount(String(value))}
        onTopUpAmountChange={setTopUpAmount}
        paymentError={paymentError}
        paymentSuccess={paymentSuccess}
        payments={paymentHistoryQuery.data?.items ?? []}
        pendingPaymentId={pendingPaymentId}
        subscription={studentSubscriptionQuery.data ?? null}
        topUpAmount={topUpAmount}
      />
    );
  }

  if (route.kind === "applications") {
    return (
      <ApplicationsScreen
        applications={studentApplicationsQuery.data?.items ?? []}
        canAuthenticateInTelegram={canAuthenticateInTelegram}
        currentUser={currentUser}
        errorMessage={
          studentScreenError ??
          (studentApplicationsQuery.error ? getApiErrorMessage(studentApplicationsQuery.error, "Не удалось загрузить отклики.") : null)
        }
        isLoading={authStatus === "authenticating" || studentApplicationsQuery.isLoading}
        onNavigate={handleNavigate}
        onOpenFeed={() => navigateToRoute({ kind: "feed" })}
      />
    );
  }

  return (
    <FeedScreen
      actionError={actionError}
      authLabel={authLabel}
      isError={feedQuery.isError}
      isLoading={feedQuery.isLoading}
      onNavigate={handleNavigate}
      onOpenVacancy={(vacancyId) => void handleOpenVacancy(vacancyId)}
      onRetry={() => void feedQuery.refetch()}
      onSuccessAction={() => navigateToRoute({ kind: "applications" })}
      previewCount={previewCount}
      previewLimit={GUEST_VIEW_LIMIT}
      showPreviewCounter={!isAuthenticated}
      successActionLabel="Открыть мои отклики"
      successMessage={successMessage}
      vacancies={feedQuery.data?.items ?? []}
    />
  );
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}
