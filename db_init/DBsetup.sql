CREATE TABLE IF NOT EXISTS users(
    id SERIAL,
    user_id INT,
    username text,
    name text,
    reg_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admins(
    id SERIAL,
    user_id INT,
    username text
);

CREATE TABLE IF NOT EXISTS orders(
    id SERIAL,
    order_id INT,
    user_id INT,
    service_id INT,
    order_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contacts(
    id SERIAL,
    user_id INT,
    first_name TEXT,
    last_name TEXT,
    phone TEXT
);