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
def sliceselect(scans, vertebra, output):
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
    """
    process = SliceSelectProcess(
        inputs={'root_directory': scans},
        output=output,
        vertebra=vertebra,
        resume=True,
    )
    process.execute()