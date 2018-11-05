from setuptools import setup

setup(
    name='webotron-70',
    version='0.1',
    author='Ibrahima ba',
    author_email='ibbe4@yahoo.com',
    description='Webotron 70 is a tool to deploy static websites to AWS.',
    license='GPLv3+',
    packages=['webotron'],
    url='https://github.com/ibbe08/Automating-Aws-with-Python/tree/master/01-webotron',
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        webotron=webotron.webotron:cli
    '''

)
