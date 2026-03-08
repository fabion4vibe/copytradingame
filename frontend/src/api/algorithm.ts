import client from './client';
import type { Recommendation, TraderRanking, ScenarioResult } from '../types';

export const algorithmApi = {
  getRecommendations: () =>
    client.get<Recommendation[]>('/algorithm/recommendations'),

  getRankings: () =>
    client.get<TraderRanking[]>('/algorithm/rankings'),

  simulateScenario: (
    traderId: string,
    scenario: 'TRANSITION_TO_MONETIZATION' | 'MAINTAIN_CURRENT_PHASE',
    nTicks = 10
  ) =>
    client.post<ScenarioResult>('/algorithm/simulate-scenario', {
      trader_id: traderId,
      scenario,
      n_ticks: nTicks,
    }),
};
