import { Heading } from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";

import { Order, readOrders } from "../../../client";
import { OrdersTable } from "../../../components/ordersTable.tsx";

export const Route = createFileRoute("/_main/orders/")({
  component: Orders,
  loader: async () => {
    const { data } = await readOrders();
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
