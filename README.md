# Procurement Quote Platform

Compares supplier quotes, flags price increases, and automates approvals and reports.

## Status
- [x] Step 1: Suppliers, products, quotes API with tests
- [ ] Step 2: Quote comparison and ranking
- [ ] Step 3: Excel import and weekly report
- [ ] Step 4: Auth (JWT)
- [ ] Step 5: React dashboard
- [ ] Step 6: Docker, CI and deployment

## Run locally
```bash
python -m venv venv && source venv\Scripts\activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs to try the API.

## Run tests
```bash
pytest -v
```
