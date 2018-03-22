import setuptools

setuptools.setup(
    name='weechat-notify',
    version='0.0.1',
    url='https://github.com/kdeal/weechat-notify',

    author='Kyle Deal',
    author_email='kdeal@kyledeal.com',

    description='Weechat notifications via weechat relay',

    packages=setuptools.find_packages('.', exclude=('tests*',)),

    install_requires=['pyweechat', 'pync'],
    entry_points={
        'console_scripts': [
            'weechat-notify = weechat_notify.notify:main',
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)
