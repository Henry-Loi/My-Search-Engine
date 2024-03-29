import sqlite3

class SpiderDbTest:
    def __init__(self, database, result_filename, key_word_limit=10, child_link_limit = 10) -> None:
        self.keyword_limit = key_word_limit
        self.child_link_limit = child_link_limit
        self.result_filename = result_filename

        # db connection
        self.conn = sqlite3.connect(database)
        self.cursor = self.conn.cursor()

    def run(self):
        # Fetch data from the database
        self.cursor.execute('''
            SELECT id, title, url, last_modification_date, page_size
            FROM Pages;
        ''')

        pages_data = self.cursor.fetchall()

        output = ""

        # Iterate over each row of the fetched data
        for row in pages_data:
            id, title, url, last_modification_date, page_size = row
            output += f"{title}\n{url}\n{last_modification_date}, {page_size}\n"

            # Fetch keywords and their frequencies for each page
            self.cursor.execute('''
                SELECT k.keyword, i.frequency
                FROM Keywords k
                JOIN Indexer i ON k.id = i.keyword_id
                WHERE i.page_id = ?
                ORDER BY i.frequency DESC
                LIMIT ?
            ''', (id,self.keyword_limit,))

            keywords_data = self.cursor.fetchall()
            # print(keywords_data)

            # Format keywords and their frequencies
            keyword_freq = '; '.join([f"{keyword} {frequency}" for keyword, frequency in keywords_data])
            output += f"{keyword_freq};"

            # Fetch child links for each page
            self.cursor.execute('''
                SELECT child_link_list
                FROM Pages
                WHERE id = ?;
            ''', (row[0],))

            row = self.cursor.fetchone()
            
            index = -1
            if row is not None:
                child_links = row[0]
                for _ in range(self.child_link_limit):
                    index = child_links.find("\n", index + 1)
                    if index == -1:
                        break
                output += f"{child_links[:index]}\n----\n"

        # Write the output to a text file
        with open(self.result_filename, 'w') as file:
            file.write(output)


if __name__ == "__main__":
    db_name = "search_engine.db"
    output_filename = "spider_result.txt"
    
    test = SpiderDbTest(db_name, output_filename)
    
    test.run()
    
