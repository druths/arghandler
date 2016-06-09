
test_inplace:	
	PYTHONPATH=.:${PYTHONPATH} python -m arghandler.test
	PYTHONPATH=.:${PYTHONPATH} python -m arghandler.tests.decorator
	PYTHONPATH=.:${PYTHONPATH} python -m arghandler.tests.decorator2

test_inplace_p3:
	PYTHONPATH=.:${PYTHONPATH} python3 -m arghandler.test
	PYTHONPATH=.:${PYTHONPATH} python3 -m arghandler.tests.decorator
	PYTHONPATH=.:${PYTHONPATH} python3 -m arghandler.tests.decorator2
