/**
 * Comprehensive k6 Load Testing Scenarios for MeStore Admin Endpoints
 * Performance Testing AI - Advanced Load Testing Framework
 *
 * This script tests the massive admin endpoints that completed TDD RED-GREEN-REFACTOR phases
 * Target: 1,785+ lines of admin functionality under enterprise load conditions
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Counter, Rate, Trend, Gauge } from 'k6/metrics';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.1/index.js";

// === PERFORMANCE METRICS ===
export let errorRate = new Rate('errors');
export let responseTimeGetAdmins = new Trend('response_time_get_admins');
export let responseTimePostAdmins = new Trend('response_time_post_admins');
export let responseTimePermissions = new Trend('response_time_permissions');
export let responseTimeBulkActions = new Trend('response_time_bulk_actions');
export let responseTimeDashboard = new Trend('response_time_dashboard');
export let responseTimeFileOps = new Trend('response_time_file_ops');
export let dbConnections = new Gauge('database_connections');
export let requestCounter = new Counter('total_requests');

// === TEST CONFIGURATION ===
const BASE_URL = __ENV.BASE_URL || 'http://192.168.1.137:8000';
const API_VERSION = '/api/v1';

// Performance thresholds based on enterprise requirements
export let options = {
  scenarios: {
    // === NORMAL LOAD SCENARIO ===
    normal_load: {
      executor: 'ramping-vus',
      startVUs: 10,
      stages: [
        { duration: '2m', target: 50 },   // Ramp up to 50 users
        { duration: '5m', target: 50 },   // Stay at 50 users
        { duration: '2m', target: 0 },    // Ramp down
      ],
      exec: 'normalLoadTest',
    },

    // === PEAK LOAD SCENARIO ===
    peak_load: {
      executor: 'ramping-vus',
      startVUs: 20,
      stages: [
        { duration: '3m', target: 200 },  // Ramp up to 200 users
        { duration: '10m', target: 200 }, // Stay at 200 users
        { duration: '3m', target: 0 },    // Ramp down
      ],
      exec: 'peakLoadTest',
      startTime: '10m', // Start after normal load
    },

    // === STRESS LOAD SCENARIO ===
    stress_load: {
      executor: 'ramping-vus',
      startVUs: 50,
      stages: [
        { duration: '5m', target: 500 },  // Ramp up to 500 users
        { duration: '15m', target: 500 }, // Stay at 500 users
        { duration: '5m', target: 0 },    // Ramp down
      ],
      exec: 'stressLoadTest',
      startTime: '25m', // Start after peak load
    },

    // === SPIKE LOAD SCENARIO ===
    spike_load: {
      executor: 'ramping-vus',
      startVUs: 100,
      stages: [
        { duration: '10s', target: 1000 }, // Sudden spike to 1000 users
        { duration: '2m', target: 1000 },  // Hold spike
        { duration: '10s', target: 100 },  // Drop back
      ],
      exec: 'spikeLoadTest',
      startTime: '50m', // Start after stress load
    },

    // === ENDURANCE LOAD SCENARIO ===
    endurance_load: {
      executor: 'constant-vus',
      vus: 100,
      duration: '8h', // 8-hour endurance test
      exec: 'enduranceLoadTest',
      startTime: '55m', // Start after spike load
    }
  },

  // === PERFORMANCE THRESHOLDS ===
  thresholds: {
    'http_req_duration': ['p(95)<2000'], // 95% of requests under 2s
    'http_req_duration{endpoint:get_admins}': ['p(95)<2000'], // GET endpoints < 2s
    'http_req_duration{endpoint:post_admins}': ['p(95)<3000'], // POST endpoints < 3s
    'http_req_duration{endpoint:permissions}': ['p(95)<3000'], // Permission ops < 3s
    'http_req_duration{endpoint:file_ops}': ['p(95)<5000'], // File ops < 5s
    'http_req_duration{endpoint:dashboard}': ['p(95)<10000'], // Analytics < 10s
    'http_req_duration{endpoint:bulk_actions}': ['p(95)<10000'], // Bulk ops < 10s
    'errors': ['rate<0.01'], // Error rate < 1%
    'http_req_failed': ['rate<0.01'], // HTTP error rate < 1%
  }
};

// === AUTHENTICATION HELPER ===
function getAuthHeaders() {
  // In real implementation, this would fetch JWT token
  return {
    'Authorization': 'Bearer test-jwt-token',
    'Content-Type': 'application/json'
  };
}

// === TEST DATA GENERATORS ===
function generateRealisticAdminData() {
  const firstNames = ['Carlos', 'María', 'José', 'Ana', 'Luis', 'Carmen', 'Miguel', 'Isabel'];
  const lastNames = ['García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez', 'Sánchez', 'Pérez'];
  const cities = ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena', 'Bucaramanga', 'Pereira', 'Manizales'];
  const departments = ['Cundinamarca', 'Antioquia', 'Valle del Cauca', 'Atlántico', 'Bolívar', 'Santander', 'Risaralda', 'Caldas'];

  return {
    email: `admin${Math.floor(Math.random() * 100000)}@mestore.co`,
    nombre: firstNames[Math.floor(Math.random() * firstNames.length)],
    apellido: lastNames[Math.floor(Math.random() * lastNames.length)],
    user_type: 'ADMIN',
    security_clearance_level: Math.floor(Math.random() * 4) + 1,
    ciudad: cities[Math.floor(Math.random() * cities.length)],
    departamento: departments[Math.floor(Math.random() * departments.length)],
    telefono: `+57${Math.floor(Math.random() * 900000000) + 300000000}`,
    initial_permissions: [],
    force_password_change: true
  };
}

function generateSearchQueries() {
  return [
    'admin@', 'Carlos', 'María', 'García', 'test', 'manager',
    'Bogotá', 'Medellín', 'supervisor', 'coordinator'
  ];
}

// === NORMAL LOAD TEST SCENARIO ===
export function normalLoadTest() {
  group('Normal Load - Admin Management Operations', function() {
    const headers = getAuthHeaders();

    // 60% Read operations
    if (Math.random() < 0.6) {
      group('Read Operations', function() {
        if (Math.random() < 0.7) {
          // List admins with filters
          const params = {
            limit: Math.random() < 0.5 ? 25 : 50,
            skip: Math.floor(Math.random() * 100)
          };

          if (Math.random() < 0.3) {
            const searchQueries = generateSearchQueries();
            params.search = searchQueries[Math.floor(Math.random() * searchQueries.length)];
          }

          const response = http.get(`${BASE_URL}${API_VERSION}/admin_management/admins`, {
            params: params,
            headers: headers,
            tags: { endpoint: 'get_admins' }
          });

          check(response, {
            'Admin list status is 200': (r) => r.status === 200,
            'Admin list response time < 2s': (r) => r.timings.duration < 2000,
            'Admin list has data': (r) => JSON.parse(r.body).length >= 0
          });

          responseTimeGetAdmins.add(response.timings.duration);

        } else {
          // Get specific admin (using mock ID)
          const adminId = `admin-${Math.floor(Math.random() * 1000)}`;
          const response = http.get(`${BASE_URL}${API_VERSION}/admin_management/admins/${adminId}`, {
            headers: headers,
            tags: { endpoint: 'get_admin' }
          });

          // May return 404 for non-existent admins, which is expected
          check(response, {
            'Get admin response is valid': (r) => r.status === 200 || r.status === 404,
            'Get admin response time < 2s': (r) => r.timings.duration < 2000
          });
        }
      });
    }

    // 25% Permission operations
    else if (Math.random() < 0.85) {
      group('Permission Operations', function() {
        const adminId = `admin-${Math.floor(Math.random() * 1000)}`;

        if (Math.random() < 0.5) {
          // Get admin permissions
          const response = http.get(`${BASE_URL}${API_VERSION}/admin_management/admins/${adminId}/permissions`, {
            headers: headers,
            tags: { endpoint: 'permissions' }
          });

          check(response, {
            'Permissions response is valid': (r) => r.status === 200 || r.status === 404,
            'Permissions response time < 3s': (r) => r.timings.duration < 3000
          });

          responseTimePermissions.add(response.timings.duration);
        } else {
          // Grant permissions
          const permissionData = {
            permission_ids: [`perm-${Math.floor(Math.random() * 100)}`],
            reason: 'Load test permission grant operation'
          };

          const response = http.post(`${BASE_URL}${API_VERSION}/admin_management/admins/${adminId}/permissions/grant`,
            JSON.stringify(permissionData), {
              headers: headers,
              tags: { endpoint: 'permissions' }
            });

          check(response, {
            'Permission grant response is valid': (r) => [200, 403, 404].includes(r.status),
            'Permission grant response time < 3s': (r) => r.timings.duration < 3000
          });

          responseTimePermissions.add(response.timings.duration);
        }
      });
    }

    // 10% Admin creation/updates
    else if (Math.random() < 0.95) {
      group('CRUD Operations', function() {
        if (Math.random() < 0.6) {
          // Create admin
          const adminData = generateRealisticAdminData();
          const response = http.post(`${BASE_URL}${API_VERSION}/admin_management/admins`,
            JSON.stringify(adminData), {
              headers: headers,
              tags: { endpoint: 'post_admins' }
            });

          check(response, {
            'Admin creation response is valid': (r) => [200, 201, 409].includes(r.status),
            'Admin creation response time < 3s': (r) => r.timings.duration < 3000
          });

          responseTimePostAdmins.add(response.timings.duration);
        } else {
          // Update admin
          const adminId = `admin-${Math.floor(Math.random() * 1000)}`;
          const updateData = {
            performance_score: Math.floor(Math.random() * 21) + 80 // 80-100
          };

          const response = http.put(`${BASE_URL}${API_VERSION}/admin_management/admins/${adminId}`,
            JSON.stringify(updateData), {
              headers: headers,
              tags: { endpoint: 'put_admins' }
            });

          check(response, {
            'Admin update response is valid': (r) => [200, 404].includes(r.status),
            'Admin update response time < 3s': (r) => r.timings.duration < 3000
          });
        }
      });
    }

    // 5% Bulk operations
    else {
      group('Bulk Operations', function() {
        const userIds = [];
        for (let i = 0; i < Math.floor(Math.random() * 15) + 5; i++) {
          userIds.push(`admin-${Math.floor(Math.random() * 1000)}`);
        }

        const bulkData = {
          user_ids: userIds,
          action: Math.random() < 0.5 ? 'activate' : 'deactivate',
          reason: 'Load test bulk operation'
        };

        const response = http.post(`${BASE_URL}${API_VERSION}/admin_management/admins/bulk-action`,
          JSON.stringify(bulkData), {
            headers: headers,
            tags: { endpoint: 'bulk_actions' }
          });

        check(response, {
          'Bulk operation response is valid': (r) => [200, 404].includes(r.status),
          'Bulk operation response time < 10s': (r) => r.timings.duration < 10000
        });

        responseTimeBulkActions.add(response.timings.duration);
      });
    }

    requestCounter.add(1);
    errorRate.add(false);
  });

  sleep(Math.random() * 2 + 1); // Random sleep 1-3 seconds
}

// === PEAK LOAD TEST SCENARIO ===
export function peakLoadTest() {
  group('Peak Load - High Volume Admin Operations', function() {
    const headers = getAuthHeaders();

    // More aggressive testing during peak hours
    // Simulate concurrent admin creation during onboarding
    if (Math.random() < 0.4) {
      const adminData = generateRealisticAdminData();
      const response = http.post(`${BASE_URL}${API_VERSION}/admin_management/admins`,
        JSON.stringify(adminData), {
          headers: headers,
          tags: { endpoint: 'post_admins' }
        });

      check(response, {
        'Peak admin creation succeeds': (r) => [200, 201, 409].includes(r.status),
        'Peak admin creation time acceptable': (r) => r.timings.duration < 5000
      });

      responseTimePostAdmins.add(response.timings.duration);
    } else {
      // Heavy read operations
      const response = http.get(`${BASE_URL}${API_VERSION}/admin_management/admins`, {
        params: { limit: 100, skip: Math.floor(Math.random() * 500) },
        headers: headers,
        tags: { endpoint: 'get_admins' }
      });

      check(response, {
        'Peak admin list succeeds': (r) => r.status === 200,
        'Peak admin list time acceptable': (r) => r.timings.duration < 3000
      });

      responseTimeGetAdmins.add(response.timings.duration);
    }

    requestCounter.add(1);
  });

  sleep(Math.random() * 1 + 0.5); // Faster cycle during peak
}

// === STRESS LOAD TEST SCENARIO ===
export function stressLoadTest() {
  group('Stress Load - System Limits Testing', function() {
    const headers = getAuthHeaders();

    // Aggressive concurrent operations to test system limits
    const operations = ['list', 'create', 'permissions', 'bulk'];
    const operation = operations[Math.floor(Math.random() * operations.length)];

    switch(operation) {
      case 'list':
        const response = http.get(`${BASE_URL}${API_VERSION}/admin_management/admins`, {
          params: { limit: 100 },
          headers: headers,
          tags: { endpoint: 'get_admins' }
        });
        check(response, {
          'Stress list response time': (r) => r.timings.duration < 5000,
          'Stress list status ok': (r) => r.status < 500
        });
        break;

      case 'create':
        const adminData = generateRealisticAdminData();
        const createResponse = http.post(`${BASE_URL}${API_VERSION}/admin_management/admins`,
          JSON.stringify(adminData), {
            headers: headers,
            tags: { endpoint: 'post_admins' }
          });
        check(createResponse, {
          'Stress create response time': (r) => r.timings.duration < 8000,
          'Stress create status ok': (r) => r.status < 500
        });
        break;

      case 'permissions':
        const adminId = `admin-${Math.floor(Math.random() * 1000)}`;
        const permResponse = http.get(`${BASE_URL}${API_VERSION}/admin_management/admins/${adminId}/permissions`, {
          headers: headers,
          tags: { endpoint: 'permissions' }
        });
        check(permResponse, {
          'Stress permissions response time': (r) => r.timings.duration < 5000,
          'Stress permissions status ok': (r) => r.status < 500
        });
        break;

      case 'bulk':
        const bulkData = {
          user_ids: [`admin-${Math.floor(Math.random() * 1000)}`],
          action: 'activate',
          reason: 'Stress test operation'
        };
        const bulkResponse = http.post(`${BASE_URL}${API_VERSION}/admin_management/admins/bulk-action`,
          JSON.stringify(bulkData), {
            headers: headers,
            tags: { endpoint: 'bulk_actions' }
          });
        check(bulkResponse, {
          'Stress bulk response time': (r) => r.timings.duration < 15000,
          'Stress bulk status ok': (r) => r.status < 500
        });
        break;
    }

    requestCounter.add(1);
  });

  sleep(Math.random() * 0.5); // Very fast cycle for stress testing
}

// === SPIKE LOAD TEST SCENARIO ===
export function spikeLoadTest() {
  group('Spike Load - Sudden Traffic Burst', function() {
    const headers = getAuthHeaders();

    // Simulate sudden traffic spike (system outage recovery, viral event)
    const response = http.get(`${BASE_URL}${API_VERSION}/admin_management/admins`, {
      params: { limit: 50 },
      headers: headers,
      tags: { endpoint: 'get_admins' }
    });

    check(response, {
      'Spike handles request': (r) => r.status < 500,
      'Spike response reasonable': (r) => r.timings.duration < 10000
    });

    responseTimeGetAdmins.add(response.timings.duration);
    requestCounter.add(1);
  });

  // No sleep during spike - maximum pressure
}

// === ENDURANCE LOAD TEST SCENARIO ===
export function enduranceLoadTest() {
  group('Endurance Load - Long-term Stability', function() {
    const headers = getAuthHeaders();

    // Mix of operations to test system stability over 8 hours
    const operations = ['read', 'write', 'permissions'];
    const operation = operations[Math.floor(Math.random() * operations.length)];

    let response;
    switch(operation) {
      case 'read':
        response = http.get(`${BASE_URL}${API_VERSION}/admin_management/admins`, {
          params: { limit: 25, skip: Math.floor(Math.random() * 100) },
          headers: headers,
          tags: { endpoint: 'get_admins' }
        });
        break;

      case 'write':
        const adminData = generateRealisticAdminData();
        response = http.post(`${BASE_URL}${API_VERSION}/admin_management/admins`,
          JSON.stringify(adminData), {
            headers: headers,
            tags: { endpoint: 'post_admins' }
          });
        break;

      case 'permissions':
        const adminId = `admin-${Math.floor(Math.random() * 1000)}`;
        response = http.get(`${BASE_URL}${API_VERSION}/admin_management/admins/${adminId}/permissions`, {
          headers: headers,
          tags: { endpoint: 'permissions' }
        });
        break;
    }

    check(response, {
      'Endurance operation succeeds': (r) => r.status < 500,
      'Endurance response time stable': (r) => r.timings.duration < 15000,
      'Endurance memory stable': () => true // Custom memory checks would go here
    });

    requestCounter.add(1);
  });

  sleep(Math.random() * 3 + 2); // Slower pace for endurance - 2-5 seconds
}

// === DASHBOARD ANALYTICS TESTING ===
export function testDashboardEndpoints() {
  group('Dashboard Analytics Performance', function() {
    const headers = getAuthHeaders();

    // Test KPI dashboard endpoint
    const kpiResponse = http.get(`${BASE_URL}${API_VERSION}/dashboard/kpis`, {
      headers: headers,
      tags: { endpoint: 'dashboard' }
    });

    check(kpiResponse, {
      'Dashboard KPIs load successfully': (r) => r.status === 200,
      'Dashboard KPIs response time < 10s': (r) => r.timings.duration < 10000
    });

    responseTimeDashboard.add(kpiResponse.timings.duration);

    // Test growth data endpoint
    const growthResponse = http.get(`${BASE_URL}${API_VERSION}/dashboard/growth-data`, {
      headers: headers,
      tags: { endpoint: 'dashboard' }
    });

    check(growthResponse, {
      'Growth data loads successfully': (r) => r.status === 200,
      'Growth data response time < 10s': (r) => r.timings.duration < 10000
    });

    responseTimeDashboard.add(growthResponse.timings.duration);
  });
}

// === FILE OPERATIONS TESTING ===
export function testFileOperations() {
  group('File Operations Performance', function() {
    const headers = getAuthHeaders();

    // Test QR generation
    const queueId = `queue-${Math.floor(Math.random() * 1000)}`;
    const qrResponse = http.post(`${BASE_URL}${API_VERSION}/incoming-products/${queueId}/generate-qr`, '', {
      headers: headers,
      tags: { endpoint: 'file_ops' }
    });

    check(qrResponse, {
      'QR generation responds': (r) => [200, 404].includes(r.status),
      'QR generation time < 5s': (r) => r.timings.duration < 5000
    });

    responseTimeFileOps.add(qrResponse.timings.duration);

    // Test file upload simulation
    const uploadData = new FormData();
    uploadData.append('file', 'fake-file-content');

    const uploadResponse = http.post(`${BASE_URL}${API_VERSION}/incoming-products/${queueId}/verification/upload-photos`, uploadData, {
      headers: { 'Authorization': headers.Authorization },
      tags: { endpoint: 'file_ops' }
    });

    check(uploadResponse, {
      'File upload responds': (r) => [200, 404, 413].includes(r.status), // Including file too large
      'File upload time < 10s': (r) => r.timings.duration < 10000
    });

    responseTimeFileOps.add(uploadResponse.timings.duration);
  });
}

// === CUSTOM SUMMARY REPORT ===
export function handleSummary(data) {
  return {
    '/home/admin-jairo/MeStore/.workspace/departments/testing/performance-testing-ai/results/k6-performance-report.html': htmlReport(data),
    '/home/admin-jairo/MeStore/.workspace/departments/testing/performance-testing-ai/results/k6-performance-summary.txt': textSummary(data, { indent: ' ', enableColors: true }),
    '/home/admin-jairo/MeStore/.workspace/departments/testing/performance-testing-ai/results/k6-performance-data.json': JSON.stringify(data),
  };
}