CREATE USER bot WITH PASSWORD '12345';

GRANT CONNECT ON DATABASE visit_center TO bot;

GRANT SELECT, INSERT, UPDATE, DELETE ON users TO bot;
GRANT SELECT, INSERT, UPDATE, DELETE ON admins TO bot;
GRANT SELECT, INSERT, UPDATE, DELETE ON orders TO bot;
GRANT SELECT, INSERT, UPDATE, DELETE ON contacts TO bot;

GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO bot;
GRANT UPDATE ON SEQUENCE users_id_seq TO bot;

GRANT USAGE, SELECT ON SEQUENCE admins_id_seq TO bot;
GRANT UPDATE ON SEQUENCE admins_id_seq TO bot;

GRANT USAGE, SELECT ON SEQUENCE orders_id_seq TO bot;
GRANT UPDATE ON SEQUENCE users_id_seq TO bot;

GRANT USAGE, SELECT ON SEQUENCE contacts_id_seq TO bot;
GRANT UPDATE ON SEQUENCE admins_id_seq TO bot;