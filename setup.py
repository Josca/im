from setuptools import setup

setup(
    name='im',
    description='Fast and simple console image processing tool.',
    version='1.0',
    packages=['im'],
    install_requires=[
        'Click==6.2',
        'numpy==1.10.4',
        'Pillow==3.1.0',
        'piexif==1.0.3'
    ],
    entry_points='''
        [console_scripts]
        im=im.im:im_cmd
    ''',
)
