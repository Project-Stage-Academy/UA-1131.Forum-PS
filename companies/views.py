from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from authentication.models import Company
from .filters import CompanyFilter
from .models import Subscription
from .serializers import CompaniesSerializer, SubscriptionSerializer, SubscriptionListSerializer
from .managers import ArticlesManager as am, LIMIT

JWT_authenticator = JWTAuthentication()


class CompaniesListCreateView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompaniesSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = CompanyFilter


class CompaniesRetrieveUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompaniesSerializer
    # permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = CompanyFilter


class SubscriptionCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        auth_response = JWT_authenticator.authenticate(request)
        if auth_response is None:
            return Response({'error': "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = auth_response[1].get('user_id')
        request.data['investor'] = user_id
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            subs = Subscription.objects.filter(investor=user_id, company=request.data.get('company'))
            if not subs:
                subscription = serializer.save()
            else:
                subscription = subs.first()
            company = subscription.company
            brand = company.brand
            subscription_id = subscription.subscription_id
            message = f"You're subscribed to {brand}, subscription id: {subscription_id}"
            return Response({'message': message}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnsubscribeAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, subscription_id, *args, **kwargs):
        response = JWT_authenticator.authenticate(request)
        if response is None:
            return Response({'error': "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = response[1].get('user_id')

        try:
            subscription = Subscription.objects.get(subscription_id=subscription_id, investor_id=user_id)
        except Subscription.DoesNotExist:
            return Response({'error': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)

        subscription.delete()
        return Response({'message': 'Successfully unsubscribed'}, status=status.HTTP_204_NO_CONTENT)


class SubscriptionListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        response = JWT_authenticator.authenticate(request)
        if response is None:
            return Response({'error': "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = response[1].get('user_id')
        subs = Subscription.objects.filter(investor_id=user_id).values()
        if not subs:
            return Response({'message': "You have no subs"}, status=status.HTTP_204_NO_CONTENT)
        serializer = SubscriptionListSerializer(subs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RetrieveArticles(APIView):
    def get(self, request, pk=None, page=None):
        if not pk or not page:
            return Response({'error': "No company id or page was provided"}, status=status.HTTP_400_BAD_REQUEST)
        skip = LIMIT * (page - 1)
        articles = am.get_articles_for_company(pk, skip=skip, projection=['articles'])
        return Response(articles, status=status.HTTP_200_OK)

class CreateArticle(APIView):
    authentication_classes = ()
    def post(self, request):
        data = request.data
        company_id = data.get('company_id')
        # company_id and relation_id should be retrieved from request.user
        try:
            company = Company.get_company(company_id=company_id)
        except Company.DoesNotExist:
            return Response({'error':'The company you tried rto create article for does not exist or was deleted.'}, status=status.HTTP_404_NOT_FOUND)
        res = am.add_article(data)
        # article = res.get('articles')[0]
        return Response(res, status=status.HTTP_201_CREATED)

    def patch(self, request):
        pass

class DeleteArticle(APIView):
    def delete(self, request, pk):
        pass

