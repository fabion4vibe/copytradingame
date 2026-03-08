import client from './client';
import type { Asset, MarketStatus, TickSummary } from '../types';

export const marketApi = {
  getAssets: () =>
    client.get<Asset[]>('/market/assets'),

  getAsset: (id: string) =>
    client.get<Asset>(`/market/assets/${id}`),

  getHistory: (id: string, lastN?: number) =>
    client.get<{ history: number[]; ticks: number }>(
      `/market/assets/${id}/history`,
      { params: lastN !== undefined ? { last_n: lastN } : {} }
    ),

  advanceTick: (nTicks = 1) =>
    client.post<{ tick: number; summaries: TickSummary[] }>(
      '/market/tick',
      { n_ticks: nTicks }
    ),

  getStatus: () =>
    client.get<MarketStatus>('/market/status'),
};
