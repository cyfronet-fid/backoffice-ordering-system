import { getProviderById } from "@/client";
import { NotFound } from "@/components/common/notFound.tsx";
import { OrdersTable } from "@/components/order/ordersTable.tsx";
import { ProviderCard } from "@/components/provider/providerCard.tsx";
import { getAuthorizationHeader } from "@/utils.ts";
import { Box, Button, Flex, Heading } from "@chakra-ui/react";
import { createFileRoute, Link as RouterLink } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/providers/$providerId")({
  component: RouteComponent,
  loader: async ({ context, params }) => {
    const { data } = await getProviderById({
      headers: { ...getAuthorizationHeader(context.auth) },
      path: { provider_id: Number(params.providerId) },
    });
    return data;
  },
});

function RouteComponent() {
  const provider = Route.useLoaderData()!;

  if (!provider) {
    return <NotFound />;
  }

  return (
    <Box p={6}>
      <Flex justify="space-between" align="center" mb={4}>
        <Heading>{`Provider > ${provider.id}`}</Heading>
        <Button as={RouterLink} to={"/providers"} variant="outline">
          Back to providers
        </Button>
      </Flex>

      <Flex gap={6} align="flex-start">
        <Box flex="1">
          <ProviderCard provider={provider} />
        </Box>

        <Box flex="1">
          {provider.orders && provider.orders.length > 0 ? (
            <OrdersTable orders={provider.orders!} />
          ) : (
            <Flex align={"center"} justify={"center"}>
              <Heading size={"md"}>No orders!</Heading>
            </Flex>
          )}
        </Box>
      </Flex>
    </Box>
  );
}
