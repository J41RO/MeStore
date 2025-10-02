# Shopping Cart System - Testing Checklist
**MeStore Marketplace - Colombian E-commerce**

## Overview
Complete testing guide for the shopping cart system implementation using Zustand state management, localStorage persistence, and Colombian pricing (IVA 19%).

---

## 1. Cart Store Testing (cartStore.ts)

### State Management
- [ ] Cart initializes empty on first visit
- [ ] Cart persists items after page reload
- [ ] Cart hydrates correctly from localStorage
- [ ] Cart handles localStorage quota exceeded gracefully

### Add Item Operations
- [ ] Add new product to cart
- [ ] Add same product increases quantity
- [ ] Cannot exceed max stock when adding
- [ ] Drawer opens automatically after adding
- [ ] Badge counter updates immediately

### Update Quantity Operations
- [ ] Increase quantity from cart drawer
- [ ] Decrease quantity from cart drawer
- [ ] Quantity cannot exceed stock limit
- [ ] Quantity cannot go below 1
- [ ] Setting quantity to 0 removes item

### Remove Item Operations
- [ ] Remove single item from cart
- [ ] Clear entire cart with confirmation
- [ ] Cart updates immediately after removal

### Calculations (Colombian Pricing)
- [ ] Subtotal calculates correctly (sum of item prices)
- [ ] IVA calculates at 19% of subtotal
- [ ] Shipping is FREE for orders ≥ $200,000 COP
- [ ] Shipping is $15,000 COP for orders < $200,000 COP
- [ ] Total = Subtotal + IVA + Shipping
- [ ] Total items counter is accurate

### Price Formatting
- [ ] Prices format as Colombian Pesos (COP)
- [ ] No decimal places shown (e.g., $150.000)
- [ ] Thousands separator uses period (e.g., 150.000)

---

## 2. CartDrawer Component Testing

### UI/UX Testing
- [ ] Drawer slides in from right smoothly
- [ ] Backdrop overlay appears with blur effect
- [ ] Click backdrop closes drawer
- [ ] Close button (X) closes drawer
- [ ] Body scroll is locked when drawer is open
- [ ] Smooth animations with framer-motion

### Empty State
- [ ] Empty cart shows appropriate message
- [ ] "Explorar Productos" button closes drawer
- [ ] Empty cart icon displays correctly

### Cart Items Display
- [ ] All cart items render correctly
- [ ] Product images display (or placeholder)
- [ ] Product name, SKU, price shown
- [ ] Quantity controls (+/-) work
- [ ] Individual item subtotal calculates
- [ ] Remove button (trash icon) works

### Free Shipping Progress
- [ ] Progress bar shows when subtotal < $200,000
- [ ] Message shows amount needed for free shipping
- [ ] Progress bar fills based on percentage
- [ ] Message changes to "¡GRATIS!" when threshold reached
- [ ] Progress section hides when cart is empty

### Price Breakdown
- [ ] Subtotal displays correctly
- [ ] IVA (19%) displays correctly
- [ ] Shipping cost displays correctly
- [ ] Shipping shows "¡GRATIS!" when applicable
- [ ] Total displays in large blue text
- [ ] All prices use formatCOP utility

### Action Buttons
- [ ] "Ir al Checkout" navigates to /checkout
- [ ] "Ir al Checkout" closes drawer
- [ ] "Seguir Comprando" closes drawer
- [ ] "Vaciar Carrito" shows confirmation
- [ ] Cart clears after confirmation

### Accessibility
- [ ] Drawer has proper ARIA labels
- [ ] Dialog role is set
- [ ] Keyboard navigation works (Tab, Escape)
- [ ] Screen reader announces cart items

---

## 3. CartButton Component Testing

### Visual Testing
- [ ] Shopping cart icon renders
- [ ] Badge shows when items > 0
- [ ] Badge hides when cart is empty
- [ ] Badge shows "99+" for items > 99
- [ ] Pulse animation on badge

### Badge Counter
- [ ] Counter updates immediately on add
- [ ] Counter updates on quantity change
- [ ] Counter updates on item removal
- [ ] Counter resets on clear cart
- [ ] Animated badge entrance/exit

### Click Behavior
- [ ] Click opens CartDrawer
- [ ] Hover changes color to blue
- [ ] Icon scales on hover
- [ ] Proper aria-label for accessibility

---

## 4. AddToCartButton Component Testing

### Stock Validation
- [ ] Shows "Producto agotado" when stock = 0
- [ ] Disables button when disabled prop = true
- [ ] Shows "Ya en tu carrito" when all stock in cart
- [ ] Displays available stock correctly
- [ ] Prevents adding beyond available stock

