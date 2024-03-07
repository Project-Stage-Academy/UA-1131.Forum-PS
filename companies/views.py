from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.models import Company
from authentication.permissions import IsAuthenticated, IsRelatedToCompany, IsInvestor
from .models import Subscription
from .serializers import SubscriptionSerializer, SubscriptionListSerializer

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
        company_id = request.data.get('company')

        check_sub = Subscription.get_subcription(
            investor=profile_id, company=company_id)
        if check_sub:
            msg = f"You're already subscribed to {check_sub.company.brand}."
            return Response({'message': msg}, status=status.HTTP_200_OK)
        request.data['investor'] = profile_id
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            subscription = serializer.save()
            msg = f"You're successfully subscribed to {subscription.company.brand}"
            return Response({'message': self.msg, 'subscription_id': subscription.subscription_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnsubscribeAPIView(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany, IsInvestor)
    # should we notify startup company who exactly unsubscribed from their startup profile?
    def delete(self, request, subscription_id):
        try:
            subscription = Subscription.get_subcription(
                subscription_id=subscription_id)
        except Subscription.DoesNotExist:
            return Response({'error': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)
        company_id = subscription.company.company_id
        subscription.delete()
        return Response({'message': 'Successfully unsubscribed', 'company_id': company_id}, status=status.HTTP_204_NO_CONTENT)

class SubscriptionListView(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany)

    def get(self, request):
        profile_id = request.user.relation_id
        subs = Subscription.get_subcriptions(investor=profile_id).values()
        if not subs:
            return Response({'message': "You have no subsriptions yet!"}, status=status.HTTP_204_NO_CONTENT)
        serializer = SubscriptionListSerializer(subs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
