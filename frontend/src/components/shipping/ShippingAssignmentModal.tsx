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

  // Validation errors
  const [courierError, setCourierError] = useState<string | null>(null);
  const [daysError, setDaysError] = useState<string | null>(null);
  const [touched, setTouched] = useState({ courier: false, days: false });

  const couriers = shippingService.getAvailableCouriers();

  // Validation functions
  const validateCourier = (value: string): boolean => {
    if (!value) {
      setCourierError('Debe seleccionar un courier');
      return false;
    }
    setCourierError(null);
    return true;
  };

  const validateDays = (value: number): boolean => {
    if (!value || value < 1 || value > 30) {
      setDaysError('Días debe estar entre 1 y 30');
      return false;
    }
    setDaysError(null);
    return true;
  };

  // Check if form is valid
  const isFormValid = (): boolean => {
    return !!courier && estimatedDays >= 1 && estimatedDays <= 30;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    setTouched({ courier: true, days: true });

    // Validate all fields
    const isCourierValid = validateCourier(courier);
    const areDaysValid = validateDays(estimatedDays);

    // Don't submit if validation fails
    if (!isCourierValid || !areDaysValid) {
      return;
    }

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
      setCourierError(null);
      setDaysError(null);
      setTouched({ courier: false, days: false });
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
            label="Courier *"
            value={courier}
            onChange={(e) => {
              setCourier(e.target.value);
              if (touched.courier) validateCourier(e.target.value);
            }}
            onBlur={() => {
              setTouched({ ...touched, courier: true });
              validateCourier(courier);
            }}
            required
            disabled={loading || success}
            error={touched.courier && !!courierError}
            sx={{ mb: 2 }}
            helperText={
              touched.courier && courierError
                ? courierError
                : 'Seleccione la empresa de envío'
            }
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
            label="Días estimados de entrega *"
            value={estimatedDays}
            onChange={(e) => {
              const value = parseInt(e.target.value);
              setEstimatedDays(value);
              if (touched.days) validateDays(value);
            }}
            onBlur={() => {
              setTouched({ ...touched, days: true });
              validateDays(estimatedDays);
            }}
            required
            disabled={loading || success}
            error={touched.days && !!daysError}
            inputProps={{ min: 1, max: 30 }}
            helperText={
              touched.days && daysError
                ? daysError
                : 'Número de días hábiles estimados (1-30)'
            }
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
            disabled={loading || success || !isFormValid()}
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
