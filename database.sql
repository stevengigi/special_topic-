create database sql_my;
show databases;
use test; /*test 為 database*/
/* tt 為 databale 裡面的table */
describe tt; /*顯示表格內容狀態*/
select * from tt; /*顯示表格內容*/
update tt
set local_frequency = 62
where frequency =60.4516;
drop table tt;
create table tt(
	time_t timestamp,
    frequency decimal(6,4),
    local_frequency decimal(6,4),
    primary key (time_t)
);
alter table prac1 add gpa decimal(6,4);
describe tt;
drop table prac1; /*刪除表格*/
insert into tt (time_t,frequency,local_frequency) values (2022-03-19 22:05:39,62,61,5);
select *from prac1;

set SQL_SAFE_UPDATES=0;

update prac1
set f=50
where local_f=61;