import argparse


def read_params():
    parser = argparse.ArgumentParser(description='read params for XXX.')
    parser.add_argument('-i', '--input', metavar='input', dest='input_file', required=True, type=str,
                        help='input XXX.')
    parser.add_argument('-o', '--output_dir', metavar='output_dir', dest='output_dir', required=True, type=str,
                        help='output dirname.')
    args = parser.parse_args()
    params = vars(args)
    return params


if __name__ == '__main__':
    params = read_params()
    input = params['input_file']
    output = params['output_dir']
    
