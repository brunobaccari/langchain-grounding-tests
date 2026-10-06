# LangChain — context and response contracts

[Versão em português](README.md)

Tests for an LCEL chain answering questions about synthetic refund policies. The focus is integration: selecting current documents for the right product, building messages and validating structured output. Models are LangChain's `FakeListChatModel` and explicit test doubles; **no real provider or model is called**.

## Run

Python 3.12 or newer.

```bash
python -m venv .venv
# Activate .venv before the following commands
python -m pip install -r requirements.txt
cp .env.example .env
python -m pytest --junitxml=results/junit.xml
```

Windows: `.venv\Scripts\Activate.ps1` and `Copy-Item .env.example .env`. Linux/macOS: `source .venv/bin/activate`. `QA_CORPUS_PATH` points to the local synthetic JSON corpus; process environment variables take precedence. No API key or external account required.

## What blocks the run

| Risk | Check |
| --- | --- |
| Revoked or wrong-product policies enter the context | Inspect messages sent to the chain |
| No applicable document | Abstain before calling the model |
| Invented, revoked or wrong-product reference | Reject sources outside the selected set |
| String deadline, negative number, extra field or inconsistent decision | Strict Pydantic parser without response repair |
| Document command becomes a system instruction | Inspect message roles and content |
| One call leaks context into the next | Different products using the same chain |
| Timeout becomes a valid abstention | Propagate the error without fabricating output |

The corpus rejects duplicate IDs, invalid fields and empty collections. Scripted responses isolate orchestration behavior. The document-command test checks the message boundary; it does not establish an LLM's resistance to prompt injection.

## Results and decisions

[Actions](https://github.com/brunobaccari/langchain-grounding-tests/actions) publishes a per-test summary and the `results` artifact with JUnit, retained for 14 days. Failures, skips, missing reports and incomplete counts block CI. `python scripts/summary.py --self-test` checks the parser. Outputs stay out of Git.

When changing a rule, update the synthetic document and its test together; do not relax the parser to approve invalid output. After offline approval, a real model evaluation and manual review of deadline support would still be needed. A valid schema and an allowed reference do not prove that semantic relationship.

No vector search, ranking, persistent memory, vendor benchmark or live evaluation. Selection uses exact metadata. References: [LangChain testing](https://docs.langchain.com/oss/python/langchain/test) and [native fake models](https://reference.langchain.com/python/langchain-core/language_models/fake_chat_models).
