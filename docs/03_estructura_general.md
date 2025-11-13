moe-router-demo/
├─ README.md
├─ docs/
│  ├─ 00_overview_moe_router.md
│  ├─ 01_context_backend.md
│  └─ 02_context_frontend.md
├─ backend/
│  ├─ pyproject.toml              # o requirements.txt
│  ├─ README_backend.md
│  └─ app/
│     ├─ __init__.py
│     ├─ main.py                  # FastAPI
│     ├─ config/
│     │  ├─ __init__.py
│     │  └─ settings.py
│     ├─ core/
│     │  ├─ __init__.py
│     │  ├─ router_engine.py      # MoE router principal
│     │  └─ decision_rules.py     # reglas/heurísticas de enrutamiento
│     ├─ providers/
│     │  ├─ __init__.py
│     │  ├─ base_client.py
│     │  ├─ openai_client.py                # gpt-4o-mini
│     │  ├─ gemini_pro_client.py            # gemini-2.5-pro
│     │  └─ gemini_flash_image_client.py    # gemini-2.5-flash-image
│     ├─ models/
│     │  ├─ __init__.py
│     │  └─ schemas.py            # Pydantic: Request/Response
│     └─ metrics/
│        ├─ __init__.py
│        ├─ metrics_service.py    # calcular latencia, costo, score
│        └─ storage.py            # sqlite
└─ frontend/
   ├─ package.json
   ├─ README_frontend.md
   └─ src/
      ├─ main.tsx / main.jsx
      ├─ App.tsx / App.jsx
      ├─ components/
      │  ├─ QueryForm.tsx
      │  ├─ MetricsTable.tsx
      │  └─ RouterDecisionCard.tsx
      └─ services/
         └─ apiClient.ts
