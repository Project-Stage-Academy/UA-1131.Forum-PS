from rest_framework.generics import ListAPIView
import django_filters
from rest_framework import filters, status
from rest_framework.response import Response

from authentication.models import Company
from companies.filters import CompanyFilter
from companies.serializers import CompaniesSerializer
from search.models import SavedCompany


class SearchCompanyView(ListAPIView):
    """
    API view for searching and filtering companies.

    This view allows users to search for companies and apply filters based on various criteria.
    Filters can be applied to fields like name and region.

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
    ordering_fields = ["name", "region"]

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

    @staticmethod
    def post(request, *args, **kwargs):
        """
        Save a company for the authenticated user.

        This method creates a new SavedCompany object for the authenticated user,
        saving the specified company.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: The HTTP response object.
        """
        # Check if the request is authenticated
        if not request.user.is_authenticated:
            company_id = request.data.get('company_id')
            # Check if the company ID is provided in the request data
            if company_id:
                # Save information about the saved company
                SavedCompany.objects.create(user=request.user, company_id=company_id)
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Company ID is missing in request data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Authentication is required to save a company"},
                            status=status.HTTP_401_UNAUTHORIZED)
