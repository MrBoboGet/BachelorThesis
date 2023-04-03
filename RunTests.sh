

if [[ -d TempOutput ]]; then
    rm -r TempOutput
fi
mkdir TempOutput
declare -i i=0
for EdgeFile in Data/*.edge; do
    ResFile=${EdgeFile#Data/}
    py ModularColoring.py $EdgeFile > "TempOutput/${ResFile/%.edge/.res}" &
    Jobs[$i]=$!
    i+=1
done

for pid in ${Jobs[*]}; do
    echo "Job finished $pid"
    wait $pid
done

for Res in ./TempOutput/*.res; do
    cat "$Res" >> TotalOutput.csv
done
