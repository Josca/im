import click
import numpy as np
from PIL import Image, ImageOps
import piexif


def imread(filepath):
    image = Image.open(filepath)
    try:
        exf = piexif.load(image.info['exif'])
    except:
        exf = None
    return image, exf


def imwrite(image, filename, exif=None):
    if exif:
        image.save(filename, exif=piexif.dump(exif))
    else:
        image.save(filename)


def append_postfix(filename, postfix):
    arr = filename.split('.')
    arr[-2] = arr[-2] + postfix
    result = '.'.join(arr)
    return result


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


@click.command(help='Exif manipulation command.')
@click.argument('input', nargs=-1)
@click.option('--remove', '-r', help='Remove exif info from image.', is_flag=True)
@click.option('--show', '-s', help='Show image exif info.', is_flag=True)
def exif(input, remove, show):
    for i, m_input in enumerate(input):
        image, exf = imread(m_input)
        if show:
            print('Image: %s' % m_input)
            for ifd in ['0th', '1st']:
                for tag in exf[ifd]:
                    print(piexif.TAGS[ifd][tag]['name'], exf[ifd][tag])
            print()
        if remove:
            imwrite(image, m_input)

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
        image, exf = imread(m_input)
        if exf:
            orientation_flag = exf['0th'][piexif.ImageIFD.Orientation]
            exf['0th'][piexif.ImageIFD.Orientation] = 1
            if not k:
                if orientation_flag == 3:
                    k = 2
                elif orientation_flag == 6:
                    k = -1
                elif orientation_flag == 8:
                    k = 1
                else:
                    k = 0
        mat = np.asarray(image, dtype=np.uint8)
        mat2 = np.rot90(mat, k)
        imwrite(Image.fromarray(mat2), output[i], exf)

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
