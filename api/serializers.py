from rest_framework import serializers
from .models import Segment, Brand, Vehicle
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {
            'write_only': True,
            'required': True,   # 入力必須とする。
            'min_length': 5     # パスワード最小値
            }}

    # ユーザーを新規作成するメソッド
    # しかし、通常のSerializerにはパスワードをハッシュ化する機能がないので、フロント側から受け取ったそのままのデータをDBに保存してしまう。
    # そのため、 createのserializerをカスタマイズする場合には、createのメソッドをオーバーライドする。
    # Djangoのユーザーモデルで予め準備されているcreate_userというメソッドを使うことで、
    # パスワードのハッシュ化などを全部そこで行ってくれる。
    # 引数validated_dataには上に記載した password と username が入ってくる。
    # ただし、validated_dataはdict型なので、これをcreate_userメソッドの引数として渡すために **validated_data としている。
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = ['id', 'segment_name']



class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'brand_name']

class VehicleSerializer(serializers.ModelSerializer):
    # DBのどこからデータを取得するかを設定
    # 以下は、segmentモデルのsegment_name要素からデータを取得する。
    segment_name = serializers.ReadOnlyField(source='segment.segment_name', read_only=True)
    brand_name = serializers.ReadOnlyField(source='brand.brand_name', read_only=True)

    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_name', 'release_year', 'price', 'segment', 'brand', 'segment_name', 'brand_name']
        extra_kwargs = {'users': {'read_only': True}}
        ''' react側で新規Vehicleを作成する際、自動で作成者としてログインUserを記録する。'''
