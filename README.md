Customer Complaint Root-Cause Intelligence (Lite)
Project Overview

Large organizations receive a high volume of customer complaints but often lack clear visibility into recurring issues, root causes, and how these issues evolve over time.

This project builds an unsupervised NLP pipeline to:

Discover recurring complaint themes

Extract root causes using weak supervision

Track issue trends over time

The focus is on applied NLP, data quality, and system design, not supervised classification.

Dataset

Source: CFPB Consumer Complaint Database (Kaggle mirror)
Total records: ~100,000 complaints
Narrative complaints used for NLP: ~20,000

Only complaints containing free-text narratives are included in the NLP pipeline. Complaints without narrative text were excluded, which is standard practice for text-based complaint analysis.

Work Completed
1. Dataset Preparation & Scoping

Adapted the project scope to financial services based on data availability

Standardized column names for consistent pipeline usage

Identified relevant vs irrelevant fields for NLP analysis

2. Narrative Filtering & Text Cleaning

Removed complaints without narrative text

Filtered out empty or whitespace-only narratives

Applied minimal text normalization:

lowercasing

whitespace normalization

Removed common boilerplate phrases

Filtered out very short complaints (< 20 words)

Removed exact duplicate complaint texts

Result:
A high-quality corpus of complaint narratives suitable for unsupervised NLP.

3. Temporal Preparation

Converted complaint receipt dates into proper datetime format

Removed records with invalid dates

Created temporal features (year, month, week)

Selected weekly aggregation as the primary temporal unit to balance noise reduction and responsiveness

This enables:

trend analysis

spike detection

issue evolution tracking

4. Product Category Normalization (Light Data Hustle)

Inspected raw product labels and identified noisy and overlapping categories

Defined 10 canonical product categories

Mapped verbose and inconsistent raw labels to normalized categories

Saved the mapping for reproducibility

Canonical categories include:

Debt Collection

Mortgage

Credit Reporting

Credit Card

Bank Account

Student Loan

Personal Loan

Money Transfer / Payments

Auto Loan

Other

This step reduces category fragmentation and significantly improves interpretability of downstream analysis.

Current State

The project currently has:

Clean and meaningful complaint narratives

Reliable temporal features for trend analysis

Normalized product categories

A stable and interpretable data foundation

No modeling or clustering has been performed yet by design.

Remaining Work
1. Text Representation

Generate sentence embeddings from cleaned complaint narratives

Select an embedding model suitable for semantic clustering

2. Complaint Clustering

Apply unsupervised clustering to group recurring complaint issues

Validate cluster coherence and adjust parameters as needed

3. Root-Cause Extraction

Use weak supervision (keyword signals + keyphrase extraction) to infer dominant root causes per cluster

Generate human-readable cluster labels

4. Temporal Intelligence

Track complaint clusters over time using weekly aggregation

Identify:

growing issues

declining issues

newly emerging problems

5. Insight Reporting

Generate structured weekly insight summaries:

top recurring issues

root causes

trend changes

(Optional) build a lightweight dashboard for exploration

Key Design Principles

Data quality before modeling

Unsupervised discovery over predefined labels

Interpretability over raw accuracy

Human judgment for semantics, models for patterns

Outcome Goal

Deliver a practical NLP system that:

Identifies recurring customer issues

Explains why problems occur

Tracks how issues change over time

This mirrors how complaint intelligence systems are built in real organizations.
