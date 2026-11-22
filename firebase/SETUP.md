# Setup Firebase — Desafio Nanda Carvalho

## 1. Criar projeto no Firebase
1. Acesse https://console.firebase.google.com
2. Clique em **Adicionar projeto** → nome: `desafio-nanda` → criar
3. No menu lateral: **Compilação → Firestore Database → Criar banco de dados**
   - Modo: **Produção** → localização: **southamerica-east1** (São Paulo)
4. No menu lateral: **Compilação → Authentication → Começar**
   - Ative: **E-mail/senha**
   - Em **Usuários**, clique **Adicionar usuário** → coloque o e-mail e senha de admin

## 2. Pegar a config do projeto
1. Console → ⚙️ **Configurações do projeto** → aba **Geral**
2. Role até **Seus apps** → clique em **</>** (web)
3. Registre o app → copie o bloco `firebaseConfig`

## 3. Colar a config nos dois arquivos
Abra `index.html` e `admin.html` e substitua **os 6 campos** `"COLE_AQUI"`:

```js
const cfg = {
  apiKey:            "AIzaSy...",
  authDomain:        "desafio-nanda.firebaseapp.com",
  projectId:         "desafio-nanda",
  storageBucket:     "desafio-nanda.appspot.com",
  messagingSenderId: "123456789",
  appId:             "1:123456789:web:abc..."
};
```

## 4. Publicar as regras do Firestore
No terminal (precisa do Firebase CLI: `npm install -g firebase-tools`):

```bash
firebase login
firebase use --add   # selecione o projeto desafio-nanda
firebase deploy --only firestore:rules,firestore:indexes
```

Ou cole o conteúdo de `firestore.rules` manualmente:
Console → Firestore → aba **Regras** → colar → Publicar

## 5. Deploy do site (opcional)
```bash
firebase deploy --only hosting
```
Ou hospede os arquivos em qualquer servidor estático (Netlify, Vercel, PythonAnywhere, etc.)
— são arquivos HTML puros.

## 6. Usar
- Página pública: `index.html` — ranking em tempo real, sem login
- Painel admin:   `admin.html` — login com e-mail/senha cadastrado na etapa 1
  - Aba **Participantes**: cadastra os competidores
  - Aba **Registrar Dia**: seleciona a data → preenche a tabela com todos → Salvar

## Pontuação implementada (emagrecimento)
| Atividade | Regra | Pontos |
|-----------|-------|--------|
| Musculação | qualquer duração | 20 |
| Cardio | 20–29 min | 2 |
| Cardio | 30–39 min | 3 |
| Cardio | 40–49 min | 4 |
| Cardio | 50+ min | 5 |
| Encontro coletivo | presença confirmada | 5 |
| Post Instagram | @nandacarvalhopersonal + @terrafarma_manipulacao | 2 |

## Critérios de desempate (já implementados no ranking)
1. Maior tempo acumulado em cardio (minutos)
2. Maior número de dias com atividade registrada
3. Maior número de encontros coletivos
4. Maior número de posts no Instagram
5. Sorteio ao vivo
