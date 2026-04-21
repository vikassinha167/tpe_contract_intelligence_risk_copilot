# Contract Intelligence & Risk Scoring — Multi-Agent Enterprise Solution

An end-to-end, **teaching-grade** Python reference implementation of a multi-agent
Contract Intelligence & Risk Scoring system built on **Azure AI Foundry**.

The codebase is intentionally written to demonstrate **SOLID** principles, clean
architecture, and clear separation of concerns so it can be used as a learning
artifact as well as a production starting point.

---

## Contract Intelligence Risk Copilot
A system that ingests contracts (PDFs, Emails, Scans), extracts structured clauses  (using Azure Document Intelligence), enriches with semantic understanding (using Azure Language), stores &amp; indexes knowledge (using Azure Search + SQL + Blob Storage) and enables conversational querying (Azure Open AI via Foundry) with RAI guardrails implementation.


## Creating Virtual Environment and Installing all dependencies - Step by step instructions

### Open the Terminal in VS Code:

In your Codespace, open the integrated terminal (View > Terminal or Ctrl+`).
Navigate to Your Project Root (if not already there):

cd /workspaces/tpe_contract_intelligence_risk_copilot

### Create the Virtual Environment:

Run the following command to create a virtual environment named .venv in your project folder:

python -m venv .venv

This creates a venv/ directory in your project root with the isolated environment.


### Activate the Virtual Environment:

source .venv/bin/activate

Your terminal prompt should now show (.venv) at the beginning, indicating it's active.

### Install Dependencies (if applicable):

If you have a requirements.txt file (or plan to create one), install packages:

pip install -r requirements.txt

For your Azure-based project, you might need to install Azure SDKs later, e.g., pip install azure-ai-documentintelligence azure-ai-textanalytics azure-search-documents.

### Deactivate When Done (optional):

To exit the virtual environment:

deactivate

## Additional Notes
1. The .venv/ folder should be added to your .gitignore to avoid committing it to Git.
2. In GitHub Codespaces, Python 3 is typically pre-installed, but if you encounter issues, run python --version to confirm.
3. For your project, consider creating a requirements.txt file to list dependencies like Azure SDKs and any ML libraries.
---------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------
## 1. Use case

Enterprises receive thousands of contracts (MSAs, SOWs, NDAs, vendor agreements).
Manual review is slow, inconsistent, and risky. This solution:

1. **Ingests** contracts (PDF/DOCX/scanned) from Azure Blob Storage.
2. **Extracts** raw text + structure using Azure **Document Intelligence**.
3. **Detects entities, key phrases, PII** via Azure **Language Service**.
4. **Indexes** the contract into Azure **AI Search** for hybrid retrieval.
5. **Analyzes clauses** (termination, liability, indemnity, IP, payment, SLA, GDPR,…)
   using an LLM agent backed by Azure **OpenAI**.
6. **Scores risk** (Low / Medium / High / Critical) with rationale per clause and
   an aggregated contract-level score.
7. **Checks compliance** against a configurable policy set.
8. **Summarizes** the contract into an executive brief.
9. **Persists** structured results into Azure **SQL**.
10. Every LLM call is wrapped with **Azure AI Content Safety / Guardrails** and
    evaluated by Azure AI **Evaluators** (groundedness, relevance, coherence).

## 2. Architecture (clean / hexagonal)

```
                          ┌────────────────────────────┐
                          │       OrchestratorAgent     │
                          └──────────────┬─────────────┘
                                         │
   ┌────────────┬───────────────┬────────┼────────┬───────────────┬────────────┐
   ▼            ▼               ▼        ▼        ▼               ▼            ▼
Ingestion   Extraction    Language    Indexing  Clause         Risk        Compliance
  Agent       Agent         Agent      Agent    Analysis       Scoring       Agent
                                                  Agent          Agent
                                         │
                                         ▼
                                Summarization Agent
                                         │
                                         ▼
                                 SQL Persistence

src/
 ├─ domain/         Pure business entities & value objects (no Azure imports)
 ├─ interfaces/     Abstract Ports — agents depend on these (DIP)
 ├─ infrastructure/ Concrete Adapters wrapping Azure SDKs
 ├─ agents/         One agent = one Single Responsibility
 ├─ services/       Pipeline + Dependency Injection container
 └─ utils/          Cross-cutting concerns (retry, exceptions)
```

## 3. SOLID mapping

| Principle | Where it lives |
|-----------|----------------|
| **S**RP   | Each agent does **one** thing (e.g. `RiskScoringAgent` only scores). |
| **O**CP   | Add a new agent or new storage backend by implementing an interface — no edits to existing code. |
| **L**SP   | All adapters honour their interface contracts so they can be swapped (e.g. `LocalBlobStorage` for tests). |
| **I**SP   | Interfaces are small & focused (`IDocumentProcessor`, `ILlmClient`, `ISecretProvider`…). No fat interfaces. |
| **D**IP   | Agents depend on **abstractions** in `interfaces/`. The DI container wires concretes. |

## 4. Quick start

```powershell
cd contract_intelligence
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # fill in your Azure endpoints
python main.py --blob-name "sample_msa.pdf"
```

## 5. Testing

```powershell
pytest -q
```

Unit tests use **fakes** that implement the same interfaces as Azure adapters —
proving DIP/LSP work in practice.