### Quantity Selector
- [ ] Quantity starts at 1
- [ ] Plus button increases quantity
- [ ] Minus button decreases quantity
- [ ] Cannot decrease below 1
- [ ] Cannot exceed available stock
- [ ] Shows current in-cart quantity info

### Add to Cart Action
- [ ] Shows loading spinner while adding
- [ ] Success message "¡Agregado al carrito!" shows
- [ ] Success state persists for 2 seconds
- [ ] Quantity resets to 1 after adding
- [ ] Error message shows on failure
- [ ] onAddToCart callback fires (if provided)

### Price Display
- [ ] Unit price shows correctly
- [ ] Total price calculates (price × quantity)
- [ ] Prices format as Colombian Pesos
- [ ] Total updates when quantity changes

### Integration
- [ ] Uses Zustand cartStore.addItem()
- [ ] Uses formatCOP for price formatting
- [ ] Checks existing cart quantity via getCartItem()
- [ ] Works with Product type from types/index.ts

---

## 5. MarketplaceNavbar Integration Testing

### Component Mounting
- [ ] CartButton renders in navbar
- [ ] CartDrawer mounts with navbar
- [ ] No console errors on mount
- [ ] Imports are correct

### Visual Integration
- [ ] CartButton positioned correctly (top-right)
- [ ] Spacing around CartButton is appropriate
- [ ] CartButton aligns with other nav items
- [ ] Responsive on mobile (stays visible)

### Functionality
- [ ] Click CartButton opens drawer
- [ ] Badge counter updates from navbar
- [ ] Drawer overlays entire viewport
- [ ] Navbar remains accessible with drawer open

---

## 6. ProductDetail Page Integration Testing

### Product Adapter
- [ ] Local Product type maps to global Product type
- [ ] All required fields are mapped correctly
- [ ] Images map correctly (primary image)
- [ ] vendor_id converts to string
- [ ] stock_quantity maps to stock

### Add to Cart Flow
- [ ] AddToCartButton renders on product page
- [ ] Product data passes correctly
- [ ] Add to cart works from detail page
- [ ] Badge updates after adding from detail
- [ ] Drawer shows newly added product

---

## 7. End-to-End User Flow Testing

### Complete Purchase Journey
1. [ ] Navigate to marketplace
2. [ ] Browse products
3. [ ] Click product to view details
4. [ ] Select quantity (e.g., 3 units)
5. [ ] Click "Agregar al carrito"
6. [ ] See success message
7. [ ] See badge counter update (3)
8. [ ] Click cart button
9. [ ] Drawer opens showing product
10. [ ] Verify price breakdown is correct
11. [ ] Adjust quantity in drawer (+/-)
12. [ ] Badge updates accordingly
13. [ ] Remove item (trash icon)
14. [ ] Add another product
15. [ ] Verify free shipping progress
16. [ ] Click "Ir al Checkout"
17. [ ] Navigate to /checkout page

### Cart Persistence Flow
1. [ ] Add items to cart
2. [ ] Reload page (F5)
3. [ ] Cart items still present
4. [ ] Badge counter correct after reload
5. [ ] Open drawer - items still there
6. [ ] Clear localStorage manually
7. [ ] Cart should be empty on next load

### Multi-Product Scenarios
- [ ] Add multiple different products
- [ ] Each product shows in drawer
- [ ] Total calculates across all items
- [ ] IVA applies to combined subtotal
- [ ] Free shipping triggers at $200,000+ total

### Error Handling
- [ ] Try to add more than available stock
- [ ] Error message shows appropriately
- [ ] Cart doesn't update with invalid quantity
- [ ] localStorage quota exceeded handled gracefully
- [ ] Network errors don't crash app

---

## 8. Mobile Responsiveness Testing

### Drawer on Mobile
- [ ] Drawer takes full width on mobile
- [ ] Drawer takes 480px width on desktop
- [ ] Touch gestures work for closing
- [ ] Scroll works inside drawer
- [ ] Body scroll locked on mobile

### CartButton on Mobile
- [ ] Badge visible and readable on small screens
- [ ] Touch target large enough (min 44px)
- [ ] Tap works reliably

### AddToCartButton on Mobile
- [ ] Quantity controls large enough to tap
- [ ] Button full-width on mobile
- [ ] Text doesn't overflow
- [ ] Price formatting readable

---

## 9. Performance Testing

### Load Times
- [ ] Cart drawer opens < 300ms
- [ ] Badge counter updates < 50ms
- [ ] Add to cart action < 500ms
- [ ] localStorage read/write < 100ms

