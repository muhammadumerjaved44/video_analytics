-- DROP SCHEMA dbo;

--CREATE SCHEMA dbo;
-- point_duty.dbo.videos definition

-- Drop table

-- DROP TABLE point_duty.dbo.videos;

CREATE TABLE point_duty.dbo.videos (
	id bigint IDENTITY(1,1) NOT NULL,
	video_name varchar(255) COLLATE Latin1_General_BIN NOT NULL,
	version_id varchar(100) COLLATE Latin1_General_BIN NOT NULL,
	is_video_processed tinyint DEFAULT 0 NULL,
	is_in_progress tinyint DEFAULT 0 NULL,
	video_url text COLLATE Latin1_General_BIN NOT NULL,
	CONSTRAINT PK_26 PRIMARY KEY (id)
);


-- point_duty.dbo.frames definition

-- Drop table

-- DROP TABLE point_duty.dbo.frames;

CREATE TABLE point_duty.dbo.frames (
	id bigint IDENTITY(0,1) NOT NULL,
	video_id bigint NOT NULL,
	frame_no varchar(255) COLLATE Latin1_General_BIN NOT NULL,
	video_name varchar(255) COLLATE Latin1_General_BIN NOT NULL,
	file_path text COLLATE Latin1_General_BIN NOT NULL,
	is_processed tinyint DEFAULT 0 NULL,
	is_ocr_processed tinyint DEFAULT 0 NULL,
	is_pic_purified tinyint DEFAULT 0 NULL,
	is_qr_processed tinyint DEFAULT 0 NULL,
	CONSTRAINT PK_24 PRIMARY KEY (id,video_id),
	CONSTRAINT FK_94 FOREIGN KEY (video_id) REFERENCES point_duty.dbo.videos(id)
);
 CREATE NONCLUSTERED INDEX FK_96 ON dbo.frames (  video_id ASC  )
	 WITH (  PAD_INDEX = OFF ,FILLFACTOR = 100  ,SORT_IN_TEMPDB = OFF , IGNORE_DUP_KEY = OFF , STATISTICS_NORECOMPUTE = OFF , ONLINE = OFF , ALLOW_ROW_LOCKS = ON , ALLOW_PAGE_LOCKS = ON  )
	 ON [PRIMARY ] ;


-- point_duty.dbo.frame_data definition

-- Drop table

-- DROP TABLE point_duty.dbo.frame_data;

CREATE TABLE point_duty.dbo.frame_data (
	id bigint IDENTITY(0,1) NOT NULL,
	frame_id bigint NOT NULL,
	video_id bigint NOT NULL,
	frame_no varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	video_name varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	object_ varchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	attribute_ varchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	value_ text COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	CONSTRAINT PK__frame_data__3213E83F62FC9096 PRIMARY KEY (id,frame_id,video_id),
	CONSTRAINT FK_85 FOREIGN KEY (frame_id,video_id) REFERENCES point_duty.dbo.frames(id,video_id)
);
 CREATE NONCLUSTERED INDEX FK_88 ON dbo.frame_data (  frame_id ASC  , video_id ASC  )
	 WITH (  PAD_INDEX = OFF ,FILLFACTOR = 100  ,SORT_IN_TEMPDB = OFF , IGNORE_DUP_KEY = OFF , STATISTICS_NORECOMPUTE = OFF , ONLINE = OFF , ALLOW_ROW_LOCKS = ON , ALLOW_PAGE_LOCKS = ON  )
	 ON [PRIMARY ] ;
