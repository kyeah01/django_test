from django.test import TestCase
from django.conf import settings
from .models import Board

class SettingsTest(TestCase):
    def test_01_settings(self):
        self.assertEqual(settings.USE_I18N, True)
        self.assertEqual(settings.LANGUAGE_CODE, 'ko-kr')
        self.assertEqual(settings.TIME_ZONE, 'Asia/Seoul')
        self.assertEqual(settings.USE_TZ, False)
        
class BoardModelTest(TestCase):
    def test_01_model(self):
        # board = Board.objects.create(title='test title', content='test content')
        board = Board.objects.create(
            title='test title', content='test content', user_id=1)
        self.assertEqual(str(board), f'Board{ board.pk }', msg='출력값이 일치하지 않음')