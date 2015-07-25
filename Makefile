
test_inplace:	
	PYTHONPATH=.:${PYTHONPATH} python -m arghandler.test
	PYTHONPATH=.:${PYTHONPATH} python -m arghandler.tests.decorator
