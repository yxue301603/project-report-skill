# Service Performance Review

**Demonstration only.** All names and measurements below are synthetic. This example illustrates report formatting, not a benchmark or production recommendation.

> [!IMPORTANT]
> **Decision:** In this fictional experiment, the optimized configuration increases throughput while remaining below the memory budget. Validate the result on your own workload before drawing a real conclusion.

<!-- report:metrics -->
| Metric | Value | Context |
| --- | --- | --- |
| Throughput | 160 req/s | Synthetic optimized run |
| Improvement | +60% | Relative to a 100 req/s baseline |
| Peak memory | 6.4 GB | Under an 8 GB demo budget |
| Error rate | 0.2% | Same fictional test protocol |

## Configuration comparison

The chart reads the Markdown table directly. Change a cell and regenerate the HTML to update the chart and its labels.

```report-chart
{"type":"bar","title":"Throughput by configuration","table":"comparison","label":"Configuration","values":["Throughput"],"unit":"req/s"}
```

<!-- report:table comparison -->
| Configuration | Throughput | Peak memory GB |
| --- | ---: | ---: |
| Baseline | 100 | 4.0 |
| Batching | 135 | 5.6 |
| Optimized | 160 | 6.4 |

> [!WARNING]
> **Measurement scope:** Compare results only when hardware, input data, and measurement windows match. These values are invented for the example.

## Throughput during a run

These fictional observations are taken at equally spaced one-minute intervals. Both series share the same unit and measurement window.

<!-- report:table timeline -->
| Minute | Baseline | Optimized |
| --- | ---: | ---: |
| 1 | 98 | 152 |
| 2 | 100 | 158 |
| 3 | 101 | 160 |
| 4 | 99 | 159 |
| 5 | 100 | 160 |

```report-chart
{"type":"line","title":"Throughput over time","table":"timeline","label":"Minute","values":["Baseline","Optimized"],"unit":"req/s"}
```

## Trade-offs

<!-- report:table changes -->
| Metric | Change |
| --- | ---: |
| Throughput | 60% |
| Peak memory | 60% |
| Latency | -20% |

```report-chart
{"type":"bar","title":"Relative change from baseline","table":"changes","label":"Metric","values":["Change"],"unit":"%"}
```

Positive values do not always mean improvement: higher memory consumption is a cost. Interpret each metric in context.

## Reproduction notes

```text
Configuration: fictional demo
Input: fixed synthetic workload
Measurement window: 5 equally spaced observations
```

> [!TIP]
> Keep real commands, data sources, and limitations alongside the measurements. Edit Markdown and regenerate HTML; do not maintain two separate report bodies.

## Next steps

1. Replace the fictional measurements with verified project data.
2. Update the decision and limitations to match the evidence.
3. Regenerate the HTML and inspect it in a browser.
