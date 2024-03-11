from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from authentication.models import Company
from authentication.permissions import IsAuthenticated, IsRelatedToCompany, IsStartup, IsInvestor, IsFounder
from .filters import CompanyFilter
from .models import Subscription
from .serializers import CompaniesSerializer, SubscriptionSerializer
from .managers import ArticlesManager as am, LIMIT
from forum import errors as er
from pydantic import ValidationError as PydanticValidationError


class CompaniesListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = CompaniesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompanyRetrieveView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, pk=None):
        if pk:
           try:
               company = Company.get_company(company_id=pk)
               return Response(company.get_info(), status=status.HTTP_200_OK)
           except Company.DoesNotExist:
               return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND) 
        else: 
            return Response({'error': er.NO_CREDENTIALS.msg}, status=er.NO_CREDENTIALS.status)
    
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
            return Response({'error': er.NO_COMPANY_FOUND.msg}, status=er.NO_COMPANY_FOUND.status)
        return Response(companies, status=status.HTTP_200_OK)
    
class SubscriptionCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany, IsInvestor)

    def post(self, request, pk=None):
        if not pk:
            return Response({'error': er.NO_CREDENTIALS.msg}, status=er.NO_CREDENTIALS.status)
        
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
                return Response({'message': msg, 'subscription_id': serializer.subscription_id}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

class RetrieveArticles(APIView):
    # do we need to block access to the articles for an unauthorized viewers?
    def get(self, request, pk=None, page=None):
        if not pk or not page:
            return Response({'error': "No company id or page was provided"}, status=status.HTTP_400_BAD_REQUEST)
        skip = LIMIT * (page - 1)
        articles = am.get_articles_for_company(pk, skip=skip, projection=['articles'])
        return Response(articles, status=status.HTTP_200_OK)

class CreateArticle(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany, IsStartup)
    def post(self, request):
        data = request.data
        company_id = request.user.company['company_id']
        relation_id = request.user.relation_id
        data['relation'] = relation_id
        data['company_id'] = company_id
        try:
            res = am.add_article(data)
        except PydanticValidationError as e:
            return Response({'error': er.Error.INVALID_ARTICLE.msg}, status=er.Error.INVALID_ARTICLE.status)    
        return Response({'document_was_created': res}, status=status.HTTP_201_CREATED)

class UpdateArticle(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany)
    def patch(self, request, art_id=None):
        data = request.data
        company_id = request.user.company['company_id']
        updated_article = am.update_article(company_id, art_id, data)
        return Response(updated_article)


class DeleteArticle(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany, IsStartup, IsFounder)
    def delete(self, request, art_id=None):
        company_id = request.user.company['company_id']
        res = am.delete_article(company_id, art_id)
        if res:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(er.Error.INVALID_ARTICLE_ID.msg, status=er.Error.INVALID_ARTICLE_ID.status)

        

