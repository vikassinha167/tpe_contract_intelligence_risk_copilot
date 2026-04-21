# Contract Intelligence Risk Copilot
A system that ingests contracts (PDFs, Emails, Scans), extracts structured clauses  (using Azure Document Intelligence), enriches with semantic understanding (using Azure Language), stores &amp; indexes knowledge (using Azure Search + SQL + Blob Storage) and enables conversational querying (Azure Open AI via Foundry) with RAI guardrails implementation.


# Creating Virtual Environment and Installing all dependencies - Step by step instructions

### Open the Terminal in VS Code:

In your Codespace, open the integrated terminal (View > Terminal or Ctrl+`).
Navigate to Your Project Root (if not already there):

cd /workspaces/tpe_contract_intelligence_risk_copilot

### Create the Virtual Environment:

Run the following command to create a virtual environment named venv in your project folder:

python -m venv venvsource venv/bin/activate

This creates a venv/ directory in your project root with the isolated environment.
Activate the Virtual Environment:

### Activate it using:

source venv/bin/activate

Your terminal prompt should now show (venv) at the beginning, indicating it's active.

### Install Dependencies (if applicable):

If you have a requirements.txt file (or plan to create one), install packages:

pip install -r requirements.txt

For your Azure-based project, you might need to install Azure SDKs later, e.g., pip install azure-ai-documentintelligence azure-ai-textanalytics azure-search-documents.

### Deactivate When Done (optional):

To exit the virtual environment:

deactivate

## Additional Notes
1. The venv/ folder should be added to your .gitignore to avoid committing it to Git.
2. In GitHub Codespaces, Python 3 is typically pre-installed, but if you encounter issues, run python --version to confirm.
3. For your project, consider creating a requirements.txt file to list dependencies like Azure SDKs and any ML libraries.