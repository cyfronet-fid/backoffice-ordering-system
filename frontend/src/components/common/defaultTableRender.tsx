import { Table, Tbody, Td, Th, Thead, Tr } from "@chakra-ui/react";
import { flexRender, Table as TanStackTable } from "@tanstack/react-table";

interface Props<T> {
  table: TanStackTable<T>;
}
export function DefaultTableRender<T>({ table }: Props<T>) {
  return (
    <>
      <div className="p-2">
        <Table>
          <Thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <Tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <Th key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                  </Th>
                ))}
              </Tr>
            ))}
          </Thead>
          <Tbody>
            {table.getRowModel().rows.map((row) => (
              <Tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <Td key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </Td>
                ))}
              </Tr>
            ))}
          </Tbody>
        </Table>
      </div>
    </>
  );
}
