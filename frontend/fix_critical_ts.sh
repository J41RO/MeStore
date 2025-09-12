#!/bin/bash

echo "🔧 Fixing critical TypeScript errors..."

# Remove unused variables by commenting or prefixing
sed -i 's/const _getUtilizationBgColor/\/\/ const _getUtilizationBgColor/' src/components/admin/LocationAssignmentForm.tsx
sed -i 's/const _ProductosRecientesSection/\/\/ const _ProductosRecientesSection/' src/components/dashboard/VendorDashboard.tsx
sed -i 's/const _response/\/\/ const _response/' src/components/forms/EarlyAccessForm.tsx
sed -i 's/const _response/\/\/ const _response/' src/components/forms/LeadCaptureForm.tsx
sed -i 's/const _processedData/\/\/ const _processedData/' src/components/forms/ProductForm.tsx

# Fix imports
sed -i 's/import { ShoppingBag, Star, TrendingUp/import { TrendingUp/' src/pages/MarketplaceHome.tsx
sed -i 's/import { Download, Upload/import {/' src/pages/admin/SystemConfig.tsx

# Fix other unused variables
sed -i 's/const \[saving, setSaving\]/const [_saving, setSaving]/' src/pages/VendorProfile.tsx
sed -i 's/const \[realtimeData, setRealtimeData\]/const [_realtimeData, setRealtimeData]/' src/hooks/useVendorMetrics.ts
sed -i 's/getSettingsByCategory/_getSettingsByCategory/' src/pages/admin/SystemConfig.tsx
sed -i 's/(key: string)/(_key: string)/' src/pages/admin/SystemConfig.tsx
sed -i 's/handleAvatarUpdate/_handleAvatarUpdate/' src/pages/VendorProfile.tsx

# Fix VendorProfile avatar_url type issue
sed -i 's/avatar_url: null,/avatar_url: undefined,/' src/pages/VendorProfile.tsx

echo "✅ Critical TypeScript fixes applied"