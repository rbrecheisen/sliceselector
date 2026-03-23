# sliceselector
Tool for automatically selecting vertebral images slices in CT and MRI scans

## Find DICOM series
Tab that allows searching scans/series recursively in a root directory. The 
detected scans are listed in a table. The user can then select the scans he
wishes to use for slice selection by copying the scans to an output directory.
Optionally, the user can copy the scans in batches. 

## Slice selection
Tab that allows running Total Segmentator on a single root directory. Each 
detected slice will be copied to an output directory. 