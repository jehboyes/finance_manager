"""
Module for user defined functions required by the database

Not to be confused with python functions, held in a seperate folder in the parent directory
"""
from finance_manager.database.replaceable import ReplaceableObject as o

function_list = [
    o("udfGetMonthProp",
      """ 
(
	@acad_year int,
	@period int, 
	@start DATE, 
	@end DATE
)
RETURNS float
AS
BEGIN
	-- Declare the return variable here
	DECLARE @result float

	-- Declare month start and end 
	DECLARE @pstart DATE
	DECLARE @pdays float
	DECLARE @pend DATE
	SET @pstart = DATEADD(MONTH,@period, DATEFROMPARTS(@acad_year, 7,1))
	SET @pdays = DAY(EOMONTH(@pstart))
	SET @pend = DATEADD(DAY,@pdays-1, @pstart)

	--SET arbitrary upper and lower limits for dates if invalid 
	SET @end = ISNULL(@end, DATEFROMPARTS(3000,01,01))
	SET @start = ISNULL(@start, DATEFROMPARTS(1950,01,01))
	
	SET @result = CASE
		WHEN @end <= @start	THEN 1 --End before start (invalid so full cost)
		WHEN @end > @pend AND @start < @pstart THEN 1 -- work through
		WHEN @end < @pstart then 0 --End before month start 
		WHEN @start > @pend THEN 0 --Start after month; By this point, must start or end in month 
		WHEN DATEDIFF(DAY, @start, @end) < @pdays THEN CAST(DATEDIFF(DAY, @start, @end) AS FLOAT) / @pdays --Start and end in month 
		WHEN @start >= @pstart THEN (CAST(DATEDIFF(DAY,@start, @pend) as float)+1)/@pdays -- start in month 
		ELSE CAST(DATEDIFF(DAY, @pstart, @end) as float)/@pdays -- end in month 
		END 
	-- Return the result of the function
	RETURN @result

END
"""
      ),
    o("udfFracFTE", f"""
(
    @hours float, 
    @work_hours float, 
    @hol_hours float 
)
RETURNS float 
AS 
BEGIN 
	if @hours < 0
		SET @hours = 0
    DECLARE @result float 
    DECLARE @epsilon float -- Error term derived from historic contract calculation 
    SET @epsilon = 0.002873557
    SET @result = @hours/@work_hours + (1+@hol_hours/@work_hours)*@epsilon
    RETURN @result
END
    """),
    o("udfNI", f"""
(
    @monthly_sal float, 
	@threshold float, 
	@rate float
)
RETURNS float 
AS 
BEGIN 
    DECLARE @result float 
	DECLARE @NIable float
	SET @NIable = @monthly_sal - @threshold * 52 /12 
	SET @result = CASE  
					WHEN @NIable <= 0 THEN 0
					ELSE  @NIable * @rate
					END 
    RETURN @result
END
    """),
    o("udfGetMonthSpine",
      """ 
(
	@acad_year int,
	@period int, 
	@start DATE = '1950/01/01', 
	@spine int = 0, 
	@grade int = 0,
	@set_cat_id CHAR(3)
)
RETURNS float
AS
BEGIN
	-- Returns the spine value after applicable increment. 

	-- Declare the return variable here
	DECLARE @result float

	-- Alter start to be month start
	SET @start = ISNULL(@start, DATEFROMPARTS(1950,01,01))
	SET @start = DATEFROMPARTS(YEAR(@start),MONTH(@start),1)

	-- Declare month start and end 
	DECLARE @pstart DATE
	DECLARE @pdays int
	DECLARE @pend DATE
	SET @pstart = DATEADD(MONTH,@period, DATEFROMPARTS(@acad_year, 7,1))
	SET @pdays = DAY(EOMONTH(@pstart))
	SET @pend = DATEADD(DAY,@pdays-1, @pstart)

	--Probation 
	DECLARE @probation int
	SET @probation = 8

	-- Months since started
	DECLARE @monthdiff int
	SET @monthdiff = DATEDIFF(m, @start, @pstart) 

	--GET max spine
	DECLARE @max_spine int
	SET @max_spine = (SELECT sp FROM (SELECT MAX(spine) as sp, grade FROM staff_spine_grade GROUP BY grade) x WHERE grade = @grade)
	
	SET @spine = CASE
		WHEN @spine < 1 THEN 1
		WHEN @grade = 0 THEN @spine --no grade supplied
		WHEN @spine >= @max_spine THEN @spine  --If at top of grade, then current
		WHEN @monthdiff < @probation THEN @spine --If still in probation, then current
		WHEN @monthdiff >= @probation AND @start >= DATEFROMPARTS(@acad_year,8,1) THEN @spine --If passed probation but started in year
		ELSE @spine+1 --Increment reached by staff with space in grade who ended 
					  --probation at least eight months ago and started in previous year
		END 

	SET @result = (SELECT value FROM staff_spine WHERE acad_year = @acad_year AND set_cat_id = @set_cat_id AND spine = @spine)
	
	-- Return the result of the function
	RETURN @result

END
"""
      ),
    o("udfGetMonthSpinePoint",
      """ 
(
	@acad_year int,
	@period int, 
	@start DATE = '1950/01/01', 
	@spine int = 0, 
	@grade int = 0
)
RETURNS float
AS
BEGIN
	-- Returns the spine point after applicable increment. 

	-- Declare the return variable here
	DECLARE @result float

	-- Alter start to be month start
	SET @start = ISNULL(@start, DATEFROMPARTS(1950,01,01))
	SET @start = DATEFROMPARTS(YEAR(@start),MONTH(@start),1)

	-- Declare month start and end 
	DECLARE @pstart DATE
	DECLARE @pdays int
	DECLARE @pend DATE
	SET @pstart = DATEADD(MONTH,@period, DATEFROMPARTS(@acad_year, 7,1))
	SET @pdays = DAY(EOMONTH(@pstart))
	SET @pend = DATEADD(DAY,@pdays-1, @pstart)

	--Probation 
	DECLARE @probation int
	SET @probation = 8

	-- Months since started
	DECLARE @monthdiff int
	SET @monthdiff = DATEDIFF(m, @start, @pstart) 

	--GET max spine
	DECLARE @max_spine int
	SET @max_spine = (SELECT sp FROM (SELECT MAX(spine) as sp, grade FROM staff_spine_grade GROUP BY grade) x WHERE grade = @grade)
	
	SET @spine = CASE
		WHEN @spine < 1 THEN 1
		WHEN @grade = 0 THEN @spine --no grade supplied
		WHEN @spine >= @max_spine THEN @spine  --If at top of grade, then current
		WHEN @monthdiff < @probation THEN @spine --If still in probation, then current
		WHEN @monthdiff >= @probation AND @start >= DATEFROMPARTS(@acad_year,8,1) THEN @spine --If passed probation but started in year
		ELSE @spine+1 --Increment reached by staff with space in grade who ended 
					  --probation at least eight months ago and started in previous year
		END 

		-- Return the result of the function
	RETURN @spine

END
"""
      )
]
