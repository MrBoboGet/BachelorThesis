library(tidyverse)

args <- commandArgs(trailingOnly = TRUE)

DataFile <- "Temp.csv"
OutFile <- "Out.tex"

DataFile <- args[1]
OutFile <- args[2]

Data <- read_csv(DataFile)

ResultTable <- Data %>% group_by(Heuristic,Graph) %>% summarise(Time=mean(Time),ColorCount=mean(ColorCount)) %>% arrange(Heuristic)

print(xtable(ResultTable, type = "latex"), file = OutFile)
