# IM: Simple Command Line Image Manipulation Tool
IM is easy-to-use fast image manipulation command line tool. It enables both single and __batch__ image processing.

![](im.gif)

* [Install](#install)
* [Usage](#usage)
* [Examples](#examples)
* [Dependencies](#deps)

You can resize, join (stack), rotate, convert and do more with your images without using any GUI.

## <a name="install"></a>Install
Install program as a standard Python package:

~~~bash
pip install .
~~~

## <a name="usage"></a>Usage
Application is used using command line with `im` command.

### Help option
Use `--help` option for global help and also as a help for a specific subcommand:

~~~bash
im --help
im resize --help
~~~

Help:

~~~bash
Usage: im [OPTIONS] COMMAND [ARGS]...

  Image manipulation tool.

Options:
  --help  Show this message and exit.

Commands:
  border     Add border to image.
  convert    Convert image to another format.
  crop       Crop image using [x, y, width, height]...
  ev         Evaluate common code over image.
  exif       Exif manipulation command.
  filter     Filter input images using given criterion.
  find_ext   Find correct image extension.
  find_noim  Find non-image files.
  gauss      Generate image with Gauss noise.
  gray       Convert image to grayscale.
  optimize   Optimize JPG compression.
  rename     Rename image using pattern.
  resize     Resize image to inserted size (higher...
  rotate     Rotate image according to exif orientation...
  show       Show image(s) - terminal view.
  stack      Join inserted images vertically (default) or...
~~~

### <a name="examples"></a>Examples
You can get testing `lena.jpg` image [here](https://raw.githubusercontent.com/opencv/opencv/master/samples/data/lena.jpg).

Convert between image formats:

~~~bash
im convert lena.jpg -e .png
~~~

Crop image with specific rectangle:

~~~bash
im crop lena.jpg -x 100 -y 100 -w 200 -h 300 -o lena_crop.jpg
~~~

Join multiple images vertically or horizontally (`-h`):

~~~bash
im stack lena.jpg lena.jpg lena.jpg -o out.jpg
~~~

Resize all `.jpg` images in current folder to max. width 1000 pixels:

~~~bash
im resize *.jpg -s 1000
~~~

Convert all `.jpg` images in current folder to grayscale.

~~~bash
im gray *.jpg
~~~

## <a name="deps"></a>Dependencies
All dependencies are standard pip installable packages. They are automatically installed with setup script.

* [Pillow](https://python-pillow.org/) -- _Image manipulation package._
* [Numpy](http://www.numpy.org/) -- _Matrix processing package._
* [Click](http://click.pocoo.org/5/) -- _CLI helper package._
* [Piexif](http://piexif.readthedocs.io/en/latest/) -- _EXIF data processing package._
