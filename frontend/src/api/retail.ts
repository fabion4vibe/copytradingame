import client from './client';
import type { RetailSummary, RetailDetail, Trade, CopyRelation } from '../types';

export const retailApi = {
  listTraders: () =>
    client.get<RetailSummary[]>('/retail/traders'),

  getTrader: (id: string) =>
    client.get<RetailDetail>(`/retail/traders/${id}`),

  createTrader: (name: string, initialBalance = 10000, isRealUser = false) =>
    client.post<RetailSummary>('/retail/traders', {
      name,
      initial_balance: initialBalance,
      is_real_user: isRealUser,
    }),

  executeTrade: (id: string, assetId: string, action: 'BUY' | 'SELL', quantity: number) =>
    client.post<Trade>(`/retail/traders/${id}/trade`, {
      asset_id: assetId,
      action,
      quantity,
    }),

  startCopy: (id: string, professionalId: string, allocationPct = 0.5) =>
    client.post<CopyRelation>(`/retail/traders/${id}/copy`, {
      professional_id: professionalId,
      allocation_pct: allocationPct,
    }),

  stopCopy: (id: string, professionalId: string) =>
    client.delete<{ success: boolean }>(`/retail/traders/${id}/copy/${professionalId}`),

  getHistory: (id: string) =>
    client.get<Trade[]>(`/retail/traders/${id}/history`),

  getPnl: (id: string) =>
    client.get<{ pnl: number; portfolio_value: number }>(`/retail/traders/${id}/pnl`),
};
