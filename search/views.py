from rest_framework.generics import ListAPIView
import django_filters
from rest_framework import filters

from authentication.models import Company
from companies.filters import CompanyFilter
from companies.serializers import CompaniesSerializer
from search.models import SavedCompany


class SearchCompanyView(ListAPIView):
    """
    API view for searching and filtering companies.

    This view allows users to search for companies and apply filters based on various criteria.
    Filters can be applied to fields like brand.

    Attributes:
        queryset (QuerySet): The queryset containing all companies.
        serializer_class (Serializer): The serializer class for serializing company data.
        filter_backends (list): The filter backends used for filtering companies.
        filterset_class (FilterSet): The filterset class used for defining filters.
        ordering_fields (list): The fields by which companies can be ordered.
    """

    queryset = Company.objects.all()
    serializer_class = CompaniesSerializer
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_class = CompanyFilter
    ordering_fields = ["brand"]

    def get_serializer_context(self):
        """
        Get the context for the serializer.

        This method adds the list of saved companies for the authenticated user
        to the serializer context.

        Returns:
            dict: The context for the serializer.
        """
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            saved_companies_pk = frozenset(
                SavedCompany.objects.filter(
                    user=self.request.user.id
                ).values_list("company_id", flat=True)
            )
            context.update({"saved_companies_pk": saved_companies_pk})
        return context
