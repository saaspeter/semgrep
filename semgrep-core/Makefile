all:
    # Update output of semgrep-core -version
	echo 'let version = "$(shell git describe --dirty --tags --long)"' > ./bin/version.ml

	dune build
	dune build ./_build/default/tests/test.bc
clean:
	dune clean
test:
	dune runtest
e2etest:
	python3 tests/e2e/test_target_file.py
install:
	dune install
dump:
	./_build/default/tests/test.bc -dump_ast tests/lint/stupid.py

.PHONY: all clean install test dump
