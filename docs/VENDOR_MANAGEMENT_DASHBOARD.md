# VENDOR MANAGEMENT DASHBOARD - QUICK START GUIDE

## Overview
The admin vendor management dashboard is now complete and ready for testing. This feature allows administrators to review and process pending vendor registration applications.

## Access Instructions

### 1. Start the Application

**Backend (Terminal 1)**:
```bash
cd /home/admin-jairo/MeStore
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (Terminal 2)**:
```bash
cd /home/admin-jairo/MeStore/frontend
npm run dev
```

### 2. Login as Admin

1. Navigate to: `http://localhost:5173`
2. Click "Portal Admin" in the footer
3. Click "Acceder al Sistema"
4. Login with credentials:
   - **Email**: `admin@mestocker.com`
   - **Password**: `Admin123456`

### 3. Access Vendor Management

Once logged in, navigate to:
```
http://localhost:5173/admin-secure-portal/vendor-management
```

## Dashboard Features

### Main View
- **Header**: Gradient orange-to-purple header with "Gestión de Vendedores Pendientes"
- **Vendor Table**: Professional table displaying all pending vendors
- **Loading State**: Spinner while fetching data
- **Empty State**: Friendly message when no pending vendors

### Vendor Information Displayed
- **Name/Display Name**: Full name (Natural) or Business name (Jurídica)
- **Email**: Contact email address
- **Phone**: Contact phone number
- **Type**: Natural or Jurídica with color-coded badge
- **ID**: Cédula (Natural) or NIT (Jurídica)
- **Address**: Fiscal address with city and department
- **Status**: Current vendor status (DRAFT, PENDING_DOCUMENTS, etc.)
- **Registration Date**: When the vendor registered

### Actions

#### Approve Vendor
1. Click green "Aprobar" button
2. Confirmation modal appears with vendor details
3. Review information
4. Click "Aprobar" to confirm or "Cancelar" to cancel
5. Success toast notification appears
6. Vendor is removed from pending list
7. Vendor receives approval email (background task)

#### Reject Vendor
1. Click red "Rechazar" button
2. Modal appears with rejection reason textarea
3. Enter reason (minimum 20 characters required)
4. Character counter shows progress
5. Green checkmark appears when valid
6. Click "Rechazar" to confirm or "Cancelar" to cancel
7. Success toast notification appears
8. Vendor is removed from pending list
9. Vendor receives rejection email with reason

## UI Components

### Vendor Table Columns
| Column | Content |
|--------|---------|
| Vendedor | Avatar, Name, Email, Phone |
| Tipo | Badge (Natural/Jurídica), ID number |
| Estado | Status badge with icon |
| Registro | Date, Location |
| Acciones | Approve/Reject buttons |

### Modal Features
- **Approve Modal**:
  - Green theme
  - Vendor summary
  - Confirm/Cancel buttons
  - Loading state with spinner

- **Reject Modal**:
  - Red theme
  - Reason textarea (20-500 characters)
  - Real-time validation
  - Character counter
  - Visual feedback (checkmark when valid)
  - Confirm/Cancel buttons
  - Loading state with spinner

### Toast Notifications
- **Position**: Top-right corner
- **Auto-dismiss**: 5 seconds
- **Animation**: Slide in from right
- **Types**:
  - Success (green) with checkmark icon
  - Error (red) with X icon

## API Endpoints Used

### GET `/api/v1/auth/admin/pending-sellers`
- Fetches list of all pending vendors
- Returns vendor details including:
  - Personal/business information
  - Contact details
  - Fiscal address
  - Registration date
  - Current status

### POST `/api/v1/auth/admin/approve-seller/{user_id}`
- Approves a vendor
- Changes status to APPROVED
- Activates vendor account
- Triggers approval email

### POST `/api/v1/auth/admin/reject-seller/{user_id}`
- Rejects a vendor with reason
- Changes status to REJECTED
- Stores rejection reason
- Triggers rejection email with reason

## Testing Scenarios

### Happy Path - Approve Vendor
1. Navigate to vendor management dashboard
2. View list of pending vendors
3. Click "Aprobar" on a vendor
4. Review vendor information in modal
5. Confirm approval
6. See success toast: "Vendedor {email} aprobado exitosamente"
7. Verify vendor removed from list
8. Verify vendor can now login (status APPROVED)

### Happy Path - Reject Vendor
1. Navigate to vendor management dashboard
2. View list of pending vendors
3. Click "Rechazar" on a vendor
4. Enter rejection reason: "La documentación proporcionada no cumple con los requisitos necesarios"
5. Verify character counter shows >=20
6. Confirm rejection
7. See success toast
8. Verify vendor removed from list

