/** Contenuto narrativo per il pannello HowItWorks (5 sezioni). */

export interface HowItWorksSection {
  id: string;
  title: string;
  content: string[];
  highlight?: string;
}

export const howItWorksSections: HowItWorksSection[] = [
  {
    id: 'actors',
    title: '1. La piattaforma e i suoi attori',
    content: [
      'Questa simulazione coinvolge tre tipi di attori con interessi diversi e spesso opposti.',
      'I trader retail sono utenti comuni che investono il proprio capitale. Possono operare manualmente o copiare i professionisti. Non hanno visibilità sulle strategie dei professionisti né sui meccanismi interni della piattaforma.',
      'I trader professionisti sono gestiti direttamente dalla piattaforma. Il loro comportamento è controllato da un algoritmo che decide quando è il momento di "attivare" le perdite per i follower.',
      'Il gestore della piattaforma ha visione completa: vede i dati aggregati, controlla le fasi dei trader professionisti e riceve raccomandazioni dall\'algoritmo su quando agire.',
    ],
    highlight: 'Il retail non sa che il professionista che copia è uno strumento della piattaforma, non un trader indipendente.',
  },
  {
    id: 'lifecycle',
    title: '2. Il ciclo di vita del trader professionista',
    content: [
      'Ogni trader professionista attraversa tre fasi, controllate dalla piattaforma.',
      'FASE A — Costruzione reputazione: il trader esegue operazioni con rendimento atteso positivo. Le performance sono buone, la reputazione cresce. Pochi follower, poco capitale esposto. Obiettivo: costruire credibilità.',
      'FASE B — Crescita follower: il trader mantiene performance decenti per attrarre più copiatori. Il capitale retail esposto cresce. Più follower significa più "munizioni" per la fase successiva.',
      'FASE C — Monetizzazione: il trader esegue operazioni con rendimento atteso negativo. I follower che lo copiano perdono capitale proporzionalmente alla loro allocazione. Il trader riceve un bonus fisso per tick, indipendentemente dal suo PnL personale.',
      'Esempio numerico: con 10 follower che hanno allocato il 30% di €1.000 ciascuno (€3.000 totali esposti), una perdita media del 2% per tick genera €60 di perdita retail per tick, che si traduce in guadagno della piattaforma.',
    ],
    highlight: 'I follower non vengono avvertiti del cambio di fase. La transizione avviene in modo invisibile.',
  },
  {
    id: 'revenue',
    title: '3. Come guadagna la piattaforma',
    content: [
      'Il modello di guadagno della piattaforma si basa su un meccanismo semplice ma opaco.',
      'Ogni perdita realizzata da un trader retail viene registrata come guadagno lordo della piattaforma. Se il retail perde €100, la piattaforma guadagna €100.',
      'Da questo guadagno lordo vengono sottratti i bonus pagati ai trader professionisti in Fase C. Il bonus è un costo fisso per tick per ogni trader in monetizzazione.',
      'Il guadagno netto è: Perdite retail totali − Bonus pagati ai professionisti.',
      'La piattaforma massimizza il guadagno attivando la Fase C quando il numero di follower e il capitale esposto sono sufficientemente alti. L\'algoritmo calcola il momento ottimale.',
    ],
    highlight: 'Formula: PnL Netto Piattaforma = Σ(perdite retail in copy) − Σ(bonus professionisti)',
  },
  {
    id: 'conflict',
    title: '4. Il conflitto di interesse',
    content: [
      'Il conflitto di interesse in questa simulazione è strutturale, non accidentale.',
      'La piattaforma guadagna quando i retail perdono. Questo significa che ogni miglioramento del PnL retail va a scapito del profitto della piattaforma.',
      'Il trader professionista è incentivato ad eseguire operazioni dannose perché viene pagato con un bonus fisso indipendente dal suo PnL. La sua remunerazione è disaccoppiata dalla qualità delle operazioni.',
      'Il retail che sceglie di copiare un professionista si fida di un sistema che ha tutti gli incentivi per danneggiarlo.',
      'Il gestore della piattaforma può vedere tutto questo in tempo reale e agire di conseguenza. Ha accesso alle raccomandazioni algoritmiche che calcolano il momento migliore per attivare le perdite.',
    ],
    highlight: 'Retail e piattaforma hanno interessi strutturalmente opposti. La fiducia del retail è la vulnerabilità che il sistema sfrutta.',
  },
  {
    id: 'observe',
    title: '5. Cosa osservare nella simulazione',
    content: [
      'Ecco cosa guardare per vedere il meccanismo in azione.',
      'Avanza qualche tick in Fase A e B e osserva come il PnL del professionista sia positivo — e i follower crescano di conseguenza.',
      'Attiva la Fase C dalla dashboard gestore e osserva immediatamente: il PnL retail dei follower inizia a deteriorarsi, il PnL netto della piattaforma sale, il professionista riceve bonus nonostante le perdite.',
      'Confronta il pannello "Il tuo impatto sulla piattaforma" nella vista retail: mostra quanto il tuo PnL negativo si è tradotto in guadagno per la piattaforma.',
      'Usa la simulazione scenario nella dashboard gestore per proiettare l\'impatto di una transizione a Fase C prima di attivarla.',
      'Osserva il grafico PnL piattaforma: la linea verde (netto) diverge dalla linea blu (commissioni) quando i bonus crescono.',
    ],
    highlight: 'La simulazione è progettata per rendere visibile ciò che nelle piattaforme reali rimane opaco.',
  },
];
