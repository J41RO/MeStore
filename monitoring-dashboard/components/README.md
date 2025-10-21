# Monitoring Dashboard Components

This directory contains production-ready React components for the Next.js 14 monitoring dashboard.

## Components Overview

### 1. LogsPanel.tsx
Real-time system logs display with advanced filtering capabilities.

**Features:**
- Color-coded log levels (ERROR=red, WARNING=yellow, INFO=blue, DEBUG=gray)
- Filter buttons for each severity level
- Search input with regex support
- Auto-scroll toggle for real-time monitoring
- Export to CSV functionality
- Pause/Resume live updates
- Real-time updates every 5 seconds
- Dark mode compatible
- Displays timestamp, service, and metadata

**Usage:**
```tsx
import LogsPanel from '@/components/LogsPanel';

<LogsPanel refreshInterval={5000} />
```

**Props:**
- `refreshInterval` (optional): Update interval in milliseconds (default: 5000)

---

### 2. MetricsChart.tsx
Response time visualization using Recharts library.

**Features:**
- Area chart showing response times over last 60 minutes
- X-axis: Time labels (HH:MM format)
- Y-axis: Response time in milliseconds
- Gradient fill under line for visual appeal
- Custom tooltip with detailed information
- Trend indicators (up/down percentage)
- Footer stats: Average, Min, Max response times
- Responsive design
- Dark mode compatible
- Real-time data updates

**Usage:**
```tsx
import MetricsChart from '@/components/MetricsChart';

<MetricsChart refreshInterval={5000} />
```

**Props:**
- `refreshInterval` (optional): Update interval in milliseconds (default: 5000)

---

### 3. AlertsPanel.tsx
System alerts and notifications management.

**Features:**
- Alert severity levels: Critical, Warning, Info
- Color-coded alert cards
- Icons based on severity (AlertCircle, AlertTriangle, Info)
- Dismissible alerts
- Badge count for each severity
- Auto-generated alerts based on system health:
  - Slow response times
  - Database connection issues
  - Redis connection problems
  - High error rates (4xx, 5xx)
  - Rate limit violations
  - High traffic notifications
- Clear dismissed alerts functionality
- Sorted by severity and timestamp
- Dark mode compatible

**Usage:**
```tsx
import AlertsPanel from '@/components/AlertsPanel';

<AlertsPanel refreshInterval={10000} />
```

**Props:**
- `refreshInterval` (optional): Update interval in milliseconds (default: 10000)

---

### 4. TestingPanel.tsx
Interactive API testing component for authentication endpoints.

**Features:**
- Test Registration form (email, business_name, phone)
- Test Login form (email, password)
- Test OAuth (simulates Google OAuth flow)
- Display request/response in JSON format
- Expandable details sections
- Loading states with spinners
- Success/error indicators
- Color-coded results (green=success, red=error)
- Quick test credentials helper
- Real-time backend integration
- Dark mode compatible

**Usage:**
```tsx
import TestingPanel from '@/components/TestingPanel';

<TestingPanel />
```

**Props:** None

---

## Common Features

All components include:
- **TypeScript**: Full type safety with proper interfaces
- **Tailwind CSS**: Modern styling with dark mode support
- **Lucide Icons**: Beautiful, consistent iconography
- **Next.js 14 App Router**: Compatible with latest Next.js
- **Responsive Design**: Mobile-first approach, works on all screen sizes
- **Error Handling**: Graceful error handling with user-friendly messages
- **Loading States**: Visual feedback during async operations
- **Accessibility**: Semantic HTML and ARIA labels

## Dependencies

Required packages (should be in package.json):
```json
{
  "dependencies": {
    "react": "^18.x",
    "next": "^14.x",
    "recharts": "^2.x",
    "lucide-react": "^0.x",
    "axios": "^1.x"
  }
}
```

## Backend Integration

Components use two client libraries:

1. **backend-client.ts**: Direct API communication with FastAPI backend
   - Health checks
   - User statistics
   - Auth statistics
   - API metrics
   - Redis statistics
   - Testing endpoints

2. **railway-client.ts**: Railway platform integration
   - Log retrieval via GraphQL
   - Deployment information
   - System metrics
   - Mock data fallback

## Environment Variables

Required in `.env.local`:
```bash
# Backend API
BACKEND_URL=https://mestore.onrender.com

# Railway API (optional)
RAILWAY_API_TOKEN=your_token_here
RAILWAY_PROJECT_ID=your_project_id
RAILWAY_SERVICE_ID=your_service_id
```

## Dark Mode Support

All components automatically adapt to system or user-selected dark mode using Tailwind's `dark:` variants.

To implement dark mode in your app:
```tsx
// app/layout.tsx
import { ThemeProvider } from 'next-themes';

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider attribute="class">
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

## Example Dashboard Layout

```tsx
// app/dashboard/page.tsx
import LogsPanel from '@/components/LogsPanel';
import MetricsChart from '@/components/MetricsChart';
import AlertsPanel from '@/components/AlertsPanel';
import TestingPanel from '@/components/TestingPanel';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Monitoring Dashboard
        </h1>

        {/* First Row: Metrics and Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-[400px]">
            <MetricsChart />
          </div>
          <div className="h-[400px]">
            <AlertsPanel />
          </div>
        </div>

        {/* Second Row: Logs */}
        <div className="h-[500px]">
          <LogsPanel />
        </div>

        {/* Third Row: Testing */}
        <div className="h-auto">
          <TestingPanel />
        </div>
      </div>
    </div>
  );
}
```

## Performance Considerations

1. **Refresh Intervals**: Adjust based on your needs
   - High-frequency: 1-5 seconds (heavy load)
   - Medium-frequency: 5-15 seconds (balanced)
   - Low-frequency: 15-30 seconds (light load)

2. **Data Limits**: Components implement data limits to prevent memory issues
   - LogsPanel: Max 100 logs
   - MetricsChart: Max 60 data points
   - AlertsPanel: Cleared dismissed alerts

3. **Auto-scroll**: Can be disabled in LogsPanel to reduce rendering

## Testing

Components can be tested with:
```bash
npm run test
```

## Troubleshooting

### Components not updating
- Check backend API is running
- Verify BACKEND_URL in environment variables
- Check browser console for errors

### Dark mode not working
- Ensure ThemeProvider is properly configured
- Check Tailwind config includes dark mode

### Charts not rendering
- Verify recharts is installed: `npm install recharts`
- Check container has explicit height

## Future Enhancements

Possible additions:
- WebSocket support for real-time logs
- Export alerts to PDF
- Custom alert rules
- Metric comparisons (day over day)
- User authentication for testing panel
- Database query monitoring
- Performance profiling

## Support

For issues or questions, refer to:
- Backend API docs: `/docs` endpoint
- Railway docs: https://docs.railway.app
- Next.js docs: https://nextjs.org/docs

---

**Built with React 18, Next.js 14, TypeScript, and Tailwind CSS**
