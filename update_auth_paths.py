import re

def update_auth_endpoints(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Replace all occurrences of /auth/ with /v1/auth/
    # but only when it appears in client.post() or client.get() calls
    content = re.sub(r'client\.(post|get)\(\s*"/auth/', r'client.\1("/v1/auth/', content)
    
    with open(filename, 'w') as f:
        f.write(content)

# Update the test file
update_auth_endpoints('/Users/shivs/Documents/Talentica/ailearning/book-review-backend/tests/test_auth.py')
