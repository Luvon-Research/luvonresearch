# Luvon Research Project
This is a web-based spreadsheet application with both client and server components.
## Prerequisites
- Node.js (v16 or higher)
- npm package manager
- Python 3.11+
## Getting Started
### Setting up the Environment
1. Clone the repository
2. Create a `.env` file in the server directory (see `.env.example` for required variables)
### Running the Server
1. Navigate to the server directory:
   ```bash
   cd server
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
### Running the Client
1. Navigate to the client directory:
   ```bash
   cd client
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
### Running the YJS Server
1. Navigate to the client directory:
   ```bash
   cd yjs-server
   ```
2. Install dependencies:
   ```bash
   npm install
   ```