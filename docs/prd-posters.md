# PRD — Lista de filmes só com poster verificado (RUÍDO)

> Status: ready-for-agent
> Sem issue tracker configurado neste repo; este PRD vive como arquivo até existir um tracker.

## Problem Statement

Durante uma partida de RUÍDO, alguns filmes aparecem no deck com o **placeholder cinza** (gradiente + inicial do título) em vez de um poster real. Isso deixa a interface inconsistente: lado a lado com cards que têm poster, os cards "sem foto" parecem quebrados ou inacabados. Para uma experiência de "noite de filme" — e para uma defesa de TCC — um poster faltando ou, pior, errado, prejudica a credibilidade da tela.

A causa não é que esses filmes não tenham poster: é que o poster é buscado **ao vivo no TMDB pelo título em pt-BR** a cada card, e essa busca falha para alguns títulos traduzidos (ex.: "Ponto de Ruptura", "Máquina Mortífera"). O resultado é um placeholder que pisca/permanece, mesmo quando o filme tem poster disponível.

## Solution

Garantir que **todo filme exibido no jogo tenha um poster real, já verificado e hospedado localmente** — eliminando tanto o placeholder quanto a dependência de internet durante a partida.

Da perspectiva do usuário:
- O host nunca vê um card cinza no deck; todo filme tem sua capa.
- Os celulares carregam os posters mesmo numa rede Wi-Fi local sem internet (o jogo roda em LAN via QR code).
- Nenhum poster "errado" (de um remake ou filme homônimo) é exibido.

Tecnicamente, troca-se a busca ao vivo por um **catálogo curado offline**: um script resolve uma única vez o poster de cada filme via TMDB, baixa a imagem para o disco e registra o resultado num manifesto versionado. O jogo passa a servir apenas filmes presentes nesse manifesto, com o caminho local do poster embutido. Filmes sem poster resolvido simplesmente não entram em jogo; adicionar um filme novo sem poster é, na prática, impossível de aparecer.

## User Stories

1. Como host na TV, quero que todo card de filme no deck tenha um poster real, para que a tela não pareça inconsistente ou quebrada.
2. Como jogador no celular, quero ver a capa de cada filme que avalio, para reconhecer o filme rapidamente sem ler só o título.
3. Como jogador, quero que o poster apareça imediatamente (sem o flash do placeholder cinza), para uma experiência fluida no deck estilo Tinder.
4. Como jogador numa rede local sem internet, quero que os posters carreguem mesmo assim, para que o jogo funcione em qualquer ambiente de "noite de filme".
5. Como host, quero ter certeza de que nenhum poster mostrado é de um filme errado (homônimo/remake), para não passar informação incorreta.
6. Como jogador no modal de detalhes, quero que o poster desfocado de fundo seja o poster real do filme, para manter a estética coerente.
7. Como organizador da partida, quero que filmes sem poster verificado nunca apareçam em nenhuma rodada, para uma interface uniforme do início ao fim.
8. Como jogador na rodada 2 e 3, quero que os filmes do pool (vindos dos votos anteriores) também tenham poster, já que herdam apenas filmes já servidos e verificados.
9. Como desenvolvedor, quero rodar um script único para resolver e baixar todos os posters, para não depender de chamadas ao TMDB durante o jogo.
10. Como desenvolvedor, quero que o script sinalize correspondências de baixa confiança (ano divergente, múltiplos candidatos) numa lista de revisão, para confirmar antes de publicar um poster possivelmente errado.
11. Como desenvolvedor, quero que o script registre `tmdb_id` de cada filme resolvido, para que re-execuções sejam determinísticas e imunes a variações de título/idioma.
12. Como desenvolvedor, quero um relatório de quantos filmes falham por categoria, para decidir com números reais se preciso de um piso mínimo por gênero.
13. Como desenvolvedor, quero um manifesto versionado (`data/posters.json`) como fonte da verdade do que pode ser servido, para que o filtro do catálogo seja confiável e offline.
14. Como desenvolvedor, quero adicionar um filme novo ao catálogo e que ele só apareça depois de ter poster resolvido, para que a regra "sem poster, não entra" seja automática.
15. Como desenvolvedor, quero um script de verificação que liste filmes do catálogo ausentes do manifesto, para perceber quando um filme que adicionei está sendo escondido.
16. Como mantenedor, quero que os posters fiquem hospedados em `static/img/posters/`, para que a partida não tenha nenhuma dependência externa em tempo de execução.
17. Como desenvolvedor, quero que o placeholder de gradiente permaneça no código como rede de segurança morta, para não quebrar caso algum poster falte por engano.
18. Como desenvolvedor, quero remover a rota de busca de poster ao vivo (`/api/poster`) e o caminho de fetch em runtime, para simplificar o fluxo e eliminar a fonte do flicker.
19. Como avaliador do TCC, quero uma tela visualmente consistente em qualquer demonstração, para que a qualidade percebida do projeto seja alta.
20. Como desenvolvedor, quero que a lógica de decisão de match do resolver seja testável com o TMDB mockado, para garantir a regra de auto-aceite vs. revisão sem rede.
21. Como desenvolvedor, quero que o filtro do catálogo seja testável via `GET /round/1`, para validar a garantia de "só filmes verificados" no maior seam possível.

