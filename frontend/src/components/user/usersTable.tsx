import { UserPublic } from "@/client";
import { DefaultTableRender } from "@/components/common/defaultTableRender.tsx";
import { RoleTag } from "@/components/common/roleTag.tsx";
import { convertTimestamp } from "@/utils.ts";
import { Badge, Flex } from "@chakra-ui/react";
import { useRouter } from "@tanstack/react-router";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useAuth } from "react-oidc-context";

interface Props {
  users: UserPublic[];
}

export function UsersTable({ users }: Props) {
  const router = useRouter();
  const auth = useAuth();

  const columnHelper = createColumnHelper<UserPublic>();
  const columns = [
    columnHelper.accessor("name", {
      header: () => <span>Name</span>,
      cell: (info) =>
        auth.user?.profile.email === info.row.original.email ? (
          <Flex gap={"2"}>
            {info.getValue()} <Badge colorScheme={"purple"}>You</Badge>
          </Flex>
        ) : (
          <div>{info.getValue()}</div>
        ),
    }),
    columnHelper.accessor("id", {
      header: () => <span>User ID</span>,
    }),
    columnHelper.accessor("email", {
      header: () => <span>Email</span>,
    }),
    columnHelper.accessor("user_type", {
      header: () => <span>Roles</span>,
      cell: (info) => (
        <Flex gap={"2"}>
          {info.getValue().map((userType) => (
            <RoleTag
              key={`${info.row.original.id}-${userType}`}
              role={userType}
            />
          ))}
        </Flex>
      ),
    }),
    columnHelper.accessor("created_at", {
      header: () => <span>Created at</span>,
      cell: (info) => convertTimestamp(info.getValue()!),
    }),
  ];
  const table = useReactTable<UserPublic>({
    data: users,
    columns: columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <DefaultTableRender<UserPublic>
      table={table}
      rowHook={(order) => {
        router.navigate({ to: `/users/${order.id}` });
      }}
    />
  );
}
