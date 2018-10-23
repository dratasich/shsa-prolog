Tests
=====

Run all testcases from the root directory (`..` from here):
    ```bash
    $ ./test/run_tests
    ```

Run a testcase separately (e.g., a failed one).

Problog:
    ```bash
    $ ./test/run_test test/test_some-name.pl
    ```

Python:
    ```bash
    $ python3 -m unittest test/test_some-name.py
    ```

Debug a (failed) python testcase:
    ```bash
    $ python3 -m pdb test/test_some-name.py
    ```

Run all python testcases:
    ```bash
    $ python3 -m unittest discover
    ```
