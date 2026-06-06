# Frontend

React + TypeScript + Vite frontend for the malicious traffic detection system.

## Current pages

- Overview dashboard
- Detection workflow
- Traffic replay
- Blacklist management
- Model metrics
- System settings

## Local development

```bash
npm install
npm run dev
```

## Production build

```bash
npm run build
```

## Backend requirement

The frontend expects the FastAPI backend to be running at `http://127.0.0.1:8000`.

Vite proxy is already configured for `/api` requests in `vite.config.ts`.
