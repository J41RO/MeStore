import React, { useState } from 'react';
import { UserFilters as UserFiltersType } from '../../services/superuserService';

interface UserFiltersProps {
  filters: UserFiltersType;
  onFiltersChange: (filters: UserFiltersType) => void;
  onReset: () => void;
  userCounts?: {
    total: number;
    active: number;
    inactive: number;
    verified: number;
    unverified: number;
    buyers: number;
    vendors: number;
    admins: number;
    superusers: number;
  };
}

const UserFilters: React.FC<UserFiltersProps> = ({
  filters,
  onFiltersChange,
  onReset,
  userCounts,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [localFilters, setLocalFilters] = useState<UserFiltersType>(filters);

  const handleFilterChange = (key: keyof UserFiltersType, value: any) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleReset = () => {
    const emptyFilters = {};
    setLocalFilters(emptyFilters);
    onFiltersChange(emptyFilters);
    onReset();
  };

  const getActiveFiltersCount = () => {
    return Object.values(localFilters).filter(value =>
      value !== undefined && value !== '' && value !== null
    ).length;
  };

  const activeFiltersCount = getActiveFiltersCount();

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      {/* Filter Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <h3 className="text-lg font-medium text-gray-900">User Filters</h3>
            {activeFiltersCount > 0 && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {activeFiltersCount} filter{activeFiltersCount !== 1 ? 's' : ''} active
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {activeFiltersCount > 0 && (
              <button
                onClick={handleReset}
                className="text-sm text-gray-500 hover:text-gray-700 px-3 py-1 rounded-md hover:bg-gray-100"
              >
                Clear All
              </button>
            )}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-800"
            >
              <span>{isExpanded ? 'Less Filters' : 'More Filters'}</span>
              <span className="transform transition-transform duration-200" style={{
                transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)'
              }}>
                ↓
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Quick Filters */}
      <div className="px-6 py-4">
        <div className="flex flex-wrap gap-3">
          {/* User Type Filter */}
          <div className="flex-1 min-w-48">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              User Type
            </label>
            <select
              value={localFilters.user_type || ''}
              onChange={(e) => handleFilterChange('user_type', e.target.value || undefined)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="">All Types</option>
              <option value="BUYER">🛒 Buyers {userCounts && `(${userCounts.buyers})`}</option>
              <option value="VENDOR">🏪 Vendors {userCounts && `(${userCounts.vendors})`}</option>
              <option value="ADMIN">⚙ Admins {userCounts && `(${userCounts.admins})`}</option>
              <option value="SUPERUSER">👑 Superusers {userCounts && `(${userCounts.superusers})`}</option>
            </select>
          </div>

          {/* Status Filter */}
          <div className="flex-1 min-w-40">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={localFilters.is_active === undefined ? '' : localFilters.is_active.toString()}
              onChange={(e) => handleFilterChange('is_active',
                e.target.value === '' ? undefined : e.target.value === 'true'
              )}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="">All Status</option>
              <option value="true">✅ Active {userCounts && `(${userCounts.active})`}</option>
              <option value="false">❌ Inactive {userCounts && `(${userCounts.inactive})`}</option>
            </select>
          </div>

          {/* Verification Filter */}
          <div className="flex-1 min-w-40">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Verification
            </label>
            <select
              value={localFilters.is_verified === undefined ? '' : localFilters.is_verified.toString()}
              onChange={(e) => handleFilterChange('is_verified',
                e.target.value === '' ? undefined : e.target.value === 'true'
              )}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="">All Verification</option>
              <option value="true">🔒 Verified {userCounts && `(${userCounts.verified})`}</option>
              <option value="false">⏳ Unverified {userCounts && `(${userCounts.unverified})`}</option>
            </select>
          </div>

          {/* Search Input */}
          <div className="flex-1 min-w-64">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <span className="text-gray-400">🔍</span>
              </div>
              <input
                type="text"
                value={localFilters.search || ''}
                onChange={(e) => handleFilterChange('search', e.target.value || undefined)}
                placeholder="Search by name, email, ID..."
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
              {localFilters.search && (
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <button
                    onClick={() => handleFilterChange('search', undefined)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Advanced Filters (Expandable) */}
      {isExpanded && (
        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Date Range Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Registration Date From
              </label>
              <input
                type="date"
                value={localFilters.date_from || ''}
                onChange={(e) => handleFilterChange('date_from', e.target.value || undefined)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Registration Date To
              </label>
              <input
                type="date"
                value={localFilters.date_to || ''}
                onChange={(e) => handleFilterChange('date_to', e.target.value || undefined)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            {/* Security Level Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Security Clearance Level
              </label>
              <select
                value={localFilters.security_clearance_level || ''}
                onChange={(e) => handleFilterChange('security_clearance_level',
                  e.target.value ? parseInt(e.target.value) : undefined
                )}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">All Levels</option>
                <option value="1">Level 1 (Standard)</option>
                <option value="2">Level 2 (Standard+)</option>
                <option value="3">Level 3 (Medium)</option>
                <option value="4">Level 4 (Medium+)</option>
                <option value="5">Level 5 (High)</option>
                <option value="6">Level 6 (High+)</option>
                <option value="7">Level 7 (Critical)</option>
              </select>
            </div>

            {/* Has Phone Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <select
                value={localFilters.has_phone === undefined ? '' : localFilters.has_phone.toString()}
                onChange={(e) => handleFilterChange('has_phone',
                  e.target.value === '' ? undefined : e.target.value === 'true'
                )}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">All</option>
                <option value="true">📞 Has Phone</option>
                <option value="false">No Phone</option>
              </select>
            </div>

            {/* Last Login Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Last Login
              </label>
              <select
                value={localFilters.last_login_period || ''}
                onChange={(e) => handleFilterChange('last_login_period', e.target.value || undefined)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Any Time</option>
                <option value="today">Today</option>
                <option value="week">Last 7 days</option>
                <option value="month">Last 30 days</option>
                <option value="never">Never logged in</option>
              </select>
            </div>

            {/* Email Domain Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Domain
              </label>
              <input
                type="text"
                value={localFilters.email_domain || ''}
                onChange={(e) => handleFilterChange('email_domain', e.target.value || undefined)}
                placeholder="e.g., @gmail.com"
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
          </div>

          {/* Filter Presets */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-2">Quick Filter Presets</h4>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => onFiltersChange({ user_type: 'VENDOR', is_active: true })}
                    className="px-3 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full hover:bg-green-200 transition-colors"
                  >
                    🏪 Active Vendors
                  </button>
                  <button
                    onClick={() => onFiltersChange({ user_type: 'BUYER', is_verified: false })}
                    className="px-3 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full hover:bg-yellow-200 transition-colors"
                  >
                    🛒 Unverified Buyers
                  </button>
                  <button
                    onClick={() => onFiltersChange({ user_type: 'ADMIN', security_clearance_level: 5 })}
                    className="px-3 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded-full hover:bg-purple-200 transition-colors"
                  >
                    ⚙ High Security Admins
                  </button>
                  <button
                    onClick={() => onFiltersChange({ is_active: false })}
                    className="px-3 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full hover:bg-red-200 transition-colors"
                  >
                    ❌ Inactive Users
                  </button>
                  <button
                    onClick={() => onFiltersChange({
                      date_from: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
                    })}
                    className="px-3 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full hover:bg-blue-200 transition-colors"
                  >
                    🆕 New This Week
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Active Filters Summary */}
      {activeFiltersCount > 0 && (
        <div className="px-6 py-3 bg-blue-50 border-t border-blue-200">
          <div className="flex items-center justify-between">
            <div className="flex flex-wrap gap-2">
              <span className="text-sm text-blue-900 font-medium">Active Filters:</span>
              {localFilters.user_type && (
                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                  Type: {localFilters.user_type}
                  <button
                    onClick={() => handleFilterChange('user_type', undefined)}
                    className="ml-1 text-blue-600 hover:text-blue-800"
                  >
                    ✕
                  </button>
                </span>
              )}
              {localFilters.is_active !== undefined && (
                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                  Status: {localFilters.is_active ? 'Active' : 'Inactive'}
                  <button
                    onClick={() => handleFilterChange('is_active', undefined)}
                    className="ml-1 text-blue-600 hover:text-blue-800"
                  >
                    ✕
                  </button>
                </span>
              )}
              {localFilters.is_verified !== undefined && (
                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                  Verification: {localFilters.is_verified ? 'Verified' : 'Unverified'}
                  <button
                    onClick={() => handleFilterChange('is_verified', undefined)}
                    className="ml-1 text-blue-600 hover:text-blue-800"
                  >
                    ✕
                  </button>
                </span>
              )}
              {localFilters.search && (
                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                  Search: "{localFilters.search}"
                  <button
                    onClick={() => handleFilterChange('search', undefined)}
                    className="ml-1 text-blue-600 hover:text-blue-800"
                  >
                    ✕
                  </button>
                </span>
              )}
              {(localFilters.date_from || localFilters.date_to) && (
                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                  Date Range
                  <button
                    onClick={() => {
                      handleFilterChange('date_from', undefined);
                      handleFilterChange('date_to', undefined);
                    }}
                    className="ml-1 text-blue-600 hover:text-blue-800"
                  >
                    ✕
                  </button>
                </span>
              )}
            </div>
            <button
              onClick={handleReset}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              Clear All Filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserFilters;