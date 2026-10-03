# Streamlit Community Cloud deployment

The app entry point is `app.py`. Use branch `main` in a private GitHub repository.
`packages.txt` installs Linux LibreOffice for PDF conversion. Python dependencies
are listed in `requirements.txt`. Select Python 3.11 in Advanced settings; the
current local test environment uses Python 3.9, so a Cloud build remains required.

## Private employee and client datasets

Do not commit `.env`, Excel data files, SQLite databases, generated reports, backups,
or secrets. These paths are excluded by `.gitignore`.

Run `.venv/bin/python scripts/prepare_cloud_secrets.py` locally. This creates
`storage/deployment/secrets.toml` with an encoded snapshot of both workbooks.
Employee passwords in this snapshot are hashed. The original workbooks are not
modified. The snapshot still contains private employee/client data: do not share
it publicly or commit it.

In Streamlit Community Cloud, create the app from the repository and paste this
file's contents into Advanced settings > Secrets. Add an `GROQ_API_KEY`
there only if AI remark refinement is desired. No API key is required for manual
remarks or PDF generation.

AI remarks use Groq's `openai/gpt-oss-20b` by default. For local use, set
`GROQ_API_KEY` in `.env` and `AI_MODEL=openai/gpt-oss-20b`, then restart the app.
For Cloud, set these values in Secrets. Use a Groq API key from https://console.groq.com/keys.

On a clean start, the app restores missing workbooks from Secrets and initializes
its database. It preserves existing runtime workbooks to avoid overwriting admin
edits. To replace the initial dataset snapshot, update Secrets and use a fresh
runtime/redeployment. Local workbook edits do not automatically update Cloud.

## Limitations before production use

Community Cloud does not guarantee local-file persistence. Current SQLite report
history, generated PDFs and Admin Panel workbook changes can be lost on rebuild
or runtime replacement. Permanent business use needs an external database plus
object storage and an updated directory storage adapter. This has not yet been
configured. Downloading a PDF saves a copy to the user's computer, not durable
server history.

Times New Roman is installed on the development Mac, but is not supplied by the
Linux package configuration. Without appropriately licensed fonts installed on
the cloud host, LibreOffice substitutes a serif font. DOCX font declarations stay
unchanged, but PDF line wrapping can differ. Verify the cloud PDFs before use.
Do not commit or redistribute fonts copied from the Mac without permission.

## Publishing

A GitHub connection/account and repository destination are still required. Local
Git initialization is not a GitHub publication. After publication, deploy with:

- Repository: the chosen private repository
- Branch: `main`
- Main file: `app.py`
- Secrets: the private deployment snapshot described above

Verify login, both offices, preview and PDF generation on the deployed Linux app.

Sources:
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- https://docs.streamlit.io/develop/concepts/connections/connecting-to-data
