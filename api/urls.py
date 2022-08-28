# この api/urls.py は、アプリケーション・レベルのUrlsであり、
# コレに対して rest_api/urls.py は、プロジェクト・レベルのUrlsである。
# そして、最終的には rest_api/urls.py に api/urls.py を読み込むことになる。

from django.urls import path, include
# Token認証で使う
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from rest_framework.routers import DefaultRouter


# ********** ********** **********
# routerを使って、ViewsとUrlsの連携を行う
router = DefaultRouter()

# segmentsというUrlパスとSegmentViewSetを紐付ける
router.register('segments', views.SegmentViewSet)
router.register('brands', views.BrandViewSet)
router.register('vehicles', views.VehicleViewSet)

app_name = 'api'

# genericsから継承してきたものは以下に記載する
urlpatterns = [
    # genericsのViewSetの場合は、最後に.as_view()を付ける必要がある。
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('profile/', views.ProfileUserView.as_view(), name='profile'),
    # auth/というエンドポイントへユーザ名とパスワードでアクセスした際、Tokenを返す
    # obtain_auth_tokenは、Django_Rest_Framework に標準で装備されているViewである。
    # これを紐付けることで、この機能を実現できる。
    path('auth/', obtain_auth_token, name='auth'),
    # ルートパスにアクセスが有った場合は、上部に記載したrouter.register()の
    path('', include(router.urls)),
]