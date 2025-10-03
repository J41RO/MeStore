import React from 'react';
import {
  Box,
  Typography,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
  Paper,
  Chip
} from '@mui/material';
import {
  LocalShipping,
  Warehouse,
  LocationOn,
  CheckCircle,
  Error,
  Assignment
} from '@mui/icons-material';
import { ShippingEvent, ShippingStatus } from '../../services/shippingService';
import shippingService from '../../services/shippingService';

interface ShippingTrackingTimelineProps {
  events: ShippingEvent[];
  trackingNumber: string | null;
  courier: string | null;
  estimatedDelivery: string | null;
}

const ShippingTrackingTimeline: React.FC<ShippingTrackingTimelineProps> = ({
  events,
  trackingNumber,
  courier,
  estimatedDelivery
}) => {
  const getStatusIcon = (status: ShippingStatus | string) => {
    switch (status) {
      case ShippingStatus.IN_TRANSIT:
        return <LocalShipping />;
      case ShippingStatus.AT_WAREHOUSE:
        return <Warehouse />;
      case ShippingStatus.OUT_FOR_DELIVERY:
        return <LocationOn />;
      case ShippingStatus.DELIVERED:
        return <CheckCircle />;
      case ShippingStatus.RETURNED:
      case ShippingStatus.FAILED:
        return <Error />;
      default:
        return <Assignment />;
    }
  };

  const getStatusColor = (status: ShippingStatus | string): any => {
    const color = shippingService.getStatusColor(status);
    const colorMap: Record<string, any> = {
      blue: 'info',
      orange: 'warning',
      purple: 'secondary',
      green: 'success',
      red: 'error',
      gray: 'default'
    };
    return colorMap[color] || 'default';
  };

  const daysUntilDelivery = estimatedDelivery
    ? shippingService.getDaysUntilDelivery(estimatedDelivery)
    : null;

  if (!trackingNumber) {
    return (
      <Box p={3} textAlign="center">
        <Typography color="text.secondary">
          No hay información de envío disponible para esta orden
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Shipping Summary */}
      <Paper elevation={0} sx={{ p: 2, mb: 3, bgcolor: 'background.default' }}>
        <Box display="flex" flexWrap="wrap" gap={2} alignItems="center">
          <Box flex={1} minWidth={200}>
            <Typography variant="caption" color="text.secondary">
              Número de Tracking
            </Typography>
            <Typography variant="body1" fontWeight="bold">
              {trackingNumber}
            </Typography>
          </Box>

          <Box flex={1} minWidth={200}>
            <Typography variant="caption" color="text.secondary">
              Courier
            </Typography>
            <Typography variant="body1">
              {courier || 'N/A'}
            </Typography>
          </Box>

          <Box flex={1} minWidth={200}>
            <Typography variant="caption" color="text.secondary">
              Entrega Estimada
            </Typography>
            <Typography variant="body1">
              {estimatedDelivery
                ? shippingService.formatDate(estimatedDelivery)
                : 'N/A'}
            </Typography>
            {daysUntilDelivery !== null && daysUntilDelivery > 0 && (
              <Chip
                label={`En ${daysUntilDelivery} día${daysUntilDelivery > 1 ? 's' : ''}`}
                size="small"
                color="info"
                sx={{ mt: 0.5 }}
              />
            )}
          </Box>
        </Box>
      </Paper>

      {/* Timeline */}
      {events.length > 0 ? (
        <Timeline position="right">
          {events.map((event, index) => (
            <TimelineItem key={index}>
              <TimelineOppositeContent color="text.secondary" sx={{ flex: 0.3 }}>
                <Typography variant="caption">
                  {shippingService.formatDate(event.timestamp)}
                </Typography>
              </TimelineOppositeContent>

              <TimelineSeparator>
                <TimelineDot color={getStatusColor(event.status)}>
                  {getStatusIcon(event.status)}
                </TimelineDot>
                {index < events.length - 1 && <TimelineConnector />}
              </TimelineSeparator>

              <TimelineContent>
                <Paper elevation={1} sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight="bold">
                    {shippingService.getStatusDisplayText(event.status)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mt={0.5}>
                    📍 {event.location}
                  </Typography>
                  {event.description && (
                    <Typography variant="body2" color="text.secondary" mt={0.5}>
                      {event.description}
                    </Typography>
                  )}
                </Paper>
              </TimelineContent>
            </TimelineItem>
          ))}
        </Timeline>
      ) : (
        <Box p={3} textAlign="center">
          <Typography color="text.secondary">
            No hay eventos de seguimiento registrados aún
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ShippingTrackingTimeline;
