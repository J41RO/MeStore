/**
 * Common types for admin components
 */

import { LucideIcon } from 'lucide-react';

export interface TableColumn<T = any> {
  id: string;
  header: string;
  accessor: keyof T;
  sortable?: boolean;
  align?: 'left' | 'center' | 'right';
  hideOnMobile?: boolean;
  cell?: (value: any, row: T) => React.ReactNode;
}

export interface TableAction<T = any> {
  id: string;
  label: string;
  icon: LucideIcon;
  variant?: 'default' | 'primary' | 'danger' | 'success' | 'warning';
  action: (row: T) => void;
  hidden?: (row: T) => boolean;
}

export interface DashboardCardProps {
  title: string;
  value?: number | string;
  icon: LucideIcon;
  theme?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
  isLoading?: boolean;
  subtitle?: string;
}

export interface StatusBadgeProps {
  variant: 'success' | 'warning' | 'danger' | 'info' | 'inactive' | 'pending';
  size?: 'xs' | 'sm' | 'md';
  children: React.ReactNode;
}

export interface DataTableProps<T = any> {
  data: T[];
  columns: TableColumn<T>[];
  isLoading?: boolean;
  error?: string | null;
  rowActions?: TableAction<T>[];
  searchable?: boolean;
  searchPlaceholder?: string;
  onRefresh?: () => void;
  emptyMessage?: string;
  selectable?: boolean;
  onSelectionChange?: (selected: T[]) => void;
}