## Implementation Decisions

### Módulos novos / modificados

- **`data/posters.json` (novo, versionado):** manifesto fonte-da-verdade. Mapeia `movie_id → { tmdb_id, file }`, onde `file` é o caminho local do poster (ex.: relativo a `static/img/posters/`). Apenas filmes com poster resolvido constam aqui.
- **Script resolvedor (novo, build-time, ex.: `scripts/resolve_posters.py`):** percorre os 300 filmes de `data/movies.py`. Para cada um: busca no TMDB (título pt-BR + ano; fallback para título original), captura `tmdb_id` + URL do poster, **baixa a imagem** para `static/img/posters/<movie_id>.jpg`, e grava a entrada no manifesto. Reaproveita a lógica de fetch existente em `posters.py`. Requer `TMDB_API_KEY` no ambiente uma única vez (build-time).
- **Match-safety no resolver:** auto-aceita correspondências limpas (título + ano exato); escreve casos ambíguos (ano divergente, múltiplos candidatos) numa **lista de revisão** (saída do script / arquivo à parte) para confirmação humana antes de entrar no manifesto. Não publica poster de baixa confiança automaticamente.
- **Seam de serving do catálogo (modificado, em `routes/game.py`):** introduzir um ponto único que (a) filtra `MOVIES` para apenas ids presentes no manifesto e (b) injeta o caminho local do poster em cada dict de filme, antes de serializar para `#movies-data`. Rodadas 2/3 herdam automaticamente: o `RoundPool` é construído a partir dos votos da rodada 1, que já são filmes servidos/verificados; `pool_grouped` apenas carrega o `poster` adiante.
- **`round.js` (modificado):** lê `m.poster` diretamente do payload em vez de chamar `/api/poster`. Aplica o poster no card e no fundo desfocado do modal sem fetch assíncrono. O placeholder de gradiente permanece como rede de segurança morta (não deve disparar para filmes do catálogo).
- **Remoção do caminho ao vivo:** a rota `/api/poster/<movie_id>` e o fetch lazy em runtime saem; `posters.py` passa a ser utilitário do script de build (busca no TMDB), não dependência de runtime.
- **Script de verificação (novo, ex.: `scripts/verify_posters.py`):** função pura sobre `(catálogo, manifesto)` que devolve os ids do catálogo ausentes do manifesto; usado para detectar filmes adicionados sem poster.

### Contratos / formatos

- Manifesto: objeto JSON `{ "<movie_id>": { "tmdb_id": <int>, "file": "<path local>" }, ... }`.
- Payload servido em `#movies-data`: mesma estrutura agrupada de `MOVIES` atual, com cada filme acrescido de um campo `poster` (caminho local). Filmes ausentes do manifesto **não** aparecem no payload.
- Piso por categoria: **decisão diferida** — rodar o resolvedor e relatar falhas por categoria antes de definir qualquer mínimo. Com 25 filmes por categoria há folga; o piso (se necessário) será definido com números reais.

### Decisões arquiteturais

