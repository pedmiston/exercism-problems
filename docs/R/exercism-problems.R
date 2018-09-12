# ---- setup ----
set.seed(254)

library(tidyverse)
library(lme4)
library(exercism)
data("problem_specifications")
data("languages")
data("exercises")
data("test_cases")

active_languages <- filter(languages, active == 1)$language

exercises <- exercises %>%
  filter(difficulty > 0, language %in% active_languages)

# Core exercises are implemented in all top 10 most popular languages according to StackOverflow
top_10_languages <- c("python", "php", "r", "go", "ruby", "c", "objective-c", "scala", "swift", "javascript", "typescript", "java")
core_exercises <- exercises %>%
  group_by(exercise) %>%
  summarize(in_core_languages = all(top_10_languages %in% language)) %>%
  filter(in_core_languages) %>%
  .$exercise

test_cases_per_problem <- count(test_cases, exercise) %>%
  rename(n_test_cases = n)

problem_specifications <- left_join(problem_specifications, test_cases_per_problem) %>%
  mutate(
    has_test_cases = n_test_cases > 0,
    in_core_languages = exercise %in% core_exercises
  )

make_recoder <- function(key) {
  recoder <- function(frame) {
    if(missing(frame)) return(key)
    left_join(frame, key)
  }
  recoder
}

make_color_palette <- function(hex_colors, names) {
  names(hex_colors) <- names
  get_colors <- function(...) {
    hex_colors[...] %>%
      unname()
  }
  get_colors
}

theme_set(theme_minimal())
set2 <- make_color_palette(RColorBrewer::brewer.pal(3, "Set2"), c("green", "orange", "blue"))


recode_one_v_two <- make_recoder(data_frame(
  n_test_cases = c(1, 2),
  one_v_two = c(-0.5, 0.5)
))
recode_three_plus <- make_recoder(data_frame(
  n_test_cases = 3:30,
  three_plus = TRUE,
  n_test_cases_1 = n_test_cases - min(n_test_cases) + 1,
  n_test_cases_log = log10(n_test_cases_1)
))

problems_by_language <- left_join(exercises, problem_specifications)

problem_difficulty <- problems_by_language %>%
  group_by(exercise, n_test_cases, has_test_cases) %>%
  summarize(difficulty = mean(difficulty)) %>%
  ungroup() %>%
  recode_one_v_two() %>%
  recode_three_plus()

language_per_n_test_case <- problems_by_language %>%
  group_by(language, n_test_cases, has_test_cases) %>%
  summarize(difficulty = mean(difficulty)) %>%
  ungroup() %>%
  recode_one_v_two() %>%
  recode_three_plus()

# ---- difficulty ----
difficulty_plot <- ggplot(exercises) +
  aes(fct_reorder(exercise, difficulty, .fun = mean), difficulty) +
  stat_summary(fun.y = mean,
               fun.ymin = function(x) mean(x) - sd(x),
               fun.ymax = function(x) mean(x) + sd(x),
               geom = "linerange", alpha = 0.8) +
  geom_point(aes(color = language), position = position_jitter(width=0, height=0.2), shape = 1, alpha = 0.6) +
  coord_flip() +
  scale_y_continuous("self-assigned difficulty", breaks = 1:10, position = "right") +
  labs(x = "", caption = "Problems sorted by average difficulty across languages. Lineranges show mean difficulties ±1 standard deviation.\nSource: github.com/exercism") +
  theme(legend.position = "none")

# Fit lmer mod with one param per language
lang_difficulty_mod <- lme4::lmer(difficulty ~ -1 + language + (1|exercise),
                                  data = exercises)

get_lang_difficulty_preds <- function(mod) {
  broom::tidy(mod, effects = "fixed") %>%
    rename(language = term) %>%
    mutate(language = str_replace(language, "^language", ""))
}

lang_difficulty_preds <- get_lang_difficulty_preds(lang_difficulty_mod)
lang_difficulty_plot <- ggplot(lang_difficulty_preds) +
  aes(fct_reorder(language, estimate, .desc = TRUE), estimate) +
  geom_linerange(aes(ymin = estimate - std.error, ymax = estimate + std.error)) +
  coord_flip(ylim = c(0.7, 5.9), expand = FALSE, clip = "off") +
  labs(x = "", y = "average difficulty") +
  scale_y_continuous(breaks = 1:6)

core_lang_difficulty_mod <- lme4::lmer(difficulty ~ -1 + language + (1|exercise),
                                       data = filter(exercises, exercise %in% core_exercises, language %in% top_10_languages))
core_lang_difficulty_preds <- get_lang_difficulty_preds(core_lang_difficulty_mod)
core_difficulty_plot <- lang_difficulty_plot %+% core_lang_difficulty_preds

