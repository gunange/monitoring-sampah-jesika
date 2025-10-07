export const appName = import.meta.env.VITE_APP_NAME;
export const appCode = import.meta.env.VITE_APP_CODE;
export const appDeskripsi = import.meta.env.VITE_APP_DESCRIPTION;
export const appLogo = import.meta.env.VITE_APP_LOGO;
export const appLogoDark = import.meta.env.VITE_APP_LOGO_DARK;
export const appLogoLight = import.meta.env.VITE_APP_LOGO_LIGHT;
export const appMaxFileSize = Number(import.meta.env.VITE_APP_MAX_FILE_SIZE_MB) * 1024 * 1024; // dalam byte

export const apps_version = import.meta.env.VITE_APP_VERSION;
export const apps_env = import.meta.env.VITE_APP_ENV;
export const apps_debug = import.meta.env.VITE_APP_DEBUG === "true";

export const tokenName = `token-${appCode}`;
