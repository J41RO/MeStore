# Product Detail Page - Testing Guide

## Quick Start Testing

### Prerequisites
- Backend running on port 8000: `http://192.168.1.137:8000`
- Frontend running on port 5173: `http://192.168.1.137:5173`
- Database has approved products with images

## Manual Testing Scenarios

### Test 1: Navigate from Catalog to Product Detail
**Steps:**
1. Open browser: `http://192.168.1.137:5173/catalog`
2. Wait for products to load (should see 12-48 products)
3. Click on any product card
4. **Expected Result:** Navigates to `/marketplace/product/[id]`
5. **Verify:** Product details page loads with all information

### Test 2: Direct URL Access
**Steps:**
1. Get a product ID from catalog
2. Open browser: `http://192.168.1.137:5173/productos/[id]`
3. **Expected Result:** Product detail page loads directly
4. Try alternative URL: `http://192.168.1.137:5173/marketplace/product/[id]`
5. Try catalog URL: `http://192.168.1.137:5173/catalog/[id]`
6. **Verify:** All three URL patterns work

### Test 3: Image Gallery Navigation
**Steps:**
1. Navigate to any product with multiple images
2. Click thumbnail images
3. **Expected Result:** Main image changes
4. Click left/right navigation arrows (desktop)
5. **Expected Result:** Cycles through images
6. Click zoom button
7. **Expected Result:** Image zooms in
8. **Verify:** Counter shows "1/X" where X is total images

### Test 4: Quantity Selector
**Steps:**
1. On product detail page, find quantity selector
2. Click "+" button
3. **Expected Result:** Quantity increases to 2
4. Click "-" button
5. **Expected Result:** Quantity decreases to 1
6. Try clicking "-" again at quantity 1
7. **Expected Result:** Button disabled, quantity stays at 1
8. Increase quantity to match available stock
9. **Expected Result:** "+" button becomes disabled

### Test 5: Add to Cart Functionality
**Steps:**
1. Set quantity to 2
2. Click "Agregar al carrito" button
3. **Expected Result:**
   - Button shows loading spinner
   - After ~500ms, shows checkmark and "¡Agregado al carrito!"
   - Button turns green
   - Quantity resets to 1
4. Open browser DevTools → Application → Local Storage
5. **Verify:** Key `mestore_cart` exists with product data
6. Click "Agregar al carrito" again
7. **Verify:** Cart quantity updates (not duplicates)

### Test 6: Stock Validation
**Steps:**
1. Find product with low stock (e.g., 3 units)
2. Add 2 units to cart
3. **Expected Result:** Success message, 1 unit remaining
4. Try to add 2 more units
5. **Expected Result:** Error message "Solo hay X unidades disponibles (2 ya en carrito)"
6. **Verify:** Cannot exceed available stock

### Test 7: Out of Stock Product
**Steps:**
1. Find product with 0 stock
2. Navigate to product detail
3. **Expected Result:**
   - "Producto agotado" message
   - Add to cart button disabled
   - Gray background indicator
4. **Verify:** No way to add to cart

### Test 8: Back Navigation
**Steps:**
1. From catalog, click product
2. Click "Volver" button (back arrow)
3. **Expected Result:** Returns to catalog with previous scroll position
4. Navigate to product detail via direct URL
5. Click "Volver"
6. **Expected Result:** Falls back to `/marketplace/search`

### Test 9: Product Not Found (404)
**Steps:**
1. Navigate to: `http://192.168.1.137:5173/productos/999999`
2. **Expected Result:**
   - Red error icon
   - "Producto no encontrado" message
   - "Volver" and "Ir al Marketplace" buttons
3. Click "Volver" button
4. **Verify:** Navigates correctly

### Test 10: Vendor Information
**Steps:**
1. Navigate to any product detail
2. Scroll to bottom
3. **Expected Result:** Vendor info section displays:
   - Business name
   - Email (if available)
   - "Ver más productos" link (optional)
4. **Verify:** Vendor details match backend data

### Test 11: Price Formatting (Colombian)
**Steps:**
1. Check product price display
2. **Expected Result:** Format: $50.000 (Colombian style)
3. **Verify:** No decimals for COP currency
4. Check total price in cart section
5. **Verify:** Updates correctly with quantity

### Test 12: Responsive Layout
**Mobile (<768px):**
1. Open DevTools, set viewport to iPhone (375px)
2. **Expected Result:**
   - Image gallery full width
   - Product info stacked below
   - Touch indicators (dots) visible
   - Thumbnails scrollable horizontally

**Tablet (768-1023px):**
1. Set viewport to iPad (768px)
2. **Expected Result:**
   - Two-column layout (50/50)
   - All functionality intact

**Desktop (>1024px):**
1. Set viewport to 1440px
2. **Expected Result:**
   - Two-column layout (60/40)
   - Hover effects on images
   - Arrows visible on image hover

### Test 13: Multiple Image Handling
**Steps:**
1. Find product with 0 images
2. **Expected Result:** Placeholder with "Sin imagen" icon
3. Find product with 1 image
4. **Expected Result:** No thumbnails, no navigation arrows
5. Find product with 5+ images
6. **Expected Result:** Thumbnail strip scrollable

