

for File in ./*.csv; do
    if [[ File =~ Disturbed ]]; then
        for Number in 250 500 750 1000; do
            if [[ File =~ $Number ]]; then
                sed -i '1a ,VertexCount'
                sed -i "2,\$a ,$Number"
            fi
        done
    fi
done
