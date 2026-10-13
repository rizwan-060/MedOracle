# MedOracle: project brief

Condensed from the approved FYP proposal. This is the source of truth for what the system does. Qarshi University, Lahore, BS Computer Science. Team: Rizwan Ahmed (group leader, backend and agent orchestration), Hadia Fatima (Flutter app, Symptom Analysis Agent), Mahnoor Fatima (database, Medical History and Laboratory agents, forecasting, counterfactuals, doctor dataset).

## What it is
A mobile-first healthcare platform that moves care from reactive diagnosis to proactive prevention. Instead of one AI model, a team of specialised agents each analyse a different dimension of a patient's health, then debate and reach a consensus that is explainable. It is a preventive decision-support assistant and not a replacement for medical advice.

**Users:** people aged 25 to 65 with chronic conditions or risk factors (family history of diabetes, heart disease, hypertension), health-conscious individuals, people with limited access to specialists. Secondary: general practitioners wanting a second opinion, clinics, medical students.

**Core research contribution:** a Dynamic Multi-Agent Consensus Framework with Agent Debate, plus disease trajectory forecasting (30 days, 6 months, 1 year) and a counterfactual health simulator.

## Architecture (three layers)
1. **Flutter client** (`frontend/`): symptom input, medical history, lab values (optional photo upload), risk timelines, reasoning graphs, counterfactual scenarios, authentication.
2. **FastAPI backend** (`backend/`): REST endpoints, agent pipeline orchestration, LLM routing, database access, background processing.
3. **Agent ecosystem**: LLM-powered agents communicating through structured JSON messages over LangGraph.

## Agent communication model
Every agent has five properties: **Role, Knowledge Base, Confidence Score (0 to 100%), Reasoning Chain, Challenge Protocol**. Agents pass structured JSON. They never see each other's internal prompts, only each other's outputs and confidence scores. This prevents sycophancy cascades where one agent simply agrees with another.

## Modules
1. **Symptom Analysis Agent**: natural-language understanding of symptoms, severity classification, symptom-cluster detection, initial disease-category mapping.
2. **Medical History Agent**: contextualises the presentation against personal and family history, hereditary risk multipliers, lifestyle-to-disease correlations.
3. **Laboratory Analysis Agent**: interprets lab values against reference ranges, trend analysis, correlates lab findings with the symptom cluster.
4. **Risk Prediction Agent**: combines agents 1 to 3 with validated clinical models (Framingham, FINDRISC, CKD-EPI) for quantified risk at 30-day, 6-month and 1-year horizons.
5. **Consensus and Debate Agent** (core contribution): five-step protocol: (1) evidence submission, (2) contradiction detection, (3) challenge round, (4) confidence adjustment, (5) consensus resolution.
6. **Explainable Reasoning Engine**: turns every conclusion into a traceable reasoning chain, delivered as a structured narrative and a node-connection graph for the app.
7. **Disease Trajectory Forecasting**: projected health path if nothing changes, over 30 days, 6 months and 1 year.
8. **Counterfactual Health Simulator** (simplified): how lifestyle changes (daily walking, dietary change, smoking cessation) change the predicted trajectory. At least three interventions.
9. **Doctor Recommendation Module**: after the consensus verdict, matches disease category and urgency to a specialty (high cardiovascular risk to cardiologists, high FINDRISC to endocrinologists or diabetologists), then ranks nearby doctors from a directory by specialty match and proximity. Exists to direct the patient to a real clinical second opinion.

## Technology
- **Frontend:** Flutter, `fl_chart`, `graphview`, `dio`, `riverpod`, `flutter_secure_storage`.
- **Backend:** Python, FastAPI, Uvicorn, LangGraph, LangChain, Pydantic, SQLAlchemy, Alembic, Celery with Redis, authentication.
- **LLMs:** Groq (LLaMA 3.3 70B for complex reasoning agents, LLaMA 3.1 8B for structured, lower-complexity agents) as primary. Google Gemini Flash as backup.
- **Database:** PostgreSQL on Supabase free tier. Stores users, medical history, lab results, sessions, agent outputs. (Neo4j knowledge graph is a stretch goal and out of scope.)
- **Deployment (development):** Render.com for the backend, Supabase for the database, GitHub for version control.

## Data strategy
No models are trained from scratch. Validated clinical formulas (Framingham, FINDRISC, CKD-EPI) are the quantitative backbone, LLM agents add reasoning on top, and public datasets are used for validation and testing:
- UCI Heart Disease (303 records, 14 attributes)
- PIMA Indians Diabetes (768 records)
- Framingham Heart Study (4,200+ longitudinal records)
- MIMIC-III (de-identified ICU records, needs PhysioNet registration)
- Public symptom-to-disease mapping datasets from Kaggle

The Doctor Recommendation Module needs a directory of doctors (name, specialty, clinic or hospital, city or area, contact). The team will look for a public dataset first and compile one from public doctor listings if none fits. Specialty labels must use the same schema as the Risk Prediction and Consensus agents.

## MVP scope
**In scope:** Symptom, Medical History, Laboratory, Risk Prediction and Consensus and Debate agents; Explainable Reasoning Engine; Trajectory Forecasting; simplified Counterfactual Simulator; Doctor Recommendation Module; Flutter app; FastAPI backend; PostgreSQL; user authentication.

**Out of scope (future work):** full Health Digital Twin simulation, live medical-literature research agent (continuous RAG), Neo4j knowledge graph, community pattern discovery, wearable integration, HL7/FHIR interoperability, iOS App Store deployment, cloud-scale deployment.

## Success criteria
- Flutter app captures symptoms, history and lab values and shows risk predictions, reasoning graphs and counterfactual scenarios.
- FastAPI backend runs the Symptom, History, Lab, Risk and Consensus agents through LangGraph, each producing structured, confidence-scored output.
- Contradictory agent conclusions are detected, challenged and resolved through the formal debate protocol.
- Trajectory forecasting over 30 days, 6 months and 1 year using Framingham and FINDRISC.
- Counterfactual simulator quantifies at least three lifestyle interventions.
- Agent outputs validated against UCI Heart Disease, PIMA Indians Diabetes and Framingham.
- Doctor Recommendation Module presents specialty-matched nearby doctors after the final verdict.

## Timeline (12 months)
- Phase 1, months 1 to 3: repository, DB schema, FastAPI skeleton, basic Flutter screens, Groq integration, Symptom agent.
- Phase 2, months 4 to 6: Medical History and Lab agents, Risk Prediction agent, LangGraph pipeline, Flutter to backend integration.
- Phase 3, months 7 to 9: Consensus and Debate agent, Explainable Reasoning Engine, trajectory, counterfactuals, doctor module.
- Phase 4, months 10 to 12: end-to-end testing, UI polish, performance, security review, report, demo.

## Known limitations of existing tools (what MedOracle answers)
Single-model health tools give unexplained percentages, no multi-perspective challenge, no forecasting, and no "what would reduce this risk" simulation. MedOracle addresses each of these.
