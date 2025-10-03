# Vendor Orders - Quick Testing Guide

## Prerequisites

### 1. Services Running
```bash
# Backend (Terminal 1)
cd /home/admin-jairo/MeStore
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (Terminal 2)
cd /home/admin-jairo/MeStore/frontend
npm run dev
```

### 2. Verify Services
- Backend: http://192.168.1.137:8000/docs
- Frontend: http://192.168.1.137:5173

---

## Quick Test Steps

### Step 1: Login as Vendor
1. Navigate to: http://192.168.1.137:5173/login
2. Login with vendor credentials:
   - Email: `vendor@example.com` (or your vendor account)
   - Password: [your vendor password]
3. Should redirect to vendor dashboard

### Step 2: Navigate to Orders
1. Click on navigation menu
2. Find "Orders" or "Órdenes" link
3. Or directly navigate to: http://192.168.1.137:5173/app/vendor/orders

### Step 3: Verify Stats Dashboard
**Should see 4 cards**:
- Total Órdenes (white card)
- Pendientes (amber card)
- Preparando (red card)
- Listos (green card)

**Check**:
- [ ] Numbers display correctly
- [ ] Cards have gradient backgrounds
- [ ] Responsive layout (resize browser)

### Step 4: Verify Order List
**Should see**:
- List of orders (or empty state if no orders)
- Each order card shows:
  - Order number (e.g., #ORD-12345)
  - Order date and time
  - Customer name and phone
  - Product items with images
  - Status badges (colored)
  - Action buttons (Preparando, Listo)
  - Shipping address
  - Total amount in COP

**Check**:
- [ ] Order cards display correctly
- [ ] Currency is formatted (e.g., $50.000)
- [ ] Dates are in Spanish format
- [ ] Product images load (if available)

### Step 5: Test Status Filter
1. Click filter dropdown
2. Select "Pendiente"
3. Should show only pending orders
4. Try other filters:
   - Preparando
   - Listo para Envío
   - Enviado
   - Entregado

**Check**:
- [ ] Filter works correctly
- [ ] "Todos" shows all orders
- [ ] Empty state shows if no matching orders

### Step 6: Test Status Updates

#### Test 1: Pending → Preparing
1. Find an order item with status "Pendiente"
2. Click "Preparando" button (yellow)
3. **Should see**:
   - Loading spinner on button
   - Status badge updates to "Preparando" (red)
   - Button becomes disabled
   - "Listo" button becomes enabled
   - Stats refresh automatically

#### Test 2: Preparing → Ready
1. Find an order item with status "Preparando"
2. Click "Listo" button (green)
3. **Should see**:
   - Loading spinner on button
   - Status badge updates to "Listo para Envío" (green)
   - Both buttons become disabled
   - Stats refresh automatically

**Check**:
- [ ] Status updates successfully
- [ ] UI reflects changes immediately
- [ ] No page refresh needed
- [ ] Stats update correctly
- [ ] Error handling if update fails

### Step 7: Test Error Handling

#### Test Network Error
1. Stop the backend server
2. Try to update an item status
3. **Should see**:
   - Red error alert box
   - Error message displayed
   - Button returns to normal state

#### Test No Orders
1. Use a new vendor account with no orders
2. Navigate to orders page
3. **Should see**:
   - Empty state message
   - Icon indicating no orders
   - Helpful text

**Check**:
- [ ] Error messages are clear
- [ ] Empty state is friendly
- [ ] No console errors

### Step 8: Test Responsive Design

#### Mobile View (375px)
1. Resize browser to mobile size
2. **Should see**:
   - Stats cards stack vertically (1 column)
   - Action buttons stack vertically
   - Order cards take full width
   - All content readable

#### Tablet View (768px)
1. Resize to tablet size
2. **Should see**:
   - Stats cards in 2 columns
   - Order cards adapt width
   - Buttons side-by-side

#### Desktop View (1920px)
1. Resize to desktop size
2. **Should see**:
   - Stats cards in 4 columns
   - Order cards full layout
   - Everything aligned nicely

**Check**:
- [ ] Mobile layout works
- [ ] Tablet layout works
- [ ] Desktop layout works
- [ ] No horizontal scrolling
- [ ] Text is readable at all sizes

---

## Common Issues & Solutions

### Issue 1: Page Not Loading
**Symptom**: Blank page or 404 error

**Solution**:
1. Check backend is running (port 8000)
2. Check frontend is running (port 5173)
3. Verify you're logged in as VENDOR user
4. Check browser console for errors

### Issue 2: No Orders Showing
**Symptom**: Empty state even though orders exist

**Solution**:
1. Check backend API: http://192.168.1.137:8000/api/v1/vendor/orders
2. Verify JWT token in localStorage
3. Check browser Network tab for API errors
4. Ensure vendor has orders in database

### Issue 3: Status Update Fails
**Symptom**: Error message after clicking button

**Possible Causes**:
1. Backend not running
2. Invalid order/item ID
3. Database error
4. Network connectivity

**Solution**:
1. Check backend logs
2. Verify order exists in database
3. Check API endpoint is working
4. Test with curl/Postman

### Issue 4: Stats Not Updating
**Symptom**: Numbers don't change after status update

**Solution**:
1. Refresh page manually
2. Check backend stats endpoint
3. Verify stats calculation logic
4. Check browser console errors

---

## API Testing (Optional)

### Test Backend Directly

#### Get Orders
```bash
# Get vendor orders
curl -X GET "http://192.168.1.137:8000/api/v1/vendor/orders" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

#### Update Item Status
```bash
# Update item to preparing
curl -X PATCH "http://192.168.1.137:8000/api/v1/vendor/orders/ORDER_ID/items/ITEM_ID/status" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "preparing"}'
```

#### Get Stats
```bash
# Get vendor stats
curl -X GET "http://192.168.1.137:8000/api/v1/vendor/orders/stats/summary" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Browser DevTools Checks

