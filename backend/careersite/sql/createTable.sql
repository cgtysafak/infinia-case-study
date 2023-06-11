DROP VIEW IF EXISTS job_application_count;
DROP VIEW IF EXISTS average_age_view;
DROP TABLE IF EXISTS Application;
DROP TABLE IF EXISTS Blocked;
DROP TABLE IF EXISTS Connection;
DROP TABLE IF EXISTS Notification;
DROP TABLE IF EXISTS Comment;
DROP TABLE IF EXISTS Post;
DROP TABLE IF EXISTS Job;
DROP TABLE IF EXISTS CareerGrade;
DROP TABLE IF EXISTS Education;
DROP TABLE IF EXISTS Employment;
DROP TABLE IF EXISTS Company;
DROP TABLE IF EXISTS Experience;
DROP TABLE IF EXISTS Report;
DROP TABLE IF EXISTS CareerExpert;
DROP TABLE IF EXISTS Recruiter;
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS NonAdmin;
DROP TABLE IF EXISTS Admin;
DROP TABLE IF EXISTS User;
--DROP TRIGGER IF EXISTS update_average;

CREATE TABLE User(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(50) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100),
    email_address VARCHAR(100) UNIQUE NOT NULL,
    dp_url VARCHAR(255),
    date_of_registration DATETIME,
    user_type VARCHAR(30)
);

CREATE TABLE Admin(
    user_id INTEGER PRIMARY KEY,
    FOREIGN KEY(user_id) REFERENCES User(user_id)
);

CREATE TABLE NonAdmin(
    user_id INTEGER PRIMARY KEY,
    company_id,
    birth_date DATETIME,
    profession VARCHAR(100),
    skills VARCHAR(1023),
    FOREIGN KEY(user_id) REFERENCES User(user_id)
);

CREATE TABLE Artist(
    user_id INTEGER PRIMARY KEY,
    portfolio_url VARCHAR(255),
    avg_career_grd REAL,
    FOREIGN KEY(user_id) REFERENCES NonAdmin(user_id)
);

CREATE TABLE Recruiter(
    user_id INTEGER PRIMARY KEY,
    FOREIGN KEY(user_id) REFERENCES NonAdmin(user_id)
);

CREATE TABLE CareerExpert(
    user_id INTEGER PRIMARY KEY,
    FOREIGN KEY(user_id) REFERENCES NonAdmin(user_id)
);

CREATE TABLE Report(
    report_id INTEGER PRIMARY KEY,
    report_url VARCHAR(255) NOT NULL,
    start_date DATETIME,
    location VARCHAR(100),
    job_type VARCHAR(100),
    user_type VARCHAR(100),
    creator_id INTEGER NOT NULL,
    FOREIGN KEY(creator_id) REFERENCES Admin(user_id)
);

CREATE TABLE Experience(
    experience_id INTEGER PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100),
    description TEXT,
    start_date DATETIME NOT NULL,
    end_date DATETIME,
    FOREIGN KEY(user_id) REFERENCES NonAdmin(user_id)
);

CREATE TABLE Company(
    company_id INTEGER PRIMARY KEY,
    location VARCHAR(255),
    description VARCHAR(1023),
    name VARCHAR(255) NOT NULL
);

CREATE TABLE Employment(
    experience_id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL,
    profession VARCHAR(100),
    FOREIGN KEY(experience_id) REFERENCES Experience(experience_id),
    FOREIGN KEY(company_id) REFERENCES Company(company_id)
);

CREATE TABLE Education(
    experience_id INTEGER PRIMARY KEY,
    school_name VARCHAR(255) NOT NULL,
    degree VARCHAR(255),
    department VARCHAR(255),
    cgpa NUMERIC(3, 2) CHECK (cgpa BETWEEN 0.00 AND 4.00),
    FOREIGN KEY (experience_id) REFERENCES Experience(experience_id)
);

