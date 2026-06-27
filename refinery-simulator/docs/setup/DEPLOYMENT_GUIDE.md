# DEPLOYMENT_GUIDE.md

## Deployment Options

### 1. Local Development

```bash
cd refinery-simulator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
# Open http://127.0.0.1:5001
```

### 2. Vercel (Serverless)

1. Push to GitHub
2. Import project in Vercel dashboard
3. Set environment variables
4. Deploy

Environment variables to set:
- `SECRET_KEY`
- `DATABASE_URL`
- `LLM_PROVIDER`
- `OLLAMA_URL`
- `OLLAMA_MODEL`

### 3. Railway

1. Connect GitHub repository
2. Railway auto-detects Dockerfile
3. Set environment variables
4. Deploy

### 4. Render

1. Create new Web Service
2. Connect GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn wsgi:app`
5. Set environment variables
6. Deploy

### 5. Docker

```bash
# Build
docker build -t rdis .

# Run
docker run -p 5001:5001 \
  -e SECRET_KEY=your-secret \
  -e DATABASE_URL=sqlite:///refinery.db \
  rdis
```

### 6. Fly.io

```bash
fly launch
fly deploy
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | (dev key) | Flask session secret |
| `DATABASE_URL` | No | `sqlite:///refinery.db` | Database URL |
| `LLM_PROVIDER` | No | `mock` | SLM provider |
| `OLLAMA_URL` | No | `http://localhost:11434/api/generate` | Ollama endpoint |
| `OLLAMA_MODEL` | No | `qwen2.5:1.5b` | Ollama model |
| `HF_MODEL_PATH` | No | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | HuggingFace model |

## Production Recommendations

1. **Database**: Migrate from SQLite to PostgreSQL for production
2. **HTTPS**: Use reverse proxy (nginx, Caddy) or platform SSL
3. **Logging**: Configure proper logging (not print statements)
4. **Monitoring**: Add health check monitoring
5. **Backups**: Schedule database backups
6. **Rate Limiting**: Add Flask-Limiter for API protection

## Troubleshooting

### Database Issues
- Ensure `refinery.db` exists and is writable
- Check `DATABASE_URL` environment variable

### Import Errors
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check Python version (3.11+)

### Port Issues
- Default port is 5001
- Change in `app.py` if needed
