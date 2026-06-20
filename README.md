# Enterprise HR Knowledge Bot: Secure Production RAG Pipeline on AWS

A production-grade Retrieval-Augmented Generation (RAG) chatbot designed to securely query internal enterprise HR documentation (PTO policies, Remote Work Guidelines, and Travel/Expense criteria). Built using an automated data ingestion pipeline, cloud infrastructure management, and secure cross-region AI routing.

## 🚀 Key Features
* **Zero-Shot Data Adaptation:** Ingests new policy documents into an Amazon S3 datastore and synchronizes them instantly into a vector index without rewriting backend application logic.
* **Enterprise-Grade Security:** Rejects traditional, leakable static API keys in favor of native AWS IAM roles and cryptographic SigV4 authorization via Boto3.
* **High-Availability Load Balancing:** Utilizes AWS Cross-Region Inference Profiles to dynamically route high-throughput token traffic across optimal US data centers.
* **Full Lineage Tracking:** Enforces strict compliance by accompanying every text response with granular source citations mapping back to the original source object.

## 🏗️ Architecture & Tech Stack
* **Infrastructure as Code (IaC):** Terraform (`hr-bot-infra`)
* **Generative AI Engine:** Amazon Bedrock (Knowledge Bases for Amazon Bedrock)
* **Foundational LLM:** Anthropic Claude 3.5 Sonnet / Sonnet 4.6
* **Vector Datastore:** Amazon OpenSearch Serverless
* **Storage & Ingestion:** Amazon S3
* **Runtime Environment:** Python 3 (Boto3 SDK)

---

## 🛠️ Real-World Engineering Challenges Overcome

### 1. The "Legacy Model" Block & Model Catalog Evolution
* **The Problem:** Initial attempts to invoke baseline Claude 3 models resulted in `ResourceNotFoundException` blocks due to ongoing AWS infrastructure deprecations and service lifecycle shifts.
* **The Fix:** Queried live system inventories programmatically via the Bedrock API to mapping out the actual available account catalogs. Upgraded the pipeline to leverage active **Claude Sonnet 4.6** nodes.

### 2. On-Demand Throughput Bottlenecks (Cross-Region Profiles)
* **The Problem:** Standard base model execution requests failed with `ValidationException: Invocation of model ID with on-demand throughput isn't supported.`
* **The Fix:** Transitioned the application framework from basic foundation model ARNs to account-specific **Cross-Region Inference Profiles** (`arn:aws:bedrock:us-east-1:[account_id]:inference-profile/us.anthropic...`). This successfully routed requests through AWS's managed load balancers.

---

## 📊 Live Verification & Outputs

### Test: Dynamic Source Injection & Retrieval
When asking the system a compound policy question across isolated datasets, the retrieval architecture accurately abstracts rules from separate target documents and appends source tracking:

```text
🙋‍♂️ Question: What is the flight booking class policy and the daily meal allowance?

🤖 Answer: For flight bookings, Economy Class is required for all business flights under 6 hours. Business Class is only permitted for international flights with a continuous flight duration exceeding 6 hours. The daily meal allowance (per diem) is $75 USD, which covers meals and incidental expenses during active business travel.

📄 Source Citations:
 - Derived from: travel_policy.txt
