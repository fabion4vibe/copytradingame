import client from './client';
import type { PlatformOverview, PlatformPnL, CopyStats } from '../types';

export const managerApi = {
  getOverview: () =>
    client.get<PlatformOverview>('/manager/overview'),

  getPnl: () =>
    client.get<PlatformPnL>('/manager/pnl'),

  getCopyStats: () =>
    client.get<CopyStats>('/manager/copy-stats'),

  resetSimulation: () =>
    client.post<{ success: boolean }>('/manager/reset'),
};
