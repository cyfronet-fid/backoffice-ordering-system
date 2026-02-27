import { WebStorageStateStore } from "oidc-client-ts";
import { AuthProviderProps } from "react-oidc-context";

interface AppConfig {
  backendUrl: string;
  keycloakHost: string;
  keycloakRealm: string;
  keycloakClientId: string;
}

export const appConfig: AppConfig = {
  backendUrl: import.meta.env.VITE_BACKEND_URL || "http://localhost:8000",
  keycloakHost:
    import.meta.env.VITE_KEYCLOAK_HOST ||
    "https://keycloak.docker-fid.grid.cyf-kr.edu.pl",
  keycloakRealm: import.meta.env.VITE_KEYCLOAK_REALM || "core",
  keycloakClientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || "bos",
};

export const oidcConfig: AuthProviderProps = {
  authority: `${appConfig.keycloakHost}/realms/${appConfig.keycloakRealm}`,
  client_id: appConfig.keycloakClientId,
  redirect_uri: window.location.origin,
  onSigninCallback: async (): Promise<void> => {
    // Removes the OIDC callback params from path
    window.history.replaceState({}, document.title, window.location.pathname);
  },
  monitorSession: true,
  userStore: new WebStorageStateStore({ store: window.sessionStorage }),
  post_logout_redirect_uri: window.location.origin,
  automaticSilentRenew: true, // works even without this flag, added for clarity
};
