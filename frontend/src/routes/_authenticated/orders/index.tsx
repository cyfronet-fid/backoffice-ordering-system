import { Order, readOrders } from "@/client";
import { OrdersTable } from "@/components/ordersTable.tsx";
import { getAuthorizationHeader } from "@/utils.ts";
import { Heading } from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";

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
  const orders: Order[] = Route.useLoaderData();

  return (
    <>
      <Heading mb={2}>Orders</Heading>
      <OrdersTable orders={orders}></OrdersTable>
    </>
  );
}
