Backend README
--------------
1. Create virtualenv:
   python -m venv .venv
   source .venv/bin/activate   (Windows: .\.venv\Scripts\Activate.ps1)

2. Install:
   pip install --upgrade pip
   pip install -r requirements.txt

3. Initialize and create sample data:
   python db_init.py
   python sample_data.py

4. Run:
   python app.py
   -> API at http://localhost:8000
