/** Testi esplicativi per MechanismExplainer — separati dal codice per facilitare revisioni. */

export type MechanismColor = 'blue' | 'orange' | 'red';

export interface MechanismContent {
  title: string;
  body: string;
  keyPoint: string;
  color: MechanismColor;
}

export type MechanismId =
  | 'portfolio-pnl'
  | 'copy-trading'
  | 'platform-profit'
  | 'phase-cycle'
  | 'bonus-system';

export const mechanisms: Record<MechanismId, MechanismContent> = {
  'portfolio-pnl': {
    title: 'Cos\'è il PnL?',
    body: 'PnL sta per "Profit and Loss" — guadagno o perdita. Il tuo PnL mostra quanto hai guadagnato o perso rispetto al capitale iniziale. Un PnL negativo significa che il valore attuale del tuo portafoglio è inferiore a quello con cui hai iniziato.',
    keyPoint: 'Il PnL non realizzato cambia ad ogni tick. Diventa reale solo quando vendi.',
    color: 'blue',
  },
  'copy-trading': {
    title: 'Come funziona il copy trading?',
    body: 'Quando copi un trader, ogni sua operazione viene replicata automaticamente sul tuo portafoglio in proporzione alla percentuale di allocazione che hai scelto. Se il trader compra, compri anche tu. Se perde, perdi anche tu.',
    keyPoint: 'Non puoi intervenire sulle singole operazioni copiate. Puoi solo smettere di copiare.',
    color: 'orange',
  },
  'platform-profit': {
    title: 'Come guadagna la piattaforma?',
    body: 'In questa simulazione la piattaforma guadagna principalmente dalle perdite dei trader retail. Quando un retail perde €100, quella somma viene registrata come guadagno della piattaforma. Questo crea un incentivo strutturale: la piattaforma è più redditizia quando i suoi utenti perdono.',
    keyPoint: 'Questo è il conflitto di interesse al centro di questo progetto didattico.',
    color: 'red',
  },
  'phase-cycle': {
    title: 'Le tre fasi del trader professionista',
    body: 'I trader professionisti passano attraverso tre fasi controllate dalla piattaforma. Fase A (Costruzione reputazione): ottimi risultati, pochi follower. Fase B (Attrazione follower): buoni risultati, crescita dei copiatori. Fase C (Monetizzazione): operazioni deliberatamente svantaggiose. I follower subiscono le perdite. Il trader riceve un bonus.',
    keyPoint: 'I trader professionisti non sono indipendenti. Sono strumenti della piattaforma.',
    color: 'red',
  },
  'bonus-system': {
    title: 'Il sistema di bonus',
    body: 'In fase C, il trader professionista riceve un bonus fisso per ogni tick, indipendentemente dal suo PnL personale. Questo significa che può perdere soldi nelle sue operazioni ma essere comunque compensato. Il bonus viene pagato dalla piattaforma, che però recupera molto di più attraverso le perdite dei retail che lo copiano.',
    keyPoint: 'Il professionista è incentivato a perdere deliberatamente perché viene comunque pagato.',
    color: 'red',
  },
};
