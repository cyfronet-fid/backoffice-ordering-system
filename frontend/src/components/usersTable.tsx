import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

import { User } from "../client";
import { DefaultTableRender } from "./common/defaultTableRender.tsx";

interface Props {
  users: User[];
}

export function UsersTable({ users }: Props) {
  const columnHelper = createColumnHelper<User>();
  const columns = [
    columnHelper.accessor("id", {
      header: () => <span>User ID</span>,
    }),
    columnHelper.accessor("email", {
      header: () => <span>Email</span>,
    }),
    columnHelper.accessor("user_type", {
      header: () => <span>Role</span>,
    }),
    columnHelper.accessor("created_at", {
      header: () => <span>Created at</span>,
    }),
  ];
  const table = useReactTable<User>({
    data: users,
    columns: columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return <DefaultTableRender<User> table={table} />;
}
