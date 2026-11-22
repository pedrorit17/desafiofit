// ============================================================
//  SUBSTITUA pelos dados do seu projeto Firebase
//  Console → Configurações do projeto → Seus apps → SDK
// ============================================================
const FIREBASE_CONFIG = {
  apiKey:            "COLE_AQUI",
  authDomain:        "COLE_AQUI",
  projectId:         "COLE_AQUI",
  storageBucket:     "COLE_AQUI",
  messagingSenderId: "COLE_AQUI",
  appId:             "COLE_AQUI"
};

// Período do desafio
const DESAFIO_INICIO = "2026-11-23";   // segunda-feira
const DESAFIO_FIM    = "2026-12-18";   // sexta-feira

// Semanas oficiais (segunda → domingo)
const SEMANAS = [
  { num: 1, inicio: "2026-11-23", fim: "2026-11-29", maxCheckins: 6 },
  { num: 2, inicio: "2026-11-30", fim: "2026-12-06", maxCheckins: 6 },
  { num: 3, inicio: "2026-12-07", fim: "2026-12-13", maxCheckins: 6 },
  { num: 4, inicio: "2026-12-14", fim: "2026-12-18", maxCheckins: 5 },
];

function semanaDeData(dataStr) {
  for (const s of SEMANAS) {
    if (dataStr >= s.inicio && dataStr <= s.fim) return s;
  }
  return null;
}

// Pontuação
function ptsCardio(min) {
  if (min >= 50) return 5;
  if (min >= 40) return 4;
  if (min >= 30) return 3;
  if (min >= 20) return 2;
  return 0;
}

function calcularPontos({ musculacao, cardio_minutos, atividade_coletiva, post_insta }) {
  return (musculacao ? 20 : 0)
       + ptsCardio(cardio_minutos || 0)
       + (atividade_coletiva ? 5 : 0)
       + (post_insta ? 2 : 0);
}

// Datas válidas do desafio como array "YYYY-MM-DD"
function datasDesafio() {
  const datas = [];
  let cur = new Date(DESAFIO_INICIO + "T12:00:00");
  const fim = new Date(DESAFIO_FIM  + "T12:00:00");
  while (cur <= fim) {
    datas.push(cur.toISOString().slice(0, 10));
    cur.setDate(cur.getDate() + 1);
  }
  return datas;
}

function formatarData(dataStr) {
  const [y, m, d] = dataStr.split("-");
  return `${d}/${m}/${y}`;
}

function diaDaSemana(dataStr) {
  const dias = ["Dom","Seg","Ter","Qua","Qui","Sex","Sáb"];
  return dias[new Date(dataStr + "T12:00:00").getDay()];
}
