import os
from functools import partial
import shutil
import sys
import traceback
from datetime import datetime
import argparse

from PIL import ImageOps
import multiprocessing as mp

from im.display import CursesDisplay
from im.utils import *


def im_cmd():
    parser = argparse.ArgumentParser(description='Image manipulation tool.')
    subparsers = parser.add_subparsers()

    parser_gray = subparsers.add_parser('gray', description='Convert image to grayscale.',
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_gray.set_defaults(func=gray)
    parser_gray.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_gray.add_argument('--overwrite', '-w', help='Overwrite input images.', action='store_true')

    parser_stack = subparsers.add_parser('stack', description='Join images horizontally or vertically.',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_stack.set_defaults(func=stack)
    parser_stack.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_stack.add_argument('--vertical', '-v', help='Join images vertically.', action='store_true')
    parser_stack.add_argument('--output', '-o', help='Path to output image.', default=None)

    parser_resize = subparsers.add_parser('resize', description='Resize image to inserted size (higher dimension).',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_resize.set_defaults(func=resize)
    parser_resize.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_resize.add_argument('--size', '-s', help='Higher dimension output size.', type=int, default=1000)
    parser_resize.add_argument('--width', '-wi', help='Width.', type=int, default=0)
    parser_resize.add_argument('--height', '-he', help='Height.', type=int, default=0)
    parser_resize.add_argument('--overwrite', '-w', help='Overwrite input images.', action='store_true')

    parser_exif = subparsers.add_parser('exif', description='Exif manipulation command.',
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_exif.set_defaults(func=exif)
    parser_exif.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_exif.add_argument('--remove', '-r', help='Remove exif info from image.', action='store_true')
    parser_exif.add_argument('--comment', '-c', help='Comment.', type=str, default=None)
    parser_exif.add_argument('--overwrite', '-w', help='Overwrite input images.', action='store_true')

    parser_rotate = subparsers.add_parser('rotate', description='Rotate image according to exif data',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_rotate.set_defaults(func=rotate)
    parser_rotate.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_rotate.add_argument('--overwrite', '-w', help='Overwrite input images.', action='store_true')

    parser_crop = subparsers.add_parser('crop', description='Crop image using [x, y, width, height] window.',
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_crop.set_defaults(func=crop)
    parser_crop.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_crop.add_argument('--x', '-x', help='Upper left crop window corner x coordinate.', type=int, default=0)
    parser_crop.add_argument('--y', '-y', help='Upper left crop window corner y coordinate.', type=int, default=0)
    parser_crop.add_argument('--width', '-wi', help='Crop window width.', type=int)
    parser_crop.add_argument('--height', '-he', help='Crop window height.', type=int)
    parser_crop.add_argument('--overwrite', '-w', help='Overwrite input images.', action='store_true')

    parser_filter = subparsers.add_parser('filter', description='Filter input images using given criterion.',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_filter.set_defaults(func=filter)
    parser_filter.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_filter.add_argument('--criterion', '-c', help='''Images filtering criterion. Python expression returning
                               bool value''', default='w * h > 100')

    parser_convert = subparsers.add_parser('convert', description='Convert image to another format.',
                                           formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_convert.set_defaults(func=convert)
    parser_convert.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_convert.add_argument('--extension', '-e', help='Required new image extension', default='.png')
    parser_convert.add_argument('--overwrite', '-w', help='Overwrite input images.', action='store_true')

    parser_gauss = subparsers.add_parser('gauss', description='Generate image with Gauss noise.',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_gauss.set_defaults(func=gauss)
    parser_gauss.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_gauss.add_argument('--std-dev', '-s', help='Standard deviation.', type=int)
    parser_gauss.add_argument('--overwrite', '-w', help='Overwrite input images.', action='store_true')

    parser_show = subparsers.add_parser('show', description='Show image(s) - terminal view.',
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_show.set_defaults(func=show)
    parser_show.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_show.add_argument('--slideshow', '-s', help='Run as slideshow.', action='store_true')
    parser_show.add_argument('--timeout', '-t', help='Slideshow timeout (s).', type=int, default=1)

    parser_findext = subparsers.add_parser('findext', description='Find correct image extension.',
                                           formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_findext.set_defaults(func=find_ext)
    parser_findext.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_findext.add_argument('--append', '-a', help='Append extension to file.', action='store_true')

    parser_find_no_img = subparsers.add_parser('find_noim', description='''Find non-image files and (optionally)
                                               remove it.''',
                                               formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_find_no_img.set_defaults(func=find_noim)
    parser_find_no_img.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_find_no_img.add_argument('--delete', '-d', help='Delete found non-image files.', action='store_true')

    parser_ev = subparsers.add_parser('ev', description='Evaluate common python code over "image" and "exf" vars.',
                                      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_ev.set_defaults(func=ev)
    parser_ev.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_ev.add_argument('-c', '--code', help='Custom (python) code.', type=str, default='print(image.size)')

    parser_border = subparsers.add_parser('border', description='Add border to image.',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_border.set_defaults(func=border)
    parser_border.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_border.add_argument('--width', '-wi', help='Border width.', type=int, default=1)
    parser_border.add_argument('--color', '-c', help='Border color.', type=str, default='white')
    parser_border.add_argument('--overwrite', '-w', help='Overwrite input images.', action='store_true')

    parser_optimize = subparsers.add_parser('optimize', description='Optimize JPG compression.',
                                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_optimize.set_defaults(func=optimize)
    parser_optimize.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_optimize.add_argument('--overwrite', '-w', help='Overwrite input images.', action='store_true')

    parser_rename = subparsers.add_parser('rename', description='''Rename image using pattern. You can use timestamp
                                          pattern and original name.''',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_rename.set_defaults(func=rename)
    parser_rename.add_argument('files', metavar='FILE', nargs='+', type=str)
    parser_rename.add_argument('--pattern', '-p', help='Rename pattern', type=str,
                               default='%Y_%m_%dT%H_%M_%S-ORIG_NAME.JPG')
    parser_rename.add_argument('--overwrite', '-w', help='Overwrite input images.', action='store_true')

    args = vars(parser.parse_args())
    if 'func' in args:
        func = args.pop('func')
        func(**args)
    else:
        parser.print_help()


def gray(files: list, overwrite: bool):
    for i, src_file in enumerate(files):
        image, exf = imread(src_file)
        if overwrite:
            out_file = src_file
        else:
            path_base, ext = os.path.splitext(src_file)
            out_file = '%s_gray%s' % (path_base, ext)
        print(src_file, '-->', out_file, 'graying ...')
        image_gray = ImageOps.grayscale(image)
        imwrite(image_gray, out_file, exf)


def stack(files: list, output: str, vertical: bool):
    if not output:
        output = '-'.join(files)
    ims = [np.asarray(imread(im)[0], dtype=np.uint8) for im in files]
    if vertical:
        i_shape = 1
        i_axis = 0
    else:
        i_shape = 0
        i_axis = 1
    sizes = [im.shape[i_shape] for im in ims]
    i_max = sizes.index(max(sizes))
    for i, im in enumerate(ims):
        if i is not i_max:
            f = ims[i_max].shape[i_shape] / im.shape[i_shape]
            img = Image.fromarray(ims[i])
            h, w = list(ims[i].shape)[:2]
            h = int(f * h)
            w = int(f * w)
            new_shape_list = [w, h]
            new_shape_list[i_axis] = ims[i_max].shape[i_shape]
            img = img.resize(tuple(new_shape_list))
            ims[i] = np.asarray(img, dtype=np.uint8)
    print(', '.join(files), '-->', output, 'joining ...')
    stacked_img = np.concatenate(tuple(ims), i_axis)
    imwrite(Image.fromarray(stacked_img), output)


def resize(files: list, overwrite: bool, size: int, width: int, height: int):
    for m_input in files:
        if overwrite:
            out_file = m_input
        else:
            path_base, ext = os.path.splitext(m_input)
            out_file = '%s_gray%s' % (path_base, ext)
        print(m_input, '-->', out_file, 'resizing ...')
        image, exf = imread(m_input)
        if width > 0:
            image2 = image.resize((width, height))
        else:
            f = size / max(image.size)
            w, h = image.size
            image2 = image.resize((int(f * w), int(f * h)))
        imwrite(image2, out_file, exf)


def _remove_exif(m_input: str):
    image, exf = imread(m_input)
    print(m_input, ' removing exif.')
    _, image, exf = try_rot_exif(image, exf)
    imwrite(image, m_input)


def _add_image_description(src: str, comment: str, overwrite: bool):
    image, exf = imread(src)
    exf["0th"][piexif.ImageIFD.ImageDescription] = comment.encode()
    if overwrite:
        out_file = src
    else:
        path_base, ext = os.path.splitext(src)
        out_file = '%s_commented%s' % (path_base, ext)
    print(src, '-->', out_file, 'adding comment ...')
    imwrite(image, out_file, exf)


def exif(files: list, remove: bool, comment: str, overwrite: bool):
    if remove:
        pool = mp.Pool(mp.cpu_count())
        pool.map(_remove_exif, files)
        pool.close()
    elif comment is not None:
        with mp.Pool(mp.cpu_count()) as pool:
            pool.map(partial(_add_image_description, comment=comment, overwrite=overwrite), files)
    else:
        for i, m_input in enumerate(files):
            image, exf = imread(m_input)
            for id, desc in piexif.TAGS['Exif'].items():
                if desc['name'] == 'MakerNote':  # exclude this long value
                    continue
                if id in exf['Exif']:
                    print(f"{desc['name']}: {exf['Exif'][id]}")
            for id, desc in piexif.TAGS['Image'].items():
                if id in exf['0th']:
                    print(f"{desc['name']}: {exf['0th'][id]}")


def rotate(files: list, overwrite: bool):
    for i, m_input in enumerate(files):
        if overwrite:
            out_file = m_input
        else:
            path_base, ext = os.path.splitext(m_input)
            out_file = '%s_rotated%s' % (path_base, ext)
        print(m_input, '-->', out_file, 'rotating ...')
        try:
            image, exf = imread(m_input)
            _, image, exf = try_rot_exif(image, exf)
            imwrite(image, out_file, exf)
        except BaseException:
            print('Error processing image %s:', m_input)
            traceback.print_exception(*sys.exc_info())


def crop(files: list, x: int, y: int, width: int, height: int, overwrite: bool):
    for m_input in files:
        if overwrite:
            out_file = m_input
        else:
            path_base, ext = os.path.splitext(m_input)
            out_file = '%s_cropped%s' % (path_base, ext)
        print(m_input, '-->', out_file, 'croping ...')
        image, exf = imread(m_input)
        image = np.asarray(image, dtype=np.uint8)
        print(y, height, x, width)
        image2 = image[y:y+height, x:x+width, :]
        imwrite(Image.fromarray(image2), out_file, exf)


def filter(files: list, criterion: str):
    for m_input in files:
        image, exf = imread(m_input)
        image = np.asarray(image, dtype=np.uint8)
        shape = image.shape
        h, w, _ = shape
        criteria_satisfied = eval(criterion)
        if criteria_satisfied:
            print(m_input)


def _convert(m_input: str, extension: str, overwrite: bool):
    try:
        image, exf = imread(m_input)
        image = np.asarray(image, dtype=np.uint8)
        path_base, ext = os.path.splitext(m_input)
        new_file_path = path_base + extension
        print('%s --> %s' % (m_input, new_file_path))
        imwrite(Image.fromarray(image), new_file_path)
        if overwrite:
            os.remove(m_input)
    except Exception as e:
        print('Error conversion %s:' % m_input, e)


def convert(files: list, extension: str, overwrite: bool):
    with mp.Pool(mp.cpu_count()) as pool:
        pool.map(partial(_convert, extension=extension, overwrite=overwrite), files)


def _gauss(m_input: str, std_dev: int, overwrite: bool):
    if overwrite:
        out_file = m_input
    else:
        path_base, ext = os.path.splitext(m_input)
        out_file = '%s_gaussed%s' % (path_base, ext)
    print('%s --> %s' % (m_input, out_file))
    image, exf = imread(m_input)
    image = np.asarray(image, dtype=np.uint8)
    noise = np.random.normal(0, std_dev, image.shape)
    image = image + noise
    image -= image.min()
    image /= (image.max() / 255.0)
    image = image.astype(np.uint8)
    imwrite(Image.fromarray(image), out_file)


def gauss(files: list, std_dev: float, overwrite: bool):
    with mp.Pool(mp.cpu_count()) as pool:
        pool.map(partial(_gauss, std_dev=std_dev, overwrite=overwrite), files)


def show(files: list, slideshow: bool, timeout: int):
    d = CursesDisplay(slideshow, timeout)
    d.run(files)


def _find_ext(src: str, append: bool):
    try:
        img, _ = imread(src)
        fmt = img.format
        if append:
            ext = 'jpg' if fmt == 'JPEG' else fmt.lower()  # Use jpg extension, not jpeg.
            dst = f'{src}.{ext}'
            shutil.move(src, dst)
            print('%s --> %s' % (src, dst))
        else:
            print(f'{src} format: {fmt}')
    except Exception as e:
        print('Image %s: %s' % (src, e))


def find_ext(files: list, append=bool):
    with mp.Pool(mp.cpu_count()) as pool:
        pool.map(partial(_find_ext, append=append), files)


def _find_noim(src: str, delete: bool):
    try:
        img, _ = imread(src)
    except Exception as e:
        if delete:
            os.remove(src)
            print('Removing %s' % src)
        else:
            print('Image %s: %s' % (src, e))


def find_noim(files: list, delete=bool):
    with mp.Pool(mp.cpu_count()) as pool:
        pool.map(partial(_find_noim, delete=delete), files)


def ev(files: list, code: str):
    for i, m_input in enumerate(files):
        image, exf = imread(m_input)
        eval(code)


def _border(m_input: str, width: int, color: str, overwrite: bool):
    if overwrite:
        out_file = m_input
    else:
        path_base, ext = os.path.splitext(m_input)
        out_file = '%s_border%s' % (path_base, ext)
    print('%s --> %s' % (m_input, out_file))
    image, exf = imread(m_input)
    image = ImageOps.expand(image, border=width, fill=color)
    imwrite(image, out_file, exf)


def border(files: list, width: int, color: str, overwrite: bool):
    with mp.Pool(mp.cpu_count()) as pool:
        pool.map(partial(_border, width=width, color=color, overwrite=overwrite), files)


def bytes2megabytes(n_bytes: float) -> float:
    return n_bytes / float(1 << 20)


def _optimize(src: str, overwrite: bool):
    image, exf = imread(src)
    orig_size = os.stat(src).st_size
    path_base, ext = os.path.splitext(src)
    if overwrite:
        new_file_path = src
    else:
        new_file_path = '%s_optimized%s' % (path_base, ext)
    print('%s --> %s' % (src, new_file_path))
    imwrite(image, new_file_path, exf)
    new_size = os.stat(new_file_path).st_size
    print("%.1f MB --> %.1f MB (optimization: %.1f %%)"
          % (bytes2megabytes(orig_size), bytes2megabytes(new_size), 100.0 * (orig_size - new_size) / orig_size))


def optimize(files: list, overwrite: bool):
    with mp.Pool(mp.cpu_count()) as pool:
        pool.map(partial(_optimize, overwrite=overwrite), files)


def _rename(src: str, pattern: str, overwrite: bool):
    try:
        image, exf = imread(src)
        path_base, ext = os.path.splitext(src)
        path_arr = path_base.split(os.sep)
        filename = path_arr[-1]
        pth = os.path.join(*path_arr[:-1])
        if 'Exif' in exf:
            strdatetime = exf['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        else:
            strdatetime = exf['0th'][piexif.ImageIFD.DateTime].decode('utf-8')
        dt = datetime.strptime(strdatetime, "%Y:%m:%d %H:%M:%S")

        new_file_name = dt.strftime(pattern)
        new_file_name = new_file_name.replace('ORIG_NAME', filename)
        new_file_path = os.path.join(pth, new_file_name)
        print('%s --> %s' % (src, new_file_path))
        if overwrite:
            os.rename(src, new_file_path)
        else:
            shutil.copyfile(src, new_file_path)
    except:
        print('Error processing image %s:', src)
        traceback.print_exception(*sys.exc_info())


def rename(files: str, pattern: str, overwrite: bool):
    with mp.Pool(mp.cpu_count()) as pool:
        pool.map(partial(_rename, pattern=pattern, overwrite=overwrite), files)
