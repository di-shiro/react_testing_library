from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Brand
from .serializers import BrandSerializer

BRANDS_URL = '/api/brands/'


# テストでは何度もBrandデータを新規作成するので、
# Brandデータを簡単にDBへ新規作成する関数を作っておく。
def create_brand(brand_name):
    return Brand.objects.create(brand_name=brand_name)

# IDごとのURLを作ってくれる関数  (/api/brand/id  みたいな感じ)
def detail_url(brand_id):
    return reverse('api:brand-detail', args=[brand_id])

# トークン認証が通った（ログインした）Userに対するテスト
class AuthorizedBrandApiTests(TestCase):

    # ダミーのユーザを作成して、強制的に認証を通している
    def setUp(self):
        # まずはテスト用に新規Userを作成
        self.user = get_user_model().objects.create_user(username='dummy', password='dummy_pw')
        self.client = APIClient()
        # 強制的にトークン認証を通す。
        self.client.force_authenticate(self.user)

    def test_3_1_should_get_brands(self):
        create_brand(brand_name='Toyota')   # DBのBrandにToyotaというブランド名を作成
        create_brand(brand_name='Tesla')
        res = self.client.get(BRANDS_URL)   # GETメソッドでBRANDSエンドポイントのURLにアクセス

        # DB内のBrandテーブルから全データ（行）を取ってくる。
        # その後、BrandSerializerで brandsオブジェクトをdict型 に変換する。
        brands = Brand.objects.all().order_by('id')
        serializer = BrandSerializer(brands, many=True)

        # ステータスコードが 200_OK となっていることをテスト
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # Brandを１つ取得する。DBのBrandテーブルから任意の1行だけを取得する。
    def test_3_2_should_get_single_brand(self):
        # DB内に直接新規Brandデータを作成する（HTTPのPOSTメソッドを用いない）
        brand = create_brand(brand_name='Toyota')
        url = detail_url(brand.id)
        res = self.client.get(url)
        serializer = BrandSerializer(brand)
        # DBに新規にBrandデータを作成した後、プログラム内に新規Brandのオブジェクトが得られる。
        # 次に、GETメソッドでDBからこの新規作成したBrandデータを取得して
        # 新規オブジェクトとDBから取得したデータとを比較する。
        self.assertEqual(res.data, serializer.data) # DB内に新規Brandが想定通りに登録されているかテスト
        self.assertEqual(res.status_code, status.HTTP_200_OK)   # GETメソッド後のステータスコードをテスト


    # Web上からのHTTP通信によるPOSTメソッドを用いて新規Brandデータを作成できるかテスト
    def test_3_3_should_create_new_brand_successfully(self):
        payload = {'brand_name': 'Audi'}
        res = self.client.post(BRANDS_URL, payload)
        # BrandのDB内で、ブランド名に'Audi'（テストデータのpayloadに格納されてるbrand_name）
        # が存在するかフィルタリングして、存在すれば Trueを返す。
        exists = Brand.objects.filter(
            brand_name=payload['brand_name']
        ).exists()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    # Brandを新規作成する際、Brand名を空にしてPOSTメソッドを送信した場合、
    # responseとしてBAD_REQUESTが帰ってくるかどうか
    def test_3_4_should_not_create_brand_with_invalid(self):
        payload = {'brand_name': ''}
        res = self.client.post(BRANDS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # PATCHメソッドによりDB内のBrandデータの一部分の更新できるかをテスト
    def test_3_5_should_partial_update_brand__PATCH(self):
        brand = create_brand(brand_name='Toyota')
        payload = {'brand_name': 'Lexus'}
        url = detail_url(brand.id)
        self.client.patch(url, payload)

        # PATCH で更新できたか確認するために、BrandデータをDBから再取得して、payloadとDBから取得したbrand_nameとを比較する。
        brand.refresh_from_db()
        self.assertEqual(brand.brand_name, payload['brand_name'])


    # PUTメソッドでDB内のBrandデータの更新できるかをテスト
    def test_3_6_should_update_brand__PUT(self):
        brand = create_brand(brand_name='Toyota')
        payload = {'brand_name': 'Lexus'}
        url = detail_url(brand.id)
        self.client.put(url, payload)
        brand.refresh_from_db()
        self.assertEqual(brand.brand_name, payload['brand_name'])


    # DELETEメソッドでDB内のBrandデータを削除できるかをテスト
    def test_3_7_should_delete_brand__delete(self):
        brand = create_brand(brand_name='Toyota')
        # 上でBrandデータを１つ作成したので、DBのオブジェクト数を数えて１つだけできているか確認
        self.assertEqual(1, Brand.objects.count())
        url = detail_url(brand.id)
        self.client.delete(url)
        # 上でBrandデータを削除したので、Brandのオブジェクト数が 0 ならば正常
        self.assertEqual(0, Brand.objects.count())


# トークン認証されていない状態で、Brandエンドポイントにアクセスするテスト
class UnauthorizedBrandApiTests(TestCase):
    # トークン認証されていない状態のテストなので、
    # 強制的に認証を通しておく必要がない。

    def setUp(self):
        self.client = APIClient()

    # 認証されていない状態でBrandエンドポイントにアクセスした場合、401エラーとなれば正常。
    def test_3_8_should_not_get_brands_when_unauthorized(self):
        res = self.client.get(BRANDS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)





