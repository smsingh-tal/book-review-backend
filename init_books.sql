-- Insert popular books with varied genres and ratings
INSERT INTO public.books (title, author, isbn, publication_date, average_rating, total_reviews, genres, created_at) VALUES
-- Contemporary Fiction
('The Midnight Library', 'Matt Haig', '9780525559474', '2020-08-13', 0, 0, ARRAY['Fiction', 'Fantasy', 'Contemporary'], NOW()),
('Where the Crawdads Sing', 'Delia Owens', '9780735219090', '2018-08-14', 0, 0, ARRAY['Fiction', 'Literary Fiction', 'Mystery'], NOW()),
('The Seven Husbands of Evelyn Hugo', 'Taylor Jenkins Reid', '9781501161933', '2017-06-13', 0, 0, ARRAY['Historical Fiction', 'Romance', 'LGBT'], NOW()),

-- Classic Literature
('Pride and Prejudice', 'Jane Austen', '9780141439518', '1813-01-28', 0, 0, ARRAY['Classic', 'Romance', 'Literary Fiction'], NOW()),
('To Kill a Mockingbird', 'Harper Lee', '9780446310789', '1960-07-11', 0, 0, ARRAY['Classic', 'Literary Fiction', 'Historical'], NOW()),
('1984', 'George Orwell', '9780451524935', '1949-06-08', 0, 0, ARRAY['Classic', 'Dystopian', 'Science Fiction'], NOW()),

-- Fantasy
('The Name of the Wind', 'Patrick Rothfuss', '9780756404741', '2007-03-27', 0, 0, ARRAY['Fantasy', 'Epic Fantasy', 'Adventure'], NOW()),
('The Way of Kings', 'Brandon Sanderson', '9780765326355', '2010-08-31', 0, 0, ARRAY['Fantasy', 'Epic Fantasy', 'High Fantasy'], NOW()),
('A Game of Thrones', 'George R.R. Martin', '9780553573404', '1996-08-01', 0, 0, ARRAY['Fantasy', 'Epic Fantasy', 'Political Fantasy'], NOW()),

-- Science Fiction
('Dune', 'Frank Herbert', '9780441172719', '1965-08-01', 0, 0, ARRAY['Science Fiction', 'Space Opera', 'Political Fiction'], NOW()),
('Project Hail Mary', 'Andy Weir', '9780593135204', '2021-05-04', 0, 0, ARRAY['Science Fiction', 'Space Fiction', 'Adventure'], NOW()),
('Foundation', 'Isaac Asimov', '9780553293357', '1951-05-01', 0, 0, ARRAY['Science Fiction', 'Classic Sci-Fi', 'Space Opera'], NOW()),

-- Mystery/Thriller
('Gone Girl', 'Gillian Flynn', '9780307588371', '2012-06-05', 0, 0, ARRAY['Thriller', 'Mystery', 'Psychological Fiction'], NOW()),
('The Silent Patient', 'Alex Michaelides', '9781250301697', '2019-02-05', 0, 0, ARRAY['Thriller', 'Psychological Fiction', 'Mystery'], NOW()),
('The Da Vinci Code', 'Dan Brown', '9780307474278', '2003-03-18', 0, 0, ARRAY['Thriller', 'Mystery', 'Adventure'], NOW()),

-- Non-Fiction
('Sapiens', 'Yuval Noah Harari', '9780062316097', '2014-02-10', 0, 0, ARRAY['Non-Fiction', 'History', 'Science'], NOW()),
('Atomic Habits', 'James Clear', '9780735211292', '2018-10-16', 0, 0, ARRAY['Non-Fiction', 'Self-Help', 'Psychology'], NOW()),
('Educated', 'Tara Westover', '9780399590504', '2018-02-20', 0, 0, ARRAY['Non-Fiction', 'Memoir', 'Biography'], NOW()),

-- Historical Fiction
('The Book Thief', 'Markus Zusak', '9780375842207', '2005-09-01', 0, 0, ARRAY['Historical Fiction', 'Young Adult', 'War'], NOW()),
('All the Light We Cannot See', 'Anthony Doerr', '9781501173219', '2014-05-06', 0, 0, ARRAY['Historical Fiction', 'Literary Fiction', 'War'], NOW()),
('The Nightingale', 'Kristin Hannah', '9780312577223', '2015-02-03', 0, 0, ARRAY['Historical Fiction', 'War', 'Romance'], NOW()),

-- Romance
('The Love Hypothesis', 'Ali Hazelwood', '9780593336823', '2021-09-14', 0, 0, ARRAY['Romance', 'Contemporary', 'Comedy'], NOW()),
('Beach Read', 'Emily Henry', '9781984806734', '2020-05-19', 0, 0, ARRAY['Romance', 'Contemporary', 'Literary Fiction'], NOW()),
('Red, White & Royal Blue', 'Casey McQuiston', '9781250316776', '2019-05-14', 0, 0, ARRAY['Romance', 'LGBT', 'Contemporary'], NOW()),

