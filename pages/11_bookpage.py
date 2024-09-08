import requests
import json

def search_book_google(title):
    base_url = 'https://www.googleapis.com/books/v1/volumes?q='
    response = requests.get(base_url + title)
    result = response.json()
    
    if 'items' in result:
        book = result['items'][0]['volumeInfo']
        book_title = book.get('title', 'No Title Found')
        authors = ', '.join(book.get('authors', 'No Author Found'))
        page_count = book.get('pageCount', 'No Page Count Info')
        
        return {
            'title': book_title,
            'authors': authors,
            'page_count': page_count
        }
    else:
        return None

book_info = search_book_google("Harry Potter")
if book_info:
    print(f"Title: {book_info['title']}")
    print(f"Authors: {book_info['authors']}")
    print(f"Page Count: {book_info['page_count']}")
else:
    print("Book not found")
