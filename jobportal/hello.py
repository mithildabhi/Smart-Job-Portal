from django.http import JsonResponse

def health(request):
	"""Simple health/readiness endpoint for load balancers and probes."""
	return JsonResponse({'status': 'ok'})

def hello(request):
	return JsonResponse({'hello': 'jobportal'})
