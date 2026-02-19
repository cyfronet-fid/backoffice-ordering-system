import { getCurrentUser } from "@/client";
import { NoAccessWidget } from "@/components/common/noAccessWidget.tsx";
import { Header } from "@/components/layout/header.tsx";
import { Nav } from "@/components/layout/nav.tsx";
import { getAuthorizationHeader } from "@/utils.ts";
import { Grid, GridItem } from "@chakra-ui/react";
import { createFileRoute, Outlet } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated")({
  component: RouteComponent,
  beforeLoad: async ({ context }) => {
    if (!context.auth.isAuthenticated) {
      void context.auth.signinRedirect();
      return;
    }
  },
  loader: async ({ context }) => {
    const { data } = await getCurrentUser({
      headers: { ...getAuthorizationHeader(context.auth) },
    });
    return { appUser: data };
  },
  staleTime: Infinity,
});

function RouteComponent() {
  const { appUser } = Route.useLoaderData();

  const roles = appUser?.user_type ?? [];

  const isOnlyMpUser = roles.every((role) => role === "mp_user");

  if (isOnlyMpUser) {
    return <NoAccessWidget />;
  }

  return (
    <Grid
      templateAreas={`
        "header header"
        "nav main"
      `}
      gridTemplateRows="80px 1fr"
      gridTemplateColumns="250px 1fr"
      height="100vh"
      bg="gray.200"
    >
      <GridItem area="header" bg="gray.200">
        <Header />
      </GridItem>

      <GridItem area="nav" bg="white" borderRadius="md" mr="4">
        <Nav />
      </GridItem>

      <GridItem area="main" bg="white" borderRadius="md" p="6" mr="16">
        <Outlet />
      </GridItem>
    </Grid>
  );
}
