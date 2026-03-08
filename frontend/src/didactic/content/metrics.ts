/** Testi esplicativi per MetricExplainer — una voce per ogni KPI della dashboard manager. */

export interface MetricContent {
  label: string;
  explanation: string;
  formula?: string;
}

export const metrics: Record<string, MetricContent> = {
  'platform-net-pnl': {
    label: 'PnL Netto Piattaforma',
    explanation:
      'Somma delle perdite nette dei trader retail, al netto dei bonus pagati ai professionisti. '
      + 'Rappresenta il guadagno reale della piattaforma dopo aver remunerato i trader che ha utilizzato come strumenti.',
    formula: 'Perdite retail totali − Bonus pagati ai professionisti',
  },
  'total-retail-capital': {
    label: 'Capitale Retail Totale',
    explanation:
      'Somma del valore attuale di tutti i portafogli retail: liquidità disponibile più posizioni aperte '
      + 'valutate ai prezzi correnti. Più questo valore è alto, più capitale è esposto alle strategie della piattaforma.',
  },
  'copy-penetration': {
    label: '% Capitale in Copy Trading',
    explanation:
      'Percentuale del capitale retail totale attualmente allocata in relazioni di copy attive. '
      + 'Più è alta, più la piattaforma può influenzare i risultati attraverso i trader professionisti. '
      + 'Una penetrazione elevata in Fase C massimizza il guadagno della piattaforma.',
  },
  'retail-losing-count': {
    label: 'Retail in Perdita',
    explanation:
      'Numero di trader retail con PnL totale negativo rispetto al capitale iniziale. '
      + 'Ogni retail in perdita contribuisce direttamente al guadagno della piattaforma.',
  },
};
