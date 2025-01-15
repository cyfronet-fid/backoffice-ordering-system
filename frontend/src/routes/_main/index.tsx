import { Heading } from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_main/")({
  component: Index,
});

function Index() {
  return (
    <div>
      <Heading>Welcome to the Backoffice Ordering System</Heading>
    </div>
  );
}
