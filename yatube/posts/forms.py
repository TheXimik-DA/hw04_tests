from django import forms

from posts.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group']
        help_texts = {
            'text': 'Новый пост',
            'group': 'Группа в которой будет находится пост',
        }
