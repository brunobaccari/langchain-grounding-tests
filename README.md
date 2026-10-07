# LangChain — contratos de contexto e resposta

[English version](README.en.md)

Testes de uma cadeia LCEL para consultar políticas sintéticas de reembolso. O foco é a integração: escolher documentos vigentes do produto correto, montar mensagens e validar a saída estruturada. Os modelos são `FakeListChatModel` e doubles explícitos do LangChain; **nenhum provedor ou modelo real é chamado**.

## Executar

Python 3.12 ou superior.

```bash
python -m venv .venv
# Ative .venv antes dos comandos seguintes
python -m pip install -r requirements.txt
cp .env.example .env
python -m pytest --junitxml=results/junit.xml
```

No Windows: `.venv\Scripts\Activate.ps1` e `Copy-Item .env.example .env`. No Linux/macOS: `source .venv/bin/activate`. `QA_CORPUS_PATH` aponta para o JSON sintético local; variáveis do processo têm prioridade. Não precisa de chave ou conta externa.

## O que bloqueia

| Risco | Verificação |
| --- | --- |
| Política revogada ou de outro produto entrar no contexto | Inspeção das mensagens enviadas à cadeia |
| Resposta sem documento aplicável | Abstenção antes de chamar o modelo |
| Referência inventada, revogada ou de outro produto | Rejeição de fonte fora do conjunto selecionado |
| Número como string, prazo negativo, campo extra ou decisão incoerente | Parser Pydantic estrito, sem reparo da resposta |
| Comando de documento virar instrução de sistema | Inspeção de papéis e conteúdo das mensagens |
| Contexto de uma chamada contaminar a seguinte | Produtos diferentes na mesma cadeia |
| Timeout parecer abstenção válida | Erro propagado, sem resposta fabricada |

O corpus recusa IDs duplicados, campos inválidos e coleção vazia. Os testes usam respostas prescritas para isolar a orquestração. O teste de comando em documento verifica a fronteira das mensagens; não demonstra resistência de um LLM à injeção de prompt.

## Resultado e decisão

[Actions](https://github.com/brunobaccari/langchain-grounding-tests/actions) publica summary por teste e artifact `results` com JUnit, por 14 dias. Falhas, skips, relatórios ausentes e contagem incompleta bloqueiam. `python scripts/summary.py --self-test` confere o parser. Outputs ficam fora do Git.

Antes de alterar uma regra, mude o documento sintético e o teste correspondente; não afrouxe o parser para aprovar uma saída incorreta. Depois da aprovação offline, ainda faltaria avaliar um modelo real e revisar se o prazo está sustentado pelo documento. O schema e uma fonte permitida não comprovam essa relação semântica.

Não há busca vetorial, ranking, memória persistente, benchmark de fornecedores ou avaliação live. A seleção é por metadados exatos. Referências: [testes no LangChain](https://docs.langchain.com/oss/python/langchain/test) e [modelos fake nativos](https://reference.langchain.com/python/langchain-core/language_models/fake_chat_models).

O summary do Actions lista cada cenário, duração, totais e motivo de bloqueio. O gate exige a quantidade prevista no workflow, sem falhas ou skips; JUnit ausente ou inválido reprova. O resumo também acompanha o artifact.

Husky: com Node 24 e as dependências da stack instalados, rode `npm ci` para ativar o pre-commit. `npm run check:local` verifica o diff, o gate dos relatórios e os checks de tipos/lint existentes. O hook também bloqueia arquivos ignorados no índice. Testes que usam navegador, emulador ou API continuam no CI.
