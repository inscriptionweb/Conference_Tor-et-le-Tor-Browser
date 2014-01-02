# PSES2013 presentation
# Copyright 2013 © Lunar <lunar@anargeek.net>
# Copyright 2013 © WhilelM <whilelm@doomfr.com>
#
# License: CC BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0/>
#
# Depends: make pandoc texlive-latex-recommended latex-beamer
#
# Compass <https://compass.torproject.org> needs to be installed in either 
# `../compass` or the directory specified in the COMPASS_DIR command-line
# variable. e.g.
#
#     make COMPASS_DIR=/tmp/compass
#
# It needs Compass to have its data at hand (`--download` flag).
#
# Compass needs the `--by-network-family` feature proposed in #8932.

.PHONY: all source

PRESENTATION = 2013-06-23-PSES2013

all: $(PRESENTATION).pdf $(PRESENTATION)-notes.pdf

source: $(PRESENTATION)-src.tar.gz

COMPASS_DIR ?= ../compass
COMPASS_DATA ?= $(COMPASS_DIR)/details.json
CONSENSUS_PUBLISHED_AT = $(shell python -c 'import json; print json.load(file("$(COMPASS_DATA)"))["relays_published"]' | tr ' ' '_' | tr -d ':')

IMGS = $(shell echo $$(sed -n -e 's/^[^%]*\\includegraphics\([^{]*\)\?{\([^}]*\)}.*$$/\2.*/p' $(PRESENTATION).mdwn | sort -u) | sed -e 's/\.\*/_$(CONSENSUS_PUBLISHED_AT).pdf/g')

images/diversity_%_$(CONSENSUS_PUBLISHED_AT).pdf: $(PRESENTATION).py $(COMPASS_DATA)
	COMPASS_DIR="$(COMPASS_DIR)" ./$(PRESENTATION).py $@

PERF_START = 2009-10-01
PERF_END = $(patsubst _%,,$(CONSENSUS_PUBLISHED_AT))

images/bandwidth_$(CONSENSUS_PUBLISHED_AT).pdf: $(COMPASS_DATA)
	curl -o $@ 'https://metrics.torproject.org/bandwidth.pdf?start=$(PERF_START)&end=$(PERF_END)'

images/torperf50kb_$(CONSENSUS_PUBLISHED_AT).pdf: $(COMPASS_DATA)
	curl -o $@ 'https://metrics.torproject.org/torperf.pdf?filesize=50kb&source=all&start=$(PERF_START)&end=$(PERF_END)'

images/torperf5mb_$(CONSENSUS_PUBLISHED_AT).pdf: $(COMPASS_DATA)
	curl -o $@ 'https://metrics.torproject.org/torperf.pdf?filesize=5mb&source=all&start=$(PERF_START)&end=$(PERF_END)'

PANDOC_ARGS = \
	--variable=lang=french

$(PRESENTATION).pdf: $(PRESENTATION).mdwn $(IMGS)
	sed -e 's/\\includegraphics[^{]*{images\/\(diversity_\|bandwidth\|torperf50kb\|torperf5mb\)[^}]*/\0_$(CONSENSUS_PUBLISHED_AT)/' $< | \
		pandoc -t beamer \
			$(PANDOC_ARGS) \
			--latex-engine=xelatex -o $@ -

$(PRESENTATION)-notes.pdf: $(PRESENTATION).mdwn $(PRESENTATION)-notes-header.tex $(IMGS)
	sed -e 's/\\includegraphics[^{]*{images\/\(diversity_\|bandwidth\|torperf50kb\|torperf5mb\)[^}]*/\0_$(CONSENSUS_PUBLISHED_AT)/' $< | \
		sed -e 's/^<!--$$//;s/^-->$$//;s/\\textwidth/\\columnwidth/;s/[0-9.]*\\textheight/3cm/' | \
		pandoc -t latex \
			--include-in-header=$(PRESENTATION)-notes-header.tex \
			$(PANDOC_ARGS) \
                        --variable=fontsize=twocolumn \
			--latex-engine=xelatex -o $@ -

SRCS = \
	$(shell find . -maxdepth 1 '(' -name '$(PRESENTATION).GNUMakefile' -o -name 'Makefile' ')' -printf '%P\n') \
	$(PRESENTATION).mdwn \
        $(PRESENTATION)-notes-header.tex \
	$(PRESENTATION).py \
	$(filter-out %$(CONSENSUS_PUBLISHED_AT).pdf,$(IMGS))

$(PRESENTATION)-src.tar.gz: $(SRCS)
	tar -zcvf $@ --transform 's,$(PRESENTATION)\.GNUMakefile,Makefile,;s,^,$(PRESENTATION)/,' $(SRCS)
