import { Grid, GridItem, Spinner } from "@chakra-ui/react";
import { createRootRoute, Outlet } from "@tanstack/react-router";

import { DefaultError } from "../components/common/defaultError.tsx";
import { NotFound } from "../components/common/notFound.tsx";
import { Header } from "../components/layout/header.tsx";
import { Nav } from "../components/layout/nav.tsx";

export const Route = createRootRoute({
  component: RootLayout,
  notFoundComponent: () => <NotFound />,
  pendingComponent: () => <Spinner />,
  errorComponent: ({ error }) => <DefaultError error={error} />,
});

export function RootLayout() {
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
