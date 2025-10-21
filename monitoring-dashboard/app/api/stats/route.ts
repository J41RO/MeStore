import { NextResponse } from 'next/server';
import backendClient from '@/lib/backend-client';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function GET() {
  try {
    // Hacer todas las llamadas en paralelo para mejor performance
    const [userStats, authStats, apiStats, redisStats] = await Promise.allSettled([
      backendClient.getUserStats(),
      backendClient.getAuthStats(),
      backendClient.getAPIStats(),
      backendClient.getRedisStats(),
    ]);

    const result: any = {
      timestamp: new Date().toISOString(),
      users: userStats.status === 'fulfilled' ? userStats.value : null,
      auth: authStats.status === 'fulfilled' ? authStats.value : null,
      api: apiStats.status === 'fulfilled' ? apiStats.value : null,
      redis: redisStats.status === 'fulfilled' ? redisStats.value : null,
      errors: [],
    };

    // Agregar errores si alguna llamada falló
    if (userStats.status === 'rejected') {
      result.errors.push({ endpoint: 'users', error: userStats.reason.message });
    }
    if (authStats.status === 'rejected') {
      result.errors.push({ endpoint: 'auth', error: authStats.reason.message });
    }
    if (apiStats.status === 'rejected') {
      result.errors.push({ endpoint: 'api', error: apiStats.reason.message });
    }
    if (redisStats.status === 'rejected') {
      result.errors.push({ endpoint: 'redis', error: redisStats.reason.message });
    }

    return NextResponse.json(result);
  } catch (error) {
    console.error('Error fetching stats:', error);

    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Failed to fetch stats',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}
