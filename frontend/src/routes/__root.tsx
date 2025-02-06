import { createRootRouteWithContext, Outlet } from "@tanstack/react-router";
import { AuthContextProps } from "react-oidc-context";

interface RouterContext {
  auth: AuthContextProps;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
});

export function RootLayout() {
  return <Outlet />;
}
