import client from './client';
import type {
  ProfessionalSummary,
  ProfessionalDetail,
  Trade,
  PhaseHistoryEntry,
  StrategyProfile,
  TraderPhase,
} from '../types';

export const professionalApi = {
  listTraders: () =>
    client.get<ProfessionalSummary[]>('/professional/traders'),

  getTrader: (id: string) =>
    client.get<ProfessionalDetail>(`/professional/traders/${id}`),

  changePhase: (id: string, newPhase: TraderPhase) =>
    client.patch<ProfessionalSummary>(`/professional/traders/${id}/phase`, {
      new_phase: newPhase,
    }),

  updateStrategy: (id: string, updates: Partial<StrategyProfile>) =>
    client.patch<StrategyProfile>(`/professional/traders/${id}/strategy`, updates),

  getHistory: (id: string) =>
    client.get<Trade[]>(`/professional/traders/${id}/history`),

  getPhaseHistory: (id: string) =>
    client.get<PhaseHistoryEntry[]>(`/professional/traders/${id}/phase-history`),
};
