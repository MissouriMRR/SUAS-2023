# Add v OR -v after command for verbose results, or q OR -q after command for quiet results
if [[ -z "$1" ]]; then
    CMD="-m unittest discover vision/unit_tests/"
elif [[ "$1" = "-v" || "$1" = "v" ]]; then
    CMD="-m unittest discover vision/unit_tests/ --verbose"
elif [[ "$1" = "-q" || "$1" = "q" ]]; then
    CMD="-m unittest discover vision/unit_tests/ --quiet"
else
    CMD="-m unittest discover vision/unit_tests/"
fi

python $CMD
