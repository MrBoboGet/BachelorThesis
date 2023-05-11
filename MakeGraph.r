library(tidyverse)
library(xtable)

args <- commandArgs(trailingOnly = TRUE)

DataFile <- args[1]
OutFile <- args[2]
Caption <- args[3]

Data <- read_csv(DataFile)
ResultTable <- Data %>% group_by(Heuristic,Strategy) %>% summarise(Time=mean(Time),ColorCount=mean(ColorCount)) %>% arrange(Heuristic)
print(xtable(ResultTable, type = "latex",caption=Caption), file = OutFile)
