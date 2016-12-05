from setuptools import setup

setup(
    name='im',
    description='Fast and simple console image processing tool.',
    author='hakjosef',
    author_email='pepa.hak@gmail.com',
    version='1.0',
    packages=['im'],
    url='https://github.com/Josca/im',
    download_url='https://github.com/Josca/im/tarball/1.0',
    keywords=['image', 'viewer', 'crop', 'convert'],
    install_requires=[
        'Click>=6.6',
        'numpy>=1.11.1',
        'Pillow>=3.2.0',
        'piexif>=1.0.4'
    ],
    entry_points='''
        [console_scripts]
        im=im.im:im_cmd
    ''',
)
