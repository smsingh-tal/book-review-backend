# Script to populate the books table with 100 famous books
# Usage: poetry run python scripts/populate_books.py

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from app.db.models import Book
from app.db.session import engine

# List of 100 famous books (title, author)
BOOKS = [
    ("The Adventures of Augie March", "Saul Bellow"),
    ("All the King's Men", "Robert Penn Warren"),
    ("American Pastoral", "Philip Roth"),
    ("Animal Farm", "George Orwell"),
    ("Appointment in Samarra", "John O'Hara"),
    ("Are You There God? It's Me, Margaret", "Judy Blume"),
    ("The Assistant", "Bernard Malamud"),
    ("Atonement", "Ian McEwan"),
    ("Beloved", "Toni Morrison"),
    ("The Berlin Stories", "Christopher Isherwood"),
    ("The Big Sleep", "Raymond Chandler"),
    ("The Blind Assassin", "Margaret Atwood"),
    ("Blood Meridian", "Cormac McCarthy"),
    ("Brideshead Revisited", "Evelyn Waugh"),
    ("The Bridge of San Luis Rey", "Thornton Wilder"),
    ("Call It Sleep", "Henry Roth"),
    ("Catch-22", "Joseph Heller"),
    ("The Catcher in the Rye", "J. D. Salinger"),
    ("A Clockwork Orange", "Anthony Burgess"),
    ("The Confessions of Nat Turner", "William Styron"),
    ("The Corrections", "Jonathan Franzen"),
    ("The Crying of Lot 49", "Thomas Pynchon"),
    ("A Dance to the Music of Time", "Anthony Powell"),
    ("The Day of the Locust", "Nathanael West"),
    ("Death Comes for the Archbishop", "Willa Cather"),
    ("A Death in the Family", "James Agee"),
    ("The Death of the Heart", "Elizabeth Bowen"),
    ("Deliverance", "James Dickey"),
    ("Dog Soldiers", "Robert Stone"),
    ("Falconer", "John Cheever"),
    ("The French Lieutenant's Woman", "John Fowles"),
    ("The Golden Notebook", "Doris May Lessing"),
    ("Go Tell it on the Mountain", "James Baldwin"),
    ("Gone With the Wind", "Margaret Mitchell"),
    ("The Grapes of Wrath", "John Steinbeck"),
    ("Gravity's Rainbow", "Thomas Pynchon"),
    ("The Great Gatsby", "F. Scott Fitzgerald"),
    ("A Handful of Dust", "Evelyn Waugh"),
    ("The Heart Is A Lonely Hunter", "Carson McCullers"),
    ("The Heart of the Matter", "Graham Greene"),
    ("Herzog", "Saul Bellow"),
    ("Housekeeping", "Marilynne Robinson"),
    ("A House for Mr. Biswas", "V. S. Naipaul"),
    ("I, Claudius", "Robert Graves"),
    ("Infinite Jest", "David Foster Wallace"),
    ("Invisible Man", "Ralph Ellison"),
    ("Light in August", "William Faulkner"),
    ("The Lion, The Witch and the Wardrobe", "C. S. Lewis"),
    ("Lolita", "Vladimir Nabokov"),
    ("Lord of the Flies", "William Golding"),
    ("The Lord of the Rings", "J. R. R. Tolkien"),
    ("Loving", "Henry Green"),
    ("Lucky Jim", "Kingsley Amis"),
    ("The Man Who Loved Children", "Christina Stead"),
    ("Midnight's Children", "Salman Rushdie"),
    ("Money", "Martin Amis"),
    ("The Moviegoer", "Walker Percy"),
    ("Mrs. Dalloway", "Virginia Woolf"),
    ("Naked Lunch", "William S. Burroughs"),
    ("Native Son", "Richard Wright"),
    ("Neuromancer", "William Gibson"),
    ("Never Let Me Go", "Kazuo Ishiguro"),
    ("Nineteen Eighty Four", "George Orwell"),
    ("On the Road", "Jack Kerouac"),
    ("One Flew Over the Cuckoo's Nest", "Ken Kesey"),
    ("The Painted Bird", "Jerzy Kosinski"),
    ("Pale Fire", "Vladimir Nabokov"),
    ("A Passage to India", "E. M. Forster"),
    ("Play It As It Lays", "Joan Didion"),
    ("Portnoy's Complaint", "Philip Roth"),
    ("Possession", "A. S. Byatt"),
    ("The Power and the Glory", "Graham Greene"),
    ("The Prime of Miss Jean Brodie", "Muriel Spark"),
    ("Rabbit, Run", "John Updike"),
    ("Ragtime", "E. L. Doctorow"),
    ("The Recognitions", "William Gaddis"),
    ("Red Harvest", "Dashiell Hammett"),
    ("Revolutionary Road", "Richard Yates"),
    ("The Sheltering Sky", "Paul Bowles"),
    ("Slaughterhouse-Five", "Kurt Vonnegut"),
    ("Snow Crash", "Neal Stephenson"),
    ("The Sot-Weed Factor", "John Barth"),
    ("The Sound and the Fury", "William Faulkner"),
    ("The Sportswriter", "Richard Ford"),
    ("The Spy Who Came in From the Cold", "John le Carré"),
    ("The Sun Also Rises", "Ernest Hemingway"),
    ("Their Eyes Were Watching God", "Zora Neale Hurston"),
    ("Things Fall Apart", "Chinua Achebe"),
    ("To Kill a Mockingbird", "Harper Lee"),
    ("To the Lighthouse", "Virginia Woolf"),
    ("Tropic of Cancer", "Henry Miller"),
    ("Ubik", "Philip K. Dick"),
    ("Under the Net", "Iris Murdoch"),
    ("Under the Volcano", "Malcolm Lowry"),
    ("Watchmen", "Alan Moore"),
    ("White Noise", "Don DeLillo"),
    ("White Teeth", "Zadie Smith"),
    ("Wide Sargasso Sea", "Jean Rhys"),
]

Session = sessionmaker(bind=engine)
session = Session()

def main():
    # Optionally clear the table first
    session.query(Book).delete()
    session.commit()
    for title, author in BOOKS:
        book = Book(title=title, author=author)
        session.add(book)
    session.commit()
    print(f"Inserted {len(BOOKS)} books.")

if __name__ == "__main__":
    main()
