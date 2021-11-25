-- DROP SCHEMA dbo;

CREATE SCHEMA dbo;

-- point_duty.dbo.table_1 definition

-- Drop table

DROP TABLE point_duty.dbo.table_1;

CREATE TABLE point_duty.dbo.table_1 (
	id bigint IDENTITY(1,1) NOT NULL,
	frame_no varchar(30) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	video_id bigint NOT NULL,
	video_name varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	object_ varchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	value_ varchar(25) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	text_ text COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	detectron_object text COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	ocr_object text COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	CONSTRAINT PK__table_1__3213E83F62FC9096 PRIMARY KEY (id)
);
 CREATE NONCLUSTERED INDEX FK_29 ON dbo.table_1 (  video_id ASC  )
	 WITH (  PAD_INDEX = OFF ,FILLFACTOR = 100  ,SORT_IN_TEMPDB = OFF , IGNORE_DUP_KEY = OFF , STATISTICS_NORECOMPUTE = OFF , ONLINE = OFF , ALLOW_ROW_LOCKS = ON , ALLOW_PAGE_LOCKS = ON  )
	 ON [PRIMARY ] ;

-- point_duty.dbo.table_2 definition

-- Drop table
DROP TABLE point_duty.dbo.table_2;

CREATE TABLE point_duty.dbo.table_2 (
	id bigint IDENTITY(1,1) NOT NULL,
	video_id bigint NOT NULL,
	frame_no varchar(30) COLLATE Latin1_General_BIN NOT NULL,
	video_name varchar(255) COLLATE Latin1_General_BIN NOT NULL,
	file_path text COLLATE Latin1_General_BIN NOT NULL,
	is_processed tinyint DEFAULT 0 NULL,
	is_ocr_processed tinyint DEFAULT 0 NULL,
	CONSTRAINT PK_24 PRIMARY KEY (id)
);
 CREATE NONCLUSTERED INDEX FK_32 ON dbo.table_2 (  video_id ASC  )
	 WITH (  PAD_INDEX = OFF ,FILLFACTOR = 100  ,SORT_IN_TEMPDB = OFF , IGNORE_DUP_KEY = OFF , STATISTICS_NORECOMPUTE = OFF , ONLINE = OFF , ALLOW_ROW_LOCKS = ON , ALLOW_PAGE_LOCKS = ON  )
	 ON [PRIMARY ] ;


DROP TABLE point_duty.dbo.table_3;

CREATE TABLE point_duty.dbo.table_3 (
	id bigint IDENTITY(1,1) NOT NULL,
	video_name varchar(255) COLLATE Latin1_General_BIN NOT NULL,
	version_id varchar(100) COLLATE Latin1_General_BIN NOT NULL,
	is_video_processed tinyint DEFAULT 0 NULL,
	is_in_progress tinyint DEFAULT 0 NULL,
	video_url text COLLATE Latin1_General_BIN NOT NULL,
	CONSTRAINT PK_26 PRIMARY KEY (id)
);

-- point_duty.dbo.table_2 foreign keys

ALTER TABLE point_duty.dbo.table_2 ADD CONSTRAINT FK_30 FOREIGN KEY (video_id) REFERENCES point_duty.dbo.table_3(id);
-- point_duty.dbo.table_1 foreign keys

ALTER TABLE point_duty.dbo.table_1 ADD CONSTRAINT FK_27 FOREIGN KEY (video_id) REFERENCES point_duty.dbo.table_3(id);

