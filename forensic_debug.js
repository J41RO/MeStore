// 🕵️‍♂️ ANÁLISIS FORENSE - Script para inyectar en DevTools
// Copiar y pegar este código en la consola del navegador

console.log('🔬 INICIANDO ANÁLISIS FORENSE DEL SISTEMA DE AUTENTICACIÓN');

// 1. Verificar estado del localStorage
console.group('📦 ANÁLISIS DE LOCALSTORAGE');
console.log('auth_token:', localStorage.getItem('auth_token') ? '✅ PRESENTE' : '❌ AUSENTE');
console.log('refresh_token:', localStorage.getItem('refresh_token') ? '✅ PRESENTE' : '❌ AUSENTE');
console.log('auth-storage:', localStorage.getItem('auth-storage') ? '✅ PRESENTE' : '❌ AUSENTE');

if (localStorage.getItem('auth-storage')) {
    try {
        const authStorage = JSON.parse(localStorage.getItem('auth-storage'));
        console.log('📋 Contenido auth-storage:', authStorage);
        console.log('🔍 Usuario en storage:', authStorage?.state?.user);
        console.log('🎭 Rol en storage:', authStorage?.state?.user?.user_type);
        console.log('🔐 isAuthenticated en storage:', authStorage?.state?.isAuthenticated);
    } catch (e) {
        console.error('❌ Error parseando auth-storage:', e);
    }
}
console.groupEnd();

// 2. Verificar estado de Zustand (si es accesible)
console.group('🏪 ANÁLISIS DE ZUSTAND STORE');
try {
    // Intentar acceder al store de Zustand directamente
    const zustandStores = Object.keys(window).filter(key => key.includes('zustand') || key.includes('store'));
    console.log('🔍 Stores detectados:', zustandStores);
    
    // Verificar si hay un store global accesible
    if (window.__ZUSTAND__) {
        console.log('🏪 Zustand devtools detectado:', window.__ZUSTAND__);
    }
    
} catch (e) {
    console.log('⚠️ No se puede acceder directamente al store Zustand');
}
console.groupEnd();

// 3. Verificar enum UserType
console.group('🎭 ANÁLISIS DE ROLES');
// Intentar detectar el enum UserType desde el contexto global o React DevTools
console.log('🔍 Buscando definición de UserType...');

// Si está disponible en el contexto global
if (window.UserType) {
    console.log('✅ UserType encontrado en window:', window.UserType);
} else {
    console.log('⚠️ UserType no está en window, verificando valores esperados...');
    console.log('📝 Valores esperados:');
    console.log('   COMPRADOR = "COMPRADOR"');
    console.log('   VENDEDOR = "VENDEDOR"');
    console.log('   ADMIN = "ADMIN"');
    console.log('   SUPERUSER = "SUPERUSER"');
}
console.groupEnd();

// 4. Análisis de rutas
console.group('🛣️ ANÁLISIS DE RUTAS');
console.log('📍 Ubicación actual:', window.location.pathname);
console.log('🔍 Hash:', window.location.hash);
console.log('❓ Query params:', window.location.search);
console.groupEnd();

// 5. Interceptar React DevTools (si están disponibles)
console.group('⚛️ ANÁLISIS DE REACT DEVTOOLS');
if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
    console.log('✅ React DevTools detectado');
    console.log('🔍 Intentando encontrar componentes de autenticación...');
    
    // Función helper para buscar componentes
    window.findAuthComponents = () => {
        const hook = window.__REACT_DEVTOOLS_GLOBAL_HOOK__;
        if (hook?.renderers) {
            console.log('🔍 Renderizadores React:', Object.keys(hook.renderers));
        }
    };
    
    findAuthComponents();
} else {
    console.log('⚠️ React DevTools no detectado');
}
console.groupEnd();

// 6. Función para testear validación de roles
window.testRoleValidation = () => {
    console.group('🧪 TEST DE VALIDACIÓN DE ROLES');
    
    const authStorage = localStorage.getItem('auth-storage');
    if (!authStorage) {
        console.error('❌ No hay datos de autenticación');
        console.groupEnd();
        return;
    }
    
    try {
        const parsed = JSON.parse(authStorage);
        const userType = parsed?.state?.user?.user_type;
        
        console.log('👤 Usuario autenticado:', parsed?.state?.user?.email);
        console.log('🎭 Rol del usuario:', userType);
        console.log('🔐 Estado autenticado:', parsed?.state?.isAuthenticated);
        
        // Simular validación de RoleGuard para vendedor
        console.log('\n🔍 SIMULANDO VALIDACIÓN DE ROLEGUARD:');
        console.log('Ruta: /app/vendor-dashboard');
        console.log('Rol requerido: ["VENDEDOR"]');
        console.log('Estrategia: "minimum"');
        
        const roleHierarchy = {
            'COMPRADOR': 1,
            'VENDEDOR': 2,
            'ADMIN': 3,
            'SUPERUSER': 4
        };
        
        const userLevel = roleHierarchy[userType];
        const requiredLevel = roleHierarchy['VENDEDOR'];
        
        console.log(`👤 Nivel del usuario: ${userLevel} (${userType})`);
        console.log(`🎯 Nivel requerido: ${requiredLevel} (VENDEDOR)`);
        console.log(`✅ ¿Acceso permitido?: ${userLevel >= requiredLevel ? 'SÍ' : 'NO'}`);
        
    } catch (e) {
        console.error('❌ Error en test:', e);
    }
    
    console.groupEnd();
};

// 7. Función para forzar re-autenticación
window.forceReauth = () => {
    console.log('🔄 Forzando re-autenticación...');
    const event = new CustomEvent('auth:force-recheck');
    window.dispatchEvent(event);
};

// 8. Función para debug de RoleGuard
window.debugRoleGuard = () => {
    console.group('🛡️ DEBUG ROLEGUARD');
    
    // Buscar elementos con atributos de RoleGuard
    const roleGuardElements = document.querySelectorAll('[data-role-guard]');
    console.log(`🔍 Elementos RoleGuard encontrados: ${roleGuardElements.length}`);
    
    roleGuardElements.forEach((el, i) => {
        console.log(`Element ${i}:`, {
            element: el,
            roles: el.getAttribute('data-role-guard'),
            visible: el.style.display !== 'none'
        });
    });
    
    console.groupEnd();
};

console.log('\n🔬 ANÁLISIS FORENSE COMPLETADO');
console.log('📋 FUNCIONES DISPONIBLES:');
console.log('   testRoleValidation() - Probar validación de roles');
console.log('   forceReauth() - Forzar re-autenticación');
console.log('   debugRoleGuard() - Debug de componentes RoleGuard');
console.log('   findAuthComponents() - Buscar componentes de autenticación');

// Ejecutar test automático
testRoleValidation();