### Console Tab
**Should see**:
- No red errors
- Only informational logs (if any)
- Successful API responses

**Red flags**:
- 401 Unauthorized errors
- 500 Server errors
- CORS errors
- Network timeout errors

### Network Tab
**Check API calls**:
1. `/api/v1/vendor/orders` - Should return 200
2. `/api/v1/vendor/orders/stats/summary` - Should return 200
3. PATCH requests - Should return 200

**Headers**:
- `Authorization: Bearer [token]` present
- `Content-Type: application/json`

**Response**:
- Valid JSON data
- Proper status codes

### Application Tab
**LocalStorage**:
- `access_token` present
- `refresh_token` present
- Valid JWT format

---

## Performance Checks

### Load Time
- [ ] Initial page load < 2 seconds
- [ ] Stats load < 1 second
- [ ] Orders list load < 2 seconds
- [ ] Status update < 500ms

### Smooth UX
- [ ] No flickering during load
- [ ] Loading spinners appear immediately
- [ ] Transitions are smooth
- [ ] No layout shifts

---

## Accessibility Checks

### Keyboard Navigation
1. Use Tab key to navigate
2. Use Enter/Space to click buttons
3. Use arrow keys in dropdown

**Check**:
- [ ] All buttons are focusable
- [ ] Focus visible (outline/highlight)
- [ ] Logical tab order
- [ ] Can complete all actions with keyboard

### Screen Reader (Optional)
1. Enable screen reader (NVDA/JAWS)
2. Navigate through page
3. **Should announce**:
   - Page title
   - Card headings
   - Button labels
   - Status changes

---

## Sign-off Checklist

Before marking as complete, verify:

### Functionality
- [ ] Login as vendor works
- [ ] Orders list displays
- [ ] Stats display correctly
- [ ] Status filter works
- [ ] Status updates work
- [ ] Stats refresh after update
- [ ] Error handling works

### UI/UX
- [ ] Design looks professional
- [ ] Colors match status correctly
- [ ] Currency formatted correctly
- [ ] Dates in Spanish format
- [ ] Loading states show
- [ ] Error messages clear

### Responsive
- [ ] Mobile layout works
- [ ] Tablet layout works
- [ ] Desktop layout works
- [ ] No broken layouts

### Performance
- [ ] Page loads quickly
- [ ] No console errors
- [ ] No network errors
- [ ] Smooth interactions

### Code Quality
- [ ] TypeScript compiles
- [ ] No lint errors
- [ ] Code follows standards
- [ ] Documentation complete

---

## Success Criteria

All checkboxes above should be ✅ before considering this feature complete.

**Status**: Ready for testing
**Next Step**: Integration testing with real vendor data
