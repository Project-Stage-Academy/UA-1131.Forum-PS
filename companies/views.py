from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import Company
from authentication.permissions import (IsAuthenticated, IsInvestor,
                                        IsRelatedToCompany)
from forum.errors import Error as er
from revision.views import CustomRevisionMixin

from .filters import CompanyFilter
from .models import Subscription
from .permissions import EditCompanyPermission
from .serializers import CompaniesSerializer, SubscriptionSerializer


class CompaniesViewSet(CustomRevisionMixin, viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompaniesSerializer
    permission_classes = (EditCompanyPermission,)
    filterset_class = CompanyFilter


class CompanyRetrieveView(APIView):
    permission_classes = (IsAuthenticated,)
    filterset_class = CompanyFilter

    def get(self, request, pk=None):
        if not pk:
            return er.NO_CREDENTIALS.response()
        try:
            company = Company.get_company(company_id=pk)
            return Response(company.get_info(), status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return er.NO_COMPANY_FOUND.response()


class CompaniesRetrieveView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        type = request.data.get('company_type')
        try:
            if not type:
                companies = Company.get_all_companies_info()
            else:
                companies = Company.get_all_companies_info(type)
        except Company.DoesNotExist:
            return er.NO_COMPANY_FOUND.response()
        return Response(companies, status=status.HTTP_200_OK)


class SubscriptionCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany, IsInvestor)

    def post(self, request, pk=None):
        if not pk:
            return er.NO_CREDENTIALS.response()

        profile_id = request.user.relation_id
        company_id = pk
        try:
            check_sub = Subscription.get_subscription(
                investor=profile_id, company=company_id)
            msg = f"You're already subscribed to {check_sub.company.brand}."
            return Response({'message': msg}, status=status.HTTP_200_OK)
        except Subscription.DoesNotExist:
            data = {'investor': profile_id,
                    'company': company_id}
            serializer = SubscriptionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                msg = f"You're successfully subscribed to {serializer.company.brand}"
                return Response({'message': msg, 'subscription_id': serializer.subscription_id},
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnsubscribeAPIView(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany, IsInvestor)

    def delete(self, request, subscription_id):
        try:
            subscription = Subscription.get_subscription(
                subscription_id=subscription_id)
        except Subscription.DoesNotExist:
            return er.SUBSCRIPTION_NOT_FOUND.response()
        company_id = subscription.company.company_id
        subscription.delete()
        return Response({'message': 'Successfully unsubscribed', 'company_id': company_id}, status=status.HTTP_200_OK)


class SubscriptionListView(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany)

    def get(self, request):
        profile_id = request.user.relation_id
        subs = Subscription.get_subscriptions(investor=profile_id)
        if not subs:
            return Response({'message': "You have no subsriptions yet!"}, status=status.HTTP_200_OK)
        data = [sub.get_info() for sub in subs]
        return Response({'subscriptions': data}, status=status.HTTP_200_OK)
