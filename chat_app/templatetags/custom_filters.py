from django import template

register = template.Library()

@register.filter
def get_file_icon(file_name):
    # Example logic to return an icon based on the file extension
    extension = file_name.split('.')[-1].lower()
    if extension in ['jpg', 'png', 'gif']:
        return 'image-icon.png'
    elif extension in ['pdf']:
        return 'pdf-icon.png'
    elif extension in ['doc', 'docx']:
        return 'word-icon.png'
    else:
        return 'default-icon.png'

