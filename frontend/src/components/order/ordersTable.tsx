import { OrderPublic, OrderPublicWithDetails } from "@/client";
import { DefaultTableRender } from "@/components/common/defaultTableRender.tsx";
import { StatusTag } from "@/components/common/statusTag.tsx";
import { convertTimestamp, getMpUser, isExtendedOrder } from "@/utils.ts";
import { useRouter } from "@tanstack/react-router";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

interface Props {
  orders: (OrderPublicWithDetails | OrderPublic)[];
}

export function OrdersTable({ orders }: Props) {
  const router = useRouter();

  const baseColumnHelper = createColumnHelper<OrderPublic>();
  const baseColumns = [
    baseColumnHelper.accessor("id", {
      header: () => <span>Order ID</span>,
    }),
    baseColumnHelper.accessor("resource_name", {
      header: () => <span>Product</span>,
    }),
    baseColumnHelper.accessor("status", {
      header: () => <span>Status</span>,
      cell: (info) => <StatusTag status={info.getValue()} />,
    }),
    baseColumnHelper.accessor("updated_at", {
      header: () => <span>Updated at</span>,
      cell: (info) => convertTimestamp(info.getValue()!),
    }),
  ];

  const extendedColumnHelper = createColumnHelper<OrderPublicWithDetails>();
  const extendedColumns = [
    extendedColumnHelper.accessor("id", {
      header: () => <span>Order ID</span>,
    }),
    extendedColumnHelper.accessor("resource_name", {
      header: () => <span>Product</span>,
    }),
    extendedColumnHelper.accessor("users", {
      header: () => <span>User</span>,
      cell: (info) => {
        const users = info.getValue();
        return getMpUser(users)?.name ?? "-";
      },
    }),
    extendedColumnHelper.accessor("status", {
      header: () => <span>Status</span>,
      cell: (info) => <StatusTag status={info.getValue()} />,
    }),
    extendedColumnHelper.accessor("providers", {
      header: () => <span>Providers</span>,
      cell: (info) =>
        info
          .getValue()!
          .map(({ name }) => name)
          .join(", "),
    }),
    extendedColumnHelper.accessor("created_at", {
      header: () => <span>Created at</span>,
      cell: (info) => convertTimestamp(info.getValue()!),
    }),
    extendedColumnHelper.accessor("updated_at", {
      header: () => <span>Updated at</span>,
      cell: (info) => convertTimestamp(info.getValue()!),
    }),
  ];

  const table = useReactTable<OrderPublic | OrderPublicWithDetails>({
    data: orders,
    columns:
      orders.length > 0 && !orders.every(isExtendedOrder)
        ? baseColumns
        : extendedColumns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <DefaultTableRender<OrderPublic | OrderPublicWithDetails>
      table={table}
      rowHook={(order) => {
        if (order.id) {
          router.navigate({ to: `/orders/${order.id}` });
        }
      }}
    />
  );
}
