# scripts/changepoint_analysis.R
#
# Formal change-point detection on the Coastal Frontier event time series.
#
# Method: Binary Segmentation (BinSeg) with a top-N constraint (Q=3 regional, Q=2 per country). BinSeg with Q is more parsimonious than PELT/MBIC on short series like this one, where MBIC over-fits trivial quarter-to-quarter variance.
#
# Reference: Killick, R., Fearnhead, P., Eckley, I.A. (2012). Optimal
# Detection of Changepoints With a Linear Computational Cost. JASA 107(500).

suppressPackageStartupMessages({
  library(changepoint)
  library(dplyr)
  library(ggplot2)
  library(readr)
})

cat("Coastal Frontier change-point analysis\n")
cat("======================================\n\n")

INPUT_CSV       <- "data/interim/quarterly_counts.csv"
OUT_FIG_DIR     <- "reports/figures"
OUT_REGIONAL    <- file.path(OUT_FIG_DIR, "changepoint_regional.png")
OUT_PER_COUNTRY <- file.path(OUT_FIG_DIR, "changepoint_per_country.png")
OUT_SUMMARY     <- "reports/changepoint_summary.txt"

dir.create(OUT_FIG_DIR, recursive = TRUE, showWarnings = FALSE)
dir.create("reports", recursive = TRUE, showWarnings = FALSE)

if (!file.exists(INPUT_CSV)) {
  stop(sprintf("Input CSV not found at %s. Run scripts/prepare_changepoint_input.py first.", INPUT_CSV))
}

quarterly <- read_csv(INPUT_CSV, show_col_types = FALSE)
cat(sprintf("Loaded %d quarter-country rows from %s\n", nrow(quarterly), INPUT_CSV))

# ---- Regional aggregate per quarter ----
regional <- quarterly %>%
  group_by(quarter) %>%
  summarise(n = sum(n), .groups = "drop") %>%
  arrange(quarter)

cat(sprintf("Regional series spans %d quarters: %s to %s\n\n",
            nrow(regional), regional$quarter[1], regional$quarter[nrow(regional)]))

# ---- Regional change-point detection ----
regional_counts <- regional$n
cpt_regional    <- cpt.mean(regional_counts, method = "BinSeg", Q = 3)
regional_cpts   <- cpts(cpt_regional)
segment_means   <- param.est(cpt_regional)$mean

cat("=== Regional change-points ===\n")
if (length(regional_cpts) > 0) {
  regional_break_quarters <- regional$quarter[regional_cpts]
  cat(sprintf("Indices in series: %s\n", paste(regional_cpts, collapse = ", ")))
  cat(sprintf("Break quarters:    %s\n", paste(regional_break_quarters, collapse = ", ")))
} else {
  regional_break_quarters <- character(0)
  cat("No structural breaks detected.\n")
}
cat(sprintf("Segment means:     %s\n\n", paste(round(segment_means, 1), collapse = " -> ")))

# ---- Regional chart ----
regional$idx          <- seq_len(nrow(regional))
regional$segment      <- findInterval(regional$idx, regional_cpts + 0.5) + 1
regional$segment      <- pmin(regional$segment, length(segment_means))
regional$segment_mean <- segment_means[regional$segment]

p_regional <- ggplot(regional, aes(x = idx, y = n)) +
  geom_line(color = "steelblue", linewidth = 0.5, alpha = 0.7) +
  geom_point(color = "steelblue", size = 2) +
  geom_line(aes(y = segment_mean, group = segment), color = "firebrick", linewidth = 1.2) +
  scale_x_continuous(breaks = regional$idx, labels = regional$quarter) +
  labs(
    title    = "Regional event counts per quarter with PELT change-points",
    subtitle = if (length(regional_break_quarters) > 0)
                 sprintf("Structural breaks at: %s", paste(regional_break_quarters, collapse = ", "))
               else "No structural breaks detected",
    x = "Quarter", y = "Event count",
    caption = "Red: within-segment means. Green dashed: detected structural breaks."
  ) +
  theme_minimal(base_size = 11) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

if (length(regional_cpts) > 0) {
  p_regional <- p_regional +
    geom_vline(xintercept = regional_cpts + 0.5,
               color = "darkgreen", linetype = "dashed", linewidth = 0.6)
}

ggsave(OUT_REGIONAL, p_regional, width = 12, height = 5.5, dpi = 110)
cat(sprintf("Saved %s\n", OUT_REGIONAL))

# ---- Per-country change-points ----
countries        <- sort(unique(quarterly$country))
country_results  <- list()

