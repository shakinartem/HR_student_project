export interface VacancyListItem {
  id: string;
  title: string;
  company_name: string | null;
  category: string;
  job_type: string;
  salary_text: string;
  salary_min: number | null;
  salary_max: number | null;
  district: string | null;
  schedule: string;
  format: string | null;
  is_promoted: boolean;
  published_at: string | null;
}

export interface VacancyListResponse {
  items: VacancyListItem[];
}

export interface VacancyDetail extends VacancyListItem {
  address: string | null;
  description: string | null;
  requirements: string | null;
  conditions: string | null;
  experience_required: boolean;
}

export interface VacancyViewResponse {
  vacancy_id: string;
  view_count: number;
  viewer_type: string;
}

export interface User {
  id: string;
  telegram_id: number | null;
  role: string;
  username: string | null;
  first_name: string;
  last_name: string | null;
  phone: string | null;
  email: string | null;
  is_blocked: boolean;
  mute_until: string | null;
}

export interface TelegramAuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface UserUpdateRequest {
  first_name?: string;
  last_name?: string;
  phone?: string;
  email?: string;
}

export interface StudentProfile {
  university: string | null;
  course: number | null;
  speciality: string | null;
  preferred_job_types: string[] | null;
  preferred_schedule: string[] | null;
  preferred_districts: string[] | null;
  experience_text: string | null;
  profile_completed: boolean;
}

export interface StudentProfileUpdateRequest {
  university?: string | null;
  course?: number | null;
  speciality?: string | null;
  preferred_job_types?: string[] | null;
  preferred_schedule?: string[] | null;
  preferred_districts?: string[] | null;
  experience_text?: string | null;
}

export interface BalanceTransaction {
  id: string;
  amount: string;
  type: string;
  reason: string;
  payment_id: string | null;
  created_at: string;
}

export interface StudentBalanceResponse {
  balance: string;
  currency: string;
  transactions: BalanceTransaction[];
}

export interface StudentSubscription {
  status: string;
  starts_at: string | null;
  expires_at: string | null;
}

export interface PaymentCreateRequest {
  amount: number;
  purpose: "student_balance_topup";
}

export interface PaymentCreateResponse {
  payment_id: string;
  status: string;
  confirmation_url: string;
}

export interface Payment {
  id: string;
  amount: string;
  currency: string;
  provider: string;
  provider_payment_id: string | null;
  status: string;
  purpose: string;
  entity_type: string | null;
  entity_id: string | null;
  created_at: string;
  paid_at: string | null;
}

export interface PaymentHistoryResponse {
  items: Payment[];
}

export interface HRVacancyHiddenContacts {
  contact_name: string | null;
  contact_phone: string | null;
  contact_email: string | null;
  contact_telegram: string | null;
}

export interface HRVacancy {
  id: string;
  title: string;
  category: string;
  job_type: string;
  schedule: string;
  salary_text: string;
  salary_min: number | null;
  salary_max: number | null;
  district: string | null;
  address: string | null;
  format: string | null;
  description: string | null;
  responsibilities: string | null;
  requirements: string | null;
  conditions: string | null;
  experience_required: boolean;
  photo_url: string | null;
  status: string;
  moderation_status: string;
  payment_required: boolean;
  is_promoted: boolean;
  published_at: string | null;
  expires_at: string | null;
  hidden_contacts: HRVacancyHiddenContacts;
}

export interface HRVacancyListResponse {
  items: HRVacancy[];
}

export interface HRVacancyCreateRequest {
  title: string;
  category: string;
  job_type: string;
  schedule: string;
  salary_text: string;
  salary_min: number | null;
  salary_max: number | null;
  district: string | null;
  address: string | null;
  format: string | null;
  description: string | null;
  responsibilities: string | null;
  requirements: string | null;
  conditions: string | null;
  experience_required: boolean;
  photo_url: string | null;
}

export interface HRApplicationStudentSummary {
  first_name: string | null;
  university: string | null;
  course: number | null;
  speciality: string | null;
  preferred_schedule: string[] | null;
  experience_text: string | null;
  student_comment: string | null;
}

export interface HRApplicationContacts {
  phone: string | null;
  email: string | null;
  telegram_username: string | null;
}

export interface HRApplication {
  id: string;
  vacancy_id: string;
  vacancy_title: string | null;
  status: string;
  student: HRApplicationStudentSummary;
  contacts: HRApplicationContacts | null;
  created_at: string | null;
}

export interface HRApplicationListResponse {
  items: HRApplication[];
}

export interface StudentApplication {
  id: string;
  vacancy_id: string;
  vacancy_title: string | null;
  company_name: string | null;
  status: string;
  created_at: string | null;
}

export interface StudentApplicationListResponse {
  items: StudentApplication[];
}

export interface AdminUser extends User {
  created_at: string;
  updated_at: string;
}

export interface AdminUserListResponse {
  items: AdminUser[];
}

export interface AdminUserUpdateRequest {
  role?: string | null;
  is_blocked?: boolean | null;
  mute_until?: string | null;
}

export interface AdminUserMini {
  id: string;
  telegram_id: number | null;
  username: string | null;
  first_name: string;
  last_name: string | null;
  role: string;
}

export interface AdminCompanyMini {
  id: string;
  name: string;
  status: string;
}

export interface AdminHRProfile {
  id: string;
  position: string | null;
  verified_status: string;
  created_at: string;
  updated_at: string;
  user: AdminUserMini;
  company: AdminCompanyMini;
}

export interface AdminHRProfileListResponse {
  items: AdminHRProfile[];
}

export interface AdminModerationVacancy {
  id: string;
  title: string;
  status: string;
  moderation_status: string;
  category: string;
  salary_text: string;
  company_name: string | null;
  hr_user_id: string;
  published_at: string | null;
  created_at: string;
  moderation_reason: string | null;
}

export interface AdminModerationVacancyListResponse {
  items: AdminModerationVacancy[];
}

export interface AdminComplaint {
  id: string;
  reporter_user_id: string;
  target_user_id: string;
  vacancy_id: string | null;
  application_id: string | null;
  reason: string;
  status: string;
  admin_comment: string | null;
  created_at: string;
  updated_at: string;
}

export interface AdminComplaintListResponse {
  items: AdminComplaint[];
}

export interface AdminPayment extends Payment {
  user_id: string;
  user: AdminUserMini;
}

export interface AdminPaymentListResponse {
  items: AdminPayment[];
}

export interface AdminStats {
  total_users: number;
  students: number;
  hr_users: number;
  active_vacancies: number;
  applications: number;
  succeeded_payments: number;
  open_complaints: number;
  manual_review_vacancies: number;
}
