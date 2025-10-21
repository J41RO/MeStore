import { NextResponse } from 'next/server';
import backendClient from '@/lib/backend-client';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function GET() {
  try {
    const health = await backendClient.healthCheck();
    const responseTimeHistory = backendClient.getResponseTimeHistory();
    const avgResponseTime = backendClient.getAverageResponseTime();

    return NextResponse.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      backend: health,
      monitoring: {
        avg_response_time: avgResponseTime,
        response_time_samples: responseTimeHistory.length,
        dashboard_uptime: process.uptime(),
      },
    });
  } catch (error) {
    console.error('Health check failed:', error);

    return NextResponse.json(
      {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 503 }
    );
  }
}