# ---- n-test-cases ----
scale_color_is_core <- scale_color_brewer("", labels = c("other", "core"), palette = "Set2")
scale_fill_is_core <- scale_fill_brewer("", labels = c("other", "core"), palette = "Set2")

n_test_cases_plot <- ggplot(problem_specifications) +
  aes(n_test_cases, fill = in_core_languages) +
  geom_dotplot(binwidth = 1, stackdir = "center") +
  scale_x_continuous(breaks = seq(0, 100, by = 10)) +
  scale_y_continuous(NULL, breaks = NULL) +
  scale_fill_is_core +
  labs(x = "number of test cases", caption = "Distribution of problems by number of test cases.\nSource: github.com/exercism/problem-specifications")

problem_specifications_dotplot <- problem_specifications %>%
  group_by(n_test_cases) %>%
  mutate(height = 1:n(),
         height_c = height - mean(height)) %>%
  ungroup()

n_test_cases_labeled_plot <- ggplot(problem_specifications_dotplot) +
  aes(factor(n_test_cases), height_c) +
  geom_text(aes(label = exercise, color = in_core_languages), angle = 45, hjust = 0.5, check_overlap = TRUE, size = 10) +
  coord_cartesian(xlim = c(-0.1, 28), ylim = c(-11, 11), expand = FALSE) +
  labs(x = "number of test cases", caption = "Distribution of labeled problems for reference. Note the ordinal x-axis.\nSource: github.com/exercism/problem-specifications") +
  scale_y_continuous(NULL, breaks = NULL) +
  scale_color_is_core +
  theme(text = element_text(size = 50))

exercise_means <- problems_by_language %>%
  group_by(exercise, n_test_cases, has_test_cases) %>%
  summarize(
    difficulty = mean(difficulty),
    n_languages = length(unique(language))
  ) %>%
  ungroup()

n_test_case_means <- problems_by_language %>%
  group_by(n_test_cases) %>%
  summarize(
    difficulty = mean(difficulty),
    n_exercises = length(unique(exercise))
  ) %>%
  ungroup()

language_means <- problems_by_language %>%
  filter(n_test_cases > 0) %>%
  group_by(language, n_test_cases) %>%
  summarize(
    difficulty = mean(difficulty),
    n_exerises = length(unique(exercise))
  ) %>%
  ungroup()

difficulty_per_test_case_plot <- ggplot(problems_by_language) +
  aes(n_test_cases, difficulty) +
  geom_point(data = exercise_means, show.legend = FALSE, shape = 1) +
  geom_point(aes(size = n_exercises), data = n_test_case_means, stat = "summary", fun.y = mean, color = "black") +
  geom_smooth(aes(group = language), data = filter(problems_by_language, n_test_cases != 0, n_test_cases > 3, n_test_cases < 23),
              method = "lm", se = FALSE, size = 0.2, alpha = 0.2, color = set2("blue")) +
  geom_smooth(data = filter(problems_by_language, n_test_cases != 0, n_test_cases > 3, n_test_cases < 23), method = "lm", se = FALSE, size = 1.5, color = "black") +
  scale_x_log10("Number of test cases (log scale)", breaks = c(1, 4, 12, 24, 48, 100)) +
  scale_y_continuous("Difficulty", breaks = 1:10) +
  scale_size_continuous("Number of exercises", breaks = c(1, 2, 4, 8)) +
  coord_cartesian(clip = "off") +
  theme(legend.position = "bottom") +
  labs(caption = "Black circles show mean difficulty of all exercises with the same number of test cases.\nThin blue lines show linear regressions fit for each language.")

# ---- topics ----
data("topics")

top20_topics <- topics %>%
  distinct(exercise, topic) %>%
  count(topic) %>%
  top_n(20, wt = n)

top20_topic_names <- top20_topics$topic

top20_topics_plot <- ggplot(top20_topics) +
  aes(fct_reorder(topic, n), n) +
  geom_bar(stat = "identity") +
  coord_flip() +
  labs(x = "", y = "number of exercises", caption = "Top 20 topics across all language exercises.")

topic_difficulty <- left_join(topics, exercises) %>%
  filter(topic %in% top20_topic_names) %>%
  group_by(topic) %>%
  summarize(
    difficulty = mean(difficulty, na.rm = TRUE)
  )

difficulty_by_topic_plot <- ggplot(topic_difficulty) +
  aes(fct_reorder(topic, difficulty), difficulty) +
  geom_bar(stat = "identity") +
  coord_flip() +
  labs(x = "", y = "average difficulty", caption = "Average difficulty of top 20 topics")