### Error Scenarios
1. **Network Error**: Shows error toast, list remains unchanged
2. **Short Rejection Reason**: Shows inline error "La razón debe tener al menos 20 caracteres"
3. **Empty List**: Shows "No hay vendedores pendientes" message
4. **Unauthorized Access**: Redirected to login (handled by AuthGuard)

## Design Highlights

### Color Scheme
- **Primary Gradient**: Orange (#f97316) to Purple (#9333ea)
- **Success**: Green (#10b981)
- **Error**: Red (#ef4444)
- **Warning**: Yellow (#f59e0b)
- **Info**: Blue (#3b82f6)

### Typography
- **Headers**: Bold, large (3xl)
- **Body**: Regular, readable (base)
- **Labels**: Medium weight, small (sm)

### Icons
- User icon for Natural person
- Building icon for Jurídica
- Clock icon for pending status
- Check icon for success
- X icon for rejection
- Mail, Phone, MapPin for contact info
- Calendar for dates

### Animations
- **Toast**: Slide in from right (0.3s ease-out)
- **Modal**: Scale in (0.2s ease-out)
- **Hover Effects**: Subtle background color change on table rows

## Responsive Design

### Desktop (>1024px)
- Full table layout
- All columns visible
- Spacious padding

### Tablet (768px - 1024px)
- Horizontal scroll for table
- Stacked modals
- Adjusted padding

### Mobile (<768px)
- Table scrolls horizontally
- Buttons stack vertically
- Full-width modals
- Touch-optimized targets

## Security Features

### Access Control
- **Protected Route**: Requires authentication
- **Role-Based**: Only OWNER, SUPERUSER, ADMIN can access
- **JWT Token**: Required in Authorization header

### Input Validation
- **Rejection Reason**: Min 20, max 500 characters
- **XSS Prevention**: Backend validates for dangerous patterns
- **SQL Injection**: Protected by ORM (SQLAlchemy)

### Rate Limiting
- **GET endpoint**: 30 requests/minute
- **POST endpoints**: 10 requests/minute

## Troubleshooting

### "Error al cargar vendedores pendientes"
- **Cause**: Backend not running or API error
- **Solution**: Check backend logs, verify server is running on port 8000

### "Privilegios administrativos requeridos"
- **Cause**: User doesn't have required role
- **Solution**: Login as admin@mestocker.com

### Vendor not appearing in list
- **Cause**: Vendor status not in [DRAFT, PENDING_DOCUMENTS, PENDING_APPROVAL]
- **Solution**: Check vendor.vendor_status in database

### Toast not dismissing
- **Cause**: JavaScript error in browser
- **Solution**: Check browser console for errors

### Modal not opening
- **Cause**: State management issue
- **Solution**: Refresh page, check React DevTools

## File Locations

### Frontend
- **Component**: `/frontend/src/pages/admin/VendorManagement.tsx`
- **Route**: Defined in `/frontend/src/App.tsx`
- **Styles**: Animations in `/frontend/src/App.css`

### Backend
- **Endpoints**: `/app/api/v1/endpoints/auth.py` (lines 2101-2400)
- **Models**: `/app/models/user.py`
- **Enums**: VendorStatus, UserType

### Documentation
- **Implementation Details**: `/.workspace/vendor-management-implementation.md`
- **This Guide**: `/VENDOR_MANAGEMENT_DASHBOARD.md`

## Next Steps

1. **Manual Testing**
   - Test approve workflow
   - Test reject workflow with various reasons
   - Test error scenarios
   - Verify email notifications

2. **Add to Navigation**
   - Add link in AdminLayout sidebar
   - Add to CategoryNavigation
   - Update navigation metadata

3. **Performance Testing**
   - Test with large vendor lists (100+ vendors)
   - Verify pagination needs
   - Measure API response times

4. **User Feedback**
   - Gather feedback from admin users
   - Identify UX improvements
   - Add requested features

5. **Documentation**
   - Add user manual
   - Create video tutorial
   - Update admin handbook

## Support

For issues or questions:
- **Agent**: react-specialist-ai
- **Documentation**: `.workspace/vendor-management-implementation.md`
- **Backend API Docs**: `http://localhost:8000/docs`

---

**Created**: 2025-10-13
**Status**: READY FOR TESTING ✅
**Access URL**: `http://localhost:5173/admin-secure-portal/vendor-management`