cat("\n=== Per-country change-points ===\n")
for (cnt in countries) {
  cdata <- quarterly %>% filter(country == cnt) %>% arrange(quarter)
  ctn   <- cdata$n

  if (length(ctn) < 4 || sum(ctn > 0) < 3) {
    country_results[[cnt]] <- list(quarters = character(0), means = numeric(0))
    cat(sprintf("%-15s: insufficient data\n", cnt))
    next
  }

  ccpt   <- cpt.mean(ctn, method = "BinSeg", Q = 2)
  cidx   <- cpts(ccpt)
  cmeans <- round(param.est(ccpt)$mean, 1)
  cqs    <- if (length(cidx) > 0) cdata$quarter[cidx] else character(0)

  country_results[[cnt]] <- list(quarters = cqs, means = cmeans, series_quarters = cdata$quarter)

  q_str <- if (length(cqs) > 0) paste(cqs, collapse = ", ") else "(no breaks)"
  m_str <- paste(cmeans, collapse = " -> ")
  cat(sprintf("%-15s: breaks=%s | means=%s\n", cnt, q_str, m_str))
}

# ---- Per-country faceted chart ----
per_country_df <- quarterly %>%
  group_by(country) %>%
  arrange(quarter) %>%
  mutate(idx = row_number()) %>%
  ungroup()

p_per_country <- ggplot(per_country_df, aes(x = idx, y = n)) +
  geom_line(color = "steelblue", linewidth = 0.5) +
  geom_point(color = "steelblue", size = 1.2) +
  facet_wrap(~ country, scales = "free_y", ncol = 2) +
  theme_minimal(base_size = 10) +
  theme(axis.text.x = element_blank()) +
  labs(
    title   = "Per-country quarterly event counts with detected change-points",
    x       = "Quarter (chronological)", y = "Event count",
    caption = "Green dashed: PELT change-points (MBIC penalty)."
  )

# Build numeric x-positions for the per-country vertical lines
marker_rows <- list()
for (cnt in countries) {
  cr <- country_results[[cnt]]
  if (length(cr$quarters) == 0) next
  cidx_in_series <- match(cr$quarters, cr$series_quarters)
  cidx_in_series <- cidx_in_series[!is.na(cidx_in_series)]
  if (length(cidx_in_series) > 0) {
    marker_rows[[cnt]] <- data.frame(country = cnt, idx = cidx_in_series + 0.5)
  }
}
if (length(marker_rows) > 0) {
  cpt_markers <- do.call(rbind, marker_rows)
  p_per_country <- p_per_country +
    geom_vline(data = cpt_markers, aes(xintercept = idx),
               color = "darkgreen", linetype = "dashed", linewidth = 0.5)
}

ggsave(OUT_PER_COUNTRY, p_per_country, width = 14, height = 8, dpi = 110)
cat(sprintf("\nSaved %s\n", OUT_PER_COUNTRY))

# ---- Summary file ----
sink(OUT_SUMMARY)
cat("=== Change-Point Analysis Summary ===\n\n")
cat("Method: Binary Segmentation (BinSeg), Q=3 regional / Q=2 per country\n")
cat("Library: R `changepoint` package\n\n")
cat("Interpretation: each change-point marks a quarter where the mean of the\n")
cat("event-count series shifted significantly. The change-point quarter is the\n")
cat("LAST quarter of the prior regime; the following quarter begins the new one.\n\n")

cat("=== Regional aggregate ===\n")
cat(sprintf("Series length: %d quarters (%s to %s)\n",
            nrow(regional), regional$quarter[1], regional$quarter[nrow(regional)]))
cat(sprintf("Number of structural breaks: %d\n", length(regional_cpts)))
if (length(regional_cpts) > 0) {
  cat(sprintf("Break quarters: %s\n", paste(regional_break_quarters, collapse = ", ")))
}
cat(sprintf("Segment means: %s\n\n", paste(round(segment_means, 1), collapse = " -> ")))

cat("=== Per-country ===\n")
for (cnt in names(country_results)) {
  cr <- country_results[[cnt]]
  if (length(cr$means) == 0) {
    cat(sprintf("%-15s: insufficient data\n", cnt))
  } else if (length(cr$quarters) > 0) {
    cat(sprintf("%-15s: breaks at %s | segment means: %s\n",
                cnt, paste(cr$quarters, collapse = ", "),
                paste(cr$means, collapse = " -> ")))
  } else {
    cat(sprintf("%-15s: no structural breaks | mean: %s\n",
                cnt, paste(cr$means, collapse = " -> ")))
  }
}
sink()

cat(sprintf("\nWrote summary to %s\n", OUT_SUMMARY))
cat("\nDone.\n")

