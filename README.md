# README
* IM is easy-to-use fast image manipulation command line tool. It enables both single and batch image processing.
You can resize, join (stack), rotate, convert and do more with your images without using any GUI.

## Dependencies
* All dependencies are standard pip installable packages. They are automatically installed with setup script.
    - Pillow    _Image manipulation package._
    - numpy     _Matrix processing package._
    - Click     _CLI helper package._
    - piexif    _EXIF data processing package._

## Install
* Install program as a standard Python 3 package:
    - pip3 install setup.py

## Usage
* Application is used using command line with 'im' command.

### Help option
* Use --help option for global help and also as a help for a specific subcommand:
    - im --help
    - im resize --help
* Help:
    Usage: im [OPTIONS] COMMAND [ARGS]...

      Image manipulation tool.

    Options:
      --help  Show this message and exit.

    Commands:
      crop    Crop image using [x, y, width, height]...
      exif    Exif manipulation command.
      gray    Convert image to grayscale.
      resize  Resize image to inserted size (higher...
      rotate  Rotate image according to exif orientation...
      stack   Join inserted images vertically (default) or...

### Examples
* Resize all .jpg images in current folder to max. width 1000 pixels:
    - im resize *.jpg -s 1000
* Convert all .jpg images in current folder to grayscale.
    - im gray *.jpg
