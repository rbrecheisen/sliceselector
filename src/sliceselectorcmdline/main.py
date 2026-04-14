from sliceselectorcmdline.arguments import get_arguments
from sliceselectorcmdline.sliceselect.sliceselectrunner import SliceSelectRunner


def main():
    args = get_arguments()
    if args is not None:
        runner = SliceSelectRunner(
            args.root_dir, 
            args.patient_dir, 
            args.output_dir, 
            args.vertebra,
            resume=True,
        )
        runner.run()


if __name__ == '__main__':
    main()