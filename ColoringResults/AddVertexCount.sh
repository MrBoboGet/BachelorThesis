

for File in ./*.csv; do
    if [[ $File =~ Disturbed ]]; then
        for Number in 250 500 750 1000; do
            if [[ $File =~ $Number ]]; then
                echo "Modifying $File"
                sed -i '1s/$/,VertexCount/' $File
                sed -i "2,\$s/\$/,$Number/" $File
            fi
        done
    fi
done
