-- DROP SCHEMA dbo;

CREATE SCHEMA dbo;
-- point_duty.dbo.table_1 definition

-- Drop table

-- DROP TABLE point_duty.dbo.table_1;

CREATE TABLE point_duty.dbo.table_1 (
	id int IDENTITY(1,1) NOT NULL,
	frame_no varchar(30) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	video_name varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	detectron_object text COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	ocr_object text COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	CONSTRAINT PK__table_1__3213E83F62FC9096 PRIMARY KEY (id)
);


-- point_duty.dbo.table_2 definition

-- Drop table

-- DROP TABLE point_duty.dbo.table_2;

CREATE TABLE point_duty.dbo.table_2 (
	id int IDENTITY(1,1) NOT NULL,
	frame_no varchar(30) COLLATE Latin1_General_BIN NOT NULL,
	video_name varchar(255) COLLATE Latin1_General_BIN NOT NULL,
	file_path varchar(255) COLLATE Latin1_General_BIN NOT NULL,
	is_processed tinyint DEFAULT 0 NULL,
	is_ocr_processed tinyint DEFAULT 0 NULL,
	CONSTRAINT PK__table_2__3213E83F1E6B5C2C PRIMARY KEY (id)
);
