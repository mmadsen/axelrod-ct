from distutils.core import setup

setup(name="axelrod-ct",
      version="1.0",
      packages=['madsenlab',
                'madsenlab/axelrod',
                'madsenlab/axelrod/utils/configuration.py'],
      scripts=['simulations/sim-axelrod-original.py',
               'simulations/sim-semantic-axelrod.py',
               'admin/export-data-to-csv.py'
               ],
      author='Mark E. Madsen',
      author_email='mark@madsenlab.org',
      url='https://github.com/mmadsen/axelrod-ct',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.7',
          'Topic :: Scientific/Engineering',
      ]
      )