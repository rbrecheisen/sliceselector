# $SCANS = "M:\data\corpus\08-04-2026\original"
# $SCANS = "M:\data\corpus\06-05-2026\CT scans EMC voor CORPUS study\CT scans EMC 2.0\Deel 1\transfer_3556033_files_e6d9a3df\c1\c1"
# $SCANS = "M:\data\corpus\06-05-2026\CT scans EMC voor CORPUS study\CT scans EMC 2.0\Deel 2\transfer_3556033_files_a977c7ef\c2\c2"
# $SCANS = "M:\data\corpus\06-05-2026\CT scans EMC voor CORPUS study\CT scans EMC 2.0\Deel 3\transfer_3556033_files_fb1e2eab\c3\c3"
# $SCANS = "M:\data\corpus\06-05-2026\CT scans EMC voor CORPUS study\CT scans EMC 2.0\Deel 4\transfer_3556033_files_756f4039\c4\c4"
$SCANS = "M:\data\corpus\06-05-2026\CT scans EMC voor CORPUS study\CT scans EMC 2.0\Deel 5\transfer_3556033_files_1eb6ecf9\c5\c5" # is empty

# $OUTPUT = "M:\data\corpus\06-05-2026\CT scans EMC voor CORPUS study\CT scans EMC 2.0\Deel 1\L3"
# $OUTPUT = "M:\data\corpus\06-05-2026\CT scans EMC voor CORPUS study\CT scans EMC 2.0\Deel 2\L3"
# $OUTPUT = "M:\data\corpus\06-05-2026\CT scans EMC voor CORPUS study\CT scans EMC 2.0\Deel 3\L3"
# $OUTPUT = "M:\data\corpus\06-05-2026\CT scans EMC voor CORPUS study\CT scans EMC 2.0\Deel 4\L3"
$OUTPUT = "M:\data\corpus\06-05-2026\CT scans EMC voor CORPUS study\CT scans EMC 2.0\Deel 5\L3"

$VERTEBRA = "L3"
$PATIENT_DIR_IDX = 10

sliceselector-cli sliceselect --scans ${SCANS} --output ${OUTPUT} --vertebra ${VERTEBRA} --patient_dir_idx ${PATIENT_DIR_IDX}