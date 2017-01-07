# pytest tdd watcher
tdd:
	watchmedo shell-command --patterns='*.py' --recursive \
	--command='clear && find . -wholename "*tests/test_*.py" | xargs py.test ${OPT}'

# Run all python tests
test:
	find . -wholename "*tests/test_*.py" | xargs py.test ${OPT}

check:
	isort -rc .
	flake8 .
