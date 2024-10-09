
CREATE TABLE `gg_daily` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '服务信息ID',
  `current_date` date default null comment '当前日期',
  `campaign_name` varchar(255) NOT NULL DEFAULT '' COMMENT '广告活动名称',
  `keyword` varchar(255) NOT NULL DEFAULT '' COMMENT '关键词',
  `state` varchar(50) NOT NULL DEFAULT '' COMMENT '状态，ENABLED：开启，PAUSED：暂停',
  `daily_budget` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '每日预算',
  `match_type` varchar(50) NOT NULL DEFAULT '' COMMENT '匹配类型：EXACT：精准，PHRASE：短语，BROAD：广泛',
  `spend` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT 'spend',
  `CPC` decimal(10,4) NOT NULL DEFAULT '0.00' COMMENT 'CPC',
  `ROAS` decimal(10,4) NOT NULL DEFAULT '0.00' COMMENT 'ROAS',
  `sales` decimal(10,4) NOT NULL DEFAULT '0.00' COMMENT '销售额',
  `clicks` int not null default '0' COMMENT '点击次数',
  `is_deleted` tinyint NOT NULL DEFAULT '0' COMMENT '是否删除（0、未删除，1、已删除）',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB COMMENT='每日广告数据';


CREATE TABLE `inv_stock` (
`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
`sku` varchar(255) CHARACTER SET latin1 DEFAULT NULL COMMENT 'sku',
`fnsku` varchar(255) CHARACTER SET latin1 DEFAULT NULL COMMENT 'fnsku',
`asin` varchar(255) CHARACTER SET latin1 DEFAULT NULL COMMENT 'asin',
`quantity` decimal(5,0) DEFAULT NULL COMMENT '数量总和',
`available` decimal(5,0) DEFAULT NULL COMMENT 'available',
`unfulfillable` decimal(5,0) DEFAULT NULL COMMENT 'unfulfillable',
`inbound` decimal(5,0) DEFAULT NULL COMMENT 'inbound',
`reserved` decimal(5,0) DEFAULT NULL COMMENT 'reserved',
`state` varchar(255) CHARACTER SET latin1 DEFAULT NULL COMMENT '状态，在售',
`price` decimal(10,2) DEFAULT NULL COMMENT '售价',
`created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
`remark` varchar(255) CHARACTER SET latin1 DEFAULT NULL COMMENT '备注',
`is_deleted` int(11) DEFAULT '0' COMMENT '是否删除，0正常；1删除',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存数据';


ALTER TABLE inv_stock
MODIFY COLUMN `sku` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT 'sku',
MODIFY COLUMN `fnsku` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT 'fnsku',
MODIFY COLUMN `asin` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT 'asin',
MODIFY COLUMN `state` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '状态，在售',
MODIFY COLUMN `remark` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '备注';
