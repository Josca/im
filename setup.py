from setuptools import setup

setup(
    name='im',
    description='Fast and simple console image processing tool.',
    author='Josef Hák',
    author_email='pepa.hak@gmail.com',
    version='1.0.1',
    packages=['im'],
    url='https://github.com/Josca/im',
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
