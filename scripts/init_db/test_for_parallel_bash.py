import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log",
        dest="LOGLEVEL",
        type=str,
        default="WARNING",
        help="Set logging level, defaults to: WARNING",
    )
    parser.add_argument(
        "--init",
        dest="INITIALIZE",
        type=int,
        default=0,
        help="Initialize tables in database: 1=yes, 0=no (default)",
    )
    parser.add_argument(
        "--start_after",
        dest="START_AFTER",
        type=int,
        default=None,
        help="Set limit of batch for bulk toponym lookup - starts after this report ID.",
    )
    parser.add_argument(
        "--end",
        dest="END",
        type=int,
        default=None,
        help="Set limit of batch for bulk toponym lookup - ends with this report ID.",
    )
    parser.add_argument(
        "--increment",
        dest="INCREMENT",
        type=int,
        default=None,
        help="Set upper limit of batch for bulk toponym lookup by providing an increment.",
    )

    args = parser.parse_args()
    
    if (args.END is not None) & (args.INCREMENT is not None):
        parser.error('--end and --increment may not be used simultaneuusly!')
    
            
    if args.INCREMENT:
        end = args.START_AFTER + args.INCREMENT
    if args.END:
        end = args.END
        
    print("start_after: %d and end: %d." % (args.START_AFTER, end))
    
if __name__ == "__main__":
    main()
