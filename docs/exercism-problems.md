Analysis of Exercism.io problems
================

# Number of test cases

![](exercism-problems_files/figure-gfm/n-test-cases-dotplot-1.png)<!-- -->

![](exercism-problems_files/figure-gfm/n-test-cases-dotplot-labeled-1.png)<!-- -->

# Difficulty of the same problems in different languages

Most Exercism.io problems have been assigned a difficulty score ranging
from 1-10. For example, [python’s “hello-world” problem is assigned a
difficulty of
1](https://github.com/exercism/python/blob/master/config.json#L15). I
don’t know how these difficulty scores are assigned. It’s likely they
are self-assigned by the developers working on Exercism.io, and used in
the ordering of problems for particular learning tracks. What’s
interesting about these scores is that the same problems are assigned
different difficulty scores in different languages. Note the variability
within each problem in the plot below.

![](exercism-problems_files/figure-gfm/difficulty-1.png)<!-- -->

# Average difficulty across languages

Are all Exercism.io problems easier in some languages than others? To
test this, we can estimate the average difficulty across all problems
for each language while controlling for problem using a hierarchical
linear model.

``` r
# Fit lmer mod with one param per language
lang_difficulty_mod <- lme4::lmer(difficulty ~ -1 + language + (1|exercise),
                                  data = exercises)
```

![](exercism-problems_files/figure-gfm/ranking-1.png)<!-- -->

## Looking only at the core exercises implemented in the most popular languages

``` r
# Select problems with implementations in all languages
n_languages <- length(unique(exercises$language))
problems_in_all_languages <- count(exercises, exercise) %>%
  filter(n == n_languages)
# No problems in all languages!

# Select problems with implementations in the 10 most popular languages according to StackOverflow
exercism_languages <- unique(exercises$language)
data("stack_overflow_ranks", package = "programmingquestionnaire")
top_10_languages <- stack_overflow_ranks %>%
  filter(language_name %in% exercism_languages) %>%
  top_n(10) %>%
  .$language_name
exercises_in_all_top_10_languages <- exercises %>%
  group_by(exercise) %>%
  summarize(core = all(top_10_languages %in% language)) %>%
  filter(core) %>%
  .$exercise
core_exercises <- filter(exercises, language %in% top_10_languages, exercise %in% exercises_in_all_top_10_languages)

core_lang_difficulty_mod <- lme4::lmer(difficulty ~ -1 + language + (1|exercise),
                                       data = core_exercises)

core_lang_difficulty_preds <- broom::tidy(core_lang_difficulty_mod, effects = "fixed") %>%
  rename(language = term) %>%
  mutate(language = str_replace(language, "^language", ""))

ggplot(core_lang_difficulty_preds) +
  aes(fct_reorder(language, estimate, .desc = TRUE), estimate) +
  geom_linerange(aes(ymin = estimate - std.error, ymax = estimate + std.error)) +
  coord_flip(ylim = c(0, 5.9), expand = FALSE, clip = "off") +
  labs(x = "", y = "average difficulty")
```

![](exercism-problems_files/figure-gfm/ranking-core-1.png)<!-- -->

``` r
mod_comparison <- left_join(core_lang_difficulty_preds[,c("language", "estimate")],
          lang_difficulty_preds[,c("language", "estimate")],
          by = "language", suffix = c("_core", "_overall"))
ggplot(mod_comparison) +
  aes(estimate_core, estimate_overall, label = language) +
  geom_text(check_overlap = TRUE) +
  geom_abline(intercept = 0, slope = 1, linetype = "dashed") +
  labs(x = "estimated difficulty across core problems",
       y = "estimated difficulty across all problems") +
  coord_equal(xlim = c(1, 6), ylim = c(1, 6)) +
  scale_x_continuous(breaks = 1:6) +
  scale_y_continuous(breaks = 1:6)
```

![](exercism-problems_files/figure-gfm/ranking-core-2.png)<!-- -->
