# Contract Intelligence & Risk Scoring — Multi-Agent Enterprise Solution

An end-to-end, Python reference implementation of a multi-agent
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

This creates a .venv/ directory in your project root with the isolated environment.


### Activate the Virtual Environment:

source .venv/bin/activate

Your terminal prompt should now show (.venv) at the beginning, indicating it's active.

### Install Dependencies (if applicable):

Run following command to install all dependencies - 

pip install -r requirements.txt

### Deactivate When Done (optional):

To exit the virtual environment:

deactivate

## Additional Notes
1. The .venv/ folder should be added to your .gitignore to avoid committing it to Git.
2. In GitHub Codespaces, Python 3 is typically pre-installed, but if you encounter issues, run python --version to confirm.
---------------------------------------------------------------------------------------

### Install Azure CLI 

Run following command in terminal after activating your .venv

curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

Check the installed version of az

az version

Once the above command shows azure-cli version, type in below command 

az login

This will open a browser and ask you to sign in by pasting the code which it generates and then caches the credentials locally.

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

Create a copy of .env.example file and rename it to .env
Fill in your Azure endpoints and other values in .env file
Push one or two sample contract into blob container

```powershell
python main.py --blob-name "<ContractFileName.pdf>"
```

## RBAC Permissions (Steps to resolve `403 AuthorizationPermissionMismatch` error) with Azure Storage account

If the Ingestion agent fails with "403 AuthorizationPermissionMismatch" error, follow the below process - 
1. Open Azure Storage account 
2. Make container from Private to Public , if allowed.
3. If not, then open IAM of storage account and click on "Add - > Add Role Assignment".
4. Search for "Storage Blob Data Contributor", select this option and move next.
5. Add your identity (since we are running on azure Default Credentials) else add Service Principal identity.

## Forbidden (Steps to resolve `Operation returned an invalid status 'Forbidden'` error) with Azure AI Search Index

If the Ingestion agent fails with "403 AuthorizationPermissionMismatch" error, follow the below process - 
1. Open Azure AI Search Index 
2. Open IAM of storage account and click on "Add - > Add Role Assignment".
4. Search for "Search Service Contributor", select this option and move next.
5. Add your identity (since we are running on azure Default Credentials) else add Service Principal identity.

## 5. Testing

```powershell
pytest -q
```

Unit tests use **fakes** that implement the same interfaces as Azure adapters —
proving DIP/LSP work in practice.
