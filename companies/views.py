from rest_framework import generics
from .models import Companies
from .serializers import CompaniesSerializer


class CompaniesListCreateView(generics.ListCreateAPIView):
    queryset = Companies.objects.all()
    serializer_class = CompaniesSerializer


class CompaniesRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Companies.objects.all()
    serializer_class = CompaniesSerializer
