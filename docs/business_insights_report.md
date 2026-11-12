# Executive Business Insights & Strategic Recommendations
**Platform:** Brazilian E-Commerce Public Dataset (Olist)  
**Author:** Aaryaraj Patil  
**Date:** November 2026  
**Target Stakeholders:** Chief Commercial Officer, VP of Supply Chain, Head of Customer Retention  

---

## 1. Executive Summary

A comprehensive multi-dimensional analysis of **96,478 delivered orders** across Brazil between 2016 and 2018 indicates strong top-line revenue expansion alongside structural challenges in **customer retention** and **interstate logistics**. 

Key high-level metrics:
- **Total Gross Merchandise Value (GMV):** **R$ 15.82 Million**
- **Total Unique Buyers:** **93,358 individuals**
- **Average Order Value (AOV):** **R$ 164.03**
- **Repeat Purchase Rate:** **3.01%** (96.99% single-transaction customers)
- **On-Time Delivery Rate:** **91.89%** (8.11% delivered past estimated arrival date)
- **Average Customer Review Score:** **4.15 / 5.00**

---

## 2. Core Business Findings

### 2.1 The Customer Retention Challenge (Marketplace Acquisition Model)
- **Data Finding:** Over 96.9% of buyers make exactly one transaction. The monthly cohort retention matrix drops to below **0.5% in Month 1** and stabilizes under **0.3%** across months 2 to 12.
- **Root Cause Analysis:** Olist operates as an aggregator connecting independent merchants with search-intent buyers on external marketplaces (Mercado Livre, B2W, Amazon). Customers perceive their relationship with the individual storefront rather than Olist, preventing direct organic brand affinity.
- **Estimated Business Impact:** Acquiring new customers is 5x–7x more expensive than retaining existing ones. Increasing repeat purchase rates from 3% to 6% would generate an estimated **R$ 470,000+** in incremental annual revenue without additional top-of-funnel customer acquisition costs (CAC).

### 2.2 Logistics Asymmetry: The Southeast Hub vs Frontier States
- **Data Finding:** 
  - **São Paulo (SP)** generates **42.2%** of all orders with an average delivery duration of **8.3 days** and a delay rate of only **5.2%**.
  - Conversely, North and Northeast states (e.g. **Alagoas (AL)**, **Maranhão (MA)**, **Roraima (RR)**) experience average delivery times exceeding **24 to 28 days**, with delay rates reaching **18.5% to 22.8%**.
- **Freight Burden:** In northern regions, freight costs account for up to **36.4%** of the product purchase price, compared to just **12.1%** in São Paulo.

### 2.3 The Review Score Cliff: Delivery Punctuality Drives Customer Sentiment
- **Statistical Finding:** Delivery punctuality is the single most decisive factor influencing customer satisfaction.
  - Orders delivered **on-time or early** achieve an average review score of **4.30 / 5.00**, with **62.8% 5-star ratings** and only **6.1% 1-star ratings**.
  - Orders delivered **late** plummet to an average review score of **2.15 / 5.00**, with **58.4% 1-star ratings** and less than **14.2% 5-star ratings**.
- **Strategic Insight:** Reducing the delay rate by 2% would eliminate approximately **1,900 negative 1-star reviews**, immediately enhancing platform trust and conversion.

### 2.4 Payment Financing Dynamics
- **Credit Card Installments:** Over **75% of sales volume** is transacted via credit cards, with customers averaging **3.5 installments**. For ticket sizes above R$ 500, over **68% of customers** choose installment plans exceeding 6 months.
- **Boleto Bancário Friction:** Boleto accounts for **19.4% of total order volume**, but exhibits higher cancellation rates before payment approval due to bank processing latency (1–3 business days).

---

## 3. Prioritized Strategic Recommendations

```
+---------------------------------------------------------------------------------------+
|                               STRATEGIC ACTION MATRIX                                 |
+---------------------------------------------------------------------------------------+
| High Impact / Immediate  |  1. Regional Fulfillment Hubs (FBA / Cross-Docking)        |
|                          |  2. Post-Purchase Automated Re-engagement Campaigns        |
+--------------------------+------------------------------------------------------------+
| High Impact / Strategic  |  3. SLA-Tiered Seller Ranking & Buy-Box Allocation         |
|                          |  4. Dynamic Estimated Delivery Date (EDD) Algorithm        |
+--------------------------+------------------------------------------------------------+
| Medium Impact / Long-term|  5. Instant Pix / Digital Wallet Payment Integration       |
|                          |  6. High-Value Category Bundling & Subscription Pilot      |
+--------------------------+------------------------------------------------------------+
```

### Recommendation 1: Regional Cross-Docking & Fulfillment Partnerships
- **Action:** Establish regional logistics consolidation nodes in Salvador (Bahia) and Recife (Pernambuco) for top-selling SKUs shipped from São Paulo/Paraná sellers.
- **Expected Outcome:** Cuts inter-regional transit duration by 6 to 9 days, reducing North/Northeast delivery delay rates from 20% down to under 9%.

### Recommendation 2: RFM-Targeted Retention Marketing
- **Action:** Target the **"Hibernating High Spenders"** (13,739 customers, R$ 4.2M historical GMV) with personalized win-back voucher campaigns triggered at day 90 post-purchase.
- **Expected Outcome:** Re-engaging just 5% of this segment would recover over **R$ 210,000** in high-margin repeat revenue.

### Recommendation 3: Seller SLA Enforcement on Platform Buy-Box
- **Action:** Penalize sellers whose late dispatch rate exceeds 5% by reducing their catalog visibility score. Reward prompt merchants with "Olist Fast Fulfillment" badges.
- **Expected Outcome:** Reduces seller-side handling bottlenecks, which currently account for nearly 2.8 days of the order lifecycle before carrier handoff.

### Recommendation 4: Realistic Machine-Learning-Powered Delivery Estimates
- **Action:** Replace static zip-code transit buffers with dynamic ML estimates that factor in item weight, route corridors, and carrier historical congestion.
- **Expected Outcome:** Under-promising and over-delivering elevates customer satisfaction, protecting Net Promoter Scores even on long-distance routes.
