# 📁 Portfolio Builder App

A simple web-based Portfolio Builder where users can:
- 👤 Register/Login
- 🧱 Build portfolios using predefined templates
- 🖼️ Include text, images, timelines, tools, and outcomes
- 💼 View their own portfolios (My Portfolios)
- 🌐 Explore Public Portfolios
- ❤️ Like portfolios (1 per user)
- 👁️ Track portfolio views and likes (views only count if viewer ≠ owner)

---

## 🔧 Technologies Used

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Database**: MongoDB
- **API Testing**: Requests

---

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/portfolio-builder.git
cd portfolio-builder
```

### 2. Start MongoDB

Make sure MongoDB is running locally on port 27017.

### 3. Set up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 4. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 5. Start Backend
```bash
uvicorn backend.main:app --reload
```

### 6. Start Frontend
In a new terminal:
```bash
streamlit run frontend/app.py
```

---

## 🌍 Deployment

Deploy Backend on platforms like **Render**. Make sure to:
- Set MongoDB connection string as environment variable
- Allow CORS for frontend-backend interaction

Deploy Frontend on platforms like **Streamlit Cloud**. Make sure to:
- Set backend API endpoint(render url) as environment variable
- Some times the streamlit cloud may take timee loading due to the inactivity of render after 50s.

---

## 📄 Folder Structure

```
📁 backend/
    └── main.py
    
📁 frontend/
    └── app.py
    └── templates/
requirements.txt
```

---

## 🧑‍💻 Authors

- Vighnesh ms

