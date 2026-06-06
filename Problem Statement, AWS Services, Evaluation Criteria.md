# AI For Good 2.0 - Problem Statement, AWS Services & Evaluation Criteria

> Private and Confidential

---

## Problem Statement

### Background - Blood Warriors

- Blood Warriors is a foundation connecting voluntary blood donors with Thalassemia patients across India. With over 1,00,000 patients requiring up to 500 to 700 transfusions in a lifetime, the demand for reliable, recurring, and compatible blood is constant. Their Blood Bridge initiative and donor network are at the heart of making this happen.

### The Problem

- Today, matching donors to patients, coordinating requests, and keeping the ecosystem engaged relies heavily on manual effort. As Blood Warriors scales across cities and partner organizations, this becomes harder to sustain.

### Key Challenge Areas

#### AI-Enabled Care Coordination and Access

- How might we make it easier for different people involved in care to stay connected and informed at the right time?
- What could more intuitive, adaptive interactions between individuals and systems look like across languages and contexts?
- How might systems remember and respond appropriately over repeated interactions?

#### Smart Matching and Resource Allocation

- How can we better identify and prioritize the right people or resources when needs arise?
- What signals or patterns could be used to anticipate availability or willingness to participate?

#### Engagement and Continuity

- How might we encourage continued participation and build long term engagement among contributors?
- What kinds of feedback loops or interactions could make the system feel more responsive and human?

#### Operating at Scale

- What would it take for such a system to function effectively across a large, diverse population?
- How might it adapt to variations in language, access, and infrastructure without losing efficiency?
- What considerations come into play when expanding to support many users and regions simultaneously?

### Objective

Build an autonomous, AI-powered blood support network that can coordinate requests, engage the right participants, and manage interactions in real time with minimal manual effort.

### What the System Should Be Able to Do

- Handle multiple workflows through a unified intelligent AI layer
- Automate outreach, follow-ups, and escalations for donors
- Track and interpret donor responses to guide next steps
- React to real-time events and updates
- Enable conversational interactions with memory
- Systems must self manage improvement steps and protocols via failure learning
- Provide admins with dashboards and insights
- Ensure consent-aware, responsible data usage and compliant systems

---

## Infrastructure - AWS Services

The following AWS Services are authorized for use alongside GitHub integrations:

### Compute & Web

- S3 + CloudFront / Amplify
- AWS Cognito
- AWS App Runner
- Lambda + API Gateway
- Fargate / Amazon EKS

### Events & Streams

- Amazon SQS / SNS / SES
- Amazon EventBridge
- IAM / CloudWatch
- Kinesis Data Streams
- AWS Glue

### Databases

- Amazon DynamoDB
- RDS (Postgres / Aurora)
- Amazon Redshift
- Amazon Athena
- OpenSearch Service

### Security & Ops

- Secrets Manager / Parameter Store
- WAF / AWS Shield
- AWS X-Ray
- Managed Airflow (MWAA)

### AI & Machine Learning

- Amazon Bedrock
- Amazon SageMaker
- Amazon Lex
- SageMaker Feature Store

### DevOps

- AWS CodeBuild
- AWS CodePipeline
- AWS CodeCommit
- GitHub Actions

### Cost Policy

> We will send a soft notification when usage goes beyond $30, followed by another notification if it exceeds $40. Participants will be asked to downgrade services (e.g. Save work on GitHub) upon exceeding $40.

---

## Recommended Tech Stack

| Layer | Recommended |
|-------|-------------|
| **1. Full Stack (User Interaction Layer)** | Front-end: React.js (web UI), Back-end: Python (FastAPI / Flask), REST APIs + Async processing |
| **2. Data Engineering (Pipelines and Storage)** | Database: AWS Databases (RDS, S3, Aurora, DynamoDB), ETL pipelines via AWS (Glue, Kinesis) |
| **3. Data Science & AI (Intelligence Layer)** | ML: Matching / Ranking models, NLP, Predictions (SageMaker), AI: Conversational AI (Bedrock) |
| **4. Automation Systems (Orchestration Layer)** | AWS Step Functions, AWS Lambda, API Gateway |
| **5. Deployment and Monitoring** | AWS EC2, CloudWatch, Optional: ECS + AWS CodePipeline |

---

## Evaluation Criteria

| Criteria | Weight | Description |
|----------|--------|-------------|
| **Ideation** | 20% | Practicality & Scalability of Idea |
| **Innovation** | 20% | Uniqueness of solution design |
| **Prototype Development** | 20% | Real Implementation, not just UI |
| **AI Component** | 20% | AI Usage and Implementation |
| **End-to-End Execution** | 20% | Development & Deployment |
