import { ProviderPublic, readProviders } from "@/client";
import { ProvidersTable } from "@/components/provider/providersTable.tsx";
import { getAuthorizationHeader } from "@/utils.ts";
import { Heading } from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/providers/")({
  component: Providers,
  loader: async ({ context }) => {
    const { data } = await readProviders({
      headers: { ...getAuthorizationHeader(context.auth) },
    });
    return data;
  },
});

function Providers() {
  const providers: ProviderPublic[] = Route.useLoaderData();
  return (
    <>
      <Heading mb={2}>Providers</Heading>
      <ProvidersTable providers={providers} />
    </>
  );
}
