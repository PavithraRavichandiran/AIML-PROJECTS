# Analytics Report: Complete EDA Insights and Business Recommendations

Date: 2026-03-08
Project: Amazon India Sales Analytics
Coverage: Q01-Q10 analyses (2015-2025)

## 1. Purpose and Scope

This document consolidates exploratory data analysis (EDA) insights and business recommendations into one executive-ready report.

Sources used:
- Notebook insights from `notebooks/Q01_Revenue_Trend_Analysis.ipynb` through `notebooks/Q10_Price_Demand_Analysis.ipynb`
- Core EDA setup from `notebooks/05_eda.ipynb`
- Generated summary artifacts in `data/cleaned/*.csv`

## 2. Executive Snapshot

- Analysis period: 2015-2025 (11 years)
- Total transactions analyzed: 1,122,687
- Total revenue analyzed: INR 76.55B
- Total growth (2015-2025): 79.83%
- Revenue CAGR: 6.04%
- Average YoY growth: 11.49%
- Peak month (overall average): December (INR 910.94M)
- Lowest month (overall average): June (INR 458.24M)
- Festival revenue share: 31.84%
- Prime revenue share: 43.65%
- UPI share in 2025: 60.16%

Business implication:
- Growth is resilient but uneven. Performance depends strongly on seasonality, customer segment quality, pricing discipline, and regional execution.

## 3. Core EDA Insights

### Data Health and Readiness

- EDA and validation workflow is documented in `notebooks/05_eda.ipynb`.
- Analytical notebooks Q01-Q10 consistently produce summary sections and strategy outputs.
- Most domains have exported executive summaries in `data/cleaned`; Q07 and Q10 recommendations are present in notebooks even where summary CSV export is not currently materialized.

### Cross-Theme Patterns

- Revenue concentration: A few subcategories and periods drive disproportionate value.
- Customer concentration: Loyal and high-value segments materially influence outcomes.
- Channel shift: Digital payment adoption is structural, not temporary.
- Geography matters: Metro concentration is high, but non-metro growth headroom remains.
- Pricing leverage exists: Price, discounting, and demand behavior are measurable and actionable.

## 4. Domain-Wise Insights and Recommendations

### Q01: Revenue Trend Analysis

Key insights:
- Revenue scaled to INR 76.55B across 11 years.
- Total growth from 2015 to 2025 is 79.83%.
- Growth volatility exists despite long-term upward direction.

Recommendations:
1. Build annual plans around growth volatility, not just average trend.
2. Track category-level growth contributors to avoid concentration risk.
3. Use forecast bands (base/upside/downside) for budget and inventory planning.

### Q02: Seasonal Patterns Analysis

Key insights:
- Strong seasonality with December as peak and June as trough.
- Festival periods drive outsized value and transaction volume.

Recommendations:
1. Align inventory and marketing calendars to seasonal peaks at least 6-8 weeks in advance.
2. Pre-fund logistics capacity before Q4 demand spikes.
3. Run post-peak retention campaigns to reduce demand drop-off.

### Q03: Customer Segmentation (RFM)

Key insights:
- Customers analyzed: 354,969.
- Largest segment: Loyal Customers (85,893 customers).
- Highest revenue segment: Loyal Customers (about INR 32.12B).
- Champions contribute 23.4% of revenue.

Recommendations:
1. Protect Champions and Loyal customers with VIP retention and early-access offers.
2. Nurture Potential Loyalists with journey-based personalization.
3. Launch win-back programs for At Risk and Lost groups with strict ROI thresholds.
4. Allocate CRM budget by segment value and churn risk.

### Q04: Payment Method Evolution

Key insights:
- Shift from COD-led mix to UPI-led mix is clear.
- UPI market share reached 60.16% (2025).
- COD share dropped from 75.26% (2015) to 8.06% (2025).
- Digital share reached 68.96% (2025).

Recommendations:
1. Make UPI checkout latency and reliability a top product KPI.
2. Use digital-payment incentives to improve conversion and lower COD handling cost.
3. Keep COD available selectively for high-friction cohorts/regions while reducing exposure.
4. Expand BNPL and card EMI flows for high-ticket categories.

### Q05: Category and Subcategory Performance

Key insights:
- Top subcategory by revenue: Smartphones.
- Smartphones contribute about 73.04% share, indicating concentration.
- Fastest growth subcategory: Audio (avg YoY 24.10%).

