import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('search_engine.db')
cursor = conn.cursor()

# Create tables for documents and terms
cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY,
        title TEXT,
        url TEXT,
        content TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS terms (
        id INTEGER PRIMARY KEY,
        term TEXT UNIQUE
    )
''')

# Create a table to store the associations between terms and documents
cursor.execute('''
    CREATE TABLE IF NOT EXISTS document_terms (
        document_id INTEGER,
        term_id INTEGER,
        FOREIGN KEY (document_id) REFERENCES documents(id),
        FOREIGN KEY (term_id) REFERENCES terms(id)
    )
''')

# Function to insert a document and its terms into the index
def insert_document(document):
    # Insert the document into the documents table
    cursor.execute('INSERT INTO documents (title, url, content) VALUES (?, ?, ?)',
                   (document['title'], document['url'], document['content']))
    document_id = cursor.lastrowid

    # Extract terms from the document content and insert them into the terms table
    terms = extract_terms(document['content'])
    term_ids = []
    for term in terms:
        cursor.execute('INSERT OR IGNORE INTO terms (term) VALUES (?)', (term,))
        cursor.execute('SELECT id FROM terms WHERE term = ?', (term,))
        term_id = cursor.fetchone()[0]
        term_ids.append(term_id)

    # Insert associations between document and terms into the document_terms table
    for term_id in term_ids:
        cursor.execute('INSERT INTO document_terms (document_id, term_id) VALUES (?, ?)',
                       (document_id, term_id))

    # Commit the changes to the database
    conn.commit()

# Function to search documents based on a query
def search_documents(query):
    terms = extract_terms(query)

    # Build the SQL query to search for documents containing the query terms
    query_params = tuple(['%' + term + '%' for term in terms])
    query = '''
        SELECT title, url, content
        FROM documents
        WHERE id IN (
            SELECT document_id
            FROM document_terms
            INNER JOIN terms ON document_terms.term_id = terms.id
            WHERE terms.term LIKE ?
        )
    '''

    # Execute the query and fetch the matching documents
    cursor.execute(query, query_params)
    results = cursor.fetchall()

    return results

# Example usage
document = {
    'title': 'Example Document',
    'url': 'http://www.example.com/document',
    'content': 'This is an example document containing some text.'
}

# Insert the document into the index
insert_document(document)

# Search for documents containing a query
query = 'example text'
results = search_documents(query)

# Display the search results
for result in results:
    print('Title:', result[0])
    print('URL:', result[1])
    print('Content:', result[2])
    print('---')

# Close the database connection
conn.close()