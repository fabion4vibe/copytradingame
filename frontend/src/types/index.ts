// ── Shared ─────────────────────────────────────────────────────────────────

export type TraderPhase = 'REPUTATION_BUILD' | 'FOLLOWER_GROWTH' | 'MONETIZATION';
export type TradeAction = 'BUY' | 'SELL';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type AppRole = 'retail' | 'manager';

// ── Market ─────────────────────────────────────────────────────────────────

export interface Asset {
  id: string;
  symbol: string;
  current_price: number;
  initial_price: number;
  volatility: number;
  drift: number;
  current_return: number;
}

export interface MarketStatus {
  tick: number;
  n_assets: number;
  running: boolean;
}

export interface TickSummary {
  tick: number;
  prices: Record<string, number>;
  trades_executed: number;
  platform_pnl_delta: number;
  professionals_summary: Array<{
    id: string;
    phase: TraderPhase;
    trade_executed: boolean;
  }>;
}

// ── Retail ─────────────────────────────────────────────────────────────────

export interface RetailSummary {
  id: string;
  name: string;
  balance: number;
  portfolio_value: number;
  total_pnl: number;
  n_trades: number;
  copied_traders: string[];
}

export interface RetailDetail extends RetailSummary {
  portfolio: Record<string, number>;
  avg_buy_prices: Record<string, number>;
  is_real_user: boolean;
}

export interface Trade {
  id: string;
  trader_id: string;
  asset_id: string;
  action: TradeAction;
  quantity: number;
  price: number;
  timestamp: number;
  is_copy: boolean;
  copied_from: string | null;
  pnl_realized: number;
}

export interface CopyRelation {
  retail_id: string;
  professional_id: string;
  allocation_pct: number;
  start_tick: number;
  active: boolean;
}

// ── Professional ───────────────────────────────────────────────────────────

export interface StrategyProfile {
  expected_value: number;
  risk_level: number;
  trade_frequency: number;
  min_followers_for_B: number;
  min_followers_for_C: number;
  target_capital_exposed: number;
  bonus_per_tick_in_C: number;
}

export interface ProfessionalSummary {
  id: string;
  name: string;
  phase: TraderPhase;
  followers_count: number;
  follower_capital_exposed: number;
  pnl_personal: number;
  bonus_earned: number;
  total_compensation: number;
  n_trades: number;
  last_phase_change_tick: number | null;
}

export interface ProfessionalDetail extends ProfessionalSummary {
  strategy: StrategyProfile;
  followers: string[];
}

export interface PhaseHistoryEntry {
  tick: number;
  from_phase: TraderPhase;
  to_phase: TraderPhase;
  followers_at_transition: number;
  capital_exposed_at_transition: number;
  note: string;
}

// ── Algorithm ──────────────────────────────────────────────────────────────

export interface Recommendation {
  trader_id: string;
  trader_name: string;
  current_phase: TraderPhase;
  suggested_action: string;
  reason: string;
  expected_platform_gain: number;
  risk_level: RiskLevel;
  confidence: number;
  score: number;
}

export interface TraderRanking {
  trader_id: string;
  name: string;
  phase: TraderPhase;
  score: number;
  followers: number;
  capital_exposed: number;
  pnl_personal: number;
}

export interface ScenarioResult {
  scenario: string;
  trader_id: string;
  n_ticks: number;
  expected_retail_loss: number;
  expected_bonus_paid: number;
  expected_platform_net_gain: number;
  confidence_interval: [number, number];
}

// ── Manager ────────────────────────────────────────────────────────────────

export interface PlatformOverview {
  current_tick: number;
  platform_pnl: number;
  platform_commissions: number;
  platform_bonus_paid: number;
  platform_net: number;
  total_retail_capital: number;
  total_capital_in_copy: number;
  copy_penetration_pct: number;
  n_professionals_in_monetization: number;
  n_retail_losing: number;
  avg_retail_pnl: number;
}

export interface PlatformPnL {
  pnl: number;
  commissions: number;
  bonus_paid: number;
  net: number;
  history: Array<{ tick: number; pnl: number; net: number }>;
}

export interface CopyStats {
  total_active_relations: number;
  total_capital_in_copy: number;
  by_professional: Record<string, {
    followers: number;
    capital_exposed: number;
    phase: TraderPhase;
  }>;
}
