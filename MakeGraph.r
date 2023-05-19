library(tidyverse)

args <- commandArgs(trailingOnly = TRUE)

ResultDirectory <- args[1]
OutDirectory <- args[2]

ReadDisturbecCographCSV <- function(Path)
{
    ReturnValue <- read_csv(Path)
    VertexCount <- str_match(Path,"h_(\\d+)")[2]
    SeriesPercent <- str_match(Path,"_(\\d\\d)_")[2]
    ModuleCount <- str_match(Path,"(\\d+)R")[2]
    ReturnValue$VertexCount = strtoi(VertexCount)
    ReturnValue$SeriesPercent = strtoi(SeriesPercent)
    ReturnValue$ModuleCount = strtoi(ModuleCount)
    return(ReturnValue)
}

#Data <- read_csv(DataFile)
DataFiles <- Filter(function(x) { return(!str_detect(x,"\\.sh"))},list.files(ResultDirectory,full.names=TRUE))
DIMACSFile <- DataFiles[str_detect(DataFiles,"DIMACS")]
GeneratedDataFiles <- DataFiles[DataFiles != DIMACSFile]
GeneratedResults <- do.call(rbind,map(GeneratedDataFiles,ReadDisturbecCographCSV))
DIMACSResult <- read_csv(DIMACSFile)





SplitGeneratedResults <- map(c(250,500,750,1000),function (Count) { return(GeneratedResults %>% filter(VertexCount == Count))  })


for(Graph in SplitGeneratedResults)
{
    ProcessedGraph <- Graph %>% 
           group_by(Heuristic,Strategy,SeriesPercent,ModuleCount) %>% 
           summarise(Time=mean(Time),ColorCount=mean(ColorCount)) %>% 
           arrange(Heuristic)
    ggsave( paste0(OutDirectory,"/",max(Graph$VertexCount),".png"),
           ProcessedGraph %>%
           ggplot(aes(x=Heuristic,y=ColorCount,fill=Strategy)) + 
           geom_col(position=position_dodge()) + facet_grid(rows=vars(SeriesPercent),cols=vars(ModuleCount)))
    ggsave( paste0(OutDirectory,"/",max(Graph$VertexCount),"Time.png"),
           ProcessedGraph %>%
           ggplot(aes(x=Heuristic,y=Time,fill=Strategy)) + 
           geom_col(position=position_dodge()) + facet_grid(rows=vars(SeriesPercent),cols=vars(ModuleCount)))
}
print(SplitGeneratedResults)
#ResultTable <- Data %>% group_by(Heuristic,Strategy) %>% summarise(Time=mean(Time),ColorCount=mean(ColorCount)) %>% arrange(Heuristic)
#print(xtable(ResultTable, type = "latex",caption=Caption), file = OutFile)
