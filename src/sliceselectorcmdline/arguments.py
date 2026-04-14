import argparse


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--root_dir',
        default=None,
        help='Path to root directory containing scans (one for each patient but may be nested)',
    )
    parser.add_argument(
        '--patient_dir',
        default=None,
        help='Directory containing patient ID directories. For example: /path/to/dir/MUMC_0001, etc.',
    )
    parser.add_argument(
        '--output_dir',
        default=None,
        help='Output directory where to store selected DICOM image and sagittal PNG image for quality checking',
    )
    parser.add_argument(
        '--vertebra',
        default='L3',
        help='Vertebra to use for selecting image (options: "L3", "T4")',
    )
    args = parser.parse_args()
    if args.root_dir is None or args.patient_dir is None or args.output_dir is None:
        parser.print_usage()
        return None
    return args