"""
The current indentation.
"""
_indent = 0

def printf(format, *args):
    global _indent
    print '\t' * _indent + format % args


def assert_eq(v1, v2):
    """
    Asserts that v1 == v2.

    @raise AssertionError if not (v1 == v2)
    """
    if isinstance(v1, str) and isinstance(v1, str):
        # Handle string comparison specially
        if v1 != v2:
            for i, (v1l, v2l) in enumerate(zip(
                    v1.splitlines(), v2.splitlines())):
                if v1l != v2l:
                    raise AssertionError('On line %d: %s is not %s' % (
                        i + 1, v1, v2))
            raise AssertionError('Extra trailing text in string %d: %s' % (
                1 if len(v1) > len(v2) else 2,
                v1[len(v2):] if len(v1) > len(v2) else v2[len(v1):]))
    else:
        assert v1 == v2, \
            '%s is not %s' % (v1, v2)


class Suite(object):
    """
    The test suites to run when test.run is called.

    Use the decorator test to populate this list.
    """
    __suites__ = {}

    def __init__(self, name):
        """
        Initialises this test suite from a module instance.

        No tests are added automatically: when using the @test decorator, a test
        suite will be instantiated for the first decorated function, and all
        following decorated functions will be added to this object.

        @param name
            The name of this test suite.
        """
        super(Suite, self).__init__()
        self.tests = []
        self._name = name
        self._setup = lambda: True
        self._teardown = lambda: True

    @property
    def name(self):
        """The name of this test suite"""
        return self._name

    def run(self):
        """
        Runs this test suite.

        @return the failed tests, or None if the suite was cancelled by setup
        """
        if not self._setup():
            return None
        global _indent
        _indent += 1
        failures = [test for test in self.tests if not test()]
        self._teardown()
        _indent -= 1
        return failures

    @classmethod
    def _get_test_suite(self, test):
        """
        Returns the test suite for a test.

        If the suite does not already exist, it is created.

        @param test
            The test instance.
        @return the suite instance
        """
        # Get the global scope for the function to retrieve the name of the
        # defining module
        suite = test.suite \
            if 'suite' in test.__dict__ \
            else test.__globals__['__name__']

        # If the test suite does not yet exist, create it
        if not suite in self.__suites__:
            self.__suites__[suite] = Suite(suite)

        return self.__suites__[suite]


def test(func):
    """
    Use this decorator to mark a callable as a test.

    The description of the test is determined as follows:
        * If func.description exists, it is used.
        * If the test function has a docstring, it is used.
        * Otherwise the function name is split on '_' and then joined with '.'
          before any part that begins with a capital letter followed by a lower
          case letter and '_' for any other case.
    """
    test_name = func.name \
        if hasattr(func, 'name') \
        else func.__name__
    if hasattr(func, 'description'):
        test_description = func.description
    elif func.__doc__:
        test_description = ' '.join(func.__doc__.split())
    else:
        test_description = ''
        was_namespace = False
        for s in test_name.split('_'):
            test_description += \
                '.' + s if was_namespace else \
                '_' + s if test_description else \
                s
            was_namespace = len(s) >= 2 and (
                s[0].isupper() and s[1].islower())

    def inner():
        global _indent
        try:
            printf('%s - %s', test_name, test_description)
            try:
                _indent += 1
                func()
                return True
            finally:
                _indent -= 1
        except AssertionError as e:
            printf('Test %s did not pass: %s', test_name, e.message)
            inner.message = e.message
            return False
        except SystemExit:
            raise
        except Exception as e:
            import traceback
            printf('Test %s did not pass: %s', test_name, e.message or str(e))
            traceback.print_exc()
            inner.message = e.message
            return False

    # Add the function to the test suite for the defining module
    suite = Suite._get_test_suite(func)
    suite.tests.append(inner)

    inner.name = test_name
    inner.description = test_description
    inner.suite = suite.name
    inner.message = None
    return inner


def _before(before_func):
    """
    A decorator to make invocations of a function always call another function
    first.

    before_func is called with the same arguments as the decorated function.

    If the called function raises an exception, the decorated function is not
    called.
    """
    def decorator(func):
        def inner(*args, **kwargs):
            before_func(*args, **kwargs)
            func(*args, **kwargs)

        # Make sure to copy these necessary attributes
        inner.name = func.name \
            if hasattr(func, 'name') \
            else func.__name__
        inner.description = func.description \
            if hasattr(func, 'description') \
            else ' '.join(func.__doc__.split())
        inner.suite = Suite._get_test_suite(func).name
        return inner
    return decorator
test.before = _before

def _after(after_func):
    """
    A decorator to make invocations of a function always call another function
    after.

    after_func is called with the same arguments as the decorated function.

    If the decorated function raises an exception, after_func is still called.
    """
    def decorator(func):
        def inner(*args, **kwargs):
            try:
                func(*args, **kwargs)
            finally:
                after_func(*args, **kwargs)

        # Make sure to copy these necessary attributes
        inner.name = func.name \
            if hasattr(func, 'name') \
            else func.__name__
        inner.description = func.description \
            if hasattr(func, 'description') \
            else ' '.join(func.__doc__.split() if func.__doc__ else [])
        inner.suite = Suite._get_test_suite(func).name
        return inner
    return decorator
test.after = _after


def _setup(func):
    """
    Use this decorator to mark a callable as a test suite setup function.
    """
    Suite._get_test_suite(func)._setup = func

    return func
test.setup = _setup

def _teardown(func):
    """
    Use this decorator to mark a callable as a test suite teardown function.
    """
    Suite._get_test_suite(func)._teardown = func

    return func
test.teardown = _teardown


def run():
    global _indent
    total_failures = []

    for suite in Suite.__suites__.values():
        printf('Running test suite %s with %d tests...',
            suite.name, len(suite.tests))
        _indent += 1
        failures = [test for test in suite.tests if not test()]
        _indent -= 1
        printf('Test suite %s completed with %d failed test(s).',
            suite.name, len(failures))
        total_failures += failures

    return total_failures

