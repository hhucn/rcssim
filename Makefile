MAIN=distributed-rcs
-include .paper.settings

default: pdf

render-pdf:
	mkdir -p img_pdf
	./render_pdf.py --output-dir img_pdf fig sim/plots
	inkscape --without-gui grcs.svg --export-dpi 300 --export-pdf img_pdf/grcs.pdf

pdf: render-pdf
	@test -f ${MAIN}.aux || $(MAKE) pdf-fast
	$(MAKE) pdf-fast

pdf-fast:
	pdflatex -interaction batchmode ${MAIN}.tex


cd: pdf
	xdg-open ${MAIN}.pdf

clean:
	rm -f -- "${MAIN}.aux" "${MAIN}.log" "${MAIN}.nav" "${MAIN}.out" "${MAIN}.pdf" img_pdf

.PHONY: default render-pdf pdf pdf-fast cd clean
