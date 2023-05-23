#DataDirectories=(DIMACS CoGraphs DisturbedCoGraphs)
#DataDirectories=(DIMACS DisturbedCoGraphs_500_07_05 DisturbedCoGraphs_1000_70_50)
DataDirectories=(./TestGraphs/*)
if (( $# > 0 )); then
    DataDirectories=()
    declare -i i
    i=1
    while (( $i <= $# )) do
        DataDirectories+=(${!i})
        i+=1
    done
fi
for Directory in ${DataDirectories[@]}; do
    OutFile="ColoringResults/${Directory#./TestGraphs/}Result.csv"
    echo $OutFile
    bash RunTest.sh "$Directory" "$OutFile"
done
