import React from 'react';
import { cn } from '@/lib/utils';
import { Inbox } from 'lucide-react';

export interface Column<T> {
  /** Unique identifier for the column. Falls back to accessorKey or index if omitted. */
  id?: string;
  /** Header label or custom ReactNode */
  header: React.ReactNode;
  /** Key of property on row object to display */
  accessorKey?: keyof T;
  /** Function to compute cell value from row object */
  accessorFn?: (row: T, index: number) => React.ReactNode;
  /** Custom cell renderer (receives full row item and row index) */
  cell?: (row: T, index: number) => React.ReactNode;
  /** Text alignment for header and cells */
  align?: 'left' | 'center' | 'right';
  /** Custom CSS classes for <th> header cell */
  headerClassName?: string;
  /** Custom CSS classes for <td> body cell */
  className?: string;
}

export interface DataTableProps<T> {
  /** Array of row data */
  data: T[];
  /** Column definitions */
  columns: Column<T>[];
  /** Function to extract a unique key for each row. Defaults to row.id or index */
  getRowKey?: (row: T, index: number) => React.Key;
  /** Indicates whether the table is in a loading state */
  isLoading?: boolean;
  /** Number of skeleton rows to render while loading (default: 4) */
  skeletonRowCount?: number;
  /** Optional loading message displayed with the skeleton */
  loadingMessage?: string;
  /** Message to show when data is empty */
  emptyMessage?: string;
  /** Optional custom empty state ReactNode */
  emptyState?: React.ReactNode;
  /** Callback fired when a row is clicked */
  onRowClick?: (row: T, index: number) => void;
  /** Custom className for the outer card container */
  className?: string;
  /** Custom className for the <table> element */
  tableClassName?: string;
  /** Custom className for the <thead> element */
  theadClassName?: string;
  /** Custom className for the <tbody> element */
  tbodyClassName?: string;
  /** Custom row className or resolver function */
  rowClassName?: string | ((row: T, index: number) => string);
  /** Optional caption or table summary */
  caption?: string;
}

const ALIGN_MAP = {
  left: 'text-left',
  center: 'text-center',
  right: 'text-right',
};

const SKELETON_ALIGN_MAP = {
  left: 'w-3/4 max-w-[140px]',
  center: 'w-20 mx-auto',
  right: 'w-20 ml-auto',
};

/**
 * Reusable, typed DataTable component designed for Brightloop.
 * Supports configurable columns, custom cell renderers, row click events,
 * animated loading skeletons, and responsive horizontal scroll.
 */
export function DataTable<T>({
  data,
  columns,
  getRowKey,
  isLoading = false,
  skeletonRowCount = 4,
  loadingMessage,
  emptyMessage = 'No records found',
  emptyState,
  onRowClick,
  className,
  tableClassName,
  theadClassName,
  tbodyClassName,
  rowClassName,
  caption,
}: DataTableProps<T>) {
  const getCellContent = (column: Column<T>, row: T, index: number): React.ReactNode => {
    if (column.cell) {
      return column.cell(row, index);
    }
    if (column.accessorFn) {
      return column.accessorFn(row, index);
    }
    if (column.accessorKey !== undefined) {
      const val = row[column.accessorKey];
      if (val === null || val === undefined) {
        return <span className="text-slate-400">—</span>;
      }
      if (typeof val === 'boolean') {
        return val ? 'Yes' : 'No';
      }
      if (typeof val === 'object') {
        return JSON.stringify(val);
      }
      return String(val);
    }
    return null;
  };

  const resolveRowKey = (row: T, index: number): React.Key => {
    if (getRowKey) {
      return getRowKey(row, index);
    }
    if (typeof row === 'object' && row !== null && 'id' in row) {
      const idVal = (row as Record<string, unknown>).id;
      if (typeof idVal === 'string' || typeof idVal === 'number') {
        return idVal;
      }
    }
    return index;
  };

  return (
    <div
      className={cn(
        'bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs',
        className
      )}
    >
      <div className="overflow-x-auto w-full">
        <table className={cn('w-full text-left text-xs', tableClassName)}>
          {caption && <caption className="sr-only">{caption}</caption>}
          <thead
            className={cn(
              'bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-semibold tracking-wider',
              theadClassName
            )}
          >
            <tr>
              {columns.map((col, cIdx) => {
                const align = col.align || 'left';
                const colKey = col.id || (col.accessorKey !== undefined ? String(col.accessorKey) : `col-${cIdx}`);
                return (
                  <th
                    key={colKey}
                    scope="col"
                    className={cn(
                      'p-4 whitespace-nowrap',
                      ALIGN_MAP[align],
                      col.headerClassName
                    )}
                  >
                    {col.header}
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody className={cn('divide-y divide-slate-200', tbodyClassName)}>
            {isLoading ? (
              <>
                {Array.from({ length: skeletonRowCount }).map((_, rIdx) => (
                  <tr key={`skeleton-row-${rIdx}`} className="animate-pulse">
                    {columns.map((col, cIdx) => {
                      const align = col.align || 'left';
                      const colKey = col.id || (col.accessorKey !== undefined ? String(col.accessorKey) : `skel-${cIdx}`);
                      return (
                        <td
                          key={colKey}
                          className={cn('p-4 whitespace-nowrap', ALIGN_MAP[align], col.className)}
                        >
                          <div
                            className={cn(
                              'h-3.5 bg-slate-200 rounded',
                              SKELETON_ALIGN_MAP[align]
                            )}
                          />
                        </td>
                      );
                    })}
                  </tr>
                ))}
                {loadingMessage && (
                  <tr>
                    <td
                      colSpan={columns.length}
                      className="p-3 text-center text-xs text-slate-500 bg-slate-50/50"
                    >
                      {loadingMessage}
                    </td>
                  </tr>
                )}
              </>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="p-8 text-center">
                  {emptyState ? (
                    emptyState
                  ) : (
                    <div className="flex flex-col items-center justify-center text-slate-500 py-6">
                      <Inbox className="w-8 h-8 text-slate-300 mb-2 stroke-[1.5]" />
                      <p className="text-sm font-medium text-slate-700">{emptyMessage}</p>
                      <p className="text-xs text-slate-400 mt-0.5">There are no records to display.</p>
                    </div>
                  )}
                </td>
              </tr>
            ) : (
              data.map((row, rIdx) => {
                const key = resolveRowKey(row, rIdx);
                const isClickable = Boolean(onRowClick);
                const customRowClass =
                  typeof rowClassName === 'function' ? rowClassName(row, rIdx) : rowClassName;

                return (
                  <tr
                    key={key}
                    onClick={isClickable ? () => onRowClick?.(row, rIdx) : undefined}
                    className={cn(
                      'transition-colors',
                      isClickable
                        ? 'cursor-pointer hover:bg-slate-50/80 active:bg-slate-100'
                        : 'hover:bg-slate-50/50',
                      customRowClass
                    )}
                  >
                    {columns.map((col, cIdx) => {
                      const align = col.align || 'left';
                      const colKey = col.id || (col.accessorKey !== undefined ? String(col.accessorKey) : `cell-${cIdx}`);
                      return (
                        <td
                          key={colKey}
                          className={cn(
                            'p-4 text-slate-700',
                            ALIGN_MAP[align],
                            col.className
                          )}
                        >
                          {getCellContent(col, row, rIdx)}
                        </td>
                      );
                    })}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
