
# Sasya Arogya MCP

A FastAPI-based MCP Agent Server for providing plant insurance recommendations.

## Project Structure

```
sasya-arogya-mcp/
│
├── requirements.txt
├── README.md
├── main/
│   ├── app.py
│   ├── mcp_server.py
│   └── services/
│       └── insurance_advisor.py
```

## Installation

1. **Clone the repository:**
	```powershell
	git clone https://github.com/cds-9-group-6/sasya-arogya-mcp.git
	cd sasya-arogya-mcp
	```

2. **Create a virtual environment (recommended):**
	```powershell
	python -m venv venv
	.\venv\Scripts\activate
	```

3. **Install dependencies:**
	```powershell
	pip install -r requirements.txt
	```

## Running the Application

From the project root, run:

```powershell
python -m main.app
```

The FastAPI server will start at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## API Documentation (Swagger UI)

Once the server is running, you can access the interactive API documentation (Swagger UI) at:

- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

This interface allows you to explore and test the API endpoints directly from your browser.

## API Usage

- **Endpoint:** `/insurance/`
- **Method:** GET
- **Query Parameter:** `disease` (Name of the plant disease)

**Example:**
```
GET http://127.0.0.1:8000/insurance/?disease=Powdery%20Mildew
```