CREATE TABLE CareerGrade(
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    expert_id INTEGER NOT NULL,
    grade INTEGER NOT NULL,
    feedback_text TEXT,
    FOREIGN KEY (user_id) REFERENCES NonAdmin(user_id),
    FOREIGN KEY (expert_id) REFERENCES CareerExpert(user_id)
);

CREATE TRIGGER IF NOT EXISTS update_average
    AFTER INSERT ON CareerGrade
    FOR EACH ROW
    BEGIN
        UPDATE Artist
        SET avg_career_grd = (
            SELECT AVG(grade) FROM CareerGrade C WHERE C.user_id = NEW.user_id
        )
        WHERE Artist.user_id = NEW.user_id;
    END;

CREATE TABLE Job(
    company_id INTEGER NOT NULL,
    recruiter_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    due_date DATETIME,
    profession VARCHAR(255),
    location VARCHAR(255),
    job_requirements VARCHAR(1023),
    description VARCHAR(1023),
    FOREIGN KEY (company_id) REFERENCES Company(company_id),
    FOREIGN KEY (recruiter_id) REFERENCES Recruiter(user_id)
);

CREATE TABLE Post(
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(100),
    content TEXT,
    date DATETIME,
    FOREIGN KEY (user_id) REFERENCES NonAdmin(user_id)
);

CREATE TABLE Comment (
    comment_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    user_id INTEGER NOT NULL,
    content TEXT,
    date DATETIME,
    FOREIGN KEY (user_id) REFERENCES NonAdmin(user_id),
    FOREIGN KEY (post_id) REFERENCES Post(post_id)
);

CREATE TABLE Notification(
    notification_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    notification_type VARCHAR(100),
    content TEXT,
    timestamp DATETIME,
    PRIMARY KEY(notification_id, user_id),
    FOREIGN KEY (user_id) REFERENCES NonAdmin(user_id)
);

CREATE TABLE Connection(
    user_id1 INTEGER NOT NULL,
    user_id2 INTEGER NOT NULL,
    status TEXT CHECK (status IN ('rejected', 'approved', 'waiting') ) NOT NULL DEFAULT 'waiting',
    PRIMARY KEY(user_id1, user_id2),
    FOREIGN KEY (user_id1) REFERENCES NonAdmin(user_id),
    FOREIGN KEY (user_id2) REFERENCES NonAdmin(user_id)
);

CREATE TABLE Blocked(
    user_id1 INTEGER NOT NULL,
    user_id2 INTEGER NOT NULL,
    PRIMARY KEY(user_id1, user_id2),
    FOREIGN KEY (user_id1) REFERENCES NonAdmin(user_id),
    FOREIGN KEY (user_id2) REFERENCES NonAdmin(user_id)
);


CREATE TABLE Application(
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    date DATETIME,
    personal_info TEXT,
    cv_url VARCHAR(255),
    PRIMARY KEY(user_id, job_id),
    FOREIGN KEY(user_id) REFERENCES NonAdmin(user_id),
    FOREIGN KEY(job_id) REFERENCES Job(job_id)
);

INSERT INTO User(full_name, username, password, email_address, dp_url, date_of_registration, user_type)
VALUES
    ('John Doe', 'johndoe', 'password123', 'johndoe@example.com', 'https://example.com/johndoe.jpg', '2023-05-13 10:30:00', 'Artist'),
    ('Jane Smith', 'janesmith', 'letmein', 'janesmith@example.com', 'https://example.com/janesmith.jpg', '2023-05-14 15:45:00', 'Recruiter'),
    ('Robert Johnson', 'robjohnson', 'secret123', 'robjohnson@example.com', NULL, '2023-05-15 09:00:00', 'Artist'),
    ('Adison Miner', 'admin', 'admin123', 'admin@example.com', NULL, '2023-05-24 20:15:00', 'Admin'),
    ('Jake Ray', 'jakeray', 'hello987', 'jaker@example.com', 'https://example.com/jaker.jpg', '2023-01-09 22:33:44', 'CareerExpert'),
    ('Aubrey Dunne', 'aubrey', 'hey987', 'aubrey@example.com', NULL, '2023-06-02 00:14:24', 'Recruiter');

