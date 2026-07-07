import { backButton, init, miniApp, retrieveRawInitData, themeParams, viewport } from "@tma.js/sdk";

export function getRawInitDataSafe() {
  try {
    return retrieveRawInitData();
  } catch {
    return undefined;
  }
}

export function setupTelegramMiniApp(onBack: () => void) {
  if (typeof window === "undefined") {
    return () => undefined;
  }

  try {
    const cleanup = init();
    miniApp.mount();
    themeParams.mount();
    viewport.mount();

    try {
      miniApp.bindCssVars();
    } catch {}
    try {
      themeParams.bindCssVars();
    } catch {}
    try {
      viewport.bindCssVars();
    } catch {}

    miniApp.ready();
    viewport.expand();
    backButton.mount();
    const offBack = backButton.onClick(onBack);

    return () => {
      offBack?.();
      backButton.unmount();
      viewport.unmount();
      themeParams.unmount();
      miniApp.unmount();
      cleanup?.();
    };
  } catch {
    return () => undefined;
  }
}

export function setTelegramBackButtonVisible(visible: boolean) {
  try {
    if (visible) {
      backButton.show();
    } else {
      backButton.hide();
    }
  } catch {}
}
