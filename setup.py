from setuptools import setup

setup(
    name='im',
    description='Fast and simple console image processing tool.',
    version='1.0',
    packages=['im'],
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