INSERT INTO Admin(user_id)
VALUES
    (4);

INSERT INTO NonAdmin(user_id, company_id, birth_date, profession, skills)
VALUES
    (1, 1, '1985-07-17', 'Director', 'Film Production, Scriptwriting, Cinematography, Editing'),
    (2, 2, '1974-11-28', 'Screenwriter', 'Storytelling, Plot Development, Dialogue Writing'),
    (3, 3, '2000-06-09', 'Actor', 'Method Acting, Improvisation, Voice Modulation'),
    (5, 2, '1989-03-13', 'Illustrator', 'Digital Illustration, Traditional Art Techniques'),
    (6, 4, '1973-06-09', 'Actress', 'Stage Acting, Character Development, Emotional Range');

INSERT INTO Artist(user_id, portfolio_url, avg_career_grd)
VALUES
    (1, 'https://example.com/janesmith.pdf', 97.89),
    (3, 'https://example.com/robj.pdf', 85.324 );

INSERT INTO Recruiter(user_id)
VALUES
    (2),
    (6);

INSERT INTO CareerExpert(user_id)
VALUES
    (5);

INSERT INTO Report(report_id, report_url, start_date, location, job_type, user_type, creator_id)
VALUES
    (1, 'https://example.com/report.pdf', '2023-02-25 14:32:56', 'Ankara', 'Part-Time', 'Artist', 4);

INSERT INTO Experience(experience_id, user_id, description, start_date, end_date)
VALUES
    (1, 1, 'Artist at Art Gallery', '2019-08-30', '2022-04-04'),
    (2, 2, 'Freelance Artist', '2022-07-25', '2023-02-01'),
    (3, 2, 'Artist at Creative Studio', '2016-04-29', '2023-05-06'),
    (4, 3, 'Art Intern at Contemporary Museum', '2022-09-18', '2022-10-25'),
    (5, 5, 'Artist at Art Studio', '2005-01-13', '2018-03-23'),
    (6, 1, 'Art Student at University', '2012-09-12', '2016-06-24'),
    (7, 2, 'Art Student at University', '2008-07-27', '2012-05-05'),
    (8, 3, 'Art Student at University', '2018-08-29', '2022-06-14');

INSERT INTO Company(company_id, location, description, name)
VALUES
    (1, 'Paris', "The Louvre is the world's largest art museum.", 'Louvre Museum'),
    (2, 'Florence', 'The Uffizi Gallery houses a significant collection of Renaissance art.', 'Uffizi Gallery'),
    (3, 'New York', 'The Museum of Modern Art (MoMA) showcases modern and contemporary art.', 'MoMA'),
    (4, 'London', 'The Tate Modern is a renowned contemporary art gallery.', 'Tate Modern');

INSERT INTO Employment(experience_id, company_id, profession)
VALUES
    (1, 1, 'Painter'),
    (2, 2, 'Sculptor'),
    (3, 3, 'Photographer'),
    (4, 4, 'Illustrator'),
    (5, 2, 'Graphic Designer');

INSERT INTO Education(experience_id, school_name, degree, department, cgpa)
VALUES
    (6, 'Bilkent University', "Bachelor's Degree", 'Fine Arts', 2.92),
    (7, 'Harvard University', "Bachelor's Degree", 'Art History', 3.01),
    (8, 'Oxford University', "Bachelor's Degree", 'Visual Arts', 2.89);

INSERT INTO CareerGrade(grade_id, user_id, expert_id, grade, feedback_text)
VALUES
    (1, 1, 5, 8, 'Add more photos.'),
    (2, 3, 5, 9, 'Give more detailed descriptions for experiences.');