Recommendations:
1. Defend smartphone leadership with availability, bundling, and service quality.
2. Accelerate Audio and other growth subcategories with targeted assortment expansion.
3. Reduce concentration risk by developing second and third growth engines.
4. Drive subcategory-level merchandising and pricing playbooks.

### Q06: Prime Membership Impact

Key insights:
- Prime transactions: 38.06% of volume.
- Prime revenue: 43.65% of total.
- Prime AOV (INR 78,199.97) is 26.07% higher than non-Prime.

Recommendations:
1. Prioritize Prime acquisition among high-value non-Prime cohorts.
2. Use Prime-exclusive bundles and benefits in top Prime-preferred categories.
3. Track Prime incremental lift (not just Prime share) as a business KPI.
4. Integrate Prime propensity scores into campaign targeting.

### Q07: Geographic Analysis

Key insights:
- Revenue is concentrated in top states and metro markets.
- Tier2 and Rural markets show meaningful growth potential.
- Behavior differs by region and market maturity.

Recommendations:
1. Expand selectively in high-CAGR states using localized assortment and pricing.
2. Build a dedicated Tier2/Rural growth model (fulfillment, language, payments, trust).
3. Optimize metro wallet share through premium assortment and faster delivery.
4. Increase infrastructure and partnerships in underserved but high-potential regions.

### Q08: Festival Sales Impact

Key insights:
- Festival revenue: INR 24.37B (31.84% of total revenue).
- Festival daily average revenue is higher than non-festival days.
- Diwali is the strongest festival contributor.

Recommendations:
1. Move inventory and ad spend into pre-festival and festival windows with strict pacing.
2. Expand delivery and support capacity for peak days.
3. Launch post-festival retention journeys to convert spike buyers into repeat customers.
4. Build festival-specific forecasting and procurement playbooks.

### Q09: Customer Age Group Analysis

Key insights:
- 18-35 age bands contribute most revenue share.
- Shopping behavior and preferences vary clearly by age segment.
- Smartphones are the top subcategory across listed age groups.

Recommendations:
1. Run age-tailored creatives, product sets, and value propositions.
2. Differentiate pricing and financing by age-linked affordability patterns.
3. Map payment preferences by age to optimize checkout conversion.
4. Design segment-specific retention cadences by lifecycle stage.

### Q10: Price-Demand Analysis

Key insights:
- Pricing has measurable demand impact.
- Subcategory elasticity varies and should not be treated uniformly.
- Discounting can lift volume but may erode margin without controls.

Recommendations:
1. Implement dynamic pricing by segment and subcategory elasticity.
2. Optimize discount depth using controlled experiments and guardrail margins.
3. Use A/B testing for key price points before broad rollout.
4. Combine bundle pricing for complementary products to improve blended margin.

## 5. Cross-Functional Priority Actions (Next 2 Quarters)

1. Build an integrated planning calendar across seasonality, festivals, and promotions.
2. Launch segment-first CRM (RFM + Prime + age + geography) with measurable lift targets.
3. Roll out payment optimization focused on UPI reliability and digital conversion.
4. Institutionalize subcategory-level pricing and assortment governance.
5. Create region-tier operating plans with clear service-level and profitability targets.

## 6. KPI Framework to Track Recommendation Impact

- Revenue growth: YoY, MoM, and forecast accuracy.
- Contribution mix: by subcategory, age segment, tier, and payment method.
- Customer quality: retention, repeat rate, churn risk migration by RFM segment.
- Commercial efficiency: AOV, discount-to-revenue ratio, gross margin impact.
- Operations readiness: fill rate, delivery SLA during festival peaks.

## 7. Current Artifact Status

Available summary exports in `data/cleaned`:
- `Q01_Revenue_Analysis_Summary.csv`
- `Q02_Seasonal_Analysis_Summary.csv`
- `Q03_RFM_Analysis_Summary.csv`
- `Q04_Executive_Summary.csv`
- `Q05_Executive_Summary.csv`
- `Q06_Executive_Summary.csv`
- `Q08_Executive_Summary.csv`
- `Q09_Executive_Summary.csv`

Not currently materialized as summary CSV (insights still present in notebooks):
- Q07 Geographic summary export
- Q10 Price-demand summary export

## 8. Conclusion

The EDA and thematic analyses are complete and business-actionable. The strongest value unlocks are in four areas: customer segmentation execution, seasonal/festival operating rigor, payment and checkout optimization, and region-tier specific growth strategy.
