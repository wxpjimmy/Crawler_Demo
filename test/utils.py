import time

def timeit(func):
    def wrap(*args):
        time1 = time.time()
        ret = func(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (func.func_name, (time2-time1)*1000.0)
        return ret
    return wrap

def search_accuracy_test(es_instance, keywords, expected_url):
	search = timeit(es_instance.search)
	resp = search(keywords, True)
	result = resp['result']
	if result == []:
	    #not match
	    # increase fail_empty
            return 'fail_empty'
	elif expected_url == result[0]:
	    # expected is in the first result
	    # should increase most_match, top3_match, top5_match
            return 'first_match'
	elif len(result) > 3:
	    if expected_url in result[1:3]:
		# find moast match in  1, 2
		# should increase top3 match, top5 match
                return 'top3_match'
	    elif expected_url in result[3:]:
		# find in top5
		# only increase top5 match
                return 'top5_match'
	    else:
		# result not empty and can't find the expected url
		# increase fail_not_empty 
                return 'fail_not_empty'
	else:
	    if expected_url in result[1:]:
		# find in top3
		# increase top3 match and top5 match
                return 'top3_match'
            else:
                return 'fail_not_empty'
#	return resp
