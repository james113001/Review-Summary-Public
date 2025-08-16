# Review-Summary  

A FastAPI-based backend that collects and summarizes items. Reviews are stored in a PostgreSQL database, and summaries are generated using a local [Ollama](https://ollama.com/) model `mistral`.

---

## 🚀 Features

- Submit and store detailed reviews
- Generate natural language summaries using LLM
- FastAPI for RESTful endpoints
- PostgreSQL as the backend database
- Docker support for consistent setup

---

## 🛠️ Prerequisites

Before you begin, make sure you have the following installed:

- [Docker](https://www.docker.com/)
- [Ollama](https://ollama.com/) installed locally
- Pull the model you'll be using:

  ```bash
  ollama pull mistral
  ```

- Python 3.11+ (optional, for local development)

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory of your project:

```env
POSTGRES_USER=youruser
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=yourdb
DB_HOST=yourdb
DB_PORT=yourport
```

This is used by both the FastAPI app and the PostgreSQL database.

---

## 🐳 Running the Dockerized App

### 1. Build and Start Containers

Run this from the root of your project:

```bash
docker-compose up --build
```

This will:

- Build the FastAPI container (`web`)
- Start PostgreSQL using the official `postgres:16` image
- Mount and initialize the database from `docker-entrypoint-initdb.d/`
- Run your FastAPI app at `http://localhost:8000`
- Arbitrarily set port as 15432 to avoid conflict with 5432- you may need to set a different port in yml if you're already using 15432 

### 2. Start Ollama (Locally)

**Ollama must be installed and running on your host machine**, not inside Docker.

Start it separately:

```bash
ollama serve
```

Ensure you’ve pulled the required model (e.g. mistral):

```bash
ollama pull mistral
```

---

## 🔎 API Access

Once running:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📁 Project Structure

```
.
├── app/
│   ├── main.py                  # FastAPI routes
│   ├── db.py                    # DB connection and insert functions
│   └── summarize.py             # Ollama summarizer logic
├── docker-entrypoint-initdb.d/
│   ├── 01-schema.sql     # SQL setup
│   └── 02-seed.sql       # Sample data         
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
└── README.md
```

---

## 🧪 Local Development (Optional)

If you're not using Docker, you can run the app locally like this:

```bash
python -m venv venv
source venv/bin/activate    # or 'venv\Scripts\activate' on Windows

pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 🔐 Security To-Do

- Add authentication (JWT, OAuth)
- Use HTTPS via reverse proxy like Nginx
- Salt + hash passwords securely
- Disable direct DB port access in production

---

## 👥 Contributors

- **Data Science** – James Kim
- **Backend** – Austin Myers
- **Cybersecurity** – Xavier Gutter
- **Design/UX** – Chavis Ferguson

---

## 📝 License

This project is private and proprietary. All rights reserved.

---

## 📬 Feedback

Feel free to open issues or pull requests for improvements or bugs.
