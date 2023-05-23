for Size in 250 500 750 1000; do
    for SeriesPercent in 35 70; do
        for ModuleCount in 5 10; do
            py CreateRandomGraphs.py $Size $SeriesPercent 50 $ModuleCount $((Size/(2*ModuleCount)))\
            "TestGraphs/DisturbedCoGraph_${Size}_${SeriesPercent}_${ModuleCount}"
        done
    done
done
