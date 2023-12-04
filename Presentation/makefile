DotFiles=$(wildcard *.dot)
EpsFiles=$(DotFiles:.dot=.pdf)
Presentation.pdf: Presentation.tex $(EpsFiles)
	pdflatex $<
%.pdf: %.dot
	dot $< -Tpdf "-Gratio=1" -o $@
