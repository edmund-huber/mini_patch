import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='mini_patch',
    version='0.0.3',
    author='Edmund Huber',
    author_email='me@ehuber.info',
    description="Tiny diffs using difflib's SequenceMatcher",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/edmund-huber/mini_patch',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
