import os
from functools import partial
import shutil
import sys
import traceback

import click
from PIL import ImageOps
import multiprocessing as mp

from im.display import CursesDisplay
from im.utils import *


@click.group(help='Image manipulation tool.')
def im_cmd():
    pass


@click.command(help='Convert image to grayscale.')
@click.argument('input', nargs=-1)
@click.option('--output', '-o', help='Path to output image.', multiple=True, default=None)
@click.option('--overwrite', '-w', help='Overwrite input images.', is_flag=True)
def gray(input, output, overwrite):
    if not output:
        output = [append_postfix(m, '_gray') for m in input]
    if overwrite:
        output = input
    for i, m_input in enumerate(input):
        print(m_input, ' --> ', output[i], ' graying ...')
        image, exf = imread(m_input)
        image_gray = ImageOps.grayscale(image)
        imwrite(image_gray, output[i], exf)


im_cmd.add_command(gray)


@click.command(help='Join inserted images vertically (default) or horizontally.')
@click.argument('input', nargs=-1)
@click.option('--output', '-o', help='Path to output image.', default=None)
@click.option('--horizontal', '-h', help='Join images horizontally.', is_flag=True)
def stack(input, output, horizontal):
    if not output:
        output = '-'.join(input)
    ims = [np.asarray(imread(im)[0], dtype=np.uint8) for im in input]
    if horizontal:
        i_shape = 0
        i_axis = 1
    else:
        i_shape = 1
        i_axis = 0
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
    stacked_img = np.concatenate(tuple(ims), i_axis)
    imwrite(Image.fromarray(stacked_img), output)


im_cmd.add_command(stack)


@click.command(help='Resize image to inserted size (higher dimension).')
@click.argument('input', nargs=-1)
@click.option('--output', '-o', help='Path to output image.', multiple=True, default=None)
@click.option('--overwrite', '-w', help='Overwrite input images.', is_flag=True)
@click.option('--size', '-s', help='Higher dimension output size (1000 by default).', type=int, default=1000)
@click.option('--width', '-wi', help='Width.', type=int, default=0)
@click.option('--height', '-h', help='Height.', type=int, default=0)
def resize(input, output, overwrite, size, width, height):
    if not output:
        output = [append_postfix(m, '_resized') for m in input]
    if overwrite:
        output = input
    for i, m_input in enumerate(input):
        print(m_input, ' --> ', output[i], ' resizing ...')
        image, exf = imread(m_input)
        if width > 0:
            image2 = image.resize((width, height))
        else:
            f = size / max(image.size)
            w, h = image.size
            image2 = image.resize((int(f * w), int(f * h)))
        imwrite(image2, output[i], exf)


im_cmd.add_command(resize)


def _remove_exif(m_input: str):
    image, exf = imread(m_input)
    print(m_input, ' removing exif.')
    _, image, exf = try_rot_exif(image, exf)
    imwrite(image, m_input)


@click.command(help='Exif manipulation command.')
@click.argument('input', nargs=-1)
@click.option('--remove', '-r', help='Remove exif info from image.', is_flag=True)
def exif(input, remove):
    if not remove:
        for i, m_input in enumerate(input):
            image, exf = imread(m_input)
            print('Image: %s' % m_input)
            for ifd in ['0th', '1st']:
                for tag in exf[ifd]:
                    print(piexif.TAGS[ifd][tag]['name'], exf[ifd][tag])
    else:
        pool = mp.Pool(mp.cpu_count())
        pool.map(_remove_exif, input)
        pool.close()


im_cmd.add_command(exif)


@click.command(help='Rotate image according to exif orientation\
 info or by 90 degrees in the counter-clockwise direction.')
@click.argument('input', nargs=-1)
@click.option('--output', '-o', help='Path to output image.', multiple=True, default=None)
@click.option('--overwrite', '-w', help='Overwrite input images.', is_flag=True)
@click.option('--k', '-k', help='Number of times the array is rotated by 90 degrees.', type=int, default=None)
def rotate(input, output, overwrite, k):
    if not output:
        output = [append_postfix(m, '_rotated') for m in input]
    if overwrite:
        output = input
    for i, m_input in enumerate(input):
        print(m_input, ' --> ', output[i], ' rotating ...')
        try:
            image, exf = imread(m_input)
            _, image, exf = try_rot_exif(image, exf)
            imwrite(image, output[i], exf)
        except BaseException:
            traceback.print_exception(*sys.exc_info())


im_cmd.add_command(rotate)


@click.command(help='Crop image using [x, y, width, height] window.')
@click.argument('input', nargs=-1)
@click.option('--output', '-o', help='Path to output image.', multiple=True, default=None)
@click.option('--x', '-x', help='Upper left crop window corner x coordinate.', default=0)
@click.option('--y', '-y', help='Upper left crop window corner y coordinate.', default=0)
@click.option('--width', '-w', help='Crop window width.', type=int)
@click.option('--height', '-h', help='Crop window height.', type=int)
@click.option('--overwrite', help='Overwrite input images.', is_flag=True)
def crop(input, output, x, y, width, height, overwrite):
    if not output:
        output = [append_postfix(m, '_crop') for m in input]
    if overwrite:
        output = input
    print(output)
    for i, m_input in enumerate(input):
        print(m_input, ' --> ', output[i], ' croping ...')
        image, exf = imread(m_input)
        image = np.asarray(image, dtype=np.uint8)
        image2 = image[y:y+height, x:x+width, :]
        imwrite(Image.fromarray(image2), output[i], exf)


im_cmd.add_command(crop)


