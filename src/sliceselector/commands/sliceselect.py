import click
from sliceselector.processes.sliceselect.sliceselectprocess import SliceSelectProcess


@click.command(help='Select L3/T4 slice from CT scans')
@click.option(
    '--scans', 
    required=True, 
    type=click.Path(exists=True), 
    help='Root directory with scans',
)
@click.option(
    '--output', 
    required=True, 
    type=click.Path(), 
    help='Output directory'
)
@click.option(
    '--vertebra', 
    required=True,
    default='L3',
    help='Vertebral level for selecting slice (default: "L3", options: "L3", "T4")'
)
@click.option(
    '--patient_dir_idx',
    required=True,
    default=0,
    type=int,
    help='Index patient identifying directory name in scan directory (including drive letter)',
)
def sliceselect(scans, vertebra, output, patient_dir_idx):
    """
    Selects specific slice from list of CT scans
    
    Parameters
    ----------
    --scans : str
        Root directory to scans. Each should have only one relevant scan although
        the scan may be down somewhere in nested directories.

    --output : str
        Path to output directory where selected slices will be placed. Each
        slice's file name will be the same as the scan directory name, so in
        the example above that would be "patient1", "patient2", etc.

    --vertebra : str
        Vertebral level where to take slice (default: L3, options: L3, T4)

    --patient_dir_idx : int
        Index of patient identifying directory name in current scan directory. E.g.,
        if scan directory is: C:\a\b\c\d and patient_dir_idx=2, the patient identifying
        directory name is "b" because the drive letter C: is index 0
    """
    process = SliceSelectProcess(
        inputs={'root_directory': scans},
        output=output,
        vertebra=vertebra,
        patient_dir_idx=patient_dir_idx,
        resume=True,
    )
    process.execute()