CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT,
    user_name VARCHAR(30) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    bio TEXT,
    profile_pic VARCHAR(255),
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE,
   
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



CREATE TABLE IF NOT EXISTS files (
    id INT NOT NULL AUTO_INCREMENT,
    file_name VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(4),
    size_bytes BIGINT,
    thumbnail_path VARCHAR(255),
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    visibility ENUM('public', 'private', 'unlisted') DEFAULT 'public',
    user_id INT NOT NULL,
    
    CONSTRAINT fk_files_users
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    

    PRIMARY KEY(id),

    FULLTEXT KEY idx_files_fulltext (file_name, description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



CREATE TABLE IF NOT EXISTS comments (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    file_id INT NOT NULL,
    parent_id INT,
    content TEXT NOT NULL,
    publi_date DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_comments_users
        FOREIGN KEY(user_id) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_comments_files
        FOREIGN KEY(file_id) REFERENCES files(id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_comments_comments
        FOREIGN KEY(parent_id) REFERENCES comments(id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



CREATE TABLE IF NOT EXISTS ratings (
    id INT NOT NULL AUTO_INCREMENT,
    file_id INT NOT NULL,
    user_id INT NOT NULL,
    value TINYINT NOT NULL CHECK(value BETWEEN 1 AND 5),

    CONSTRAINT uq_user_file
        UNIQUE (user_id, file_id),

    CONSTRAINT fk_ratings_files
        FOREIGN KEY(file_id) REFERENCES files(id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_ratings_users
        FOREIGN KEY(user_id) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



CREATE TABLE IF NOT EXISTS subscriptions (
    id INT NOT NULL AUTO_INCREMENT,
    subscriber_id INT NOT NULL,
    subscribed_id INT NOT NULL,
    subscription_date DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_subscriber_subscribed
        UNIQUE (subscriber_id, subscribed_id),

    CONSTRAINT fk_subscriber_users
        FOREIGN KEY(subscriber_id) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_subscribed_users
        FOREIGN KEY(subscribed_id) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



CREATE TABLE IF NOT EXISTS password_resets (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expiration DATETIME NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    creation DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_password_resets_users
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;