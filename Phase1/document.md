# Design of SQLite Database

> **Outline:** \
> In this project we used SQLite3 for our project database package with Python
> 3.9.13.

## Database Structure
There are three tables in the database: Pages, Indexer and Keywords.

Here is the database schema:
```sql
Table: Pages
    id (INTEGER, PRIMARY KEY)
    title (TEXT)
    url (TEXT)
    last_modification_date (TEXT)
    page_size (INTEGER)
    child_link_list (TEXT)

Table: Keywords
    id (INTEGER, PRIMARY KEY)
    keyword (TEXT)

Table: Indexer
    page_id (INTEGER, FOREIGN KEY references Pages(id))
    keyword_id (INTEGER, FOREIGN KEY references Keywords(id))
    frequency (INTEGER)
```

## Explanation
This schema design allows us to store information about pages, keywords, their frequencies within each page, and child links associated with each page.

Using the `Indxer` table, we can implement forward and inverted indexing through this table using SQL query as it is a relationship type in this database design.

Moreover, the mapping between URL <=> page ID and word <=> word ID can be easily done without joining any extra table.

In a nutshell, with the database shown above, we can access our data by minimizing the number of joining operation while preserving all the required functionality of the database.
