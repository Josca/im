from setuptools import setup

setup(
    name='im',
    description='Fast and simple console image processing tool.',
    author='Josef Hák',
    author_email='pepa.hak@gmail.com',
    version='1.2.3',
    packages=['im'],
    url='https://github.com/Josca/im',
    keywords=['image', 'viewer', 'crop', 'convert', 'optimize jpeg'],
    install_requires=[
        'numpy>=2.0.2',
        'Pillow>=11.1.0',
        'piexif>=1.1.3'
    ],
    extras_require={
        'test': ['pytest', 'ruff'],
    },
    entry_points='''
        [console_scripts]
        im=im.im:im_cmd
    ''',
)
