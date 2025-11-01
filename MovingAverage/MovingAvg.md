# Moving Average Crossover Strategy (Explanation)

A moving average helps smooth price data to identify the trend.  
We use two moving averages:

- **Short-Term MA** = captures recent momentum
- **Long-Term MA** = captures long-term trend

Comparing them tells us whether momentum is **increasing** or **decreasing**.

---

## Buy Signal (Uptrend Start)

**Condition:**


-  When MA_short > MA_long

**Meaning:**
- Recent prices are rising faster than the long-term trend.
- Market momentum is shifting **upward**.

**Action:**



### Trend Interpretation:
| Before Cross | At Cross | After Cross |
|-------------|----------|-------------|
| Short MA < Long MA (downtrend) | Short MA meets Long MA (trend shift) | Short MA > Long MA (uptrend confirmed) |

---

## Sell Signal (Downtrend Start)

**Condition:**

When MA_short < MA_long


**Meaning:**
- Recent prices are falling below the long-term trend.
- Market momentum is shifting **downward**.

**Action:**

- when MA_short - MA_long


When this value changes sign:

| Sign | Interpretation | Trend |
|------|----------------|-------|
| Positive (> 0) | Recent price > Long-term average | **Uptrend** |
| Negative (< 0) | Recent price < Long-term average | **Downtrend** |

So the **crossover** marks the **exact point where trend direction changes**.

---

## Visual Concept (Text Sketch)

Prices: _///_//___
Long MA: ------------------- smooth line
Short MA: ~~~~~~~~~~~~~~~~~~~~ faster line



---

## Summary

| Condition               | Meaning                          | Action        |
|------------------------|----------------------------------|---------------|
| `MA_short > MA_long`   | Recent trend stronger than long   | **Buy/Go Long** |
| `MA_short < MA_long`   | Recent trend weaker than long     | **Sell/Exit** |

---

