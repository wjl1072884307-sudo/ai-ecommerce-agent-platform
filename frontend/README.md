# Frontend

Vue3 + Vite frontend for the AI ecommerce customer service and after-sales Agent platform.

## Setup

Install dependencies:

```bash
npm install
```

Run local dev server:

```bash
npm run dev
```

Build production assets:

```bash
npm run build
```

## API Proxy

Vite proxies `/api` requests to the backend:

```text
http://127.0.0.1:8000
```

Start the backend before opening the Dashboard so the API status card can call `/api/health`.

