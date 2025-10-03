# Loading Components Guide

Comprehensive guide for using loading states across the MeStore application.

## 📋 Table of Contents

- [Overview](#overview)
- [LoadingSpinner](#loadingspinner)
- [SkeletonLoader](#skeletonloader)
- [ProgressBar](#progressbar)
- [Best Practices](#best-practices)
- [Examples](#examples)

---

## Overview

This library provides three main types of loading components:

1. **LoadingSpinner** - Animated spinners for general loading states
2. **SkeletonLoader** - Placeholder UI that matches final content layout
3. **ProgressBar** - Progress indicators for long-running operations

### When to Use Each Component

| Component | Use Case | Example |
|-----------|----------|---------|
| LoadingSpinner | Simple loading state, button actions | "Loading..." overlay |
| SkeletonLoader | Initial page load, content placeholders | Product list loading |
| ProgressBar | Upload/download, multi-step processes | File upload, order processing |

---

## LoadingSpinner

Animated spinner component with multiple variants.

### Basic Usage

```tsx
import { LoadingSpinner } from '@/components/common';

// Simple spinner
<LoadingSpinner />

// With size
<LoadingSpinner size="lg" />

// With color
<LoadingSpinner color="primary" />

// With message
<LoadingSpinner message="Loading data..." />

// Fullscreen overlay
<LoadingSpinner fullScreen message="Processing order..." />
```

### Props

```tsx
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';        // Default: 'md'
  color?: 'primary' | 'secondary' | 'white' | 'gray';  // Default: 'primary'
  fullScreen?: boolean;                     // Default: false
  message?: string;                         // Optional loading message
  className?: string;                       // Additional CSS classes
}
```

### Variants

#### ButtonSpinner

For use inside buttons during loading states:

```tsx
import { ButtonSpinner } from '@/components/common';

<button disabled={loading}>
  {loading ? (
    <span className="flex items-center gap-2">
      <ButtonSpinner />
      Loading...
    </span>
  ) : (
    'Submit'
  )}
</button>
```

#### InlineLoader

Small inline loading indicator:

```tsx
import { InlineLoader } from '@/components/common';

<InlineLoader text="Updating" />
```

---

## SkeletonLoader

Skeleton screens for better perceived performance.

### Basic Usage

```tsx
import { SkeletonLoader } from '@/components/common';

// Text skeleton
<SkeletonLoader variant="text" count={3} />

// Rectangular placeholder
<SkeletonLoader variant="rectangular" width="100%" height={200} />

// Circular avatar
<SkeletonLoader variant="circular" width={40} height={40} />

// Card skeleton
<SkeletonLoader variant="card" count={5} />

// Table row skeleton
<SkeletonLoader variant="table-row" count={10} />
```

### Props

```tsx
interface SkeletonLoaderProps {
  variant?: 'text' | 'circular' | 'rectangular' | 'card' | 'table-row' | 'stats-card';
  width?: string | number;      // Default: varies by variant
  height?: string | number;     // Default: varies by variant
  count?: number;               // Default: 1
  className?: string;           // Additional CSS classes
  animation?: 'pulse' | 'wave' | 'none';  // Default: 'pulse'
}
```

### Specialized Variants

#### SkeletonTable

For table layouts:

```tsx
import { SkeletonTable } from '@/components/common';

<SkeletonTable rows={10} columns={5} />
```

#### SkeletonGrid

For grid layouts:

```tsx
import { SkeletonGrid } from '@/components/common';

<SkeletonGrid count={6} columns={3} />
```

#### SkeletonStatsCards

For statistics dashboards:

```tsx
import { SkeletonStatsCards } from '@/components/common';

<SkeletonStatsCards count={4} />
```

#### SkeletonOrderCard

For order listings:

```tsx
import { SkeletonOrderCard } from '@/components/common';

{isLoading ? (
  <>
    <SkeletonOrderCard />
    <SkeletonOrderCard />
    <SkeletonOrderCard />
  </>
) : (
  orders.map(order => <OrderCard key={order.id} {...order} />)
)}
```

---

## ProgressBar

Progress indicators for operations with known duration.

### Basic Usage

```tsx
import { ProgressBar } from '@/components/common';

// Simple progress bar
<ProgressBar progress={45} />

// With label and percentage
<ProgressBar
  progress={45}
  label="Uploading..."
  showPercentage
/>

// Different colors
<ProgressBar progress={100} color="green" label="Complete!" />

// Different sizes
<ProgressBar progress={50} size="lg" />

// Indeterminate (unknown duration)
<ProgressBar indeterminate label="Processing..." />
```

### Props

```tsx
interface ProgressBarProps {
  progress?: number;           // 0-100, default: 0
  label?: string;              // Optional label
  showPercentage?: boolean;    // Default: false
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'gray';  // Default: 'blue'
  size?: 'sm' | 'md' | 'lg';   // Default: 'md'
  indeterminate?: boolean;     // Default: false
  className?: string;
}
```

### Specialized Variants

#### CircularProgress

Ring-style circular progress:

```tsx
import { CircularProgress } from '@/components/common';

<CircularProgress
  progress={75}
  size={120}
  color="#3B82F6"
  showPercentage
/>
```

#### StepProgress

Multi-step progress indicator:

```tsx
import { StepProgress } from '@/components/common';

<StepProgress
  steps={['Cart', 'Shipping', 'Payment', 'Confirmation']}
  currentStep={2}
/>
```

#### UploadProgress

Specialized for file uploads:

```tsx
import { UploadProgress } from '@/components/common';

<UploadProgress
  fileName="document.pdf"
  progress={65}
  onCancel={() => cancelUpload()}
/>
```

---

## Best Practices

### 1. Initial Page Load

Use skeleton loaders for initial content loading:

```tsx
const [loading, setLoading] = useState(true);
const [data, setData] = useState(null);

const isInitialLoading = loading && !data;

return (
  <>
    {isInitialLoading ? (
      <SkeletonLoader variant="card" count={5} />
    ) : (
      <DataDisplay data={data} />
    )}
  </>
);
```

### 2. Button Actions

Use ButtonSpinner for action buttons:

```tsx
const [submitting, setSubmitting] = useState(false);

<button
  disabled={submitting}
  onClick={handleSubmit}
  className="btn-primary"
>
  {submitting ? (
    <span className="flex items-center gap-2">
      <ButtonSpinner />
      Submitting...
    </span>
  ) : (
    'Submit'
  )}
</button>
```

### 3. Pagination/Filtering

Don't show full skeleton on filter changes:

```tsx
const isInitialLoading = loading && items.length === 0;

// Show skeleton only on initial load
{isInitialLoading ? (
  <SkeletonLoader variant="card" count={10} />
) : (
  <ItemList items={items} />
)}

// Show inline spinner on filter changes
{loading && items.length > 0 && (
  <InlineLoader text="Updating" />
)}
```

### 4. Long Operations

Use progress bars for operations with known progress:

```tsx
const [uploadProgress, setUploadProgress] = useState(0);

<UploadProgress
  fileName={file.name}
  progress={uploadProgress}
  onCancel={cancelUpload}
/>
```

### 5. Accessibility

All components include ARIA attributes:

```tsx
// Automatically included
<div
  role="status"
  aria-busy="true"
  aria-label="Loading content"
>
  <LoadingSpinner />
</div>
```

---

## Examples

### Example 1: Admin Orders Page

```tsx
import { SkeletonTable, LoadingSpinner } from '@/components/common';

const AdminOrders = () => {
  const [loading, setLoading] = useState(true);
  const [orders, setOrders] = useState([]);

  const isInitialLoading = loading && orders.length === 0;

  return (
    <div>
      <h1>Orders Management</h1>

      {isInitialLoading ? (
        <SkeletonTable rows={20} columns={8} />
      ) : (
        <OrdersTable orders={orders} />
      )}
    </div>
  );
};
```

### Example 2: Vendor Dashboard

```tsx
import { SkeletonStatsCards, SkeletonOrderCard } from '@/components/common';

const VendorDashboard = () => {
  const [statsLoading, setStatsLoading] = useState(true);
  const [ordersLoading, setOrdersLoading] = useState(true);

  return (
    <div>
      {/* Stats Cards */}
      {statsLoading ? (
        <SkeletonStatsCards count={4} />
      ) : (
        <StatsCards data={stats} />
      )}

      {/* Orders List */}
      {ordersLoading ? (
        <>
          <SkeletonOrderCard />
          <SkeletonOrderCard />
          <SkeletonOrderCard />
        </>
      ) : (
        orders.map(order => <OrderCard key={order.id} {...order} />)
      )}
    </div>
  );
};
```

### Example 3: Form Submission

```tsx
import { ButtonSpinner, ProgressBar } from '@/components/common';

const OrderForm = () => {
  const [submitting, setSubmitting] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  return (
    <form onSubmit={handleSubmit}>
      {/* File upload with progress */}
      {uploadProgress > 0 && uploadProgress < 100 && (
        <ProgressBar
          progress={uploadProgress}
          label="Uploading attachments..."
          showPercentage
          color="blue"
        />
      )}

      {/* Submit button */}
      <button
        type="submit"
        disabled={submitting}
        className="btn-primary"
      >
        {submitting ? (
          <span className="flex items-center gap-2">
            <ButtonSpinner />
            Processing...
          </span>
        ) : (
          'Create Order'
        )}
      </button>
    </form>
  );
};
```

### Example 4: Modal with Loading

```tsx
import { LoadingSpinner } from '@/components/common';

const OrderDetailModal = ({ orderId, open, onClose }) => {
  const [loading, setLoading] = useState(true);
  const [order, setOrder] = useState(null);

  useEffect(() => {
    if (open && orderId) {
      loadOrderDetails(orderId);
    }
  }, [open, orderId]);

  return (
    <Modal open={open} onClose={onClose}>
      <ModalHeader>Order Details</ModalHeader>
      <ModalBody>
        {loading ? (
          <LoadingSpinner message="Loading order details..." />
        ) : (
          <OrderDetails order={order} />
        )}
      </ModalBody>
    </Modal>
  );
};
```

---

## Performance Tips

1. **Use skeletons for initial loads** - Better perceived performance
2. **Avoid fullScreen overlays** - Unless absolutely necessary
3. **Match skeleton to final layout** - Reduces layout shift
4. **Use indeterminate for unknown duration** - More honest UX
5. **Disable actions during loading** - Prevent duplicate submissions

---

## Styling Customization

All components support Tailwind CSS customization:

```tsx
// Custom spinner color
<LoadingSpinner className="text-purple-600" />

// Custom skeleton animation
<SkeletonLoader animation="wave" />

// Custom progress bar height
<ProgressBar className="h-4" />
```

---

## Integration with Existing Components

### Material-UI Components

These components work alongside MUI:

```tsx
import { CircularProgress } from '@mui/material';
import { LoadingSpinner } from '@/components/common';

// Use MUI for consistency if already using MUI
<CircularProgress />

// Use custom spinner for Tailwind-based pages
<LoadingSpinner />
```

### Zustand Stores

Integrate with global loading states:

```tsx
const useLoadingStore = create((set) => ({
  isLoading: false,
  setLoading: (loading) => set({ isLoading: loading }),
}));

const Component = () => {
  const { isLoading } = useLoadingStore();

  return isLoading ? <LoadingSpinner fullScreen /> : <Content />;
};
```

---

## Testing

All components are testable:

```tsx
import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from '@/components/common';

test('shows loading message', () => {
  render(<LoadingSpinner message="Loading data" />);
  expect(screen.getByText('Loading data')).toBeInTheDocument();
});
```

---

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Full support

All animations use CSS transforms for optimal performance.
