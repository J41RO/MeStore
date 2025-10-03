/**
 * Admin Order Detail Modal
 *
 * Comprehensive order detail view for SUPERUSER with:
 * - Complete order information (buyer, shipping, items, payments)
 * - Order status timeline
 * - Status update functionality
 * - Order cancellation with reason
 * - Transaction history
 *
 * Security: Used within protected admin pages
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Grid,
  Divider,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  CircularProgress,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Stack,
  Card,
  CardContent,
  IconButton,
  Collapse,
  SelectChangeEvent,
} from '@mui/material';
import {
  Close as CloseIcon,
  Edit as EditIcon,
  Cancel as CancelIcon,
  Save as SaveIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  LocalShipping as LocalShippingIcon,
  LocationOn as LocationOnIcon,
} from '@mui/icons-material';

import adminOrderService, {
  OrderDetailAdmin,
  OrderStatusUpdate,
  OrderCancellation,
} from '../../services/adminOrderService';
import ShippingAssignmentModal from '../shipping/ShippingAssignmentModal';
import ShippingLocationUpdateModal from '../shipping/ShippingLocationUpdateModal';
import ShippingTrackingTimeline from '../shipping/ShippingTrackingTimeline';

interface AdminOrderDetailProps {
  orderId: number;
  open: boolean;
  onClose: () => void;
  onOrderUpdated?: () => void;
}

const AdminOrderDetail: React.FC<AdminOrderDetailProps> = ({
  orderId,
  open,
  onClose,
  onOrderUpdated,
}) => {
  // State
  const [order, setOrder] = useState<OrderDetailAdmin | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Edit mode
  const [editMode, setEditMode] = useState(false);
  const [newStatus, setNewStatus] = useState<string>('');
  const [statusNotes, setStatusNotes] = useState<string>('');

  // Cancel mode
  const [cancelMode, setCancelMode] = useState(false);
  const [cancelReason, setCancelReason] = useState<string>('');
  const [refundRequested, setRefundRequested] = useState(false);

  // Shipping modals
  const [shippingAssignModalOpen, setShippingAssignModalOpen] = useState(false);
  const [shippingLocationModalOpen, setShippingLocationModalOpen] = useState(false);

  // Expanded sections
  const [expandedSections, setExpandedSections] = useState({
    items: true,
    transactions: true,
    shipping: true,
  });

  // Load order detail
  useEffect(() => {
    if (open && orderId) {
      loadOrderDetail();
    }
  }, [orderId, open]);

  const loadOrderDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await adminOrderService.getOrderDetail(orderId);
      setOrder(data);
      setNewStatus(data.status);
    } catch (err: any) {
      console.error('Error loading order detail:', err);
      setError(err.response?.data?.detail || 'Error al cargar detalles de la orden');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async () => {
    if (!order) return;

    try {
      setError(null);
      setSuccess(null);

      const statusUpdate: OrderStatusUpdate = {
        status: newStatus,
        notes: statusNotes || undefined,
      };

      await adminOrderService.updateOrderStatus(order.id, statusUpdate);
      setSuccess('Estado actualizado correctamente');
      setEditMode(false);
      setStatusNotes('');
      await loadOrderDetail();
      if (onOrderUpdated) onOrderUpdated();
    } catch (err: any) {
      console.error('Error updating status:', err);
      setError(err.response?.data?.detail || 'Error al actualizar estado');
    }
  };

  const handleCancelOrder = async () => {
    if (!order || !cancelReason.trim()) {
      setError('Debe proporcionar una razón para cancelar la orden');
      return;
    }

    try {
      setError(null);
      setSuccess(null);

      const cancellation: OrderCancellation = {
        reason: cancelReason,
        refund_requested: refundRequested,
      };

      await adminOrderService.cancelOrder(order.id, cancellation);
      setSuccess('Orden cancelada correctamente');
      setCancelMode(false);
      setCancelReason('');
      setRefundRequested(false);
      await loadOrderDetail();
      if (onOrderUpdated) onOrderUpdated();
    } catch (err: any) {
      console.error('Error cancelling order:', err);
      setError(err.response?.data?.detail || 'Error al cancelar orden');
    }
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('es-CO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!order && !loading) {
    return null;
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h5">
            Detalle de Orden {order?.order_number}
          </Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {loading ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : order ? (
          <Stack spacing={3}>
            {/* Alerts */}
            {error && (
              <Alert severity="error" onClose={() => setError(null)}>
                {error}
              </Alert>
            )}
            {success && (
              <Alert severity="success" onClose={() => setSuccess(null)}>
                {success}
              </Alert>
            )}

            {/* Order status and actions */}
            <Card>
              <CardContent>
                <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Estado de la Orden
                    </Typography>
                    <Stack direction="row" spacing={1}>
                      <Chip
                        label={order.status.toUpperCase()}
                        color={adminOrderService.getStatusColor(order.status) as any}
                      />
                      {order.transactions.length > 0 && (
                        <Chip
                          label={`PAGO: ${order.transactions[0].status.toUpperCase()}`}
                          color={adminOrderService.getPaymentStatusColor(order.transactions[0].status) as any}
                        />
                      )}
                    </Stack>
                  </Box>
                  <Stack direction="row" spacing={1} flexWrap="wrap">
                    {!editMode && !cancelMode && order.status !== 'cancelled' && (
                      <>
                        <Button
                          startIcon={<EditIcon />}
                          variant="outlined"
                          onClick={() => setEditMode(true)}
                        >
                          Cambiar Estado
                        </Button>
                        <Button
                          startIcon={<CancelIcon />}
                          variant="outlined"
                          color="error"
                          onClick={() => setCancelMode(true)}
                        >
                          Cancelar Orden
                        </Button>
                        <Button
                          variant="contained"
                          color="info"
                          onClick={() => setShippingAssignModalOpen(true)}
                          disabled={order.status !== 'confirmed' && order.status !== 'processing'}
                          startIcon={<LocalShippingIcon />}
                        >
                          Asignar Envío
                        </Button>
                        {order.tracking_number && (
                          <Button
                            variant="outlined"
                            color="info"
                            onClick={() => setShippingLocationModalOpen(true)}
                            startIcon={<LocationOnIcon />}
                          >
                            Actualizar Ubicación
                          </Button>
                        )}
                      </>
                    )}
                  </Stack>
                </Stack>

                {/* Status update form */}
                <Collapse in={editMode}>
                  <Box mt={2}>
                    <Divider sx={{ mb: 2 }} />
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <FormControl fullWidth>
                          <InputLabel>Nuevo Estado</InputLabel>
                          <Select
                            value={newStatus}
                            label="Nuevo Estado"
                            onChange={(e: SelectChangeEvent<string>) => setNewStatus(e.target.value)}
                          >
                            {adminOrderService.getOrderStatusOptions().map((option) => (
                              option.value && (
                                <MenuItem key={option.value} value={option.value}>
                                  {option.label}
                                </MenuItem>
                              )
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          multiline
                          rows={2}
                          label="Notas (opcional)"
                          value={statusNotes}
                          onChange={(e) => setStatusNotes(e.target.value)}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Stack direction="row" spacing={1}>
                          <Button
                            variant="contained"
                            startIcon={<SaveIcon />}
                            onClick={handleStatusUpdate}
                          >
                            Guardar
                          </Button>
                          <Button
                            variant="outlined"
                            onClick={() => {
                              setEditMode(false);
                              setNewStatus(order.status);
                              setStatusNotes('');
                            }}
                          >
                            Cancelar
                          </Button>
                        </Stack>
                      </Grid>
                    </Grid>
                  </Box>
                </Collapse>

                {/* Cancellation form */}
                <Collapse in={cancelMode}>
                  <Box mt={2}>
                    <Divider sx={{ mb: 2 }} />
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          required
                          multiline
                          rows={3}
                          label="Razón de Cancelación"
                          value={cancelReason}
                          onChange={(e) => setCancelReason(e.target.value)}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Stack direction="row" spacing={1}>
                          <Button
                            variant="contained"
                            color="error"
                            startIcon={<CancelIcon />}
                            onClick={handleCancelOrder}
                          >
                            Confirmar Cancelación
                          </Button>
                          <Button
                            variant="outlined"
                            onClick={() => {
                              setCancelMode(false);
                              setCancelReason('');
                              setRefundRequested(false);
                            }}
                          >
                            Cancelar
                          </Button>
                        </Stack>
                      </Grid>
                    </Grid>
                  </Box>
                </Collapse>
              </CardContent>
            </Card>

            {/* Buyer information */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Información del Comprador
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary">
                      Nombre
                    </Typography>
                    <Typography variant="body1">{order.buyer_name}</Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary">
                      Email
                    </Typography>
                    <Typography variant="body1">{order.buyer_email}</Typography>
                  </Grid>
                  {order.buyer_phone && (
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="text.secondary">
                        Teléfono
                      </Typography>
                      <Typography variant="body1">{order.buyer_phone}</Typography>
                    </Grid>
                  )}
                </Grid>
              </CardContent>
            </Card>

            {/* Shipping information */}
            <Card>
              <CardContent>
                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                  onClick={() => toggleSection('shipping')}
                  sx={{ cursor: 'pointer' }}
                >
                  <Typography variant="h6">Información de Envío</Typography>
                  <IconButton size="small">
                    {expandedSections.shipping ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </IconButton>
                </Box>
                <Collapse in={expandedSections.shipping}>
                  <Box mt={2}>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="body2" color="text.secondary">
                          Destinatario
                        </Typography>
                        <Typography variant="body1">{order.shipping_name}</Typography>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Typography variant="body2" color="text.secondary">
                          Teléfono
                        </Typography>
                        <Typography variant="body1">{order.shipping_phone}</Typography>
                      </Grid>
                      <Grid item xs={12}>
                        <Typography variant="body2" color="text.secondary">
                          Dirección
                        </Typography>
                        <Typography variant="body1">{order.shipping_address}</Typography>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Typography variant="body2" color="text.secondary">
                          Ciudad
                        </Typography>
                        <Typography variant="body1">{order.shipping_city}</Typography>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Typography variant="body2" color="text.secondary">
                          Departamento
                        </Typography>
                        <Typography variant="body1">{order.shipping_state}</Typography>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Typography variant="body2" color="text.secondary">
                          País
                        </Typography>
                        <Typography variant="body1">{order.shipping_country}</Typography>
                      </Grid>
                    </Grid>
                  </Box>
                </Collapse>
              </CardContent>
            </Card>

            {/* Order items */}
            <Card>
              <CardContent>
                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                  onClick={() => toggleSection('items')}
                  sx={{ cursor: 'pointer' }}
                >
                  <Typography variant="h6">
                    Items de la Orden ({order.items.length})
                  </Typography>
                  <IconButton size="small">
                    {expandedSections.items ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </IconButton>
                </Box>
                <Collapse in={expandedSections.items}>
                  <TableContainer sx={{ mt: 2 }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Producto</TableCell>
                          <TableCell>SKU</TableCell>
                          <TableCell>Vendedor</TableCell>
                          <TableCell align="right">Precio Unit.</TableCell>
                          <TableCell align="center">Cantidad</TableCell>
                          <TableCell align="right">Total</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {order.items.map((item) => (
                          <TableRow key={item.id}>
                            <TableCell>{item.product_name}</TableCell>
                            <TableCell>{item.product_sku}</TableCell>
                            <TableCell>{item.vendor_name || 'N/A'}</TableCell>
                            <TableCell align="right">
                              {formatCurrency(item.unit_price)}
                            </TableCell>
                            <TableCell align="center">{item.quantity}</TableCell>
                            <TableCell align="right">
                              {formatCurrency(item.total_price)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Collapse>
              </CardContent>
            </Card>

            {/* Order totals */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Resumen de Costos
                </Typography>
                <Grid container spacing={1}>
                  <Grid item xs={8}>
                    <Typography variant="body1">Subtotal:</Typography>
                  </Grid>
                  <Grid item xs={4} textAlign="right">
                    <Typography variant="body1">
                      {formatCurrency(order.subtotal)}
                    </Typography>
                  </Grid>
                  <Grid item xs={8}>
                    <Typography variant="body1">Envío:</Typography>
                  </Grid>
                  <Grid item xs={4} textAlign="right">
                    <Typography variant="body1">
                      {formatCurrency(order.shipping_cost)}
                    </Typography>
                  </Grid>
                  {order.tax_amount > 0 && (
                    <>
                      <Grid item xs={8}>
                        <Typography variant="body1">Impuestos:</Typography>
                      </Grid>
                      <Grid item xs={4} textAlign="right">
                        <Typography variant="body1">
                          {formatCurrency(order.tax_amount)}
                        </Typography>
                      </Grid>
                    </>
                  )}
                  {order.discount_amount > 0 && (
                    <>
                      <Grid item xs={8}>
                        <Typography variant="body1" color="success.main">
                          Descuento:
                        </Typography>
                      </Grid>
                      <Grid item xs={4} textAlign="right">
                        <Typography variant="body1" color="success.main">
                          -{formatCurrency(order.discount_amount)}
                        </Typography>
                      </Grid>
                    </>
                  )}
                  <Grid item xs={12}>
                    <Divider sx={{ my: 1 }} />
                  </Grid>
                  <Grid item xs={8}>
                    <Typography variant="h6">Total:</Typography>
                  </Grid>
                  <Grid item xs={4} textAlign="right">
                    <Typography variant="h6">
                      {formatCurrency(order.total_amount)}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Transactions */}
            {order.transactions.length > 0 && (
              <Card>
                <CardContent>
                  <Box
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                    onClick={() => toggleSection('transactions')}
                    sx={{ cursor: 'pointer' }}
                  >
                    <Typography variant="h6">
                      Transacciones ({order.transactions.length})
                    </Typography>
                    <IconButton size="small">
                      {expandedSections.transactions ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </IconButton>
                  </Box>
                  <Collapse in={expandedSections.transactions}>
                    <TableContainer sx={{ mt: 2 }}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Referencia</TableCell>
                            <TableCell>Gateway</TableCell>
                            <TableCell>Método</TableCell>
                            <TableCell align="right">Monto</TableCell>
                            <TableCell>Estado</TableCell>
                            <TableCell>Fecha</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {order.transactions.map((transaction) => (
                            <TableRow key={transaction.id}>
                              <TableCell>{transaction.transaction_reference}</TableCell>
                              <TableCell>{transaction.gateway.toUpperCase()}</TableCell>
                              <TableCell>{transaction.payment_method_type}</TableCell>
                              <TableCell align="right">
                                {formatCurrency(transaction.amount)}
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={transaction.status.toUpperCase()}
                                  color={adminOrderService.getPaymentStatusColor(transaction.status) as any}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell>{formatDate(transaction.created_at)}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Collapse>
                </CardContent>
              </Card>
            )}

            {/* Shipping Tracking Timeline */}
            {order.tracking_number && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Seguimiento de Envío
                  </Typography>
                  <ShippingTrackingTimeline
                    events={order.shipping_events || []}
                    trackingNumber={order.tracking_number}
                    courier={order.courier || null}
                    estimatedDelivery={order.estimated_delivery || null}
                  />
                </CardContent>
              </Card>
            )}

            {/* Timeline */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Cronología
                </Typography>
                <Stack spacing={1}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Creada
                    </Typography>
                    <Typography variant="body1">{formatDate(order.created_at)}</Typography>
                  </Box>
                  {order.confirmed_at && (
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Confirmada
                      </Typography>
                      <Typography variant="body1">{formatDate(order.confirmed_at)}</Typography>
                    </Box>
                  )}
                  {order.shipped_at && (
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Enviada
                      </Typography>
                      <Typography variant="body1">{formatDate(order.shipped_at)}</Typography>
                    </Box>
                  )}
                  {order.delivered_at && (
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Entregada
                      </Typography>
                      <Typography variant="body1">{formatDate(order.delivered_at)}</Typography>
                    </Box>
                  )}
                  {order.cancelled_at && (
                    <Box>
                      <Typography variant="body2" color="error">
                        Cancelada
                      </Typography>
                      <Typography variant="body1">{formatDate(order.cancelled_at)}</Typography>
                      {order.cancellation_reason && (
                        <Typography variant="body2" color="text.secondary">
                          Razón: {order.cancellation_reason}
                        </Typography>
                      )}
                    </Box>
                  )}
                </Stack>
              </CardContent>
            </Card>
          </Stack>
        ) : null}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Cerrar</Button>
      </DialogActions>

      {/* Shipping Modals */}
      {order && (
        <>
          <ShippingAssignmentModal
            open={shippingAssignModalOpen}
            onClose={() => setShippingAssignModalOpen(false)}
            orderId={order.id}
            orderNumber={order.order_number}
            onSuccess={loadOrderDetail}
          />

          {order.tracking_number && (
            <ShippingLocationUpdateModal
              open={shippingLocationModalOpen}
              onClose={() => setShippingLocationModalOpen(false)}
              orderId={order.id}
              orderNumber={order.order_number}
              trackingNumber={order.tracking_number}
              onSuccess={loadOrderDetail}
            />
          )}
        </>
      )}
    </Dialog>
  );
};

export default AdminOrderDetail;
