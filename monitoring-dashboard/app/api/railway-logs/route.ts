import { NextRequest, NextResponse } from 'next/server';
import railwayClient from '@/lib/railway-client';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const limit = parseInt(searchParams.get('limit') || '100', 10);
    const filter = searchParams.get('filter') || undefined;
    const level = searchParams.get('level') || undefined;

    let logs = await railwayClient.getLogs(limit, filter);

    // Filtrar por nivel si se especifica
    if (level && level !== 'ALL') {
      logs = logs.filter((log) => log.level === level);
    }

    return NextResponse.json({
      success: true,
      count: logs.length,
      logs,
      is_railway_configured: railwayClient.isConfigured(),
    });
  } catch (error) {
    console.error('Error fetching Railway logs:', error);

    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch logs',
        logs: [],
      },
      { status: 500 }
    );
  }
}
