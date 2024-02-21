from rest_framework import generics
from .models import Companies
from .serializers import CompaniesSerializer
from rest_framework.permissions import IsAuthenticated


class CompaniesListCreateView(generics.ListCreateAPIView):
    queryset = Companies.objects.all()
    serializer_class = CompaniesSerializer
    permission_classes = (IsAuthenticated,)



class CompaniesRetrieveUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Companies.objects.all()
    serializer_class = CompaniesSerializer
    permission_classes = (IsAuthenticated,)
