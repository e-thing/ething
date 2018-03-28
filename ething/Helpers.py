
import json
import datetime

def dict_recursive_update(a, *more):
	for b in more:
		for k, v in b.iteritems():
			if isinstance(v, dict) and k in a and isinstance(a[k], dict):
				a[k] = dict_recursive_update(a.get(k, {}), v)
			else:
				a[k] = v
	return a


def serialize(obj):
	"""JSON serializer for objects not serializable by default json code"""
	if hasattr(obj, 'toJson'):
		return obj.toJson()
	if isinstance(obj, datetime.datetime):
		return obj.isoformat()
	return obj.__dict__


def toJson(obj, **kwargs):
	return json.dumps(obj, default=serialize, **kwargs)



if __name__ == '__main__':
	
	
	a = {
		'a': {
			'a.a':1
		},
		'b': [1,2],
		'd': 4
	}
	
	b = {
		'a': {
			'a.a':45,
			'a.b':49
		},
		'b': [3,4],
		'c': 3
	}
	
	print dict_recursive_update({}, a, b)
	
	print a
	
	