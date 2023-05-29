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


MakeSummarised <- function(Graph)
{
    return(Graph %>% 
           group_by(Heuristic,Strategy,SeriesPercent,ModuleCount) %>% 
           summarise(Time=mean(Time),ColorCount=mean(ColorCount)) %>% 
           mutate(ModuleCount = paste0("ModuleCount ",ModuleCount))%>%
           mutate(SeriesPercent = paste0("SeriesPercent ",SeriesPercent))%>%
           arrange(Heuristic))
}

MakeTimePlot <- function(Graph)
{
    return(Graph %>% 
       ggplot(aes(x=Heuristic,y=Time,fill=Strategy)) + 
       geom_col(position=position_dodge()) + facet_grid(rows=vars(SeriesPercent),cols=vars(ModuleCount)) + 
       theme(axis.text.x=element_text(angle = -90, hjust = 0)))
}
MakeColorPlot <- function(Graph)
{
      return( Graph %>% 
           ggplot(aes(x=Heuristic,y=ColorCount,fill=Strategy)) + 
           geom_col(position=position_dodge()) + facet_grid(rows=vars(SeriesPercent),cols=vars(ModuleCount)) +
           theme(axis.text.x=element_text(angle = -90, hjust = 0)))
}


for(Graph in SplitGeneratedResults)
{
    ProcessedGraph <- MakeSummarised(Graph)
    ggsave( paste0(OutDirectory,"/",max(Graph$VertexCount),".png"),
            MakeColorPlot(ProcessedGraph),
            ,width=5,height=10)
    ggsave( paste0(OutDirectory,"/",max(Graph$VertexCount),"Time.png"),
            MakeTimePlot(ProcessedGraph),
            ,width=5,height=10)
}
MakeTotalSummarised <- function(Graph)
{
    return(Graph %>% 
           group_by(Heuristic,Strategy) %>% 
           summarise(Time=mean(Time),ColorCount=mean(ColorCount)) %>% 
           arrange(Heuristic))
}
MakeTotalColorPlot <- function(Graph)
{
  return( Graph %>% 
       ggplot(aes(x=Heuristic,y=ColorCount,fill=Strategy)) + 
       geom_col(position=position_dodge()) +
       theme(axis.text.x=element_text(angle = -90, hjust = 0)))
}
MakeTotalTimePlot <- function(Graph)
{
    return(Graph %>% 
       ggplot(aes(x=Heuristic,y=Time,fill=Strategy)) + 
       geom_col(position=position_dodge()) +
       theme(axis.text.x=element_text(angle = -90, hjust = 0)))
}
DIMACSSummarised <- MakeTotalSummarised(DIMACSResult)
ggsave( paste0(OutDirectory,"/DIMACS.png"),
       MakeTotalColorPlot(DIMACSSummarised %>% filter(!(Strategy == "WholePrime"))),
       ,width=5,height=10)
ggsave( paste0(OutDirectory,"/DIMACSTime.png"),
       MakeTotalTimePlot(DIMACSSummarised %>% filter(!(Strategy == "WholePrime"))),
       ,width=5,height=10)
GeneratedSummarised <- MakeTotalSummarised(GeneratedResults)
ggsave( paste0(OutDirectory,"/Generated.png"),
       MakeTotalColorPlot(GeneratedSummarised),
       ,width=5,height=10)
ggsave( paste0(OutDirectory,"/GeneratedTime.png"),
       MakeTotalTimePlot(GeneratedSummarised),
       ,width=5,height=10)


#ResultTable <- Data %>% group_by(Heuristic,Strategy) %>% summarise(Time=mean(Time),ColorCount=mean(ColorCount)) %>% arrange(Heuristic)
#print(xtable(ResultTable, type = "latex",caption=Caption), file = OutFile)
