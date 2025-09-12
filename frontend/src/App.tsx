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
const DashboardLayout = lazy(() => import('./components/DashboardLayout'));
const AdminLayout = lazy(() => import('./components/AdminLayout'));
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'));
const UserManagement = lazy(() => import('./pages/admin/UserManagement'));
const AlertasIncidentes = lazy(() => import('./pages/admin/AlertasIncidentes'));
const MovementTrackerPage = lazy(() => import('./pages/admin/MovementTracker'));
const ReportesDiscrepanciasPage = lazy(() => import('./pages/admin/ReportesDiscrepancias'));
const IncomingProductsQueuePage = lazy(() => import('./pages/admin/IncomingProductsQueuePage'));
const SystemConfig = lazy(() => import('./pages/admin/SystemConfig'));
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
const OTPVerification = lazy(() => import('./components/OTPVerification'));

// Componentes de auth con lazy loading
const OTPDemo = lazy(() => import('./components/OTPDemo'));
const VendorTest = lazy(() => import('./pages/VendorTest'));
const Marketplace = lazy(() => import('./pages/Marketplace'));
const AdminRestricted = lazy(() => import('./pages/AdminRestricted'));
const Unauthorized = lazy(() => import('./pages/Unauthorized'));
const InventoryAuditPanel = lazy(() => import('./components/admin/InventoryAuditPanel'));
const StorageManagerDashboard = lazy(() => import('./components/admin/StorageManagerDashboard'));
const SpaceOptimizerDashboard = lazy(() => import('./components/admin/SpaceOptimizerDashboard'));
const MarketplaceSearch = lazy(() => import('./pages/MarketplaceSearch'));
const ProductDetail = lazy(() => import('./pages/ProductDetail'));
const ShoppingCart = lazy(() => import('./pages/ShoppingCart'));
const BuyerDashboard = lazy(() => import('./pages/BuyerDashboard'));
const BuyerProfile = lazy(() => import('./pages/BuyerProfile'));
const BuyerOrders = lazy(() => import('./pages/BuyerOrders'));
const BuyerLayout = lazy(() => import('./components/BuyerLayout'));
const RoleBasedRedirect = lazy(() => import('./components/RoleBasedRedirect'));

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
        
        {/* Redirección de compatibilidad para dashboard directo */}
        <Route path='/dashboard' element={<Navigate to='/app/dashboard' replace />} />
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
            <AuthGuard requiredRoles={[UserType.COMPRADOR, UserType.VENDEDOR, UserType.ADMIN, UserType.SUPERUSER]}>
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
              <RoleGuard roles={[UserType.COMPRADOR]} strategy="exact">
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
              <RoleGuard roles={[UserType.VENDEDOR]} strategy="minimum">
                <Suspense fallback={<PageLoader />}>
                  <DashboardLayout>
                    <Dashboard />
                  </DashboardLayout>
                </Suspense>
              </RoleGuard>
            }
          />
          <Route
            path='productos'
            element={
              <RoleGuard roles={[UserType.VENDEDOR]} strategy="minimum">
                <Suspense fallback={<PageLoader />}>
                  <DashboardLayout>
                    <Productos />
                  </DashboardLayout>
                </Suspense>
              </RoleGuard>
            }
          />
          <Route
            path='ordenes'
            element={
              <RoleGuard roles={[UserType.VENDEDOR]} strategy="minimum">
                <Suspense fallback={<PageLoader />}>
                  <DashboardLayout>
                    <div className="p-6">
                      <h1 className="text-2xl font-bold text-gray-900 mb-6">Mis Órdenes</h1>
                      <div className="bg-white rounded-lg shadow p-6">
                        <p className="text-gray-600">Gestión de órdenes - En desarrollo</p>
                        <p className="text-sm text-gray-500 mt-2">
                          Esta sección permitirá ver y gestionar todas las órdenes de venta.
                        </p>
                      </div>
                    </div>
                  </DashboardLayout>
                </Suspense>
              </RoleGuard>
            }
          />
          <Route
            path='reportes'
            element={
              <RoleGuard roles={[UserType.VENDEDOR]} strategy="minimum">
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
              <RoleGuard roles={[UserType.VENDEDOR]} strategy="minimum">
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
              <RoleGuard roles={[UserType.VENDEDOR]} strategy="minimum">
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
              <RoleGuard roles={[UserType.COMPRADOR]} strategy="exact">
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
              <RoleGuard roles={[UserType.COMPRADOR]} strategy="exact">
                <Suspense fallback={<PageLoader />}>
                  <BuyerLayout>
                    <BuyerOrders />
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

        {/* Admin original - ACCESO RESTRINGIDO */}
        <Route
          path='/admin/*'
          element={
            <Suspense fallback={<PageLoader />}>
              <AdminRestricted />
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
                    <Route path='dashboard' element={<AdminDashboard />} />
                    <Route path='users' element={
                      <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any">
                        <UserManagement />
                      </RoleGuard>
                    } />
                    <Route path='alertas-incidentes' element={<AlertasIncidentes />} />
                    <Route path='movement-tracker' element={<MovementTrackerPage />} />
                    <Route path='reportes-discrepancias' element={<ReportesDiscrepanciasPage />} />
                    <Route path='cola-productos-entrantes' element={<IncomingProductsQueuePage />} />
                    <Route path='system-config' element={
                      <RoleGuard roles={[UserType.SUPERUSER]} strategy="exact">
                        <SystemConfig />
                      </RoleGuard>
                    } />
                    <Route path='warehouse-map' element={<WarehouseMap />} />
                    <Route path='auditoria' element={<InventoryAuditPanel />} />
                    <Route path='storage-manager' element={<StorageManagerDashboard />} />
                    <Route path='space-optimizer' element={<SpaceOptimizerDashboard />} />
                    <Route
                      index
                      element={<Navigate to='dashboard' replace />}
                    />
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