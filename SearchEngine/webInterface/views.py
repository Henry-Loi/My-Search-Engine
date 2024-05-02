from django.shortcuts import render
from .engine import * 

# Create your views here.
def index(request):
    if request.method == 'POST':
        query = request.POST.get('query')

        # Perform search engine query processing here and get the results
        results = get_search_results(query)
        
        return render(request, 'webInterface/index.html', {'results': results})
    return render(request, 'webInterface/index.html')
