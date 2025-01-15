import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

import { Order } from "../client";
import { DefaultTableRender } from "./common/defaultTableRender.tsx";

interface Props {
  orders: Order[];
}

export function OrdersTable({ orders }: Props) {
  const columnHelper = createColumnHelper<Order>();
  const columns = [
    columnHelper.accessor("id", {
      header: () => <span>Order ID</span>,
    }),
    columnHelper.accessor("resource_name", {
      header: () => <span>Product</span>,
    }),
    columnHelper.accessor("status", {
      header: () => <span>Status</span>,
    }),
    columnHelper.accessor("created_at", {
      header: () => <span>Created at</span>,
    }),
    columnHelper.accessor("updated_at", {
      header: () => <span>Updated at</span>,
    }),
  ];
  const table = useReactTable<Order>({
    data: orders,
    columns: columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return <DefaultTableRender<Order> table={table} />;
}
