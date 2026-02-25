---
name: tanstack-table
description: TanStack Table patterns covering column definitions, sorting, filtering, pagination, row selection, column visibility, grouping, virtual scrolling, and React integration for headless, type-safe data tables.
---

# TanStack Table

This skill should be used when building data tables with TanStack Table (React Table). It covers column definitions, sorting, filtering, pagination, and advanced features.

## When to Use This Skill

Use this skill when you need to:

- Build headless, fully customizable data tables
- Add sorting, filtering, and pagination
- Implement row selection and column visibility
- Handle large datasets with virtual scrolling
- Build type-safe table configurations

## Basic Table

```tsx
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  createColumnHelper,
} from "@tanstack/react-table";

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  createdAt: Date;
}

const columnHelper = createColumnHelper<User>();

const columns = [
  columnHelper.accessor("name", {
    header: "Name",
    cell: (info) => <span className="font-medium">{info.getValue()}</span>,
  }),
  columnHelper.accessor("email", { header: "Email" }),
  columnHelper.accessor("role", {
    header: "Role",
    cell: (info) => <span className="badge">{info.getValue()}</span>,
  }),
  columnHelper.accessor("createdAt", {
    header: "Joined",
    cell: (info) => info.getValue().toLocaleDateString(),
  }),
];

function UsersTable({ data }: { data: User[] }) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <table>
      <thead>
        {table.getHeaderGroups().map((hg) => (
          <tr key={hg.id}>
            {hg.headers.map((header) => (
              <th key={header.id}>
                {flexRender(header.column.columnDef.header, header.getContext())}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map((row) => (
          <tr key={row.id}>
            {row.getVisibleCells().map((cell) => (
              <td key={cell.id}>
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

## Sorting and Filtering

```tsx
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  SortingState,
  ColumnFiltersState,
} from "@tanstack/react-table";
import { useState } from "react";

function SortableTable({ data, columns }: Props) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState("");

  const table = useReactTable({
    data,
    columns,
    state: { sorting, columnFilters, globalFilter },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  return (
    <div>
      <input
        value={globalFilter}
        onChange={(e) => setGlobalFilter(e.target.value)}
        placeholder="Search all columns..."
      />
      <table>
        <thead>
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((header) => (
                <th
                  key={header.id}
                  onClick={header.column.getToggleSortingHandler()}
                  style={{ cursor: "pointer" }}
                >
                  {flexRender(header.column.columnDef.header, header.getContext())}
                  {{ asc: " ↑", desc: " ↓" }[header.column.getIsSorted() as string] ?? ""}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

## Pagination

```tsx
import { getPaginationRowModel, PaginationState } from "@tanstack/react-table";

function PaginatedTable({ data, columns }: Props) {
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

  const table = useReactTable({
    data,
    columns,
    state: { pagination },
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  return (
    <div>
      {/* ... table body ... */}
      <div className="pagination">
        <button onClick={() => table.firstPage()} disabled={!table.getCanPreviousPage()}>
          «
        </button>
        <button onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}>
          ‹
        </button>
        <span>
          Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
        </span>
        <button onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>
          ›
        </button>
        <button onClick={() => table.lastPage()} disabled={!table.getCanNextPage()}>
          »
        </button>
        <select
          value={pagination.pageSize}
          onChange={(e) => table.setPageSize(Number(e.target.value))}
        >
          {[10, 20, 50, 100].map((size) => (
            <option key={size} value={size}>Show {size}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
```

## Row Selection

```tsx
import { RowSelectionState } from "@tanstack/react-table";

const [rowSelection, setRowSelection] = useState<RowSelectionState>({});

const selectColumn = columnHelper.display({
  id: "select",
  header: ({ table }) => (
    <input
      type="checkbox"
      checked={table.getIsAllRowsSelected()}
      onChange={table.getToggleAllRowsSelectedHandler()}
    />
  ),
  cell: ({ row }) => (
    <input
      type="checkbox"
      checked={row.getIsSelected()}
      onChange={row.getToggleSelectedHandler()}
    />
  ),
});

// Access selected rows
const selectedRows = table.getSelectedRowModel().rows;
```

## Additional Resources

- TanStack Table docs: https://tanstack.com/table/latest
- Examples: https://tanstack.com/table/latest/docs/framework/react/examples
