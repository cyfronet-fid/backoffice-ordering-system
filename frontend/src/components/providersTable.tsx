import { ExternalLinkIcon } from "@chakra-ui/icons";
import { Link } from "@chakra-ui/react";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

import { Provider } from "../client";
import { DefaultTableRender } from "./common/defaultTableRender.tsx";

interface Props {
  providers: Provider[];
}

export function ProvidersTable({ providers }: Props) {
  const columnHelper = createColumnHelper<Provider>();
  const columns = [
    columnHelper.accessor("id", {
      header: () => <span>Provider ID</span>,
    }),
    columnHelper.accessor("website", {
      header: () => <span>Website</span>,
      cell: (info) => (
        <Link href={info.getValue()} isExternal>
          {info.getValue()} <ExternalLinkIcon mx="2px" />
        </Link>
      ),
    }),
    columnHelper.accessor("created_at", {
      header: () => <span>Created at</span>,
    }),
  ];
  const table = useReactTable<Provider>({
    data: providers,
    columns: columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return <DefaultTableRender<Provider> table={table} />;
}
