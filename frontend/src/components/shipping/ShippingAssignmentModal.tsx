import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Box,
  Typography,
  Alert,
  CircularProgress
} from '@mui/material';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import shippingService, { ShippingAssignment } from '../../services/shippingService';

interface ShippingAssignmentModalProps {
  open: boolean;
  onClose: () => void;
  orderId: number;
  orderNumber: string;
  onSuccess?: () => void;
}

const ShippingAssignmentModal: React.FC<ShippingAssignmentModalProps> = ({
  open,
  onClose,
  orderId,
  orderNumber,
  onSuccess
}) => {
  const [courier, setCourier] = useState('');
  const [estimatedDays, setEstimatedDays] = useState<number>(3);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const couriers = shippingService.getAvailableCouriers();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data: ShippingAssignment = {
        courier,
        estimated_days: estimatedDays
      };

      const response = await shippingService.assignShipping(orderId, data);

      setSuccess(true);
      setTimeout(() => {
        onSuccess?.();
        handleClose();
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al asignar envío');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setCourier('');
      setEstimatedDays(3);
      setError(null);
      setSuccess(false);
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <LocalShippingIcon />
          <Typography variant="h6">Asignar Envío</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" mt={1}>
          Orden: {orderNumber}
        </Typography>
      </DialogTitle>

      <form onSubmit={handleSubmit}>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Envío asignado exitosamente
            </Alert>
          )}

          <TextField
            select
            fullWidth
            label="Courier"
            value={courier}
            onChange={(e) => setCourier(e.target.value)}
            required
            disabled={loading || success}
            sx={{ mb: 2 }}
            helperText="Seleccione la empresa de envío"
          >
            {couriers.map((courierOption) => (
              <MenuItem key={courierOption} value={courierOption}>
                {courierOption}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            fullWidth
            type="number"
            label="Días estimados de entrega"
            value={estimatedDays}
            onChange={(e) => setEstimatedDays(parseInt(e.target.value))}
            required
            disabled={loading || success}
            inputProps={{ min: 1, max: 30 }}
            helperText="Número de días hábiles estimados para la entrega"
          />

          <Box mt={2} p={2} bgcolor="info.main" borderRadius={1}>
            <Typography variant="body2" color="white">
              ℹ️ Se generará automáticamente un número de tracking y se actualizará el estado de la orden a "Enviado"
            </Typography>
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancelar
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading || success || !courier}
            startIcon={loading ? <CircularProgress size={20} /> : <LocalShippingIcon />}
          >
            {loading ? 'Asignando...' : 'Asignar Envío'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default ShippingAssignmentModal;
