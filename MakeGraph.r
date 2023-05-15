library(tidyverse)
library(xtable)

args <- commandArgs(trailingOnly = TRUE)

DataFiles <- str_split(args[1],",")
OutFile <- args[2]
Caption <- args[3]

#Data <- read_csv(DataFile)
TotalDataFiles <- map(DataFiles,read_csv)
Data <- do.call(rbind,TotalDataFiles)
ResultTable <- Data %>% group_by(Heuristic,Strategy) %>% summarise(Time=mean(Time),ColorCount=mean(ColorCount)) %>% arrange(Heuristic)
print(xtable(ResultTable, type = "latex",caption=Caption), file = OutFile)
