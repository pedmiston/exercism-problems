docs/exercism-problems.md: docs/exercism-problems.Rmd
%.md: %.Rmd
	cd docs/ && Rscript -e "rmarkdown::render('`basename $<`', output_file = '`basename $@`', output_format = 'github_document')"
