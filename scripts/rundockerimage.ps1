$VERSION = "latest"
$SCANS = "M:\data\lauracools\testt4selectiontotalseg\original_unzipped_nodots"
$VERTEBRA = "L3"
$OUTPUT = "M:\data\lauracools\testt4selectiontotalseg\output"

docker run --rm `
    -v "${SCANS}:/data/scans" `
    -v "${OUTPUT}:/data/output" `
    "brecheisen/sliceselector-cli:$VERSION" sliceselect `
        --scans /data/scans --vertebra ${VERTEBRA} --output /data/output