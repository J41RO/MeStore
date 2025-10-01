import { Routes, Route, Navigate } from 'react-router-dom';
import TestImageUpload from './pages/TestImageUpload';
import TestInventory from './pages/TestInventory';
import TestStockMovements from './pages/TestStockMovements';
import { lazy, Suspense } from 'react';
import Layout from './components/Layout';
import AuthGuard from './components/AuthGuard';
import RoleGuard from './components/RoleGuard';
import { UserType } from './stores/authStore';
import ErrorBoundary from './components/ErrorBoundary';
import PageLoader from './components/ui/Loading/PageLoader';
import LandingPage from './pages/LandingPage';
import MarketplaceHome from './pages/MarketplaceHome';
import './App.css';

// Lazy loading de páginas principales
const Dashboard = lazy(() => import('./pages/Dashboard'));
const VendorDashboard = lazy(() => import('./components/dashboard/VendorDashboard'));
const DashboardLayout = lazy(() => import('./components/DashboardLayout'));
const AdminLayout = lazy(() => import('./components/AdminLayout'));
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'));
const UserManagement = lazy(() => import('./pages/admin/UserManagement'));
const AlertasIncidentes = lazy(() => import('./pages/admin/AlertasIncidentes'));
const MovementTrackerPage = lazy(() => import('./pages/admin/MovementTracker'));
const ReportesDiscrepanciasPage = lazy(() => import('./pages/admin/ReportesDiscrepancias'));
const IncomingProductsQueuePage = lazy(() => import('./pages/admin/IncomingProductsQueuePage'));
const SystemConfig = lazy(() => import('./pages/admin/SystemConfig'));
const PublicCatalog = lazy(() => import('./pages/PublicCatalog'));

// Enterprise Navigation Pages - Users Category
const UsersPage = lazy(() => import('./pages/admin/users/UsersPage'));
const RolesPage = lazy(() => import('./pages/admin/users/RolesPage'));
const UserRegistrationPage = lazy(() => import('./pages/admin/users/UserRegistrationPage'));
const AuthenticationLogsPage = lazy(() => import('./pages/admin/users/AuthenticationLogsPage'));

// Enterprise Navigation Pages - Vendors Category
const VendorsPage = lazy(() => import('./pages/admin/vendors/VendorsPage'));
const VendorApplicationsPage = lazy(() => import('./pages/admin/vendors/VendorApplicationsPage'));
const VendorProductsPage = lazy(() => import('./pages/admin/vendors/VendorProductsPage'));
const VendorOrdersPage = lazy(() => import('./pages/admin/vendors/VendorOrdersPage'));
const VendorCommissionsPage = lazy(() => import('./pages/admin/vendors/VendorCommissionsPage'));
const ProductApprovalPage = lazy(() => import('./pages/admin/ProductApprovalPage'));

// Enterprise Navigation Pages - Analytics Category
const AnalyticsDashboard = lazy(() => import('./pages/admin/analytics/AnalyticsDashboard'));
const SalesReportsPage = lazy(() => import('./pages/admin/analytics/SalesReportsPage'));
const FinancialReportsPage = lazy(() => import('./pages/admin/analytics/FinancialReportsPage'));
const PerformanceMetricsPage = lazy(() => import('./pages/admin/analytics/PerformanceMetricsPage'));
const CustomReportsPage = lazy(() => import('./pages/admin/analytics/CustomReportsPage'));

// Enterprise Navigation Pages - Settings Category
const GeneralSettingsPage = lazy(() => import('./pages/admin/settings/GeneralSettingsPage'));
const SecuritySettingsPage = lazy(() => import('./pages/admin/settings/SecuritySettingsPage'));
const PaymentSettingsPage = lazy(() => import('./pages/admin/settings/PaymentSettingsPage'));
const NotificationSettingsPage = lazy(() => import('./pages/admin/settings/NotificationSettingsPage'));
const IntegrationsPage = lazy(() => import('./pages/admin/settings/IntegrationsPage'));
const WarehouseMap = lazy(() => import('./components/admin/WarehouseMap'));
const Productos = lazy(() => import('./pages/Productos'));
const VendorProfile = lazy(() => import('./pages/VendorProfile'));
const CommissionReport = lazy(
  () => import('./components/reports/CommissionReport')
);
const Login = lazy(() => import('./pages/Login'));
const AdminLogin = lazy(() => import('./pages/AdminLogin'));
const AdminPortal = lazy(() => import('./pages/AdminPortal'));
const NotFound = lazy(() => import('./pages/NotFound'));
const RegisterVendor = lazy(() => import('./pages/RegisterVendor'));
const VendorRegistration = lazy(() => import('./pages/VendorRegistration'));
const OTPVerification = lazy(() => import('./components/OTPVerification'));

