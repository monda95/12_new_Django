from io import BytesIO
from pathlib import Path
from django.db import models
from django.contrib.auth import get_user_model
from PIL import Image
from utils.models import TimestampModel

User = get_user_model()

class Todo(TimestampModel):
    title = models.CharField(max_length=50)
    content = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_completed = models.BooleanField(default=False)

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    image = models.ImageField('이미지',upload_to='todo/%Y/%m/%d', null=True, blank=True)
    thumbnail = models.ImageField('썸네일', upload_to='todo/%Y/%m/%d/thumbnail',
                                  null=True, blank=True)

    def __str__(self):
        return self.title


    def save(self, *args, **kwargs):
        print("▶ save() 실행됨")
        if not self.image:
            print("⛔ image 없음 → 썸네일 생성 생략")
            return super().save(*args, **kwargs)

        print("🟢 썸네일 생성 시도")


        if not self.image:
            return super().save(*args, **kwargs)

        image = Image.open(self.image)
        self.image.seek(0)
        image.thumbnail((300,300))


        image_path = Path(self.image.name)

        thumbnail_name = image_path.stem #/blogproject/2025/7/31/database.png => database로 확장자빼고 가져옴
        thumbnail_extension = image_path.suffix     #/blogproject/2025/7/31/database.png => 확장자인 png가져옴
        thumbnail_filename = f'{thumbnail_name}_thumb{thumbnail_extension}' # dataabse_thumb.png

        if thumbnail_extension in ['.jpg', '.jpeg']:
            file_type = 'JPEG'
        elif thumbnail_extension == '.gif':
            file_type = 'GIF'
        elif thumbnail_extension == '.png':
            file_type = 'PNG'
        else:
            return super().save(*args, **kwargs)

        temp_thumb = BytesIO()
        image.save(temp_thumb, file_type)
        temp_thumb.seek(0)

        self.thumbnail.save(thumbnail_filename, temp_thumb, save=False)
        temp_thumb.close()
        return super().save(*args, **kwargs)



    class Meta:
        verbose_name = '할 일'
        verbose_name_plural = '할 일 목록'


class Comment(TimestampModel):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField('본문', max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.todo.title}의 댓글'

    class Meta:
        verbose_name = '댓글'
        verbose_name_plural = '댓글 목록'
        ordering = ('-created_at', '-id')