$SCANS = "M:\data\corpus\08-04-2026\original"
$VERTEBRA = "L3"
$OUTPUT = "M:\data\corpus\08-04-2026\L3"
$PATIENT_DIR_IDX = 7

sliceselector-cli sliceselect --scans ${SCANS} --output ${OUTPUT} --vertebra ${VERTEBRA} --patient_dir_idx ${PATIENT_DIR_IDX}