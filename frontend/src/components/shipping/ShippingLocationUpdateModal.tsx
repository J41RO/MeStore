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
import LocationOnIcon from '@mui/icons-material/LocationOn';
import shippingService, { ShippingStatus, ShippingLocationUpdate } from '../../services/shippingService';

interface ShippingLocationUpdateModalProps {
  open: boolean;
  onClose: () => void;
  orderId: number;
  orderNumber: string;
  trackingNumber: string;
  onSuccess?: () => void;
}

const ShippingLocationUpdateModal: React.FC<ShippingLocationUpdateModalProps> = ({
  open,
  onClose,
  orderId,
  orderNumber,
  trackingNumber,
  onSuccess
}) => {
  const [currentLocation, setCurrentLocation] = useState('');
  const [status, setStatus] = useState<ShippingStatus>(ShippingStatus.IN_TRANSIT);
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Validation errors
  const [locationError, setLocationError] = useState<string | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [touched, setTouched] = useState({ location: false, status: false });

  // Validation functions
  const validateLocation = (value: string): boolean => {
    if (!value || value.trim().length === 0) {
      setLocationError('Ubicación es requerida');
      return false;
    }
    if (value.trim().length < 3) {
      setLocationError('Ubicación debe tener al menos 3 caracteres');
      return false;
    }
    setLocationError(null);
    return true;
  };

  const validateStatus = (value: ShippingStatus): boolean => {
    if (!value) {
      setStatusError('Debe seleccionar un estado');
      return false;
    }
    setStatusError(null);
    return true;
  };

  // Check if form is valid
  const isFormValid = (): boolean => {
    return currentLocation.trim().length >= 3 && !!status;
  };

  const statusOptions = [
    { value: ShippingStatus.IN_TRANSIT, label: 'En tránsito' },
    { value: ShippingStatus.AT_WAREHOUSE, label: 'En bodega' },
    { value: ShippingStatus.OUT_FOR_DELIVERY, label: 'En reparto' },
    { value: ShippingStatus.DELIVERED, label: 'Entregado' },
    { value: ShippingStatus.RETURNED, label: 'Devuelto' },
    { value: ShippingStatus.FAILED, label: 'Fallido' }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    setTouched({ location: true, status: true });

    // Validate all fields
    const isLocationValid = validateLocation(currentLocation);
    const isStatusValid = validateStatus(status);

    // Don't submit if validation fails
    if (!isLocationValid || !isStatusValid) {
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const data: ShippingLocationUpdate = {
        current_location: currentLocation,
        status,
        description: description || undefined
      };

      await shippingService.updateShippingLocation(orderId, data);

      setSuccess(true);
      setTimeout(() => {
        onSuccess?.();
        handleClose();
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al actualizar ubicación');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setCurrentLocation('');
      setStatus(ShippingStatus.IN_TRANSIT);
      setDescription('');
      setError(null);
      setSuccess(false);
      setLocationError(null);
      setStatusError(null);
      setTouched({ location: false, status: false });
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <LocationOnIcon />
          <Typography variant="h6">Actualizar Ubicación</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" mt={1}>
          Orden: {orderNumber} | Tracking: {trackingNumber}
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
              Ubicación actualizada exitosamente
            </Alert>
          )}

          <TextField
            fullWidth
            label="Ubicación actual *"
            value={currentLocation}
            onChange={(e) => {
              setCurrentLocation(e.target.value);
              if (touched.location) validateLocation(e.target.value);
            }}
            onBlur={() => {
              setTouched({ ...touched, location: true });
              validateLocation(currentLocation);
            }}
            required
            disabled={loading || success}
            error={touched.location && !!locationError}
            sx={{ mb: 2 }}
            helperText={
              touched.location && locationError
                ? locationError
                : 'Ejemplo: Bogotá - Centro de distribución'
            }
            placeholder="Ciudad - Punto de referencia"
          />

          <TextField
            select
            fullWidth
            label="Estado del envío *"
            value={status}
            onChange={(e) => {
              setStatus(e.target.value as ShippingStatus);
              if (touched.status) validateStatus(e.target.value as ShippingStatus);
            }}
            onBlur={() => {
              setTouched({ ...touched, status: true });
              validateStatus(status);
            }}
            required
            disabled={loading || success}
            error={touched.status && !!statusError}
            sx={{ mb: 2 }}
            helperText={
              touched.status && statusError
                ? statusError
                : 'Seleccione el estado actual del envío'
            }
          >
            {statusOptions.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            fullWidth
            multiline
            rows={3}
            label="Descripción (opcional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={loading || success}
            helperText="Información adicional sobre el estado del envío"
            placeholder="Ejemplo: Paquete en tránsito hacia destino final"
          />

          {status === ShippingStatus.DELIVERED && (
            <Box mt={2} p={2} bgcolor="success.main" borderRadius={1}>
              <Typography variant="body2" color="white">
                ✓ Al marcar como "Entregado", la orden se actualizará automáticamente al estado "Entregado"
              </Typography>
            </Box>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancelar
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading || success || !isFormValid()}
            startIcon={loading ? <CircularProgress size={20} /> : <LocationOnIcon />}
          >
            {loading ? 'Actualizando...' : 'Actualizar Ubicación'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default ShippingLocationUpdateModal;
