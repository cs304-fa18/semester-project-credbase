use credbase;

drop table if exists json;
create table json (
    nm int(10) unsigned primary key,
    filename varchar(50)
);
