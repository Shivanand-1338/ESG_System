# Tradeoffs Document

## Features Deliberately Not Built

### 1. Real-Time Data Ingestion (Streaming)

**What it would do:** Accept continuous data streams from SAP, utility meters, and travel systems via webhooks or message queues (Kafka, RabbitMQ).

**Why we didn't build it:**
- The current batch ingestion model (file upload + API POST) covers the primary use case of periodic data imports
- Real-time streaming requires message queue infrastructure, connection management, and retry logic that significantly increases operational complexity
- ESG reporting is typically done on monthly/quarterly cycles, not real-time
- Adding streaming later is additive (new endpoints) and doesn't require redesigning existing components

**Impact:** Users must manually trigger data imports or schedule them via cron/external schedulers.

### 2. Machine Learning Anomaly Detection

**What it would do:** Use trained ML models (isolation forests, autoencoders, LSTM) to detect complex anomaly patterns beyond simple z-score analysis.

**Why we didn't build it:**
- Z-score analysis with |z| > 3 threshold catches the most impactful outliers with minimal false positives
- ML models require training data, model management infrastructure, and ongoing retraining
- The minimum 30-record requirement for statistical detection already handles the cold-start problem
- ML adds a "black box" element that's harder to explain to auditors who need to understand why records were flagged
- Can be added as an additional detection layer without modifying existing validation logic

**Impact:** Some subtle anomaly patterns (seasonal variations, correlated multi-field anomalies) won't be automatically detected. Analysts rely on domain expertise for these cases.

### 3. Custom Report Builder / Export Engine

**What it would do:** Allow analysts to create custom reports with drag-and-drop fields, charts, and scheduled PDF/Excel exports.

**Why we didn't build it:**
- The dashboard provides the essential views (summary stats, filtered record lists, audit trails)
- Custom reporting is a large feature area that could easily become its own product
- Most organizations already have BI tools (Power BI, Tableau, Looker) that can connect to the database directly
- The API provides all data needed for external reporting tools to consume
- Building a report builder well requires significant UX investment that's orthogonal to the core data quality mission

**Impact:** Users who need custom reports must use external BI tools or export data via the API. The API's filtering and pagination support this workflow.
