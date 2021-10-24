from django.conf import settings
import jwt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .renderers import UserRenderer
from .serializers import BookingSerializer, AdvisorSerializer, RegisterSerializer,LoginSerializer 
from .models import Booking, Advisor,User 
from rest_framework import exceptions, status
from .auth import generate_access_token, generate_refresh_token
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie


@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'Admin': 'admin/advisor/',
        'User Register': 'user/register/',
        'User Login': 'user/login/',
        'List Of Advisors': 'user/<user-id>/advisor/',
        'Book A Call With Advisor': 'user/<user-id>/advisor/<advisor-id>/',
        'Get Booked Call': 'user/<user-id>/advisor/booking/',
    }

    return Response(api_urls)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addAdvisor(request):
    serializer = AdvisorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(data=None, status=status.HTTP_200_OK)
    
    return Response(data=None, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@ensure_csrf_cookie
def userRegister(request):
    username = request.data['username']
    password = request.data['password']
    email = request.data['email']
    response = Response()
    if (username is None) or (password is None) or (email is None):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response
    user = request.data
    serializer = RegisterSerializer(data=user)
    
    
    if serializer.is_valid():
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
        response.set_cookie(key='refreshtoken',
                            value=refresh_token,
                            httponly=True)
        response.data = {
            'access_token': access_token,
            'user': user.id,
        }
        response.status_code = status.HTTP_200_OK
        return response
    
    response.status_code = status.HTTP_400_BAD_REQUEST
    return response


@api_view(['POST'])
@ensure_csrf_cookie
def userLogin(request):
    email = request.data['email']
    password = request.data['password']
    response = Response()
    if (email is None) or (password is None):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response

    user = User.objects.get(email=email)
    if(user is None):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return response
    if (not user.check_password(password)):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return response

    serialized_user = LoginSerializer(user).data
    
    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
    response.data = {
        'access_token': access_token,
        'user': serialized_user['id'],
    }

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllAdvisors(request, uid):
    try:
        advisor = Advisor.objects.filter(user=uid)
        serializer = AdvisorSerializer(advisor, many=True)
        return Response(data=serializer.data,status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data=None, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bookAdvisor(request, uid, aid):
    
    data ={
        "btime":request.data['btime'],
        "user":uid,
        "advisor":aid
    }
    serializer = BookingSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(data=None,status=status.HTTP_200_OK)
    
    return Response(data=None, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllBookings(request, uid):
    try:
        booking = Booking.objects.filter(user=uid)
        # serializer = BookingSerializer(booking, many=True)
        data=[]
        for i in booking:
            
            data.append({
                "id":i.id,
                "bookingTime":i.btime,
                "userId":i.user.id,
                "advisorId":i.advisor.id,
                "advisorName":i.advisor.aname,
                "advisorProfileURL":i.advisor.aprofileurl
            })
        return Response(data=data,status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data=None, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@csrf_protect
def refresh_token_view(request):
    refresh_token = request.COOKIES.get('refreshtoken')
    if refresh_token is None:
        raise exceptions.AuthenticationFailed(
            'Authentication credentials were not provided.')
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed(
            'expired refresh token, please login again.')

    user = User.objects.filter(id=payload.get('user_id')).first()
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')

    if not user.is_active:
        raise exceptions.AuthenticationFailed('User is inactive')


    access_token = generate_access_token(user)
    return Response({'access_token': access_token})