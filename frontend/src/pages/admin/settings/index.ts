/**
 * Admin Settings Pages Index
 */

export { default as GeneralSettingsPage } from './GeneralSettingsPage';
export { default as SecuritySettingsPage } from './SecuritySettingsPage';
export { default as PaymentSettingsPage } from './PaymentSettingsPage';
export { default as NotificationSettingsPage } from './NotificationSettingsPage';
export { default as IntegrationsPage } from './IntegrationsPage';

export const settingsPagesMetadata = {
  general: { path: '/admin-secure-portal/system-config', title: 'System Configuration', component: 'GeneralSettingsPage' },
  security: { path: '/admin-secure-portal/security', title: 'Security Settings', component: 'SecuritySettingsPage' },
  database: { path: '/admin-secure-portal/database', title: 'Database Management', component: 'PaymentSettingsPage' },
  notifications: { path: '/admin-secure-portal/notifications', title: 'Notifications', component: 'NotificationSettingsPage' },
  integrations: { path: '/admin-secure-portal/integrations', title: 'Integrations', component: 'IntegrationsPage' }
};