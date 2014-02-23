
create table thing (
    id serial primary key,
    key text unique,
    type text,
    info text
);

create table properties (
    id serial primary key,
    thing_id integer references thing,
    name text,
    value integer references thing
);

