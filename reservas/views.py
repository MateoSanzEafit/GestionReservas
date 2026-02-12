from django.shortcuts import render

def index(request):
    """
    Renders the landing page.
    """
    return render(request, 'reservas/index.html')
