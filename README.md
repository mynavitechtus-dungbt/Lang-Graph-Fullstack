# my-agent

LangGraph agents với Next.js frontend (CopilotKit).

## Yêu cầu

- **Python 3.12+**
- **Node.js** (cho frontend)
- **UV** – quản lý dependency và môi trường Python

## Cài đặt UV

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Hoặc dùng Homebrew (macOS):

```bash
brew install uv
```

### Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Kiểm tra đã cài xong:

```bash
uv --version
```

## Thiết lập project

### 1. Clone và vào thư mục

```bash
cd my-agent
```

### 2. Tạo virtual environment và cài dependency (UV)

UV đọc `pyproject.toml` và `uv.lock` để đồng bộ môi trường:

```bash
uv sync
```

Lệnh này sẽ:

- Tạo `.venv` nếu chưa có
- Cài đúng phiên bản dependency theo lock file
- Dùng Python 3.12 theo `langgraph.json` / `pyproject.toml`

```

Hoặc kích hoạt shell trong `.venv` rồi chạy bình thường:

```bash
source .venv/bin/activate   # macOS/Linux
# hoặc:  .venv\Scripts\activate   # Windows

npx @langchain/langgraph-cli dev --port 8123 --no-browser
```

### 3. Biến môi trường

Tạo file `.env` ở thư mục gốc (và nếu cần `frontend/.env` cho frontend):

```bash
cp .env.example .env
```

Sửa `.env`, thêm (ví dụ):

```
OPENAI_API_KEY=sk-...
LANGGRAPH_API_KEY=...   # nếu dùng LangGraph API
```
Cấu hình graph nằm trong `langgraph.json` (package_manager: uv, graphs: basic_agent, human_in_the_loop).

### 4. Frontend (Next.js + CopilotKit)

```bash
cd frontend
npm install
npm run dev
```

Mở http://localhost:3000 (hoặc cổng Next hiển thị).

## Cấu trúc chính

| Thành phần        | Mô tả |
|-------------------|--------|
| `pyproject.toml`  | Dependency Python, project metadata |
| `uv.lock`         | Lock phiên bản dependency (nên commit) |
| `langgraph.json`  | Cấu hình LangGraph, graphs, dùng UV |
| `basic_agent.py`  | Graph đơn giản (chat với LLM) |
| `human_in_the_loop.py` | Graph human-in-the-loop với bước thực thi |
| `frontend/`       | Next.js + CopilotKit UI |

