# InventoryManagement-Django

**Django-based Inventory Management System**  

This repository contains the full source code for the InventoryManagement-Django project, a robust system for managing inventory, suppliers, purchases, and sales.

---

## Git & Project Setup

- **Repository:** [https://github.com/Habtom-great/InventoryManagement-Django](https://github.com/Habtom-great/InventoryManagement-Django)  
- **Branch:** `main`  
- **Status:** Project is fully committed and pushed to GitHub.  
- **Virtual Environment:** `venv/` is ignored via `.gitignore`.  
- **Dependencies:** Stored in `requirements.txt` for easy environment setup.  

---

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/Habtom-great/InventoryManagement-Django.git
cd InventoryManagement-Django
Setup Virtual Environment
bash
Copy code
python -m venv venv
source venv/bin/activate  # Mac
pip install -r requirements.txt
Run the Project
bash
Copy code
python manage.py runserver
Visit http://127.0.0.1:8000/ in your browser to view the project.

Project Structure
graphql
Copy code
InventoryManagement-Django/
│
├── core/                 # Core app with settings and URLs
├── homepage/             # Homepage app
├── inventory/            # Inventory management app
├── transactions/         # Suppliers, purchases, sales
├── manage.py             # Django project entry point
├── requirements.txt      # Python dependencies
├── README.md             # Project info and setup
└── .gitignore            # Ignored files like venv/
yaml
Copy code

Save the file:

- In **VSCode:** `Cmd + S`  
- In **nano:** `Ctrl + X`, then `Y`, then `Enter`

---

### 5️⃣ Stage, commit, and push to GitHub

```bash
git add README.md
git commit -m "Add professional README with project overview and structure"
git push
