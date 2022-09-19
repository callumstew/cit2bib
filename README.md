# cit2bib

Script to pull bibtex entries from DOI, PMID, and arxiv IDs.


# Usage
By default it will read STDIN and write to STDOUT and expects a whitespace seperated list of IDs.

You can specify an input (-i, --infile) or output (-o, --outfile) file.

You can run it against a .tex file with the --tex flag.
You can run it against a latex log with the --latex_log flag. This only works with certain tex compilers and biblatex.
It will cache results so that the http requests aren't repeated. --clear_cache will clear the current cache entry for any IDs that you supply.
Print debug information to STDERR with --debug

```
echo 10.1038/227680a0 | ./cit2bib.py
cat file.tex | python3 cit2bib.py
python3 cit2bib.py -i file.tex -o references.bib
```
