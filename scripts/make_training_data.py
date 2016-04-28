import argparse
import numpy as np
import os
import skimage.io as skio

from PIL import Image
from skimage.transform import resize

parser = argparse.ArgumentParser(
    description="Create compressed training data from source images")
parser.add_argument('-f', '--filepath',
                    help="Path to directory containing images")
parser.add_argument('-o', '--output',
                    help="Path to desired output directory")
parser.add_argument('--jpg', dest='jpg', action='store_true',
                    help="Include flag to perform jpg compression")
parser.add_argument('quality', metavar='qual', type=int, nargs='+',
                    help="Specify desired quality (0 - 100) in jpg compression")
args = parser.parse_args()


def compress_img_jpg(file_dir, file_name, output_dir, quality):
    try:
        src_img = Image.open(file_dir + file_name)
    except IOError:
        return
    file_name = file_name[:file_name.index('.')] + '.jpg'
    src_img.save(output_dir + file_name, quality=quality)

def compress_img_size(file_dir, file_name, output_dir, _unused_):
    src_img = skio.imread(file_dir + file_name)
    resized_img = resize(src_img, (src_img.shape[0] / 2, src_img.shape[1] / 2))
    resized_img = resize(resized_img, src_img.shape[:2])
    skio.imsave(output_dir + file_name, resized_img)

def main():
    # Create output directory if does not exist
    if not os.path.exists(args.output):
        os.mkdir(args.output)

    # Check for directory ending slash
    if args.filepath[-1] != '/':
        args.filepath += '/'
    if args.output[-1] != '/':
        args.output += '/'

    # Choose between two possible compressions
    if args.jpg:
        fn = compress_img_jpg
    else:
        fn = compress_img_size

    filenames = os.listdir(args.filepath)
    for file_name in filenames:
        fn(args.filepath, file_name, args.output, args.quality[0])

if __name__ == '__main__':
    main()
