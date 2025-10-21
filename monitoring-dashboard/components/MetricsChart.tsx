'use client';

import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import { Activity, TrendingUp, TrendingDown } from 'lucide-react';
import { backendClient } from '@/lib/backend-client';

interface DataPoint {
  timestamp: string;
  time: string;
  responseTime: number;
}

interface MetricsChartProps {
  refreshInterval?: number;
}

export default function MetricsChart({
  refreshInterval = 5000,
}: MetricsChartProps) {
  const [data, setData] = useState<DataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentAvg, setCurrentAvg] = useState(0);
  const [previousAvg, setPreviousAvg] = useState(0);

  // Fetch response time data
  const fetchMetrics = async () => {
    try {
      const responseTimeHistory = backendClient.getResponseTimeHistory();
      const avgResponseTime = backendClient.getAverageResponseTime();

      // Create data points for the last 60 minutes
      const now = Date.now();
      const newDataPoints: DataPoint[] = [];

      // If we have historical data, use it
      if (responseTimeHistory.length > 0) {
        // Create 60 data points (one per minute)
        for (let i = 59; i >= 0; i--) {
          const timestamp = new Date(now - i * 60000);
          const historyIndex = Math.max(
            0,
            responseTimeHistory.length - 60 + i
          );
          const responseTime =
            responseTimeHistory[historyIndex] || avgResponseTime;

          newDataPoints.push({
            timestamp: timestamp.toISOString(),
            time: timestamp.toLocaleTimeString('en-US', {
              hour: '2-digit',
              minute: '2-digit',
            }),
            responseTime: Math.round(responseTime),
          });
        }
      } else {
        // Generate mock data for visualization
        for (let i = 59; i >= 0; i--) {
          const timestamp = new Date(now - i * 60000);
          const baseTime = 150;
          const variance = Math.random() * 100 - 50;
          const responseTime = Math.max(50, baseTime + variance);

          newDataPoints.push({
            timestamp: timestamp.toISOString(),
            time: timestamp.toLocaleTimeString('en-US', {
              hour: '2-digit',
              minute: '2-digit',
            }),
            responseTime: Math.round(responseTime),
          });
        }
      }

      setData(newDataPoints);

      // Calculate averages for trend
      const recentData = newDataPoints.slice(-10);
      const olderData = newDataPoints.slice(-20, -10);

      const recentAvg =
        recentData.reduce((sum, point) => sum + point.responseTime, 0) /
        recentData.length;
      const olderAvg =
        olderData.reduce((sum, point) => sum + point.responseTime, 0) /
        olderData.length;

      setPreviousAvg(olderAvg);
      setCurrentAvg(recentAvg);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching metrics:', error);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  // Calculate trend
  const trend = currentAvg - previousAvg;
  const trendPercentage =
    previousAvg > 0 ? ((trend / previousAvg) * 100).toFixed(1) : 0;
  const isImproving = trend < 0; // Lower response time is better

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
          <p className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
            {payload[0].payload.time}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Response Time:{' '}
            <span className="font-semibold text-blue-500">
              {payload[0].value} ms
            </span>
          </p>
        </div>
      );
    }
    return null;
  };

  // Calculate max and min for better scaling
  const responseTimesValues = data.map((d) => d.responseTime);
  const maxResponseTime = Math.max(...responseTimesValues, 200);
  const minResponseTime = Math.min(...responseTimesValues, 0);

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Activity className="w-6 h-6 text-blue-500" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Response Time
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Last 60 minutes
              </p>
            </div>
          </div>

          {/* Stats Card */}
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {Math.round(currentAvg)} ms
              </div>
              <div
                className={`flex items-center gap-1 text-sm ${
                  isImproving
                    ? 'text-green-500'
                    : 'text-red-500'
                }`}
              >
                {isImproving ? (
                  <TrendingDown className="w-4 h-4" />
                ) : (
                  <TrendingUp className="w-4 h-4" />
                )}
                <span>
                  {isImproving ? '-' : '+'}
                  {Math.abs(Number(trendPercentage))}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-4 flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-blue-400 rounded-full"></div>
            <span className="text-gray-600 dark:text-gray-400">
              Response Time
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-gray-600 dark:text-gray-400">
              Good (&lt;200ms)
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-gray-600 dark:text-gray-400">
              Fair (200-500ms)
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span className="text-gray-600 dark:text-gray-400">
              Poor (&gt;500ms)
            </span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="flex-1 p-4">
        {isLoading ? (
          <div className="h-full flex items-center justify-center text-gray-500 dark:text-gray-400">
            Loading metrics...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={data}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <defs>
                <linearGradient id="colorResponseTime" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#374151"
                opacity={0.1}
              />
              <XAxis
                dataKey="time"
                stroke="#9CA3AF"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                interval="preserveStartEnd"
                minTickGap={50}
              />
              <YAxis
                stroke="#9CA3AF"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                domain={[0, maxResponseTime + 50]}
                tickFormatter={(value) => `${value}ms`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="responseTime"
                stroke="#3B82F6"
                strokeWidth={2}
                fill="url(#colorResponseTime)"
                animationDuration={300}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Footer Stats */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
              Average
            </div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {Math.round(currentAvg)} ms
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
              Min
            </div>
            <div className="text-lg font-semibold text-green-500">
              {Math.round(minResponseTime)} ms
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
              Max
            </div>
            <div className="text-lg font-semibold text-red-500">
              {Math.round(maxResponseTime)} ms
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
