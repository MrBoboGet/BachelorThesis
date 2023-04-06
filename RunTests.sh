

DataDir=Data
echo $#
if [[ $# > 0 ]]; then
    DataDir=$1
    echo $1
fi

if [[ -d TempOutput ]]; then
    rm -r TempOutput
fi
mkdir TempOutput
declare -i i=0
for EdgeFile in $DataDir/*.edge; do
    ResFile=${EdgeFile#$DataDir/}
    echo $ResFile
    echo $EdgeFile
    py ModularColoring.py $EdgeFile > "TempOutput/${ResFile/%.edge/.res}" &
    Jobs[$i]=$!
    i+=1
done

for pid in ${Jobs[*]}; do
    wait $pid
    echo "Job finished $pid"
done

rm TotalOutput.csv
echo "Graph,RootType,Heuristic,Strategy,ColorCount" >> TotalOutput.csv
for Res in ./TempOutput/*.res; do
    cat "$Res" >> TotalOutput.csv
done
