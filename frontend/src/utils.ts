import { AuthContextProps } from "react-oidc-context";

export const getAuthorizationHeader = (auth: AuthContextProps) => {
  return {
    Authorization: `Bearer: ${auth.user?.access_token}`,
  };
};

export const wait = (seconds: number) =>
  new Promise((resolve) => setTimeout(resolve, 1000 * seconds));
