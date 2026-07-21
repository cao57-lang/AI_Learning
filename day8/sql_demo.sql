create database if not exists ai_dataset_db
	default character set  utf8mb4
	default collate utf8mb4_unicode_ci;
use ai_dataset_db;
create table `user`(
	id int auto_increment primary key comment '用户ID，自增主键',
	username varchar(50) not null unique comment '登录账号，不可重复',
	password varchar(255) not null comment '登陆密码(实际项目应加密存储)',
	role enum('annotator','admin') not null default 'annotator' comment '角色：annotator普通标注员，admin管理员',
	created_at timestamp default current_timestamp comment '注册时间'
)comment '标注员用户表';
create table `project`(
	id int auto_increment primary key comment '项目ID',
	name varchar(100) not null comment '项目名称',
	description text comment '项目描述',
	deadline date comment '交付截止日期',
	manager_id int not null comment '项目负责人ID，关联user表',
	created_at timestamp  default current_timestamp comment '创建时间',
	foreign key (manager_id) references `user`(id) on delete restrict
)comment 'AI标注项目表';
create table `dataset`(
	id int auto_increment primary key comment '数据集ID',
	project_id int not null comment '项目所属ID',
	total_samples int not null default 0 comment '样本总量',
	labeled_samples int not null default 0 comment '已标注样本量',
	label_type varchar(50) comment '标签类型',
	status enum('pending','in_progress','completed') default 'pending' comment '数据集状态',
	created_at timestamp default current_timestamp comment '创建时间',
	foreign key (project_id) references `project`(id) on delete cascade  
)comment '数据集表';
insert into `user` (username,password,role) values
('zhangsan','123456','annotator'),
('lisi','123456','annotator'),
('admin_wang','123456','admin');
insert into `project` (name,description,deadline,manager_id) values 
('自动驾驶标注项目','对路况图像进行2D框标注，包含行人、车辆','2026-09-30',3),
('NLP情感分析项目','对客服对话文本进行情感标签标注','2026-08-15',3);
insert into `dataset` (project_id,total_samples,labeled_samples,label_type,status) values
(1,10000,3500,'目标检测','in_progress'),
(1,5000,5000,'分类','completed'),
(2,8000,1200,'文本情感分析','in_progress');
select * from `user`;
select name,deadline from `project` order by deadline asc;
select * from `dataset`
where total_samples > 5000 and status = 'in_progress';
update  `project` set deadline = date_add(deadline,interval  7 day)
where id = 1;
delete from `user` where id = 2;
select
	project_id,
	sum(total_samples) as 总样本,
	sum(labeled_samples) as 已完成样本,
	round(sum(labeled_samples) / sum(total_samples)*100,2) as 完成率
from `dataset`
group by project_id;
select
	p.name as 项目名,
	u.username as 负责人,
	d.total_samples as 样本总量,
	d.labeled_samples as 已标注量
from `dataset` d
join `project` p on d.project_id=p.id
join `user` u on p.manager_id=u.id;
select u.username,p.name as 负责项目
from `user` u
left join `project` p on u.id=p.manager_id;