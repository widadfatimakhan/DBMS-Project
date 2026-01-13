USE [project]
GO

-- 1. Add the new column Is_Active to the Movies table
-- We use BIT (0 or 1) for boolean/status checks, and make it NOT NULL
-- with a default constraint for future inserts.
ALTER TABLE [dbo].[Movies]
ADD [Is_Active] BIT NOT NULL CONSTRAINT DF_Movies_Is_Active DEFAULT 1;
GO

-- 2. Update all existing 6 movies to be marked as ACTIVE (1)
-- Since your table currently only has the movies you inserted, this sets them all to active.
UPDATE [dbo].[Movies]
SET [Is_Active] = 1;
GO

-- Optional: Remove the default constraint if you want future movies to require a specific value
-- ALTER TABLE [dbo].[Movies]
-- DROP CONSTRAINT DF_Movies_Is_Active;
-- GO

-- Optional: Verify the change
select* from Movies
select* from Cinema
select* from Bookings
select* from Tickets