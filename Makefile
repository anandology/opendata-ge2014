
WPLISINGS=rawdata/MH/wp-listing.txt
AC_FILES=$(WPLISINGS:%/wp-listing.txt=%/ac.txt)
PC_FILES=$(WPLISINGS:%/wp-listing.txt=%/pc.txt)

.PHONY: data

TARGETS=$(AC_FILES) $(PC_FILES)

default: $(TARGETS) data

%/ac.txt: %/wp-listing.txt
	python scripts/parse_wikipedia_listing.py $< --ac | tr '\320' '-' > $@

%/pc.txt: %/wp-listing.txt
	python scripts/parse_wikipedia_listing.py $< | tr '\320' '-' > $@

data:
	python process_rawdata.py

clean:
	-rm $(TARGETS)