### Bundle Size
- [ ] Zustand adds minimal bundle size (~3KB)
- [ ] Framer Motion tree-shaken properly
- [ ] No duplicate dependencies

### Memory
- [ ] No memory leaks from drawer opening/closing
- [ ] Event listeners cleaned up properly
- [ ] useState doesn't cause re-render loops

---

## 10. Accessibility (WCAG 2.1 AA) Testing

### Keyboard Navigation
- [ ] Tab through cart items
- [ ] Enter/Space activates buttons
- [ ] Escape closes drawer
- [ ] Focus trap within drawer when open

### Screen Reader
- [ ] Cart button announces item count
- [ ] Drawer title announced when opening
- [ ] Price changes announced
- [ ] Success/error messages announced

### Visual
- [ ] Color contrast meets AA standards
- [ ] Focus indicators visible
- [ ] Text scalable to 200%
- [ ] No information conveyed by color alone

### ARIA
- [ ] role="dialog" on drawer
- [ ] aria-label on buttons
- [ ] aria-modal="true" on drawer
- [ ] aria-live regions for announcements

---

## 11. Colombian Localization Testing

### Currency Formatting
- [ ] All prices show "$ " prefix
- [ ] Thousands use period separator (150.000)
- [ ] No decimal places shown
- [ ] Currency code COP not displayed

### Language
- [ ] All UI text in Spanish
- [ ] Colombian Spanish terms used
- [ ] Error messages in Spanish
- [ ] Success messages in Spanish

### Tax/Shipping
- [ ] IVA labeled as "IVA (19%)"
- [ ] Shipping labeled as "Envío"
- [ ] Free shipping message: "¡GRATIS!"
- [ ] Thresholds use Colombian amounts

---

## 12. Browser Compatibility Testing

### Modern Browsers
- [ ] Chrome 90+ (latest features)
- [ ] Firefox 88+ (Zustand persist)
- [ ] Safari 14+ (localStorage)
- [ ] Edge 90+ (full compatibility)

### Mobile Browsers
- [ ] Chrome Mobile (Android)
- [ ] Safari Mobile (iOS)
- [ ] Samsung Internet
- [ ] Opera Mobile

### Features to Test
- [ ] localStorage API support
- [ ] CSS Grid/Flexbox layout
- [ ] Framer Motion animations
- [ ] ES6+ JavaScript features

---

## 13. Security Testing

### Data Validation
- [ ] Quantity cannot be negative
- [ ] Price cannot be tampered in localStorage
- [ ] Product IDs validated
- [ ] XSS protection in product names

### localStorage Security
- [ ] Sensitive data not stored (tokens, passwords)
- [ ] Cart data schema validated on hydration
- [ ] Malformed JSON handled gracefully
- [ ] Size limits respected

---

## Test Execution Checklist

### Before Testing
- [ ] Clear browser cache
- [ ] Clear localStorage
- [ ] Open browser DevTools
- [ ] Enable React DevTools

### During Testing
- [ ] Check console for errors
- [ ] Monitor network tab
- [ ] Verify localStorage updates
- [ ] Watch Zustand state in React DevTools

### After Testing
- [ ] Document any bugs found
- [ ] Screenshot visual issues
- [ ] Log console errors
- [ ] Note performance metrics

---

## Expected Results Summary

### Functional Requirements ✅
- [x] Add products to cart
- [x] Update quantities
- [x] Remove items
- [x] Persist across reloads
- [x] Calculate Colombian IVA (19%)
- [x] Calculate shipping costs
- [x] Navigate to checkout

### Non-Functional Requirements ✅
- [x] Fast response times (< 500ms)
- [x] Smooth animations (60fps)
- [x] Mobile responsive
- [x] Accessible (WCAG AA)
- [x] Colombian localization
- [x] Browser compatible

---

## Bugs/Issues Tracking Template

```markdown
### Issue #XXX: [Title]
**Severity**: Critical / High / Medium / Low
**Browser**: Chrome 120 / Firefox 115 / etc.
**Device**: Desktop / Mobile / Tablet

**Steps to Reproduce**:
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happens]

**Screenshots**:
[Attach if applicable]

**Console Errors**:
```
[Paste console output]
```

**Possible Fix**:
[Suggestions if any]
```

---

## Sign-Off

- [ ] All critical tests passed
- [ ] All high-priority tests passed
- [ ] Medium/low issues documented
- [ ] Performance acceptable
- [ ] Accessibility compliant
- [ ] Ready for production

**Tested By**: _______________
**Date**: _______________
**Approval**: _______________
