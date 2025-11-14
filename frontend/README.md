## Frontend: COPD Lung Sound Dashboard

### Prerequisites
- Node.js 18+
- Backend API running at `http://localhost:8000` (configurable)

### Environment
Create `.env.local` in this directory:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Install & Run
```bash
npm install
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) for the interactive dashboard.

### Key Screens
- **Upload panel**: drag-and-drop audio, progress feedback, error handling.
- **Current prediction**: live polling, confidence & probability breakdown.
- **History**: latest 10 predictions with timestamps and outcomes.

### Tech Notes
- Next.js App Router with Tailwind CSS styling.
- Client-side polling with Fetch API; ready for WebSocket upgrade.
- Types defined inline for quick iteration; consider extracting to `src/types`.

### Next Steps
- Add authentication flow (Keycloak/Auth0).
- Implement WebSocket channel for real-time inference updates.
- Localize UI copy and provide accessibility enhancements.
