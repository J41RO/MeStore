'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Filter,
  Search,
  Download,
  PlayCircle,
  PauseCircle,
  AlertCircle,
  AlertTriangle,
  Info,
  Bug
} from 'lucide-react';
import { railwayClient, RailwayLog } from '@/lib/railway-client';

type LogLevel = 'ERROR' | 'WARNING' | 'INFO' | 'DEBUG' | 'ALL';

interface LogsPanelProps {
  refreshInterval?: number;
}

export default function LogsPanel({ refreshInterval = 5000 }: LogsPanelProps) {
  const [logs, setLogs] = useState<RailwayLog[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<RailwayLog[]>([]);
  const [selectedLevel, setSelectedLevel] = useState<LogLevel>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const logsContainerRef = useRef<HTMLDivElement>(null);

  // Fetch logs from Railway API
  const fetchLogs = async () => {
    if (isPaused) return;

    setIsLoading(true);
    try {
      const newLogs = await railwayClient.getLogs(100);
      setLogs(newLogs);
    } catch (error) {
      console.error('Error fetching logs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Initial fetch and interval setup
  useEffect(() => {
    fetchLogs();

    const interval = setInterval(fetchLogs, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval, isPaused]);

  // Filter logs based on level and search query
  useEffect(() => {
    let filtered = logs;

    // Filter by level
    if (selectedLevel !== 'ALL') {
      filtered = filtered.filter((log) => log.level === selectedLevel);
    }

    // Filter by search query (supports regex)
    if (searchQuery.trim()) {
      try {
        const regex = new RegExp(searchQuery, 'i');
        filtered = filtered.filter((log) =>
          regex.test(log.message) || regex.test(log.service)
        );
      } catch {
        // Fallback to simple string search if regex is invalid
        const query = searchQuery.toLowerCase();
        filtered = filtered.filter((log) =>
          log.message.toLowerCase().includes(query) ||
          log.service.toLowerCase().includes(query)
        );
      }
    }

    setFilteredLogs(filtered);
  }, [logs, selectedLevel, searchQuery]);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [filteredLogs, autoScroll]);

  // Export logs to CSV
  const exportToCSV = () => {
    const csvHeader = 'Timestamp,Level,Service,Message\n';
    const csvRows = filteredLogs
      .map((log) => {
        const timestamp = new Date(log.timestamp).toLocaleString();
        const message = log.message.replace(/"/g, '""'); // Escape quotes
        return `"${timestamp}","${log.level}","${log.service}","${message}"`;
      })
      .join('\n');

    const csvContent = csvHeader + csvRows;
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `logs-${Date.now()}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Get icon based on log level
  const getLogIcon = (level: RailwayLog['level']) => {
    switch (level) {
      case 'ERROR':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'WARNING':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'INFO':
        return <Info className="w-4 h-4 text-blue-500" />;
      case 'DEBUG':
        return <Bug className="w-4 h-4 text-gray-500" />;
      default:
        return <Info className="w-4 h-4 text-gray-500" />;
    }
  };

  // Get text color based on log level
  const getLogColor = (level: RailwayLog['level']) => {
    switch (level) {
      case 'ERROR':
        return 'text-red-500 dark:text-red-400';
      case 'WARNING':
        return 'text-yellow-500 dark:text-yellow-400';
      case 'INFO':
        return 'text-blue-500 dark:text-blue-400';
      case 'DEBUG':
        return 'text-gray-500 dark:text-gray-400';
      default:
        return 'text-gray-600 dark:text-gray-300';
    }
  };

  // Get background color for log level badge
  const getLevelBadgeColor = (level: RailwayLog['level']) => {
    switch (level) {
      case 'ERROR':
        return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300';
      case 'WARNING':
        return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300';
      case 'INFO':
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300';
      case 'DEBUG':
        return 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300';
      default:
        return 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400';
    }
  };

  // Count logs by level
  const logCounts = {
    ERROR: logs.filter((log) => log.level === 'ERROR').length,
    WARNING: logs.filter((log) => log.level === 'WARNING').length,
    INFO: logs.filter((log) => log.level === 'INFO').length,
    DEBUG: logs.filter((log) => log.level === 'DEBUG').length,
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            System Logs
          </h2>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsPaused(!isPaused)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title={isPaused ? 'Resume' : 'Pause'}
            >
              {isPaused ? (
                <PlayCircle className="w-5 h-5 text-green-500" />
              ) : (
                <PauseCircle className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              )}
            </button>
            <button
              onClick={exportToCSV}
              className="flex items-center gap-2 px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm"
              disabled={filteredLogs.length === 0}
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="space-y-3">
          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search logs (regex supported)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Level Filter Buttons */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedLevel('ALL')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                selectedLevel === 'ALL'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              All ({logs.length})
            </button>
            <button
              onClick={() => setSelectedLevel('ERROR')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                selectedLevel === 'ERROR'
                  ? 'bg-red-500 text-white'
                  : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 hover:bg-red-200 dark:hover:bg-red-900/50'
              }`}
            >
              Errors ({logCounts.ERROR})
            </button>
            <button
              onClick={() => setSelectedLevel('WARNING')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                selectedLevel === 'WARNING'
                  ? 'bg-yellow-500 text-white'
                  : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 hover:bg-yellow-200 dark:hover:bg-yellow-900/50'
              }`}
            >
              Warnings ({logCounts.WARNING})
            </button>
            <button
              onClick={() => setSelectedLevel('INFO')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                selectedLevel === 'INFO'
                  ? 'bg-blue-500 text-white'
                  : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-900/50'
              }`}
            >
              Info ({logCounts.INFO})
            </button>
            <button
              onClick={() => setSelectedLevel('DEBUG')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                selectedLevel === 'DEBUG'
                  ? 'bg-gray-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Debug ({logCounts.DEBUG})
            </button>
          </div>

          {/* Auto-scroll Toggle */}
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="w-4 h-4 text-blue-500 rounded focus:ring-2 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">
              Auto-scroll to latest
            </span>
          </label>
        </div>
      </div>

      {/* Logs Container */}
      <div
        ref={logsContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-2 font-mono text-sm"
      >
        {isLoading && logs.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            Loading logs...
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            No logs found matching your filters
          </div>
        ) : (
          filteredLogs.map((log, index) => (
            <div
              key={`${log.timestamp}-${index}`}
              className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-900/50 hover:bg-gray-100 dark:hover:bg-gray-900 transition-colors"
            >
              {/* Icon */}
              <div className="flex-shrink-0 mt-0.5">{getLogIcon(log.level)}</div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-semibold ${getLevelBadgeColor(
                      log.level
                    )}`}
                  >
                    {log.level}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(log.timestamp).toLocaleString()}
                  </span>
                  <span className="text-xs text-gray-400 dark:text-gray-500">
                    [{log.service}]
                  </span>
                </div>
                <p
                  className={`break-words ${getLogColor(
                    log.level
                  )} text-xs leading-relaxed`}
                >
                  {log.message}
                </p>
                {log.metadata && Object.keys(log.metadata).length > 0 && (
                  <details className="mt-2">
                    <summary className="text-xs text-gray-500 dark:text-gray-400 cursor-pointer hover:text-gray-700 dark:hover:text-gray-300">
                      Metadata
                    </summary>
                    <pre className="mt-1 text-xs text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 p-2 rounded overflow-x-auto">
                      {JSON.stringify(log.metadata, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={logsEndRef} />
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
        <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
          <span>
            Showing {filteredLogs.length} of {logs.length} logs
          </span>
          <span>
            {isPaused ? (
              <span className="text-orange-500">Paused</span>
            ) : (
              <span className="text-green-500">Live</span>
            )}
          </span>
        </div>
      </div>
    </div>
  );
}
