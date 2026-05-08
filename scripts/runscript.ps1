# $SCANS = "M:\data\corpus\08-04-2026\original"
$SCANS = "M:\data\corpus\06-05-2026\CT scans EMC voor CORPUS study\CT scans EMC 2.0\Deel 1\transfer_3556033_files_e6d9a3df\c1\c1"
$VERTEBRA = "L3"
$OUTPUT = "M:\data\corpus\06-05-2026\CT scans EMC voor CORPUS study\CT scans EMC 2.0\Deel 1\L3"
$PATIENT_DIR_IDX = 10

sliceselector-cli sliceselect --scans ${SCANS} --output ${OUTPUT} --vertebra ${VERTEBRA} --patient_dir_idx ${PATIENT_DIR_IDX}