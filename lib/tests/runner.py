#!/usr/bin/env python

import os
import sys

import tests
from tests.suites import *

failures = tests.run()
if failures is None:
    print('Test suite was cancelled by setup')
    sys.exit(-1)

print('')
print('All test suites completed with %d failed tests' % len(failures))
if failures:
    print('Failed tests:\n%s' % '\n'.join(
        '\t%s - %s' % (test.name, test.message)
            for test in failures))
sys.exit(len(failures))

