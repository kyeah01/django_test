# from django.test import TestCase
from test_plus.test import TestCase
from django.conf import settings
from django.urls import reverse
from .models import Board
from .forms import BoardForm

class SettingsTest(TestCase):
    def test_01_settings(self):
        # 같은지 다른지 검증
        self.assertEqual(settings.USE_I18N, True)
        self.assertEqual(settings.LANGUAGE_CODE, 'ko-kr')
        self.assertEqual(settings.TIME_ZONE, 'Asia/Seoul')
        self.assertEqual(settings.USE_TZ, False)

# Model Test + Model Form Test
class BoardModelTest(TestCase):
    def test_01_model(self):
        # board = Board.objects.create(title='test title', content='test content')
        board = Board.objects.create(
            title='test title', content='test content', user_id=1)
        self.assertEqual(str(board), f'Board{ board.pk }', msg='출력값이 일치하지 않음')
        
    def test_02_boardForm(self):
        # given
        data = {
            'title' : '제목',
            'content' : '내용',
        }
        
        self.assertEqual(BoardForm(data).is_valid(), True)
        
    def test_03_boardform_without_title(self):
        # given
        data = {
            'content' : '내용'
        }
        self.assertEqual(BoardForm(data).is_valid(), False)

    def test_04_boardform_without_content(self):
        data = {
            'title': '제목', 
        }
        self.assertEqual(BoardForm(data).is_valid(), False)
    
        
class BoardViewTest(TestCase):
    
    # 반복되는 make user를 한번에 만들어주기 위해서 정의
    # 공통적인 given 상황을 구성하기에 유용하다.
    def setUp(self):
        self.user = self.make_user(username='test', password='1234567!')
        
    
    # create test의 포인트는 form을 제대로 주는가이다.
    # 가장 기본적으로는 get_check_200 메소드를 활용한다.
    
    def test_01_get_create(self):
        # login required를 충족하기 위해
        # given
        # user = self.make_user(username='test', password='1234567!')
        # when
        with self.login(username='test', password='1234567!'):
            response = self.get_check_200('boards:create')
            # self.assertContains(response, '<form')
            # then
            self.assertIsInstance(response.context['form'], BoardForm)
            
    def test_02_get_create_login_required(self):
        self.assertLoginRequired('boards:create')
        
    def test_03_post_create(self):
        # given | 사용자와 작성한 글 데이터
        # when  | 로그인을 해서 post 요청으로 해당 url에 보낸 경우
        # then  | 글이 작성되고, detail로 redirect(302)
        
        # given
        # user = self.make_user(username='test', password='1234567!')
        data = {
            'title' : 'test title',
            'content' : 'test content'
        }
        
        # when
        with self.login(username='test', password='1234567!'):

            # then
            self.post('boards:create', data=data)
            self.response_302()
            # self.assertEqual(response.status_code, 302)
            
    def test_04_board_create_without_content(self):
        
        # given
        data = {
            'title' : 'test_title',
        }
        
        # when
        with self.login(username='test', password='1234567!'):
            response = self.post('boards:create', data=data)
            self.assertContains(response, '')
    
    # 디테일 페이지가 제대로 출력되는지 확인
    def test_05_detail_contains(self):
        # given
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        # when
        self.get_check_200('boards:detail', board_pk=board.pk)
        
        # then
        self.assertResponseContains(board.title, html=False)
        self.assertResponseContains(board.content, html=False)
        
    def test_06_detail_templates(self):
        # given
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        
        # when
        response = self.get_check_200('boards:detail', board_pk=board.pk)
        
        # then
        self.assertTemplateUsed(response, 'boards/detail.html')
        
    def test_07_get_index(self):
        # given when then
        self.get_check_200('boards:index')
        
    def test_08_index_template(self):
        response = self.get_check_200('boards:index')
        self.assertTemplateUsed(response, 'boards/index.html')
        
    def test_09_index_queryset(self):
        # given | 글 두개 작성
        Board.objects.create(title='제목', content='내용', user=self.user)
        Board.objects.create(title='제목', content='내용', user=self.user)
        boards = Board.objects.order_by('-pk')
        
        # when
        response = self.get_check_200('boards:index')
        
        # then
        self.assertQuerysetEqual(response.context['boards'], map(repr, boards))
        
    def test_10_delete(self):
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        with self.login(username='test', password='1234567!'):
            self.get_check_200('boards:delete', board_pk=board.pk)
        
    def test_11_delete_post(self):
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        with self.login(username='test', password='1234567!'):
            self.post('boards:delete', board_pk=board.pk)
            self.assertEqual(Board.objects.count(), 0)
            
    def test_12_delete_redirect(self):
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        with self.login(username='test', password='1234567!'):
            response = self.post('boards:delete', board_pk=board.pk)
            self.assertRedirects(response, reverse('boards:index'))
            
    def test_13_get_update(self):
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        with self.login(username='test', password='1234567!'):
            response = self.get_check_200('boards:update', board.pk)
            self.assertEqual(response.context['form'].instance.pk, board.pk)
            self.post('boards:update', board_pk=board.pk)
            
    def test_14_get_update_login_required(self):
        self.assertLoginRequired('boards:update', board_pk=1)