INSERT INTO Job(company_id, recruiter_id, job_id, title, due_date, profession, location, job_requirements, description)
VALUES
    (1, 2, 1, 'Painter', '2023-07-16', 'Fine Arts', 'Los Angeles', 'Oil Painting, Watercolor', 'Full-Time Artist'),
    (2, 2, 2, 'Art Gallery Manager', '2023-06-06', 'Art Administrator', 'New York', 'Curating, Art Marketing', 'Manage operations of an art gallery.'),
    (2, 6, 3, 'Graphic Designer', '2023-06-06', 'Designer', 'Ankara', 'Adobe Photoshop, Illustrator', 'Create visually appealing designs for digital and print media.'),
    (3, 2, 4, 'Art Director', '2023-06-06', 'Creative Director', 'New York', 'Art Direction, Visual Communication', 'Lead and oversee artistic direction for creative projects.'),
    (4, 6, 5, 'Sculptor', '2023-06-06', 'Sculptor', 'New York', 'Stone Carving, Clay Modeling', 'Create sculptures using various materials and techniques.'),
    (3, 2, 6, 'Art Restorer', '2023-06-06', 'Restorer', 'Ankara', 'Art Conservation, Preservation', 'Restore and preserve artwork to maintain its integrity.'),
    (1, 6, 7, 'Photographer', '2023-06-06', 'Photographer', 'New York', 'Portrait Photography, Landscape Photography', 'Capture compelling images through photography.'),
    (4, 6, 8, 'Art Instructor', '2023-06-06', 'Art Educator', 'Istanbul', 'Teaching, Art Instruction', 'Provide guidance and instruction to aspiring artists.');

INSERT INTO Post(user_id, title, content, date)
VALUES
    (1, 'Art Exhibition Opening', 'I am excited about the opening of my art exhibition.', '2023-03-13 10:32:54'),
    (2, 'Art Workshop in Finland', 'I had an amazing time attending an art workshop in Finland.', '2023-05-03 23:48:39'),
    (3, 'Art Commission Success', 'I successfully completed a commissioned art project.', '2023-02-25 13:18:57');

INSERT INTO Comment(comment_id, post_id, user_id, content, date)
VALUES
    (1, 1, 2, 'Congrats!', '2023-03-13 11:45:36'),
    (2, 1, 3, 'Cannot wait to work with you!', '2023-03-14 08:17:39'),
    (3, 2, 1, 'I was there too.', '2023-05-04 07:53:17'),
    (4, 3, 2, 'Congratulations', '2023-02-25 16:58:03'),
    (5, 3, 1, 'Congrats on your success!', '2023-02-26 06:53:00');

INSERT INTO Connection(user_id1, user_id2, status)
VALUES
    (1, 3, 'approved'),
    (1, 5, 'rejected'),
    (3, 5, 'waiting');

INSERT INTO Blocked(user_id1, user_id2)
VALUES
    (1, 5);

INSERT INTO Application(user_id, job_id, date, personal_info, cv_url)
VALUES
    (1, 1, '2023-05-24 10:20:34', 'My name is John.', 'https://example.com/johndoe-cv.pdf'),
    (1, 6, '2023-06-01 23:38:46', 'My name is John.', 'https://example.com/johndoe-cv.pdf'),
    (3, 1, '2023-05-25 05:12:58', 'I am an artist specializing in oil painting.', 'https://example.com/robj-cv.pdf'),
    (3, 2, '2023-03-16 13:19:52', 'I have exhibited my sculptures in several galleries.', 'https://example.com/robj-cv.pdf'),
    (5, 3, '2023-04-23 12:26:37', 'I am a professional photographer with experience in capturing landscapes and portraits.', 'https://example.com/cvofjakeray.pdf');

CREATE VIEW job_application_count AS
SELECT J.job_id, J.title, COUNT(user_id) AS application_count
FROM Job J
LEFT JOIN Application A ON J.job_id = A.job_id
GROUP BY J.job_id, J.title;

CREATE VIEW average_age_view AS
SELECT AVG(CAST((strftime('%Y', 'now') - strftime('%Y', birth_date)) - (strftime('%m-%d', 'now') < strftime('%m-%d', birth_date)) AS REAL)) AS average_age
FROM NonAdmin;
