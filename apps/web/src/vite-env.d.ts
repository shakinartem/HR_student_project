/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_APP_ENV?: string;
  readonly VITE_GUEST_FREE_VACANCY_VIEWS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