- Curadoria **offline / build-time**, não em tempo de requisição: nenhuma chamada ao TMDB durante a partida.
- Posters **auto-hospedados** em `static/img/posters/` (servidos do disco como os avatares), eliminando dependência da CDN do TMDB e funcionando em LAN sem internet.
- `movies.py` permanece a lista-fonte; a elegibilidade é governada pelo manifesto. Um filme que falhe hoje pode ser reincluído numa re-execução futura sem editar a lista-fonte à mão.
- Enforcement do "sem poster, não entra" é **silencioso no serving** (filme ausente do manifesto nunca aparece) **+ script de verificação** para dar sinal ao desenvolvedor.

## Testing Decisions

Um bom teste aqui valida **comportamento externo** — o que é servido pelas rotas e a decisão observável do resolver — e **não** detalhes de implementação (nomes de funções internas, estrutura de cache). Segue o padrão "slice" já existente em `tests/`: app Flask com DB in-memory via fixtures de `conftest.py`, `test_client`, e dependências externas mockadas com `patch(...)` (como `arduino.send_led`).

Módulos/seams testados:

1. **Garantia de serving — `GET /round/1` (seam mais alto, existente):**
   - Com um manifesto de teste injetado, o payload de `#movies-data` **exclui** ids ausentes do manifesto (filmes órfãos) e **inclui** um campo `poster` (caminho local) em todo filme servido.
   - Prior art: testes que fazem `GET`/`POST` em rotas de round e asseguram a resposta (`tests/test_slice5_submit_white.py`, `tests/test_slice4_round_timer.py`).
2. **Carga do manifesto (seam novo, pequeno):** a leitura de `data/posters.json` é injetável para os testes trocarem por um manifesto falso, permitindo o teste do seam #1 sem depender do arquivo real de 300 entradas.
3. **Decisão de match do resolvedor (seam novo, build-time):** a função que classifica um resultado do TMDB como auto-aceite vs. revisão, com a chamada HTTP do TMDB **mockada** (mesmo padrão de `patch` do hardware). Verifica: ano exato → aceita; ano divergente / múltiplos candidatos → vai para a lista de revisão; sem poster → órfão. Download e IO **não** são testados em unidade (mockados na fronteira).
4. **Script de verificação (seam novo, puro):** função pura sobre `(catálogo, manifesto)` retornando os ids faltantes; testada sem IO.

Fora do teste unitário: a rede real do TMDB e o download de imagens para disco (mockados no limite), consistente com o tratamento de hardware no projeto.

## Out of Scope

- Integração de **sinopse e rating reais** (continuam derivados deterministicamente do hash do id em `round.js`). Este PRD trata apenas de posters/imagens.
- Buscar **novas fontes** de poster além do TMDB.
- Adicionar/curar **novos filmes** ao catálogo para repor categorias eventualmente reduzidas (decisão de piso é diferida ao relatório; reposição, se necessária, é trabalho separado).
- Atualização automática/agendada do manifesto (CI, cron). A resolução é um passo manual de build.
- Qualquer mudança no algoritmo de match de votos, máquina de estados, avatares ou integração Arduino.
- Otimização/redimensionamento de imagens além do tamanho `w500` já usado.

## Further Notes

- Esta mudança é **maior do que o pedido de uma linha** sugeria: adiciona um passo de build e assets versionados (imagens em `static/img/posters/`). É o caminho certo para uma demo estável, mas não é uma edição trivial.
- **Primeiro passo natural:** rodar o resolvedor e produzir o **relatório de falhas por categoria** — todas as decisões a jusante (piso por categoria, quantos órfãos remover) dependem desses números reais.
- A causa-raiz confirmada com o usuário: a `TMDB_API_KEY` está configurada no deploy real; apenas alguns filmes falham, provavelmente por correspondência ruim de títulos em pt-BR — daí a estratégia "corrigir o match (via `tmdb_id`/título original) e remover apenas os órfãos verdadeiros".
- Decisões travadas na entrevista: manifesto em arquivo novo `data/posters.json`; remoção do fetch ao vivo com URLs embutidas no deck; posters auto-hospedados; sinalização de matches de baixa confiança; enforcement silencioso + script de verificação; piso por categoria decidido após o relatório.
- Versionar imagens no repo aumenta o tamanho do checkout; aceitável dada a natureza do projeto (demo de TCC) e a garantia de funcionamento offline.
