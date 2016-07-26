CREATE TABLE content_rule
(
    Id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
    item VARCHAR(255) DEFAULT 'title' NOT NULL COMMENT 'title，ctime，gtime，content 等',
    rule VARCHAR(255) COMMENT '匹配规则',
    etc VARCHAR(255) COMMENT '备注'
);
CREATE INDEX item ON content_rule (item);
CREATE TABLE current_domain_setting
(
    Id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(255),
    start_url VARCHAR(255),
    site_domain VARCHAR(255),
    black_domain VARCHAR(255) COMMENT '以 ; 分割的列表',
    setting_json LONGTEXT COMMENT '配置简报，json版'
);
CREATE TABLE url_rule
(
    Id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(255) DEFAULT 'admin' NOT NULL COMMENT 'user',
    start_url VARCHAR(255) DEFAULT '' NOT NULL COMMENT 'homepage',
    site_domain VARCHAR(255) DEFAULT '' NOT NULL COMMENT 'domain',
    detail_or_list CHAR(1) DEFAULT '0' COMMENT '0:detail,1:list',
    scope CHAR(1) DEFAULT '0' NOT NULL COMMENT '0:netloc,1:path,2:query',
    white_or_black CHAR(1) DEFAULT '0' NOT NULL COMMENT '0:white,1:black',
    weight CHAR(1) DEFAULT '0' NOT NULL COMMENT '0:高，1：中，2：低',
    regex VARCHAR(255) COMMENT '正则表达式',
    etc VARCHAR(255) COMMENT '备注'
);
CREATE INDEX scope ON url_rule (start_url, site_domain);
CREATE TABLE user
(
    Id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(255),
    password VARCHAR(255),
    Authorization CHAR(1) COMMENT '0:admin,1:normal',
    etc VARCHAR(255) COMMENT '备注'
);