-- Young Adult
('The Hate U Give', 'Angie Thomas', '9780062498533', '2017-02-28', 0, 0, ARRAY['Young Adult', 'Contemporary', 'Social Justice'], NOW()),
('Six of Crows', 'Leigh Bardugo', '9781627792127', '2015-09-29', 0, 0, ARRAY['Young Adult', 'Fantasy', 'Adventure'], NOW()),
('The Fault in Our Stars', 'John Green', '9780525478812', '2012-01-10', 0, 0, ARRAY['Young Adult', 'Romance', 'Contemporary'], NOW()),

-- Horror/Gothic
('Mexican Gothic', 'Silvia Moreno-Garcia', '9780525620785', '2020-06-30', 0, 0, ARRAY['Horror', 'Gothic', 'Historical Fiction'], NOW()),
('Dracula', 'Bram Stoker', '9780141439846', '1897-05-26', 0, 0, ARRAY['Horror', 'Gothic', 'Classic'], NOW()),
('The Haunting of Hill House', 'Shirley Jackson', '9780143039983', '1959-10-17', 0, 0, ARRAY['Horror', 'Gothic', 'Psychological Fiction'], NOW()),

-- Science/Technology
('The Code Breaker', 'Walter Isaacson', '9781982115852', '2021-03-09', 0, 0, ARRAY['Non-Fiction', 'Science', 'Biography'], NOW()),
('A Brief History of Time', 'Stephen Hawking', '9780553380163', '1988-04-01', 0, 0, ARRAY['Non-Fiction', 'Science', 'Physics'], NOW()),
('The Phoenix Project', 'Gene Kim', '9780988262592', '2013-01-10', 0, 0, ARRAY['Non-Fiction', 'Technology', 'Business'], NOW()),

-- Business/Self-Development
('Think and Grow Rich', 'Napoleon Hill', '9781585424337', '1937-03-01', 0, 0, ARRAY['Non-Fiction', 'Business', 'Self-Help'], NOW()),
('Good to Great', 'Jim Collins', '9780066620992', '2001-10-16', 0, 0, ARRAY['Non-Fiction', 'Business', 'Leadership'], NOW()),
('Deep Work', 'Cal Newport', '9781455586691', '2016-01-05', 0, 0, ARRAY['Non-Fiction', 'Business', 'Productivity'], NOW()),

-- Contemporary Literature
('Normal People', 'Sally Rooney', '9781984822178', '2018-08-28', 0, 0, ARRAY['Literary Fiction', 'Contemporary', 'Romance'], NOW()),
('Klara and the Sun', 'Kazuo Ishiguro', '9780571364879', '2021-03-02', 0, 0, ARRAY['Literary Fiction', 'Science Fiction', 'Contemporary'], NOW()),
('A Little Life', 'Hanya Yanagihara', '9780804172707', '2015-03-10', 0, 0, ARRAY['Literary Fiction', 'Contemporary', 'LGBT'], NOW()),

-- Philosophy/Psychology
('The Power of Now', 'Eckhart Tolle', '9781577314806', '1997-09-29', 0, 0, ARRAY['Non-Fiction', 'Spirituality', 'Self-Help'], NOW()),
('Thinking, Fast and Slow', 'Daniel Kahneman', '9780374533557', '2011-10-25', 0, 0, ARRAY['Non-Fiction', 'Psychology', 'Economics'], NOW()),
('Man''s Search for Meaning', 'Viktor E. Frankl', '9780807014271', '1946-09-10', 0, 0, ARRAY['Non-Fiction', 'Psychology', 'Philosophy'], NOW()),

-- Poetry
('Milk and Honey', 'Rupi Kaur', '9781449474256', '2014-11-04', 0, 0, ARRAY['Poetry', 'Contemporary', 'Feminism'], NOW()),
('The Hill We Climb', 'Amanda Gorman', '9780593465271', '2021-03-30', 0, 0, ARRAY['Poetry', 'Contemporary', 'Social Justice'], NOW()),
('The Sun and Her Flowers', 'Rupi Kaur', '9781449486792', '2017-10-03', 0, 0, ARRAY['Poetry', 'Contemporary', 'Feminism'], NOW()),

-- Diverse Voices
('Pachinko', 'Min Jin Lee', '9781455563937', '2017-02-07', 0, 0, ARRAY['Historical Fiction', 'Literary Fiction', 'Cultural'], NOW()),
('The Vanishing Half', 'Brit Bennett', '9780525536291', '2020-06-02', 0, 0, ARRAY['Literary Fiction', 'Historical Fiction', 'Cultural'], NOW()),
('On Earth We''re Briefly Gorgeous', 'Ocean Vuong', '9780525562023', '2019-06-04', 0, 0, ARRAY['Literary Fiction', 'LGBT', 'Cultural'], NOW());

-- Create indexes for better search performance
CREATE INDEX IF NOT EXISTS ix_books_genres ON books USING GIN (genres);
CREATE INDEX IF NOT EXISTS ix_books_publication_date ON books(publication_date);
CREATE INDEX IF NOT EXISTS ix_books_average_rating ON books(average_rating);
