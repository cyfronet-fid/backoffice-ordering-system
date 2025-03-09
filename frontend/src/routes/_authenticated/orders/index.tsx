import { OrderPublicWithProviders, readOrders } from "@/client";
import { OrdersTable } from "@/components/order/ordersTable.tsx";
import { getAuthorizationHeader, useDebouncedValue } from "@/utils.ts";
import { Flex, Heading, Input } from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";

export const Route = createFileRoute("/_authenticated/orders/")({
  component: Orders,
  loader: async ({ context }) => {
    const { data } = await readOrders({
      headers: { ...getAuthorizationHeader(context.auth) },
    });
    return data;
  },
});

export function Orders() {
  const fullOrders = Route.useLoaderData()!;
  const [query, setQuery] = useState<string>("");
  // This eases off backend to not hit with every character change. Change the debounce delay if needed.
  const debouncedQuery = useDebouncedValue(query, 200);

  const orderFilterPredicate = (
    order: OrderPublicWithProviders,
    queryBy: string,
  ) => {
    // TODO: We'd probably like more sophisticated search later, but it's good enough for now
    const flattenedOrder = [
      order.id?.toString(),
      order.resource_name?.toLowerCase(),
      order.status?.toLowerCase(),
      order.providers?.map((p) => p.name.toLowerCase()).join(", "),
    ]
      .filter(Boolean)
      .join(" ");
    return flattenedOrder.includes(queryBy.trim().toLowerCase());
  };

  const filteredOrders = useMemo(() => {
    return debouncedQuery === ""
      ? fullOrders
      : fullOrders.filter((order) =>
          orderFilterPredicate(order, debouncedQuery),
        );
  }, [debouncedQuery, fullOrders]); // Recomputes when query changes

  return (
    <>
      <Flex align="center" justify="space-between">
        <Heading mb={2}>Orders</Heading>
        <Input
          placeholder={"Search orders..."}
          width={"250px"}
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
      </Flex>
      <OrdersTable orders={filteredOrders}></OrdersTable>
    </>
  );
}
