import { Heading } from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";

import { Provider, readProviders } from "../../../client";
import { ProvidersTable } from "../../../components/providersTable.tsx";

export const Route = createFileRoute("/_main/providers/")({
  component: Providers,
  loader: async () => {
    const { data } = await readProviders();
    return data;
  },
});

function Providers() {
  const providers: Provider[] = Route.useLoaderData();
  return (
    <>
      <Heading mb={2}>Providers</Heading>
      <ProvidersTable providers={providers} />
    </>
  );
}