// Componentes de auth con lazy loading
const OTPDemo = lazy(() => import('./components/OTPDemo'));
const VendorTest = lazy(() => import('./pages/VendorTest'));
const Marketplace = lazy(() => import('./pages/Marketplace'));
const AdminRestricted = lazy(() => import('./pages/AdminRestricted'));
const AdminRedirect = lazy(() => import('./components/AdminRedirect'));
const Unauthorized = lazy(() => import('./pages/Unauthorized'));
const InventoryAuditPanel = lazy(() => import('./components/admin/InventoryAuditPanel'));
const StorageManagerDashboard = lazy(() => import('./components/admin/StorageManagerDashboard'));
const SpaceOptimizerDashboard = lazy(() => import('./components/admin/SpaceOptimizerDashboard'));
const MarketplaceSearch = lazy(() => import('./pages/MarketplaceSearch'));
const CategoryPage = lazy(() => import('./pages/CategoryPage'));
const ProductDetail = lazy(() => import('./pages/ProductDetail'));
const ShoppingCart = lazy(() => import('./pages/ShoppingCart'));
const BuyerDashboard = lazy(() => import('./pages/BuyerDashboard'));
const BuyerProfile = lazy(() => import('./pages/BuyerProfile'));
// const BuyerOrders = lazy(() => import('./pages/BuyerOrders')); // Replaced by BuyerOrdersNew
const BuyerLayout = lazy(() => import('./components/BuyerLayout'));
const RoleBasedRedirect = lazy(() => import('./components/RoleBasedRedirect'));
const Checkout = lazy(() => import('./pages/Checkout'));
const CheckoutDemo = lazy(() => import('./pages/CheckoutDemo'));

// Order management pages - MICRO-FASE 4.3
const OrdersManagement = lazy(() => import('./pages/admin/OrdersManagement'));
const VendorOrders = lazy(() => import('./pages/VendorOrders'));
const BuyerOrdersNew = lazy(() => import('./pages/BuyerOrdersNew'));
const OrderTracking = lazy(() => import('./pages/OrderTracking'));

