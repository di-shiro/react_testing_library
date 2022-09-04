from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Segment
from .serializers import SegmentSerializer

SEGMENTS_URL = '/api/segments/'

# 新規セグメント（車種）を作成
def create_segment(segment_name):
    return Segment.objects.create(segment_name=segment_name)


def detail_url(segment_id):
    return reverse('api:segment-detail', args=[segment_id])


class AuthorizedSegmentApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='dummy', password='dummy_pw')
        self.client = APIClient()
        self.client.force_authenticate(self.user) # 強制的に認証を通しておく！

    # getメソッドで segment の一覧が取得できるかのテスト
    def test_2_1_should_get_all_segments(self):
        create_segment(segment_name='SUV')
        create_segment(segment_name='Sedan')

        # segmentのデータを返すAPIエンドポイントに GETメソッドでアクセスして、segment一覧を取得できるかテスト
        # APIからのresponseデータとDB内に保存してあるsegmentのデータを比較する。
        # DjangoのAPI からのresponseは dict型のデータが返される。
        # しかし、DjangoがDB内のデータを取り出す時にオブジェクトで取得するので、それをSerializerでdict型に変換する。
        res = self.client.get(SEGMENTS_URL)
        # DBからSegmentデータを取得した後、Serializerでdict型に変換する。
        segments = Segment.objects.all().order_by('id')
        print('\n★', type(segments)) # DBからでーた取得後のどうなっているか試しに表示
        serializer = SegmentSerializer(segments, many=True) # segment（車種）が複数ある場合は many=True とする。

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # segmentデータを1つだけ取得できるかのテスト
    def test_2_2_should_get_single_segment(self):
        segment = create_segment(segment_name="SUV")
        url = detail_url(segment.id)
        # detail_url()内で使われているreverseでURLを生成すると右の様な形のURLなる。    /api/segments/1/
        print('\n★ reverse生成されたURL:  ', url)

        # segmentのURLにアクセスして、このIDのオブジェクトを取得してくる
        res = self.client.get(url)
        # DBから取ってきたsegmentデータをSerializerでdict型に変換する。
        serializer = SegmentSerializer(segment)
        # responseのデータはdict型なので、dict型同士、直接に比較できる。
        self.assertEqual(res.data, serializer.data)


    # 新規セグメントを作成できるかテスト
    def test_2_3_should_create_new_segment_successfully(self):
        payload = {'segment_name': 'K-car'}
        # クライアントのPOSTメソッドで、SegmentエンドポイントにPayloadを渡す。
        res = self.client.post(SEGMENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # 新規作成したセグメントがDBに存在しているかの確認
        # Segmentオブジェクトの中から、.filterで 'K-car' というセグメント名が含まれるかを絞り込み、存在するかを判定。
        # 変数existsにはTrue, False のいずれかが代入される。これをassertTrue()でTrueになっているか判定する。
        exists = Segment.objects.filter(
            segment_name=payload['segment_name']
        ).exists()
        self.assertTrue(exists)

    # segmentを新規作成した時、空でリクエストしてしまった場合、
    # BAD_REQUESTが帰ってくるかテスト
    def test_2_4_should_not_create_new_segment_with_invalid__POST(self):
        payload = {'segment_name': ''}
        res = self.client.post(SEGMENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # PATCHのテスト
    # 例えば、DBの列（要素）が複数あるなかで、一部だけを変更したい場合、PATCHを使う。
    # UPDATEとPATCHは、どちらも同じくDB内の既存データを変更するために使う。
    # しかし、PATCHならば要素10のうち1つだけ変更ができる一方で、
    # UPDATEの場合は要素10のうち10全てに値を設定して変更せねばならない。
    # そこで、ここでは、PATCHリクエストで部分的な変更ができるかテストを行う。
    def test_2_5_should_partial_update_segment__PATCH(self):
        # 新規Segmentオブジェクトを作成しておく。このテストではSUVというsegment_nameで作成する。
        segment = create_segment(segment_name="SUV")
        # 今回はsegment_nameだけ更新する。
        payload = {'segment_name': 'Compact SUV'}
        # URLのパスを生成
        url = detail_url(segment.id)
        self.client.patch(url, payload)

        # 次に、上でテスト用に作成した新規segment_nameがDB内で変更されているか確認する。
        # セグメント名が'SUV' から 'Compact SUV' に変更できていれば正常。
        #
        # 以下のメソッドによって、PATCHメソッドで変更したDB内のデータを再取得している。
        segment.refresh_from_db()
        # DB内のデータとPATCHで変更したデータ（payload）が一致しているか比較する。
        self.assertEqual(segment.segment_name, payload['segment_name'])


    # PUTのテスト    # こちらはPATCHとほぼ同じ
    def test_2_6_should_update_segment__PUT(self):
        segment = create_segment(segment_name="SUV")
        payload = {'segment_name': 'Compact SUV'}
        # IDごとのURLを生成する。（こんな漢字のURLになる /api/segments/1/ ）reverseを使って生成する。
        url = detail_url(segment.id)
        self.client.put(url, payload)
        segment.refresh_from_db()
        self.assertEqual(segment.segment_name, payload['segment_name'])


    # DELETEのテスト
    def test_2_7_should_delete_segment(self):
        segment = create_segment(segment_name='SUV')
        self.assertEqual(1, Segment.objects.count())
        url = detail_url(segment.id)    # テスト用の新規SegmentオブジェクトからURLを生成する。（こんな感じになる /api/segments/1）
        self.client.delete(url) # 上で新規作成したsegmentオブジェクトを削除してみる。
        # 下記のSegmentオブジェクトはDB内のSegmentテーブルの全データをカウントしている。
        self.assertEqual(0, Segment.objects.count())
        # segment.refresh_from_db()   # 本当にDELETEできたか確認するためにDB内のデータを読み出してみる

# トークン認証が通っていない利用者がアクセスした場合の振る舞いのテスト
class UnauthorizedSegmentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    # トークン認証が通っていない状態（ログインしていない状態）でSegmentのエンドポイントにアクセスした場合
    # 401_Unauthorized が帰ってくれば正常。
    def test_2_8_should_not_get_segments_when_unauthorized(self):
        res = self.client.get(SEGMENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


