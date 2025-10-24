# Operator High-Frequency Interactions Plan (BMOS)

Purpose: Define what the business operator frequently does with the system, how to interact (UX patterns), what tools/APIs are invoked behind the scenes, and how we deliver the MVP then enhance.

## 1. Scenarios & Interaction Catalog

### 1.1 Data
- Import & mapping: Import CSV/Excel → field mapping to dim/fact tables → data-quality report → commit
- Data quality & clarification: Flag outliers/duplications → operator confirms/clarifies → audit trail
- Threshold & subscription: Set KPI thresholds (e.g., efficiency < 80%) → notifications (email/in-app)

### 1.2 Understanding
- Indicator explanation: Why did sales drop? Break down by time/channel/SKU/customer segment
- Association & attribution: Show Shapley TOP contributors for a campaign/order/period
- Bottleneck (TOC): Identify current system constraint; estimate global effect if improved by X%

### 1.3 Decision
- Option generation: 3 plans (cost-down/efficiency-up/growth) + expected impact/risks
- Decision creation & OGSM: Create decision → decompose to department/team → assign owners
- KPI commitment & tracking: Set quarterly target and weekly tracking view

### 1.4 Operations
- Backtest & sandbox: Simulate changes (budget +20%) and compare plans
- Auto cycle: Weekly run of value-chain analysis; auto-trigger when KPI breaches
- Collaboration & annotation: Add comments/mentions on a node and notify stakeholders

## 2. Interaction Modes (How to Interact)

- Conversational Copilot
  - Natural language intents: explain/compare/diagnose/attribute/simulate/createDecision/subscribe
  - Context binding: current page + selected nodes + time window + filters
  - Tool-calls: invoke analysis/import/decision APIs; return actionable cards (chart + CTA buttons)
- In-view inline actions
  - Right-click/hover menus on charts: drill-down/compare/set-threshold/create-decision/annotate
  - Metric cards: quick actions (Explain, Alert, Add to Sandbox)
- Command palette (Ctrl/⌘+K) shortcuts
- Wizards for structured flows: Import & Decision creation (OGSM)
- Notification inbox: Alerts, pending evaluations, metric confirmations, decision approvals

## 3. Typical End-to-End Flows

- Discover → Explain → Decide: Alert on low efficiency → Explain with root causes → Create optimization decision
- Data → Insight: Import campaign spend → quality report → update Sankey → Copilot summarizes marginal gains
- Sandbox: Increase social budget by 20% → ROI impact & bottleneck shift → save as Plan B with tracking

## 4. Standard Prompts → Tools Mapping

| Prompt (examples) | Tool-call | Output |
|---|---|---|
| "Explain why conversion dropped last week" | explain({kpi,time,filters}) | Chart + narrative + factors |
| "Run TOC diagnosis" | diagnose({valueChain, period}) | Bottleneck node + improvement list |
| "Compute Shapley attribution for Q3" | attribute({period, touchpoints}) | Top contributors + confidence |
| "Create decision: New product trial" | createDecision({OGSM, owners, KPI}) | Decision card + links |
| "Set alert: efficiency < 0.8" | subscribeMetric({kpi, threshold, recipients}) | Alert rule + test |
| "Simulate social +20%" | simulate({variable, delta, window}) | Sandbox result + compare |

Backends to call: Supabase Edge Functions
- value-chain-sankey: return {nodes,links}
- shapley-attribution: return {values}
- toc-bottleneck: return {bottleneckId, suggestions}
- decision-cycle: create execution & evaluation task
- data-import: parse/mapping/clean/commit

## 5. MVP Delivery (2 weeks)

- Week 1
  - Floating chat window (draggable/resizable, localStorage memory)
  - Copilot intents: Explain / Diagnose(TOC) / Attribute(Shapley) / Create Decision (stubs to EF)
  - Inline actions on Dashboard & Value Chain: Explain, Set threshold, Create decision
  - SQL views for Sankey (07_value_chain_views.sql) + EF spec ready
- Week 2
  - Edge Function: value-chain-sankey → front-end switch from mock
  - Decision creation wizard (OGSM minimal)
  - Alert subscription rule + inbox

## 6. Acceptance Criteria

- Conversational: latency < 2s for simple explain; actionable cards with chart + CTA
- Inline: right-click menu available on nodes/links; threshold saved and applied
- Data: SQL views compiled; EF returns Sankey JSON consumed by UI
- Decision: created card visible, OGSM fields saved, KPI tracking initialized

## 7. Security & Audit

- Role-based permissions: Owner/Manager/Analyst/Viewer
- Audit for evaluate/confirm/optimize/decision actions
- (Optional) RLS by org_id when enabled

## 8. Future Enhancements

- Full sandbox engine & plan comparison reports
- Decision traceability (execution docs ↔ facts) with auto retro reports
- Team collaboration: mentions, tasks, shared contexts

---
Deliverable: This document defines the interaction contract for Lovable to build UI/EF and for Cursor to provide algorithms/specs. It’s intentionally concise, implementation-ready, and aligned with current code and EF specs.



