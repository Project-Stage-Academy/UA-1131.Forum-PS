from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.models import Company, CustomUser, CompanyAndUserRelation
from authentication.permissions import IsAuthenticated, IsRelatedToCompany, IsInvestor
from .models import Subscription
from .serializers import SubscriptionSerializer, SubscriptionListSerializer, CompaniesSerializer

class CompaniesListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = CompaniesSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer)
            company = Company(**serializer.data)
            company.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompaniesRetrieveUpdateView(APIView):
    permission_classes = (IsAuthenticated)
    def get(request, pk=None):
        if pk:
            company = Company.get_company(company_id=pk)
            return Response(company.get_info(), status=status.HTTP_200_OK)
        type = request.data.get('company_type')
        if not type:
           companies = Company.get_all_companies_info()
        else:
            companies = Company.get_all_companies_info(type)
        return Response(companies, status=status.HTTP_200_OK)
    
class SubscriptionCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany, IsInvestor)

    def post(self, request):
        profile_id = request.user.relation_id
        company_id = request.data.get('company_id')
        try:
            check_sub = Subscription.get_subscription(
                investor=profile_id, company=company_id)
        except Subscription.DoesNotExist:
            try:
                data = {'investor': CompanyAndUserRelation.get_relation(relation_id=profile_id), 
                        'company':Company.get_company(company_id=company_id)}
            except (Company.DoesNotExist, CompanyAndUserRelation.DoesNotExist) as e:
                return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
            serializer = SubscriptionSerializer(data=data)
            if serializer.is_valid():
                subscription = Subscription(**data)
                subscription.save()
                msg = f"You're successfully subscribed to {subscription.company.brand}"
                return Response({'message': msg, 'subscription_id': subscription.subscription_id}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        msg = f"You're already subscribed to {check_sub.company.brand}."
        return Response({'message': msg}, status=status.HTTP_200_OK)

class UnsubscribeAPIView(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany, IsInvestor)

    def delete(self, request, subscription_id):
        try:
            subscription = Subscription.get_subscription(
                subscription_id=subscription_id)
        except Subscription.DoesNotExist:
            return Response({'error': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)
        company_id = subscription.company.company_id
        subscription.delete()
        return Response({'message': 'Successfully unsubscribed', 'company_id': company_id}, status=status.HTTP_200_OK)

class SubscriptionListView(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany)

    def get(self, request):
        profile_id = request.user.relation_id
        subs = Subscription.get_subscriptions(investor=profile_id)
        if not subs:
            return Response({'message': "You have no subsriptions yet!"}, status=status.HTTP_204_NO_CONTENT)
        data = [sub.get_info() for sub in subs]
        return Response({'subscriptions': data}, status=status.HTTP_200_OK)
