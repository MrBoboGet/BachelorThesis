
for EdgeFile in ./Data/*.edge; do
    echo -n "${EdgeFile}: "
    py ModularColoring.py $EdgeFile
done