@click.command(help='Filter input images using given criterion.')
@click.argument('input', nargs=-1)
@click.option('--criterion', '-c', help='Images filtering criterion (python syntax, f.e.: \'w * h > 100\').')
def filter(input, criterion):
    for m_input in input:
        image, exf = imread(m_input)
        image = np.asarray(image, dtype=np.uint8)
        shape = image.shape
        h, w, _ = shape
        criteria_satisfied = eval(criterion)
        if criteria_satisfied:
            click.echo(m_input)


im_cmd.add_command(filter)


def _convert(input: str, extension: str, overwrite: bool):
    try:
        image, exf = imread(input)
        image = np.asarray(image, dtype=np.uint8)
        path_base, ext = os.path.splitext(input)
        new_file_path = path_base + extension
        print('%s --> %s' % (input, new_file_path))
        imwrite(Image.fromarray(image), new_file_path)
        if overwrite:
            os.remove(input)
    except Exception as e:
        print('Error conversion %s:' % input, e)


@click.command(help='Convert image to another format.')
@click.argument('input', nargs=-1)
@click.option('--extension', '-e', help='Required new image extension, f.e.: \'.png\'.')
@click.option('--overwrite', '-w', help='Overwrite image (remove old one).', is_flag=True)
def convert(input, extension, overwrite):
    pool = mp.Pool(mp.cpu_count())
    pool.map(partial(_convert, extension=extension, overwrite=overwrite), input)
    pool.close()


im_cmd.add_command(convert)


def _gauss(input: str, std_dev: int):
    image, exf = imread(input)
    image = np.asarray(image, dtype=np.uint8)
    noise = np.random.normal(0, std_dev, image.shape)
    image = image + noise
    image -= image.min()
    image /= (image.max() / 255.0)
    image = image.astype(np.uint8)
    path_base, ext = os.path.splitext(input)
    new_file_path = '%s_gauss%d%s' % (path_base, std_dev, ext)
    print('%s --> %s' % (input, new_file_path))
    imwrite(Image.fromarray(image), new_file_path)


@click.command(help='Generate image with Gauss noise.')
@click.argument('input', nargs=-1)
@click.option('--std-dev', '-s', help='Standard deviation.', type=int)
def gauss(input, std_dev):
    pool = mp.Pool(mp.cpu_count())
    pool.map(partial(_gauss, std_dev=std_dev), input)
    pool.close()


im_cmd.add_command(gauss)


@click.command(help='Show image(s) - terminal view.')
@click.argument('images', nargs=-1)
@click.option('--slideshow', '-s', help='Run as slideshow.', is_flag=True)
@click.option('--timeout', '-t', help='Slideshow timeout (s).', type=int, default=1)
def show(images: list, slideshow: bool, timeout: int):
    d = CursesDisplay(slideshow, timeout)
    d.run(images)


im_cmd.add_command(show)


def _find_ext(src: str, append: bool):
    try:
        img, _ = imread(src)
        fmt = img.format
        if append:
            ext = 'jpg' if fmt == 'JPEG' else fmt.lower()  # Use jpg extension, not jpeg.
            dst = '%s.%s' % (src, ext)
            shutil.move(src, dst)
            print('%s --> %s' % (src, dst))
        else:
            print('%s format: %s' % fmt)
    except Exception as e:
        print('Image %s: %s' % (src, e))


@click.command(help='Find correct image extension.')
@click.argument('srcs', nargs=-1)
@click.argument('input', nargs=-1)
def find_ext(srcs: str, append=bool):
    pool = mp.Pool(mp.cpu_count())
    pool.map(partial(_find_ext, append=append), srcs)
    pool.close()


im_cmd.add_command(find_ext)


def _find_noim(src: str, delete: bool):
    try:
        img, _ = imread(src)
    except Exception as e:
        if delete:
            os.remove(src)
            print('Removing %s' % src)
        else:
            print('Image %s: %s' % (src, e))


@click.command(help='Find non-image files.')
@click.argument('srcs', nargs=-1)
@click.option('--delete', '-d', help='Delete found non-image files.', is_flag=True)
def find_noim(srcs: str, delete=bool):
    pool = mp.Pool(mp.cpu_count())
    pool.map(partial(_find_noim, delete=delete), srcs)
    pool.close()


im_cmd.add_command(find_noim)


@click.command(help='Evaluate common code over image.')
@click.argument('input', nargs=-1)
@click.option('-c', '--code', help='Custom code, f.e.: \'print(image.size)\'.', type=str, default='print(image.size)')
def ev(input, code: str):
    for i, m_input in enumerate(input):
        image, exf = imread(m_input)
        eval(code)


im_cmd.add_command(ev)


def _border(src: str, width: int, color: str):
    image, exf = imread(src)
    image = ImageOps.expand(image, border=width, fill=color)
    path_base, ext = os.path.splitext(src)
    new_file_path = '%s_border%s' % (path_base, ext)
    print('%s --> %s' % (src, new_file_path))
    imwrite(image, new_file_path, exf)


@click.command(help='Add border to image.')
@click.argument('srcs', nargs=-1)
@click.option('--width', '-w', help='Border width.', type=int, default=1)
@click.option('--color', '-c', help='Border color.', type=str, default='white')
def border(srcs: str, width: int, color: str):
    pool = mp.Pool(mp.cpu_count())
    pool.map(partial(_border, width=width, color=color), srcs)
    pool.close()


im_cmd.add_command(border)


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
    print("orig size: %f, new size %f, optimization: %.1f" % (orig_size, new_size, 100.0 * (orig_size - new_size) / orig_size))


@click.command(help='Optimize JPG compression.')
@click.argument('srcs', nargs=-1)
@click.option('--overwrite', '-w', help='Overwrite input images.', is_flag=True)
def optimize(srcs: str, overwrite: bool):
    pool = mp.Pool(mp.cpu_count())
    pool.map(partial(_optimize, overwrite=overwrite), srcs)
    pool.close()


im_cmd.add_command(optimize)
