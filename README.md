Customer Complaint Root-Cause Intelligence System

An end-to-end NLP pipeline that transforms unstructured customer complaints into structured operational intelligence.

This system performs semantic clustering, root-cause signal extraction, temporal trend analysis, and interactive visualization for large-scale complaint datasets.

Overview

Organizations receive high volumes of complaint data but lack structured insight into:

Recurring issue types

Emerging problem categories

Root causes behind complaints

Temporal growth or decline of issues

This project converts raw complaint narratives into actionable analytics using modern NLP and clustering techniques.

System Capabilities

Text preprocessing and normalization

Sentence-level embedding generation (Sentence-BERT)

Density-based clustering (HDBSCAN)

Weak supervision root-cause labeling

Keyphrase extraction (TF-IDF)

Weekly trend aggregation

Rolling-average growth detection

Interactive dashboard (Streamlit)

Technical Architecture
1. Data Preparation

Clean complaint narratives

Remove masked tokens (e.g., “XXXX”)

Normalize product categories

Extract temporal features (year, week)

2. Semantic Embedding

Sentence-BERT model

High-dimensional vector representation of complaint text

3. Clustering

HDBSCAN density-based clustering

Automatic noise detection

Sub-clustering of high-density clusters

4. Root Cause Signal Extraction

Keyword-based weak supervision rules:

Delay

Billing

Refund

Cancellation

Outage

Cluster-level dominant cause identification.

5. Temporal Intelligence

Weekly complaint aggregation

4-week rolling average smoothing

Growth/decline detection

High-volume cluster identification

6. Dashboard Interface

Streamlit-based interactive analytics:

Product filtering

Date range filtering

KPI overview

Root cause distribution

Weekly trend visualization

Cluster drill-down

CSV export functionality

Project Structure
Customer_Complaint/
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── dashboard_ready_light.csv
│   └── cluster_week_counts.csv
│
├── requirements.txt
└── README.md

Installation
Clone Repository
git clone https://github.com/YOUR_USERNAME/Customer_Complaint.git
cd Customer_Complaint

Install Dependencies
pip install -r requirements.txt

Run Application
streamlit run dashboard/app.py

Dataset

Source: CFPB Consumer Complaint Dataset (Kaggle)

The full raw dataset exceeds GitHub’s file size limits and is excluded from this repository.
A reduced dataset version is included for deployment and demonstration purposes.

Technologies Used

Python

Pandas

Sentence-Transformers

HDBSCAN

UMAP

Scikit-learn

Plotly

Streamlit

Engineering Challenges Addressed

High-dimensional text clustering at scale

Large noise ratio mitigation

Sub-clustering of dominant density groups

Mixed-type cluster identifier normalization

Efficient dashboard rendering on constrained cloud environments

GitHub large-file handling strategy

Potential Applications

Banking complaint monitoring

Telecom issue detection

E-commerce customer analytics

SaaS support intelligence

CX operational risk systems
