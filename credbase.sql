-- drop database if exists `credbase`;
CREATE DATABASE IF NOT EXISTS `credbase`;

USE `credbase`;


drop table if exists wikipedia;
drop table if exists alexa;
drop table if exists searchresults;
drop table if exists similar;
drop table if exists watching;
drop table if exists newsSource;
drop table if exists user;

-- drop table if exists newsSource;
CREATE TABLE newsSource(
    nsid int auto_increment primary key,
    name varchar(60),
    publisher varchar (60),
    mediatype enum ('newspaper', 'magazine', 'radio/TV', 'blog', 'website'),
    location varchar (100), 
    editor varchar (60),
    doe year
) ENGINE=InnoDB;

-- drop table if exists searchresult;
CREATE TABLE searchresults (
    sid int auto_increment primary key,
    title varchar(100),
    originQuery varchar(60),
    resultDate date,
    url varchar(100),
    nsid int,
    foreign key (nsid) references newsSource(nsid) on delete set null on update cascade
    -- primary key (nsid, sid)
) ENGINE=InnoDB;
 
-- drop table if exists alexa;
CREATE TABLE alexa (
    aid int auto_increment primary key,
    globalrank int,
    numLinksIn int,
    numLinksOut int,
    nsid int,
    foreign key (nsid) references newsSource(nsid) on delete set null on update cascade
    -- primary key (nsid, aid)
) ENGINE=InnoDB;

-- drop table if exists wikipedia;
CREATE TABLE wikipedia (
    wid int auto_increment primary key,
    url varchar(100),
    name varchar(60),
    nsid int,
    foreign key (nsid) references newsSource(nsid) on delete set null on update cascade
    -- primary key (nsid, wid)
) ENGINE=InnoDB;

-- drop table if exists user;
CREATE TABLE user(
    uid int auto_increment,
    name varchar(60),
    access enum("admin", "regular"),
    hashedPWD varchar(60),
    primary key (uid)
) ENGINE=InnoDB;


-- drop table if exists watching;
CREATE TABLE watching(
    nsid int not null,
    uid int not null,
    addDate date,
    primary key (uid, nsid),
    foreign key (nsid) references newsSource(nsid) on delete cascade,
    foreign key (uid) references user(uid) on delete cascade
) ENGINE=InnoDB;


-- drop table if exists similar;
CREATE TABLE similar(
    nsid1 int not null,
    nsid2 int not null,
    primary key (nsid1, nsid2),
    foreign key (nsid1) references newsSource(nsid) on delete cascade,
    foreign key (nsid2) references newsSource(nsid) on delete cascade
) ENGINE=InnoDB;


insert into newsSource(name, publisher, mediatype, location, editor, doe) values ("CNN", "Turner Broadcasting", "website", "Atlanta, GA", null, 1980);

insert into newsSource(name, publisher, mediatype, location, editor, doe) values ("New York Times", "A.G. Sulzberger", "newspaper", "New York, NY", null, 1851);

insert into searchresults(title, originQuery, resultDate, url, nsid) values ("Donald Trump Jr., Trump Org. in spotlight after Cohen plea", "President Trump", '11-30-2018', "https://www.cnn.com/2018/11/29/politics/donald-trump-jr-cohen-trump-organization/index.html", 1);

insert into alexa(globalrank, numLinksIn, numLinksOut, nsid) values (102, 177446, null, 1);

insert into wikipedia(url, name, nsid) values ("https://en.wikipedia.org/wiki/CNN", "CNN", 1);

insert into similar(nsid1, nsid2) values (1, 2);
