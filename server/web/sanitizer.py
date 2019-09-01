import re
import bleach

backslash_pattern = re.compile(r'\\')
double_dash_pattern = re.compile(r'--')


def sanitize(content):
    """Sanitize user input.

    - Strip out HTML tags and comments.
    - Remove backslashes.
    - Replace double dashes.
    """
    # strip HTML tags and comments
    c = bleach.clean(content, strip=True)

    # replace -- (SQL comment) with — (U+2014)
    c = re.sub(double_dash_pattern, '—', c)

    # remove backslashes
    c = re.sub(backslash_pattern, '', c)

    return c
