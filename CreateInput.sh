
for EdgeFile in ./Data/*.col; do 
    #echo ${EdgeFile//.col/.edge}
    awk '/^e/ {print $2-1 " " $3-1}' "$EdgeFile"  > ${EdgeFile/%.col/.edge}
done
