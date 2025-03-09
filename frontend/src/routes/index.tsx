import { Header } from "@/components/layout/header.tsx";
import { Button, Flex, Grid, GridItem, Heading } from "@chakra-ui/react";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { useAuth } from "react-oidc-context";

export const Route = createFileRoute("/")({
  component: RouteComponent,
  beforeLoad: ({ context }) => {
    if (context.auth.isAuthenticated) {
      throw redirect({ to: "/orders" });
    }
  },
});

function RouteComponent() {
  const auth = useAuth();

  return (
    <Grid templateRows="80px 1fr" h="100vh">
      <GridItem>
        <Header />
      </GridItem>

      <GridItem>
        <Flex height="100vh" align="center" justify="center" direction="column">
          <Heading mb={6}>Welcome to the Backoffice Ordering System</Heading>
          <Button onClick={() => void auth.signinRedirect()}>Login</Button>
        </Flex>
      </GridItem>
    </Grid>
  );
}
