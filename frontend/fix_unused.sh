#!/bin/bash

# Script to fix common TypeScript unused variable/import errors

echo "🔧 Fixing unused imports and variables..."

# Fix unused imports
sed -i 's/import { AlertCircle/import {/' src/components/forms/ProductForm.tsx
sed -i 's/import { ShoppingBag, Star/import {/' src/pages/MarketplaceHome.tsx
sed -i 's/import ImageUpload from/#import ImageUpload from/' src/pages/RegisterVendor.tsx
sed -i 's/import { vendorApi }/\/\/ import { vendorApi }/' src/hooks/useVendorMetrics.ts
sed -i 's/import { Download, Upload/import {/' src/pages/admin/SystemConfig.tsx
sed -i 's/import { CreateProductData }/\/\/ import { CreateProductData }/' src/schemas/productSchema.ts

# Fix unused variables with underscore prefix
sed -i 's/const \([a-zA-Z_][a-zA-Z0-9_]*\), set\([a-zA-Z_][a-zA-Z0-9_]*\) = useState/const _\1, set\2 = useState/' src/pages/VendorProfile.tsx
sed -i 's/const \([a-zA-Z_][a-zA-Z0-9_]*\), set\([a-zA-Z_][a-zA-Z0-9_]*\) = useState/const _\1, set\2 = useState/' src/hooks/useVendorMetrics.ts
sed -i 's/getSettingsByCategory/_getSettingsByCategory/' src/pages/admin/SystemConfig.tsx
sed -i 's/(key: string)/(\_key: string)/' src/pages/admin/SystemConfig.tsx
sed -i 's/handleAvatarUpdate/_handleAvatarUpdate/' src/pages/VendorProfile.tsx
sed -i 's/processedData/_processedData/' src/components/forms/ProductForm.tsx

# Fix unused destructured variables
sed -i 's/, isDirty, touchedFields/, _isDirty, _touchedFields/' src/components/forms/ProductForm.tsx
sed -i 's/setError,/_setError,/' src/components/forms/ProductForm.tsx
sed -i 's/clearErrors,/_clearErrors,/' src/components/forms/ProductForm.tsx
sed -i 's/getValues,/_getValues,/' src/components/forms/ProductForm.tsx

echo "✅ Basic unused variable fixes applied"