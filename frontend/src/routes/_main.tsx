import { Spinner } from "@chakra-ui/react";
import { createFileRoute, Outlet } from "@tanstack/react-router";

import { DefaultError } from "../components/common/defaultError.tsx";

export const Route = createFileRoute("/_main")({
  component: RouteComponent,
  pendingComponent: () => <Spinner />,
  errorComponent: ({ error }) => <DefaultError error={error} />,
});

function RouteComponent() {
  return <Outlet />;
}
