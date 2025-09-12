import React from 'react';
import { UserType } from './stores/authStore';

// Test component to debug role logic
const TestRoleLogic: React.FC = () => {
  // Simulate the exact same logic as useRoleAccess
  const ROLE_HIERARCHY: Record<UserType, number> = {
    [UserType.COMPRADOR]: 1,
    [UserType.VENDEDOR]: 2,
    [UserType.ADMIN]: 3,
    [UserType.SUPERUSER]: 4,
  };

  // Test with VENDEDOR user
  const currentUserType = UserType.VENDEDOR;
  const currentRoleLevel = ROLE_HIERARCHY[currentUserType];

  // Test hasMinimumRole logic
  const testMinimumRole = (minimumRole: UserType): boolean => {
    const minimumLevel = ROLE_HIERARCHY[minimumRole];
    const result = currentRoleLevel >= minimumLevel;
    console.log(`Testing minimum role ${minimumRole}:`);
    console.log(`- Current role: ${currentUserType} (level ${currentRoleLevel})`);
    console.log(`- Required role: ${minimumRole} (level ${minimumLevel})`);
    console.log(`- Result: ${result}`);
    return result;
  };

  // Test hasRole logic (exact match)
  const testHasRole = (role: UserType): boolean => {
    const result = currentUserType === role;
    console.log(`Testing exact role ${role}:`);
    console.log(`- Current role: ${currentUserType}`);
    console.log(`- Required role: ${role}`);
    console.log(`- Result: ${result}`);
    return result;
  };

  React.useEffect(() => {
    console.log('=== ROLE LOGIC TEST ===');
    console.log('Current user type:', currentUserType);
    console.log('Current role level:', currentRoleLevel);
    console.log('');

    console.log('=== MINIMUM ROLE TESTS ===');
    testMinimumRole(UserType.COMPRADOR);
    testMinimumRole(UserType.VENDEDOR);
    testMinimumRole(UserType.ADMIN);
    testMinimumRole(UserType.SUPERUSER);
    console.log('');

    console.log('=== EXACT ROLE TESTS ===');
    testHasRole(UserType.COMPRADOR);
    testHasRole(UserType.VENDEDOR);
    testHasRole(UserType.ADMIN);
    testHasRole(UserType.SUPERUSER);
    console.log('');

    // Test the RoleGuard strategy logic
    console.log('=== ROLEGUARD STRATEGY SIMULATION ===');
    const roles = [UserType.VENDEDOR];
    const strategy = 'minimum';
    
    if (strategy === 'minimum') {
      if (roles.length !== 1) {
        console.log('ERROR: minimum strategy requires exactly one role');
      } else {
        const hasAccess = testMinimumRole(roles[0]!);
        console.log(`RoleGuard access result: ${hasAccess}`);
      }
    }
  }, []);

  return (
    <div className="p-4">
      <h1>Role Logic Test</h1>
      <p>Check console for test results</p>
      <p>Current User: {currentUserType} (Level {currentRoleLevel})</p>
    </div>
  );
};

export default TestRoleLogic;