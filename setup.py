from distutils.core import setup

setup(
    name='skypy',
    version='1.0.0',
    packages=['codebase', 'codebase.tests', 'codebase.tests.test_cryptodata',
              'codebase.tests.test_socket_server', 'codebase.utils',
              'codebase.client', 'codebase.common', 'codebase.server',
              'codebase.server.db', 'codebase.frontend'],
    install_requires=[
        "pycrypto==2.6.1"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Communications :: Chat',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    package_dir={'': 'skypy'},
    url='https://github.com/Kras4ooo/skypy',
    license='MIT License',
    author='Krassi',
    author_email='krasimir.nikolov1994@gmail.com',
    description='SkyPy is a desktop application'
)
