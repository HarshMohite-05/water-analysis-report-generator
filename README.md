# Water Analysis Report Generator

Streamlit application for Nirmaan WaterTech Solutions to prepare water analysis reports for Mumbai and Ahmedabad offices.

## Features

- Employee login and Admin/Director directory management
- Custom employee roles and client assignments
- Parameter selection, sample results, and editable remarks
- Optional Groq AI remark refinement
- Office-specific DOCX templates, seals, report previews, and PDF generation
- Saved report history and audit records

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Install LibreOffice for PDF conversion. Put the private employee and client workbooks in `database/Employee Data.xlsx` and `database/Client Data.xlsx`. These files are intentionally not included in this repository. Employee credentials come from the private employee workbook; there is no public default login.

For optional AI remarks, configure `GROQ_API_KEY` locally or in your hosting provider's secret settings. The default `AI_MODEL` is `openai/gpt-oss-20b`. Never commit API keys.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Streamlit Community Cloud configuration, private dataset provisioning, and persistence limitations.

This app is not configured for direct deployment to Vercel. It runs a Streamlit server, uses LibreOffice, and writes SQLite data and report files. A Vercel deployment requires adapting the application architecture and storage, rather than only adding a configuration file.

## Tests

```bash
python -m pytest -q
```

Tests use temporary employee/client fixtures instead of production datasets.

## Private files

`.gitignore` excludes `.env`, API secrets, employee/client spreadsheets, SQLite databases, generated reports, backups, and local fonts. Provision these separately on the deployment host.