### Test 14: Category and SKU Display
**Steps:**
1. Verify category badge displays in top-right
2. **Expected Result:** Blue pill badge with category name
3. Check SKU below price
4. **Expected Result:** "SKU: XXX" in gray text

### Test 15: Date Display
**Steps:**
1. Check "Agregado el:" timestamp
2. **Expected Result:** Spanish format: "1 de octubre de 2025"
3. Check "Actualizado el:" if different
4. **Verify:** Only shows if updated_at ≠ created_at

## Browser Compatibility Testing

### Chrome/Edge (Chromium)
- Test all scenarios above
- **Verify:** LocalStorage works
- **Verify:** Image lazy loading

### Firefox
- Test add to cart
- **Verify:** LocalStorage compatibility

### Safari (if available)
- Test image gallery
- **Verify:** Webkit CSS compatibility

### Mobile Browsers
- Test on actual device if possible
- **Verify:** Touch interactions work
- **Verify:** Swipe gestures (optional)

## Performance Testing

### Load Time
1. Open Network tab in DevTools
2. Navigate to product detail
3. **Expected Result:** Page loads < 2 seconds
4. Check individual resource times
5. **Verify:** Images load progressively

### Memory Usage
1. Open Performance Monitor in DevTools
2. Navigate through 10+ products
3. **Verify:** Memory doesn't grow excessively
4. Check for memory leaks

## Error Scenarios

### Network Failure
**Steps:**
1. Open DevTools → Network tab
2. Set throttling to "Offline"
3. Navigate to product detail
4. **Expected Result:** Error message with retry button
5. Switch to "Online"
6. Click "Reintentar"
7. **Verify:** Product loads successfully

### Invalid Product ID
**Steps:**
1. Navigate to: `/productos/abc` (non-numeric)
2. **Expected Result:** Error handling or 404
3. Navigate to: `/productos/-1` (negative ID)
4. **Expected Result:** Proper error message

### Unapproved Product
**Steps:**
1. Try to access product with estado ≠ 'aprobado'
2. **Expected Result:** "Este producto no está disponible" message
3. **Verify:** Product data not displayed

## Accessibility Testing

### Keyboard Navigation
**Steps:**
1. Use Tab key to navigate through page
2. **Verify:** All interactive elements reachable
3. Use Enter on "Agregar al carrito"
4. **Verify:** Button activates
5. Use arrow keys in image gallery (if implemented)

### Screen Reader (Optional)
**Steps:**
1. Enable screen reader (NVDA/JAWS/VoiceOver)
2. Navigate product detail page
3. **Verify:** All content announced properly
4. Check image alt texts
5. **Verify:** Button labels descriptive

### Color Contrast
**Steps:**
1. Check price text contrast
2. Check button text contrast
3. **Verify:** WCAG AA compliance (4.5:1 ratio minimum)

## Data Validation

### API Response Check
**Steps:**
1. Open DevTools → Network tab
2. Navigate to product detail
3. Find request to `/api/v1/products/[id]`
4. Check response JSON
5. **Verify:** All expected fields present:
   ```json
   {
     "id": number,
     "name": string,
     "description": string,
     "precio_venta": number,
     "categoria": string,
     "sku": string,
     "estado": "aprobado",
     "stock_quantity": number,
     "images": array,
     "vendor": object
   }
   ```

### LocalStorage Validation
**Steps:**
1. Add product to cart
2. Open DevTools → Application → Local Storage
3. Check `mestore_cart` key
4. **Verify:** JSON structure:
   ```json
   [
     {
       "productId": number,
       "quantity": number,
       "price": number,
       "addedAt": "ISO 8601 timestamp"
     }
   ]
   ```

## Regression Testing

### After Code Changes
**Checklist:**
- [ ] All URL patterns still work
- [ ] Navigation from catalog intact
- [ ] Image gallery functions
- [ ] Cart operations persist
- [ ] No console errors
- [ ] Responsive layout unbroken
- [ ] Price formatting correct
- [ ] Back button works

## Bug Reporting Template

If you find issues, report using this template:

```
**Bug Title:** [Concise description]

**Steps to Reproduce:**
1.
2.
3.

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Screenshots:**
[If applicable]

**Environment:**
- Browser:
- OS:
- Frontend URL:
- Backend URL:
- Product ID tested:

**Console Errors:**
[Any errors from DevTools console]

**Network Response:**
[API response if relevant]
```

## Success Criteria

All tests should pass with these results:
- ✅ Navigation works from multiple entry points
- ✅ All three URL patterns functional
- ✅ Image gallery displays and navigates
- ✅ Quantity selector operates correctly
- ✅ Add to cart persists in localStorage
- ✅ Stock validation prevents overselling
- ✅ Responsive on all screen sizes
- ✅ Colombian formatting (prices, dates)
- ✅ Error states handled gracefully
- ✅ No console errors
- ✅ Performance < 2 seconds load time

## Automated Testing (Future)

Consider adding:
- Unit tests with Vitest/Jest
- Component tests with React Testing Library
- E2E tests with Cypress/Playwright
- Visual regression tests

---

**Last Updated:** October 1, 2025
**Testing Coverage:** Manual testing scenarios
**Status:** Ready for QA review
