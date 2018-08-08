docs/exercism-problems.md: docs/exercism-problems.Rmd
%.md: %.Rmd
	cd docs/ && Rscript -e "rmarkdown::render('`basename $<`', output_file = '`basename $@`', output_format = 'github_document')"
clean:
	rm -rf docs/*_files/ docs/*_cache/ docs/*.md