// Vendor management pages
const ProductsManagementPage = lazy(() => import('./pages/vendor/ProductsManagementPage'));

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        {/* Ruta principal pública - Nueva Landing Page */}
        <Route path='/' element={<LandingPage />} />
        
        {/* Ruta principal del marketplace */}
        <Route path="/marketplace" element={<MarketplaceHome />} />
        <Route path="/marketplace/home" element={<MarketplaceHome />} />
        <Route path="/marketplace/search" element={
          <Suspense fallback={<PageLoader />}>
            <MarketplaceSearch />
          </Suspense>
        } />

        {/* Public catalog route */}
        <Route path="/catalog" element={
          <Suspense fallback={<PageLoader />}>
            <PublicCatalog />
          </Suspense>
        } />
        <Route path="/productos" element={
          <Suspense fallback={<PageLoader />}>
            <PublicCatalog />
          </Suspense>
        } />

        <Route path="/marketplace/category/:slug" element={
          <Suspense fallback={<PageLoader />}>
            <CategoryPage />
          </Suspense>
        } />
        <Route path="/marketplace/product/:id" element={
          <Suspense fallback={<PageLoader />}>
            <ProductDetail />
          </Suspense>
        } />
        <Route path="/marketplace/cart" element={
          <Suspense fallback={<PageLoader />}>
            <ShoppingCart />
          </Suspense>
        } />
        <Route path="/checkout" element={
          <Suspense fallback={<PageLoader />}>
            <Checkout />
          </Suspense>
        } />

        {/* Checkout Demo */}
        <Route path="/checkout-demo" element={
          <Suspense fallback={<PageLoader />}>
            <CheckoutDemo />
          </Suspense>
        } />

        {/* Public Order Tracking */}
        <Route path="/track/:orderNumber" element={
          <Suspense fallback={<PageLoader />}>
            <OrderTracking />
          </Suspense>
        } />
        
        {/* Redirección de compatibilidad para dashboard directo - FIXED ROLE ROUTING */}
        <Route path='/dashboard' element={
          <AuthGuard>
            <Suspense fallback={<PageLoader />}>
              <RoleBasedRedirect />
            </Suspense>
          </AuthGuard>
        } />
        <Route path='/test-imageupload' element={<TestImageUpload />} />
        <Route path='/test-inventory' element={<TestInventory />} />
        <Route path='/test-stock-movements' element={<TestStockMovements />} />
        <Route path='/vendor-test' element={
          <Suspense fallback={<PageLoader />}>
            <VendorTest />
          </Suspense>
        } />

        {/* Portal Admin Corporativo - Página de presentación */}
        <Route
          path="/admin-portal"
          element={
            <Suspense fallback={<PageLoader />}>
              <AdminPortal />
            </Suspense>
          }
        />

        {/* Ruta del Marketplace Original para compradores autenticados */}
        <Route
          path='/marketplace/app'
          element={
            <AuthGuard requiredRoles={[UserType.BUYER, UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER]}>
              <Suspense fallback={<PageLoader />}>
                <Marketplace />
              </Suspense>
            </AuthGuard>
          }
        />

        {/* Rutas protegidas con Layout */}
        <Route
          path='/app'
          element={
            <AuthGuard>
              <Layout />
            </AuthGuard>
          }
        >
          <Route index element={
            <Suspense fallback={<PageLoader />}>
              <RoleBasedRedirect />
            </Suspense>
          } />
          
          {/* Dashboard principal para COMPRADORES */}
          <Route
            path='dashboard'
            element={
              <RoleGuard roles={[UserType.BUYER]} strategy="exact">
                <Suspense fallback={<PageLoader />}>
                  <BuyerLayout>
                    <BuyerDashboard />
                  </BuyerLayout>
                </Suspense>
              </RoleGuard>
            }
          />

          {/* Dashboard para VENDEDORES y superiores */}
          <Route
            path='vendor-dashboard'
            element={
              <RoleGuard roles={[UserType.VENDOR]} strategy="minimum">
                <Suspense fallback={<PageLoader />}>
                  <DashboardLayout>
                    <VendorDashboard />
                  </DashboardLayout>
                </Suspense>
              </RoleGuard>
            }
          />
          <Route
            path='productos'
            element={
              <RoleGuard roles={[UserType.VENDOR]} strategy="minimum">
                <Suspense fallback={<PageLoader />}>
                  <DashboardLayout>
                    <Productos />
                  </DashboardLayout>
                </Suspense>
              </RoleGuard>
            }
          />
          <Route
            path='vendor/products'
            element={
              <RoleGuard roles={[UserType.VENDOR]} strategy="minimum">
                <Suspense fallback={<PageLoader />}>
                  <ProductsManagementPage />
                </Suspense>
              </RoleGuard>
            }
          />
          <Route
            path='ordenes'
            element={
              <RoleGuard roles={[UserType.VENDOR]} strategy="minimum">
                <Suspense fallback={<PageLoader />}>
                  <DashboardLayout>
                    <VendorOrders />
                  </DashboardLayout>
                </Suspense>
              </RoleGuard>
            }
          />
          <Route
            path='reportes'
            element={
              <RoleGuard roles={[UserType.VENDOR]} strategy="minimum">
                <Suspense fallback={<PageLoader />}>
                  <DashboardLayout>
                    <div className="p-6">
                      <h1 className="text-2xl font-bold text-gray-900 mb-6">Reportes</h1>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-white rounded-lg shadow p-6">
                          <h3 className="text-lg font-semibold text-gray-900 mb-2">Reportes Disponibles</h3>
                          <div className="space-y-2">
                            <a href="/app/reportes/comisiones" className="block text-blue-600 hover:text-blue-800">
                              📊 Reporte de Comisiones
                            </a>
                            <p className="text-sm text-gray-500">Más reportes próximamente...</p>
                          </div>
                        </div>
                        <div className="bg-white rounded-lg shadow p-6">
                          <h3 className="text-lg font-semibold text-gray-900 mb-2">Estadísticas</h3>
                          <p className="text-gray-600">Análisis detallado de ventas y performance</p>
                        </div>
                      </div>
                    </div>
                  </DashboardLayout>
                </Suspense>
              </RoleGuard>
            }
          />
          <Route
            path='reportes/comisiones'
            element={
              <RoleGuard roles={[UserType.VENDOR]} strategy="minimum">
                <Suspense fallback={<PageLoader />}>
                  <DashboardLayout>
                    <CommissionReport />
                  </DashboardLayout>
                </Suspense>
              </RoleGuard>
            }
          />
          <Route
            path='perfil'
            element={
              <RoleGuard roles={[UserType.VENDOR]} strategy="minimum">
                <Suspense fallback={<PageLoader />}>
                  <DashboardLayout>
                    <VendorProfile />
                  </DashboardLayout>
                </Suspense>
              </RoleGuard>
            }
          />

          {/* Rutas específicas para COMPRADORES */}
          <Route
            path='mi-perfil'
            element={
              <RoleGuard roles={[UserType.BUYER]} strategy="exact">
                <Suspense fallback={<PageLoader />}>
                  <BuyerLayout>
                    <BuyerProfile />
                  </BuyerLayout>
                </Suspense>
              </RoleGuard>
            }
          />
          <Route
            path='mis-compras'
            element={
              <RoleGuard roles={[UserType.BUYER]} strategy="exact">
                <Suspense fallback={<PageLoader />}>
                  <BuyerLayout>
                    <BuyerOrdersNew />
                  </BuyerLayout>
                </Suspense>
              </RoleGuard>
            }
          />
        </Route>

        {/* Rutas públicas de autenticación */}
        <Route
          path='/auth/login'
          element={
            <Suspense fallback={<PageLoader />}>
              <Login />
            </Suspense>
          }
        />
        <Route
          path='/login'
          element={
            <Suspense fallback={<PageLoader />}>
              <Login />
            </Suspense>
          }
        />
        <Route
          path='/register'
          element={
            <Suspense fallback={<PageLoader />}>
              <RegisterVendor />
            </Suspense>
          }
        />
        <Route
          path='/vendor/register'
          element={
            <Suspense fallback={<PageLoader />}>
              <VendorRegistration />
            </Suspense>
          }
        />
        <Route
          path='/verify-otp'
          element={
            <Suspense fallback={<PageLoader />}>
              <OTPVerification />
            </Suspense>
          }
        />
        <Route
          path='/auth/otp'
          element={
            <Suspense fallback={<PageLoader />}>
              <OTPDemo />
            </Suspense>
          }
        />

        {/* Admin original - INTELLIGENT REDIRECT FOR AUTHORIZED USERS */}
        <Route
          path='/admin/*'
          element={
            <Suspense fallback={<PageLoader />}>
              <AdminRedirect />
            </Suspense>
          }
        />

        {/* Ruta específica para login admin en subdominio */}
        <Route
          path="/admin-login"
          element={
            <Suspense fallback={<PageLoader />}>
              <AdminLogin />
            </Suspense>
          }
        />
        {/* Portal Admin Oculto - FUTURO SUBDOMAIN admin.mestocker.com */}
        {/* MIGRATION NOTE: Esta ruta será migrada a admin.mestocker.com en producción */}
        {/* Ver MIGRATION_TO_SUBDOMAIN.md para pasos completos de migración */}
        <Route
          path='/admin-secure-portal/*'
          element={
            <AuthGuard requiredRoles={[UserType.ADMIN, UserType.SUPERUSER]} unauthorizedPath="/unauthorized">
              <Suspense fallback={<PageLoader />}>
                <AdminLayout>
                  <Routes>
                    {/* Default route - redirect to analytics dashboard */}
                    <Route index element={<Navigate to='analytics' replace />} />

                    {/* Legacy dashboard route */}
                    <Route path='dashboard' element={<AdminDashboard />} />

                    {/* USERS Category Routes */}
                    <Route path='users' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <UserManagement />
                      </RoleGuard>
                    } />
                    <Route path='roles' element={
                      <RoleGuard roles={[UserType.SUPERUSER]} strategy="exact">
                        <RolesPage />
                      </RoleGuard>
                    } />
                    <Route path='user-registration' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <UserRegistrationPage />
                      </RoleGuard>
                    } />
                    <Route path='auth-logs' element={
                      <RoleGuard roles={[UserType.SUPERUSER]} strategy="exact">
                        <AuthenticationLogsPage />
                      </RoleGuard>
                    } />

                    {/* VENDORS Category Routes */}
                    <Route path='vendors' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <VendorsPage />
                      </RoleGuard>
                    } />
                    <Route path='vendor-applications' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <VendorApplicationsPage />
                      </RoleGuard>
                    } />
                    <Route path='vendor-products' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <VendorProductsPage />
                      </RoleGuard>
                    } />
                    <Route path='product-approval' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <ProductApprovalPage />
                      </RoleGuard>
                    } />
                    <Route path='vendor-orders' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <VendorOrdersPage />
                      </RoleGuard>
                    } />
                    <Route path='vendor-commissions' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <VendorCommissionsPage />
                      </RoleGuard>
                    } />

                    {/* ANALYTICS Category Routes */}
                    <Route path='analytics' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <AnalyticsDashboard />
                      </RoleGuard>
                    } />
                    <Route path='sales-reports' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <SalesReportsPage />
                      </RoleGuard>
                    } />
                    <Route path='financial-reports' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <FinancialReportsPage />
                      </RoleGuard>
                    } />
                    <Route path='performance' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <PerformanceMetricsPage />
                      </RoleGuard>
                    } />
                    <Route path='custom-reports' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <CustomReportsPage />
                      </RoleGuard>
                    } />

                    {/* SETTINGS Category Routes */}
                    <Route path='system-config' element={
                      <RoleGuard roles={[UserType.SUPERUSER]} strategy="exact">
                        <GeneralSettingsPage />
                      </RoleGuard>
                    } />
                    <Route path='security' element={
                      <RoleGuard roles={[UserType.SUPERUSER]} strategy="exact">
                        <SecuritySettingsPage />
                      </RoleGuard>
                    } />
                    <Route path='database' element={
                      <RoleGuard roles={[UserType.SUPERUSER]} strategy="exact">
                        <PaymentSettingsPage />
                      </RoleGuard>
                    } />
                    <Route path='notifications' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <NotificationSettingsPage />
                      </RoleGuard>
                    } />
                    <Route path='integrations' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <IntegrationsPage />
                      </RoleGuard>
                    } />

                    {/* Legacy Routes - Keep for backward compatibility */}
                    <Route path='orders' element={<OrdersManagement />} />
                    <Route path='alertas-incidentes' element={<AlertasIncidentes />} />
                    <Route path='movement-tracker' element={<MovementTrackerPage />} />
                    <Route path='reportes-discrepancias' element={<ReportesDiscrepanciasPage />} />
                    <Route path='cola-productos-entrantes' element={<IncomingProductsQueuePage />} />
                    <Route path='warehouse-map' element={<WarehouseMap />} />
                    <Route path='auditoria' element={<InventoryAuditPanel />} />
                    <Route path='storage-manager' element={<StorageManagerDashboard />} />
                    <Route path='space-optimizer' element={<SpaceOptimizerDashboard />} />
                  </Routes>
                </AdminLayout>
              </Suspense>
            </AuthGuard>
          }
        />

        {/* Página de acceso denegado */}
        <Route
          path="/unauthorized"
          element={
            <Suspense fallback={<PageLoader />}>
              <Unauthorized />
            </Suspense>
          }
        />

        {/* Ruta 404 - DEBE IR AL FINAL */}
        <Route
          path='*'
          element={
            <Suspense fallback={<PageLoader />}>
              <NotFound />
            </Suspense>
          }
        />
      </Routes>
    </ErrorBoundary>
  );
}

export default App;