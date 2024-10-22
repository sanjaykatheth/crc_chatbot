def CustomTraining(vn):
    return
    # List of training examples, each with a question and corresponding SQL query
    training_data = [
        {
         
            #Q:1
            "question": "What are the top 5 operators with the shortest average wait time from submitted date to permitted date, excluding certain notice types?",
            "sql": """
                SELECT TOP 5 OPERATOR, AVG(DATEDIFF(DAY, SUBMITTED_DATE, PERMITTED_DATE)) AS AVGWAITTIME 
                FROM [CRC].[DBO].[CALGEM_PERMITS_T] 
                WHERE NOTICE_TYPE NOT IN ('Re-Abandon', 'Abandon') 
                AND PERMITTED_DATE IS NOT NULL 
                AND SUBMITTED_DATE IS NOT NULL 
                AND SUBMITTED_DATE <> PERMITTED_DATE  -- Exclude same submitted and permitted dates
                GROUP BY OPERATOR 
                ORDER BY AVGWAITTIME ASC;
            """
        },
        {
            #Q:2
            "question": "Which field has the shortest wait time from submit to permit date for all permits excluding abandonments?",
            "sql": """
                SELECT FIELD, AVG(DATEDIFF(DAY, SUBMITTED_DATE, PERMITTED_DATE)) AS AVGWAITTIME 
                FROM [CRC].[DBO].[CALGEM_PERMITS_T] 
                WHERE NOTICE_TYPE NOT IN ('Re-Abandon', 'Abandon') 
                AND PERMITTED_DATE IS NOT NULL 
                AND SUBMITTED_DATE IS NOT NULL 
                AND SUBMITTED_DATE <> PERMITTED_DATE  -- Exclude where submitted and permitted dates are equal
                GROUP BY FIELD 
                ORDER BY AVGWAITTIME ASC;
            """
        },
        {   
            #Q:3
            "question": "What are the top 5 operators in approved permits for the year 2023?",
            "sql": """
                SELECT TOP 5 OPERATOR, COUNT(*) AS PERMITCOUNT 
                FROM [CRC].[DBO].[CALGEM_PERMITS_T] 
                WHERE FORM_STATUS = 'APPROVED' 
                AND YEAR(PERMITTED_DATE) = 2023 
                AND PERMITTED_DATE IS NOT NULL 
                AND SUBMITTED_DATE IS NOT NULL 
                AND SUBMITTED_DATE <> PERMITTED_DATE  -- Exclude where submitted and permit are the same
                AND NOTICE_TYPE NOT IN ('Abandon', 'Re-Abandon')  -- Exclude specific notice types
                GROUP BY OPERATOR 
                ORDER BY PERMITCOUNT DESC;
            """
        },
        {
             #Q:4
             "question": "What are the approval trends for New Drills, Sidetracks, and Reworks among the top 5 operators in approved permits for the year 2023?",
             "sql": """
                ;WITH TOPOPERATORS AS 
                (
                SELECT TOP 5 OPERATOR 
                FROM [CRC].[DBO].[CALGEM_PERMITS_T] 
                WHERE PERMIT_STATUS = 'Approved' 
                AND NOTICE_TYPE IN ('New Drill', 'Sidetrack', 'Rework') 
                AND NOTICE_TYPE NOT IN ('Abandon', 'Re-Abandon') -- Exclude unwanted notice types
                AND YEAR(PERMITTED_DATE) = 2023  -- Filter by year 2023
                AND PERMITTED_DATE IS NOT NULL 
                AND SUBMITTED_DATE IS NOT NULL 
                AND SUBMITTED_DATE <> PERMITTED_DATE  -- Exclude where submitted and permit are the same
                GROUP BY OPERATOR 
                ORDER BY COUNT(*) DESC
                ) 
                SELECT OPERATOR, 
                NOTICE_TYPE, 
                COUNT(*) AS APPROVEDCOUNT 
                FROM [CRC].[DBO].[CALGEM_PERMITS_T] 
                WHERE PERMIT_STATUS = 'Approved'
                AND NOTICE_TYPE IN ('Rework') 
                AND NOTICE_TYPE NOT IN ('Abandon', 'Re-Abandon') -- Exclude unwanted notice types
                AND OPERATOR IN (SELECT OPERATOR FROM TOPOPERATORS) 
                AND YEAR(PERMIT_DATE) = 2023  -- Filter by year 2023
                GROUP BY OPERATOR, NOTICE_TYPE 
                ORDER BY OPERATOR, APPROVEDCOUNT DESC;
                """ 
                },
        {
             #Q:6
            "question": "How many days have CRC’s Rework (or other) permits been pending with CalGEM??",
            "sql": """
                SELECT FORM_ID, 
                       OPERATOR, 
                       NOTICE_TYPE, 
                       DATEDIFF(DAY, SUBMITTED_DATE, PERMITTED_DATE) AS PENDINGDAYS, 
                       DATEDIFF(MONTH, SUBMITTED_DATE, PERMITTED_DATE) AS PENDINGMONTHS 
                FROM [CRC].[DBO].[CALGEM_PERMITS_T] 
                WHERE NOTICE_TYPE NOT IN ('Abandon', 'Re-Abandon')  -- Exclude unwanted notice types
                AND NOTICE_TYPE IN ('Rework') 
                AND FORM_STATUS = 'Approved' 
                AND PERMITTED_DATE IS NOT NULL 
                ORDER BY PENDINGDAYS DESC;
                 """
        },
        {
            "question": "What is the average time (in days/months) that CRC’s Reworks have been waiting on CalGEM to approve the NOI?",
            "sql": """
                SELECT AVG(DATEDIFF(DAY, SUBMITTED_DATE, PERMITTED_DATE)) AS AVERAGEPENDINGDAYS,
                       AVG(DATEDIFF(MONTH, SUBMITTED_DATE, PERMITTED_DATE)) AS AVERAGEPENDINGMONTHS 
                FROM [CRC].[DBO].[CALGEM_PERMITS_T] 
                WHERE NOTICE_TYPE NOT IN ('Abandon', 'Re-Abandon') -- Exclude unwanted notice types
                  AND FORM_STATUS = 'Approved' 
                  AND PERMITTED_DATE IS NOT NULL 
                  AND NOTICE_TYPE = 'Rework'; -- Only considering Rework permits
              """
        },

        {
            #Q:7
            "question": "What is the API number for the well RVGU 284",
            "sql": """
                SELECT DISTINCT WELL_DESIGNATION, API 
                FROM [CRC].[DBO].[CALGEM_PERMITS_T] 
                WHERE WELL_DESIGNATION = 'RVGU 284';
             """
        },
        
        {
            #Q:8
            "question": "Find the API for well name 'RVGU 284' in the field 'RIO VISTA GAS'.",
            "sql": """
                SELECT distinct API , WELL_DESIGNATION, FIELD
                FROM [CRC].[DBO].[CALGEM_PERMITS_T] 
                WHERE WELL_DESIGNATION = 'RVGU 284' AND FIELD = 'RIO VISTA GAS';
            """
        },
        {
            #Q:9
            "question": "Return all notice types that were approved in 2024",
            "sql": """
                SELECT NOTICE_TYPE, COUNT(*) AS NOTICECOUNT 
                FROM [CRC].[DBO].[CALGEM_PERMITS_T] 
                WHERE FORM_STATUS = 'Approved' 
                AND YEAR(PERMITTED_DATE) = 2024 
                GROUP BY NOTICE_TYPE 
                ORDER BY NOTICECOUNT DESC;
            """
        },
        {
            #Q:10
            "question": "What are the different notice types for each status in 2023 (approved, on hold, submitted, returned).",
            "sql": """
                SELECT PERMIT_STATUS, NOTICE_TYPE, COUNT(*) AS PERMITCOUNT  
                FROM [CRC].[dbo].[CALGEM_PERMITS_T] 
                WHERE FORM_STATUS IN ('Approved', 'On Hold', 'Submitted', 'Returned') 
                AND YEAR(PERMITTED_DATE) = 2023
                GROUP BY PERMIT_STATUS, NOTICE_TYPE 
                ORDER BY NOTICE_TYPE;
            """
        },
        {
            #Q:11
            ##question - only our operators or compititors too means?
            "question": "List all the approved permits by each operator.",
            "sql": """
                SELECT OPERATOR, COUNT(*) AS APPROVAL_COUNT 
                FROM [CALGEM_PERMITS_T] 
                WHERE FORM_STATUS = 'Approved' 
                GROUP BY OPERATOR 
                ORDER BY APPROVAL_COUNT DESC;
            """
        },
        {
            #Q:12
            "question": "Return forms with form_status in or equal to 'On Hold' or 'Submitted' that have a calgem_permit_review_status_t.status of 'Pass'.",
            "sql": """
                SELECT P.* 
                FROM [CALGEM_PERMITS_T] P 
                JOIN [CALGEM_PERMIT_REVIEW_T] R 
                ON P.FORM_ID = R.FORM_ID 
                WHERE P.FORM_STATUS IN ('On Hold', 'Submitted') 
                AND R.STATUS = 'Pass';
            """
        },
        {
            #Q:13
            "question": "Return forms with FORM_STATUS in or equal to 'On Hold' or 'Submitted' and COMMENTS equal to 'CEQA HQ NOI REVIEW' that have a CALGEM_PERMIT_REVIEW_STATUS_T.STATUS as null.",
            "sql": """
                SELECT P.* 
                FROM [CRC].[DBO].[CALGEM_PERMITS_T] P 
                JOIN [CRC].[DBO].[CALGEM_PERMIT_REVIEW_T] R 
                ON P.FORM_ID = R.FORM_ID 
                WHERE P.FORM_STATUS IN ('On Hold', 'Submitted', 'Approved') 
                AND R.COMMENTS = 'CEQA HQ NOI REVIEW' 
                AND R.STATUS IS NULL;
            """
        },
        {
            #Q:14
            "question": "What is the average time from submitted_date to the comment_date where comments = 'CEQA HQ NOI REVIEW' and calgem_permit_review_status_t.status = 'Pass' for each district?",
            "sql": """
                SELECT P.DISTRICT, AVG(DATEDIFF(DAY, P.SUBMITTED_DATE, R.COMMENT_DATE)) AS AVERAGEDAYS 
                FROM [CRC].[DBO].[CALGEM_PERMITS_T] P 
                JOIN [CRC].[DBO].[CALGEM_PERMIT_REVIEW_T] R 
                ON P.FORM_ID = R.FORM_ID 
                WHERE R.COMMENTS = 'CEQA HQ NOI REVIEW' 
                AND R.STATUS = 'Pass' 
                GROUP BY P.DISTRICT;
            """
        }
    ]


    # Iterate over each training example and train the model
    for data in training_data:
        vn.train(question=data["question"], sql=data["sql"])

    vn.train(ddl='''
        SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[CALGEM_PERMITS_T](
	[FORM_ID] [int] NOT NULL,
	[DISTRICT] [varchar](8) NULL,
	[NOTICE_TYPE] [varchar](10) NULL,
	[OPERATOR] [varchar](91) NULL,
	[API] [varchar](10) NULL,
	[WELL_DESIGNATION] [varchar](255) NULL,
	[WELL_TYPE] [varchar](20) NULL,
	[FIELD] [varchar](255) NULL,
	[PLSS] [varchar](16) NULL,
	[FORM_STATUS] [varchar](9) NULL,
	[COUNTY] [varchar](22) NULL,
	[LEASE] [varchar](30) NULL,
	[UGS_PROJECT] [varchar](18) NULL,
	[CONFIDENTIALITY_REQUESTED] [varchar](3) NULL,
	[SUBMITTED_DATE] [date] NULL,
	[PERMITTED_DATE] [date] NULL,
	[LAST_UPDATED_BY] [varchar](20) NULL,
	[LAST_UPDATED_DATE] [datetime] NULL,
	[CREATED_BY] [varchar](20) NULL,
	[CREATED_BY_DATE] [date] NULL,
	[PERMIT_EXP] [date] NULL,
	[PERMIT_NO] [int] NULL,
	[PERMIT_LINK] [varchar](1000) NULL,
	[COMMENTS] [varchar](4000) NULL,
	[COMMENTS_DATE] [date] NULL,
	[INITIAL_SUB_DATE] [date] NULL,
	[EVENT_YORN] [varchar](20) NULL,
	[EVENT_DATE] [date] NULL,
	[DAY_UNTIL_PERMIT] [int] NULL,
	[STATUS_DATE] [date] NULL,
	[HISTORY_DUE] [date] NULL,
	[HISTORY_SUBMITTED_DATE] [date] NULL,
	[RIG_RELEASE] [date] NULL,
	[PRIORITY] [int] NULL,
	[ENGINEER] [varchar](200) NULL,
	[FAULT_BLOCK] [varchar](20) NULL,
	[DATE_REQUIRED] [date] NULL,
	[CONDUCTOR_SET_DATE] [date] NULL,
	[EST_PERMIT_EXP] [date] NULL,
	[EXP_YN] [varchar](20) NULL,
	[APPROV_QTR] [int] NULL,
	[OTHER_TYPE] [varchar](20) NULL,
PRIMARY KEY CLUSTERED 
(
	[FORM_ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
            ''')
    
    vn.train(sql='''
             SELECT TOP (1000) [FORM_ID]
      ,[DISTRICT]
      ,[NOTICE_TYPE]
      ,[OPERATOR]
      ,[API]
      ,[WELL_DESIGNATION]
      ,[WELL_TYPE]
      ,[FIELD]
      ,[PLSS]
      ,[FORM_STATUS]
      ,[COUNTY]
      ,[LEASE]
      ,[UGS_PROJECT]
      ,[CONFIDENTIALITY_REQUESTED]
      ,[SUBMITTED_DATE]
      ,[PERMITTED_DATE]
      ,[LAST_UPDATED_BY]
      ,[LAST_UPDATED_DATE]
      ,[CREATED_BY]
      ,[CREATED_BY_DATE]
      ,[PERMIT_EXP]
      ,[PERMIT_NO]
      ,[PERMIT_LINK]
      ,[COMMENTS]
      ,[COMMENTS_DATE]
      ,[INITIAL_SUB_DATE]
      ,[EVENT_YORN]
      ,[EVENT_DATE]
      ,[DAY_UNTIL_PERMIT]
      ,[STATUS_DATE]
      ,[HISTORY_DUE]
      ,[HISTORY_SUBMITTED_DATE]
      ,[RIG_RELEASE]
      ,[PRIORITY]
      ,[ENGINEER]
      ,[FAULT_BLOCK]
      ,[DATE_REQUIRED]
      ,[CONDUCTOR_SET_DATE]
      ,[EST_PERMIT_EXP]
      ,[EXP_YN]
      ,[APPROV_QTR]
      ,[OTHER_TYPE]
  FROM [CRC].[dbo].[CALGEM_PERMITS_T]
            ''')
    
    # CRC Table: CALGEM_PERMIT_REVIEW_T 
    vn.train(ddl='''
        SET ANSI_NULLS ON
        GO
        SET QUOTED_IDENTIFIER ON
        GO
        CREATE TABLE [dbo].[CALGEM_PERMIT_REVIEW_T](
            [ID] [int] NULL,
            [COMMENTS] [nvarchar](max) NULL,
            [COMMENT_DATE] [date] NULL,
            [COMMENTER] [nvarchar](255) NULL,
            [API_10] [nvarchar](255) NULL,
            [STATUS] [nvarchar](255) NULL,
            [FORM_ID] [int] NULL,
            [last_updated_ts] [datetime] NULL
        ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
        GO
            ''')
    
    vn.train(sql='''
            SELECT TOP (1000) [ID]
      ,[COMMENTS]
      ,[COMMENT_DATE]
      ,[COMMENTER]
      ,[API_10]
      ,[STATUS]
      ,[FORM_ID]
      ,[last_updated_ts]
      ,[RowID]
  FROM [CRC].[dbo].[CALGEM_PERMIT_REVIEW_T]             
            ''')
    
    # CRC Table: CALGEM_PERMIT_STATUS_T 
    vn.train(ddl='''
        SET ANSI_NULLS ON
        GO
        SET QUOTED_IDENTIFIER ON
        GO
        CREATE TABLE [dbo].[CALGEM_PERMIT_STATUS_T](
            [REC_ID] [int] NULL,
            [FORM_ID] [int] NULL,
            [FORM_STATUS] [varchar](20) NULL,
            [STATUS_DATE] [date] NULL
        ) ON [PRIMARY]
        GO
            ''')
    
    vn.train(sql='''
             SELECT TOP (1000) [REC_ID]
            ,[FORM_ID]
            ,[FORM_STATUS]
            ,[STATUS_DATE]
        FROM [CRC].[dbo].[CALGEM_PERMIT_STATUS_T]
            ''')
    
    # CRC Table: CALGEM_WELL_LIST_T 
    vn.train(ddl='''
       SET ANSI_NULLS ON
        GO
        SET QUOTED_IDENTIFIER ON
        GO
        CREATE TABLE [dbo].[CALGEM_WELL_LIST_T](
            [API] [varchar](10) NULL,
            [DESIGNATION] [varchar](220) NULL,
            [OP_NAME] [varchar](180) NULL,
            [OP_CODE] [varchar](50) NULL,
            [WELL_TYPE] [varchar](140) NULL,
            [CALGEM_STATUS] [varchar](60) NULL,
            [FIELD_NAME] [varchar](210) NULL,
            [LEASE_NAME] [varchar](160) NULL,
            [WELL_NO] [varchar](60) NULL,
            [DISTRICT] [varchar](60) NULL,
            [SEC] [varchar](20) NULL,
            [TWN] [varchar](40) NULL,
            [RGE] [varchar](40) NULL,
            [BM] [varchar](30) NULL,
            [LAT] [varchar](110) NULL,
            [LONGITUDE] [varchar](120) NULL,
            [AREA] [varchar](80) NULL,
            [COUNTY] [varchar](40) NULL,
            [SPUD_DATE] [varchar](100) NULL,
            [CONF_STATUS] [varchar](80) NULL,
            [CONF_EXP_DATE] [varchar](100) NULL,
            [STATUS_DATE] [varchar](90) NULL,
            [NEXT_TEST_DUE] [varchar](100) NULL,
            [WELL_STIM] [varchar](50) NULL,
            [WELL_MAIN] [varchar](50) NULL
        ) ON [PRIMARY]
        GO

            ''')
    
    vn.train(sql='''
        SELECT TOP (1000) [API]
        ,[DESIGNATION]
        ,[OP_NAME]
        ,[OP_CODE]
        ,[WELL_TYPE]
        ,[CALGEM_STATUS]
        ,[FIELD_NAME]
        ,[LEASE_NAME]
        ,[WELL_NO]
        ,[DISTRICT]
        ,[SEC]
        ,[TWN]
        ,[RGE]
        ,[BM]
        ,[LAT]
        ,[LONGITUDE]
        ,[AREA]
        ,[COUNTY]
        ,[SPUD_DATE]
        ,[CONF_STATUS]
        ,[CONF_EXP_DATE]
        ,[STATUS_DATE]
        ,[NEXT_TEST_DUE]
        ,[WELL_STIM]
        ,[WELL_MAIN]
    FROM [CRC].[dbo].[CALGEM_WELL_LIST_T]
            ''')