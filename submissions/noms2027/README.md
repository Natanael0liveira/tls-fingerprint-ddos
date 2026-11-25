# NOMS 2027 — versão submetida registrada em 24/11/2026

**An Empirical Evaluation of TLS Fingerprint-Based Filtering for Application-Layer DDoS**

Esta entrega está em `submissions/noms2027/` e está sincronizada com o fonte
e o PDF canônicos em `papers/http-session-noms/`. A r53 congelada permanece
intacta em `archive/noms2027/r53/`.

O autor identificou o `papers/http-session-noms/article.tex` atual como o TEX
final submetido em sua mensagem de 24/11/2026. O conteúdo foi preservado sem
edições e copiado para `latex/article.tex`. O PDF desta pasta foi recompilado
localmente a partir desse fonte; não foi comparado ao arquivo enviado ao
sistema de submissão.

## Arquivos

| Caminho | Conteúdo |
|---|---|
| `article.pdf` | PDF recompilado localmente a partir do TEX submetido |
| `latex/article.tex` | Fonte completo em um arquivo |
| `latex/references.bib` | Bibliografia atual |
| `latex/IEEEtran.cls`, `IEEEtran.bst`, `stfloats.sty` | Dependências locais de compilação |
| `latex/figures/` | As duas figuras usadas pelo artigo |
| `figure-sources/` | Scripts das figuras |
| `changes-from-r53.diff` | Comparação do fonte atual com a r53 congelada |
| `verification.json` | Hashes e alcance das verificações desta entrega |
| `SHA256SUMS` | Manifesto dos arquivos da entrega |

## Conteúdo atual

- Abstract e introdução apresentam cobertura após o trigger, custo por falso
  alarme em cada endpoint e exposição ao fallback como critérios de decisão.
- A Seção V abre com a tabela-síntese do período prospectivo; seguem os
  mecanismos de seleção, a perda de cobertura pelo trigger, as variantes e
  verificações post hoc, e os ataques reais.
- A tabela distingue bloqueios de desafios e identifica o cap como post hoc.
  `n/a` significa ausência de falso alarme em E1–E4; E5 é discutido separadamente.
- O replay de persistência descreve explicitamente o modelo executado: pool
  diário de 25 stacks, com a fingerprint de cada bot sorteada a cada janela.
  Os 8,4% e 91% pertencem a esse modelo; não demonstram o caso de atribuições
  fixas por bot. O resultado somado de 60% e a explicação “picks add up” saíram.
- A declaração de IA inclui Claude (Anthropic) e Codex (OpenAI).

O script `experiments/sprint-6-noms/scripts/posthoc/sustained_ratelimit.py`, no
repositório, agora usa atribuições fixas por padrão e oferece
`--assignment resampled` para reproduzir o modelo anterior. A execução corrigida
sobre os dados de produção depende dos exports privados, indisponíveis nesta
verificação. Nenhum resultado novo foi inventado ou atribuído a essa execução.

## Compilar e conferir

```sh
cd latex
pdflatex -interaction=nonstopmode -halt-on-error article
bibtex article
pdflatex -interaction=nonstopmode -halt-on-error article
pdflatex -interaction=nonstopmode -halt-on-error article
```

Resultado conferido: 11 páginas; texto principal, conclusão, agradecimentos,
declaração de IA e reprodutibilidade na página 8, seguidos pelas referências e
pelo apêndice, que termina na página 11. Sem overfull, citações ou referências
indefinidas. O hash de uma nova compilação pode variar com os metadados do PDF.

No repositório, `make -C experiments/sprint-6-noms audit` verifica 217 células
numéricas contra os resultados salvos. As seis células numéricas das duas
primeiras linhas da tabela-síntese foram conferidas separadamente. Esses testes
não reexecutam os dados privados nem auditam todos os resultados em prosa ou os
números do cap; o relatório registra essas limitações.

Para conferir a integridade desta pasta no macOS:

```sh
shasum -a 256 -c SHA256SUMS
```

## Reprodução no Overleaf

Suba **todo o conteúdo de `submissions/noms2027/latex/`** no Overleaf, com
`article.tex` como documento principal. A bibliografia também mudou desde a entrega antiga; trocar apenas o
`.tex` não é suficiente. O TEX desta pasta corresponde à versão submetida
identificada pelo autor; o PDF é uma recompilação local.

As figuras são as mesmas da r53. Para regenerá-las, siga o guia
`docs/figures.md` no repositório. E5 continua anonimizado: não acrescente hosts,
endereços, redes nem datas que identifiquem o cliente.

## Atualizar a entrega

Edite o fonte canônico em `papers/http-session-noms/`. Depois de conferir o
artigo e registrar a verificação correspondente, execute `make submission`
na raiz do repositório. O comando sincroniza os arquivos e regenera o diff e
os checksums; ele recusa fonte, bibliografia ou PDF diferentes dos registrados
em `verification.json`. Execute `make check` para verificar toda a estrutura.
