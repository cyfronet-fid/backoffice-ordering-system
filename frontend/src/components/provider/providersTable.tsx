import { ProviderPublic } from "@/client";
import { DefaultTableRender } from "@/components/common/defaultTableRender.tsx";
import { convertTimestamp } from "@/utils.ts";
import { Link } from "@chakra-ui/react";
import { useRouter } from "@tanstack/react-router";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

interface Props {
  providers: ProviderPublic[];
}

export function ProvidersTable({ providers }: Props) {
  const router = useRouter();

  const columnHelper = createColumnHelper<ProviderPublic>();
  const columns = [
    columnHelper.accessor("name", {
      header: () => <span>Name</span>,
    }),
    columnHelper.accessor("id", {
      header: () => <span>Provider ID</span>,
    }),
    columnHelper.accessor("website", {
      header: () => <span>Contact</span>,
      cell: (info) => (
        <Link href={info.getValue()} color="blue.500" isExternal>
          {info.getValue()}
        </Link>
      ),
    }),
    columnHelper.accessor("created_at", {
      header: () => <span>Created at</span>,
      cell: (info) => convertTimestamp(info.getValue()!),
    }),
  ];
  const table = useReactTable<ProviderPublic>({
    data: providers,
    columns: columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <DefaultTableRender<ProviderPublic>
      table={table}
      rowHook={(provider) => {
        router.navigate({ to: `/providers/${provider.id}` });
      }}
    />
  );
}
