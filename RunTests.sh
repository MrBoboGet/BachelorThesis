
for EdgeFile in ./Data/*.edge; do
    echo "${EdgeFile}: "
    py ModularColoring.py $EdgeFile
done
