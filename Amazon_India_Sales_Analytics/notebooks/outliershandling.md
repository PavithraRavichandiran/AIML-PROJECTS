

# 📌 OUTLIER DETECTION & CORRECTION – `base_price_2015`

---

## 🟢 1️⃣ Problem Statement

The dataset contains potential pricing errors in `base_price_2015`, including values that appear disproportionately high due to data-entry mistakes (e.g., decimal shift issues).

Objective:

* Identify anomalous price values.
* Distinguish between genuine premium products and incorrect entries.
* Correct confirmed errors using a structured strategy.

---

## 🟢 2️⃣ Initial Exploration (Univariate Analysis)

Since we were analyzing a single numeric column (`base_price_2015`), we began with **univariate analysis**.

### Methods Used:

* Histogram → To inspect distribution shape.
* Boxplot → To identify statistical outliers using IQR.

### Observations:

* The distribution is **right-skewed**, typical for e-commerce pricing.
* Majority of products lie between ₹5,000 – ₹50,000.
* Several high-value points exist above ₹2,00,000.
* These appeared as statistical outliers in the boxplot.

However, statistical outliers do not automatically indicate data errors.

---

## 🟢 3️⃣ Why Global IQR Was Insufficient

All products belong to the Electronics category, but pricing varies significantly by:

* Subcategory (Smartphones, Laptops, TVs)
* Brand (Apple vs Samsung)
* Model positioning

Therefore:

* Global IQR would incorrectly classify premium Apple products as outliers.
* Price validation must consider brand-level pricing structure.

---

## 🟢 4️⃣ Hierarchical Outlier Detection Strategy

We refined detection using a hierarchical approach:

### Level 1: Brand-Level IQR

Outliers were detected within each brand group.

```python
brand-wise IQR applied
```

This reduced false positives from premium brands.

---

### Level 2: Price-to-Brand-Median Ratio

To identify contextual anomalies:

```
price_ratio = product_price / brand_median
```

Interpretation:

* Ratio < 3 → Normal variation
* Ratio 3–5 → Possibly premium
* Ratio > 5 → Suspicious
* Ratio > 10 → Highly likely error

This prevented incorrect correction of valid high-end Apple products.

---

## 🟢 5️⃣ Case Study: Apple iPhone 13

Original price observed:

```
₹261,706.39
```

Smartphone median ≈ ₹39,894
Apple median ≈ ₹176,895

Ratio to Apple median:

```
1.48×
```

Conclusion:

* Value lies within Apple’s upper quartile.
* Not a decimal-shift pattern.
* Considered valid premium pricing.
* No correction applied.

---

## 🟢 6️⃣ Final Outlier Flag Logic

A product was flagged as an error only if:

* It was a statistical outlier within its brand
  AND
* It exceeded 5× the brand median

This ensured:

* Premium products remained untouched.
* True anomalies were corrected.

---

## 🟢 7️⃣ Correction Method

Confirmed anomalies were corrected using **brand-level median imputation**.

Rationale:

* Maintains distribution integrity.
* Avoids arbitrary scaling.
* Respects brand pricing structure.

Original values were preserved in a separate column for traceability.

---

## 🟢 8️⃣ Final Validation

After correction:

* Re-plotted boxplot.
* Verified reduced extreme anomalies.
* Ensured price range aligns with brand positioning.

---

# 🎯 Final Summary

Outlier handling was performed using a structured, domain-aware methodology:

* Univariate statistical detection
* Brand-level contextual validation
* Ratio-based anomaly screening
* Controlled median-based correction

This ensured robust correction without distorting legitimate premium pricing.

---

