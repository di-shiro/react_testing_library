from rest_framework import generics, permissions, viewsets, status
from .serializers import UserSerializer, SegmentSerializer, BrandSerializer, VehicleSerializer
from .models import Segment, Brand, Vehicle
from rest_framework.response import Response


# これは、ModelとViewによる２つがある。
# ModelViewは、CRUDの機能をまるごと提供している。
# Createの機能に特化したものを作りたい場合はgenericsから、CreateAPIViewを継承してくる。
class CreateUserView(generics.CreateAPIView):
    # ユーザに関するViewなのでSerializerを割り当てる。
    serializer_class = UserSerializer

    # 現状、ユーザ認証を通貨したユーザのみが各Viewにアクセスできるようになっている。
    # settings.pyにて、プロジェクト全体に対して適用されている。
    # しかし、Userを新規作成できるためには誰でも新規作成画面にアクセスできる必要がある。
    # そのため、以下のpermissionで権限を上書きしている。
    permission_classes = (permissions.AllowAny,)

# ログインUserの情報を返してくれるView
class ProfileUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer


    def get_object(self):
        # ログインしているユーザのオブジェクトを返す
        return self.request.user    # これがログインユーザを表している

    # RetrieveUpdateAPIViewを継承しているが、
    # 今回はUpdate機能は使わないので、UpdateとPatchのメソッドを変更して上書きする。
    # 変更内容は、これらのメソッドにアクセスがあった際にはエラーを返すというもの。

    # Updateメソッドをオーバーライドする
    def update(self, request, *args, **kwargs):
        response = {'message': 'PUT method is not allowed'} # Errorメッセージ
        s = status.HTTP_405_METHOD_NOT_ALLOWED # ステータス
        return Response(response, status=s)

    # Patchメソッドでアクセスがあった際、オーバーライドしてエラーを返すように設定する
    def partial_update(self, request, *args, **kwargs):
        response = {'message': 'PATCH method is not allowed'} # Errorメッセージ
        s = status.HTTP_405_METHOD_NOT_ALLOWED # ステータス
        return Response(response, status=s)



    # CRUDの全ての機能を使えるようにしておきたいので、ModelViewSetを継承しておく。
    # ModelViewSetを継承した場合は、以下のquerysetにオブジェクトの一覧を割り当てておく必要がある。
    # 以下の２行を書くだけでSegmentViewSetでCRUDの操作ができるようになる。
class SegmentViewSet(viewsets.ModelViewSet):    # 分類情報: 車種: ワゴン、セダン等の車の形状による車種
    queryset = Segment.objects.all()
    serializer_class = SegmentSerializer

class BrandViewSet(viewsets.ModelViewSet):      # 分類情報: ブランド（製造メーカーとか）
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class VehicleViewSet(viewsets.ModelViewSet):    # 実際に管理する車
    queryset = Vehicle.objects.all()
    serializer_class =  VehicleSerializer

    # 新しくVehicleオブジェクトを作る際、どのuserが作成したのかを設定する必要がある。
    def perform_create(self, serializer):
        serializer.save(user=self.request.user) # user属性に、今ログインしているユーザを割り当てている






