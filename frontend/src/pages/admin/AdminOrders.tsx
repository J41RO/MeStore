/**
 * Admin Orders Page
 *
 * Comprehensive order management interface for SUPERUSER.
 * Features:
 * - View all orders in the system
 * - Filter by status and search
 * - Pagination support
 * - Quick status updates
 * - Detailed order view
 * - Order cancellation with reason
 *
 * Security: Protected by ProtectedRoute with SUPERUSER requirement
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Stack,
  Tooltip,
  SelectChangeEvent,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  Cancel as CancelIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

import adminOrderService, {
  OrderListItem,
  OrdersListResponse,
} from '../../services/adminOrderService';
import AdminOrderDetail from '../../components/admin/AdminOrderDetail';
import SkeletonLoader, { SkeletonTable } from '../../components/common/SkeletonLoader';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const AdminOrders: React.FC = () => {
  // State management
  const [orders, setOrders] = useState<OrderListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  // Filters and pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchInput, setSearchInput] = useState<string>('');

  // Detail modal
  const [selectedOrderId, setSelectedOrderId] = useState<number | null>(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);

  // Load orders
  useEffect(() => {
    loadOrders();
  }, [page, rowsPerPage, statusFilter, searchQuery]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      setError(null);

      const response: OrdersListResponse = await adminOrderService.getAllOrders(
        page * rowsPerPage,
        rowsPerPage,
        statusFilter,
        searchQuery
      );

      setOrders(response.orders);
      setTotal(response.total);
    } catch (err: any) {
      console.error('Error loading orders:', err);
      setError(err.response?.data?.detail || 'Error al cargar órdenes');
    } finally {
      setLoading(false);
    }
  };

  // Event handlers
  const handlePageChange = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleStatusFilterChange = (event: SelectChangeEvent<string>) => {
    setStatusFilter(event.target.value);
    setPage(0);
  };

  const handleSearchInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchInput(event.target.value);
  };

  const handleSearchSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    setSearchQuery(searchInput);
    setPage(0);
  };

  const handleViewDetail = (orderId: number) => {
    setSelectedOrderId(orderId);
    setDetailModalOpen(true);
  };

  const handleCloseDetail = () => {
    setDetailModalOpen(false);
    setSelectedOrderId(null);
  };

  const handleOrderUpdated = () => {
    // Reload orders after update
    loadOrders();
  };

  const handleRefresh = () => {
    loadOrders();
  };

  // Initial loading state with skeleton
  const isInitialLoading = loading && orders.length === 0;

  // Get status chip color
  const getStatusColor = (status: string): "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning" => {
    const colorMap: Record<string, "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning"> = {
      pending: 'warning',
      confirmed: 'info',
      processing: 'primary',
      shipped: 'secondary',
      delivered: 'success',
      cancelled: 'error',
      refunded: 'default',
    };
    return colorMap[status.toLowerCase()] || 'default';
  };

  const getPaymentStatusColor = (status: string): "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning" => {
    const colorMap: Record<string, "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning"> = {
      pending: 'warning',
      processing: 'info',
      approved: 'success',
      declined: 'error',
      error: 'error',
      cancelled: 'default',
    };
    return colorMap[status.toLowerCase()] || 'default';
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4" component="h1">
            Gestión de Órdenes
          </Typography>
          <Tooltip title="Actualizar">
            <IconButton onClick={handleRefresh} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Filters */}
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ mb: 3 }}>
          {/* Search */}
          <Box component="form" onSubmit={handleSearchSubmit} sx={{ flex: 1 }}>
            <TextField
              fullWidth
              label="Buscar"
              placeholder="Número de orden, email, nombre..."
              value={searchInput}
              onChange={handleSearchInputChange}
              size="small"
            />
          </Box>

          {/* Status filter */}
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Estado</InputLabel>
            <Select
              value={statusFilter}
              label="Estado"
              onChange={handleStatusFilterChange}
            >
              {adminOrderService.getOrderStatusOptions().map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Search button */}
          <Button
            variant="contained"
            onClick={handleSearchSubmit}
            disabled={loading}
            sx={{ minWidth: 100 }}
          >
            {loading && !isInitialLoading ? (
              <CircularProgress size={20} color="inherit" sx={{ mr: 1 }} />
            ) : null}
            Buscar
          </Button>
        </Stack>

        {/* Error alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Loading indicator with skeleton */}
        {isInitialLoading ? (
          <Box sx={{ py: 2 }}>
            <SkeletonTable rows={rowsPerPage} columns={8} />
          </Box>
        ) : (
          <>
            {/* Orders table */}
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Número de Orden</TableCell>
                    <TableCell>Cliente</TableCell>
                    <TableCell>Fecha</TableCell>
                    <TableCell align="right">Total</TableCell>
                    <TableCell align="center">Estado</TableCell>
                    <TableCell align="center">Pago</TableCell>
                    <TableCell align="center">Items</TableCell>
                    <TableCell align="center">Acciones</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {orders.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} align="center">
                        <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                          No se encontraron órdenes
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    orders.map((order) => (
                      <TableRow key={order.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {order.order_number}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{order.buyer_name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {order.buyer_email}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {formatDate(order.created_at)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight="medium">
                            {formatCurrency(order.total_amount)}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={order.status.toUpperCase()}
                            color={getStatusColor(order.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={order.payment_status.toUpperCase()}
                            color={getPaymentStatusColor(order.payment_status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Chip label={order.items_count} size="small" variant="outlined" />
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip title="Ver detalle">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleViewDetail(order.id)}
                            >
                              <VisibilityIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Pagination */}
            <TablePagination
              component="div"
              count={total}
              page={page}
              onPageChange={handlePageChange}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={handleRowsPerPageChange}
              rowsPerPageOptions={[10, 20, 50, 100]}
              labelRowsPerPage="Filas por página:"
              labelDisplayedRows={({ from, to, count }) =>
                `${from}-${to} de ${count !== -1 ? count : `más de ${to}`}`
              }
            />
          </>
        )}
      </Paper>

      {/* Order detail modal */}
      {selectedOrderId && (
        <AdminOrderDetail
          orderId={selectedOrderId}
          open={detailModalOpen}
          onClose={handleCloseDetail}
          onOrderUpdated={handleOrderUpdated}
        />
      )}
    </Container>
  );
};

export default AdminOrders;
