
/* This script creates or replaces a function that returns
an integer representing the year of a date  */
CREATE OR REPLACE FUNCTION YEAR(DATE) RETURNS INTEGER
AS $$
      SELECT EXTRACT(YEAR FROM $1)::INTEGER;
$$ LANGUAGE SQL IMMUTABLE;


/* This script creates or replaces a function that returns
an integer representing the MONTH of a date  */
CREATE OR REPLACE FUNCTION MONTH(DATE) RETURNS INTEGER
AS $$
      SELECT EXTRACT(MONTH FROM $1)::INTEGER;
$$ LANGUAGE SQL IMMUTABLE;

/* This script creates A unique index if it does not exist
that restrics the amount of monthly invoices to one per month
 */
CREATE UNIQUE INDEX IF NOT EXISTS uniqueMonthlyInvoicePerMonth
ON account_keeping_invoice (condo_id, YEAR(account_keeping_invoice.invoice_date), MONTH(account_keeping_invoice.invoice_date))
WHERE invoice_type = 'm';


/* This script creates a constraint in the transactions table that prohibits
posting at dates later than the present day.
 */
ALTER TABLE account_keeping_transaction DROP CONSTRAINT IF EXISTS lessThanOrEqualsToday;
ALTER TABLE account_keeping_transaction
ADD CONSTRAINT lessThanOrEqualsToday
CHECK (transaction_date <= date(NOW()) at time zone 'utc');

/* This script creates a constraint in the invoices table that prohibits
posting at dates later than the present day.
 */
ALTER TABLE account_keeping_invoice DROP CONSTRAINT IF EXISTS invoiceLessThanOrEqualsToday;
ALTER TABLE account_keeping_invoice
ADD CONSTRAINT invoiceLessThanOrEqualsToday
CHECK (invoice_date <= date(NOW()) at time zone 'utc');


/* This function determines if one monthly invoice has been issued for a particular insert date
and returns a trigger function
 */
CREATE OR REPLACE FUNCTION monthIsClosed()
RETURNS TRIGGER AS $$
BEGIN
	-- IF (TG_OP = 'INSERT') THEN
	    IF EXISTS(
	        SELECT * FROM account_keeping_invoice
	        WHERE condo_id=new.condo_id
	        AND invoice_type='m'
	        AND YEAR(invoice_date) = YEAR(new.invoice_date)
	        AND MONTH(invoice_date)= MONTH(new.invoice_date)
	      ) IS TRUE AND new.invoice_type <> 'm' THEN 
	      RAISE EXCEPTION 'This is an invalid date, this monthly period is closed';
	    END IF;
	  RETURN NEW;
	-- END IF; 
END
$$ LANGUAGE plpgsql;


/* This is the trigger function that is returned by the above function
it prevents an insert if a monthly invoice already exists for the invoice date.
 */
DROP TRIGGER IF EXISTS monthIsClosedForInsert ON account_keeping_invoice;
CREATE TRIGGER monthIsClosedForInvoiceInsert 
BEFORE INSERT OR UPDATE ON account_keeping_invoice
FOR EACH ROW EXECUTE PROCEDURE monthIsClosed();


CREATE OR REPLACE FUNCTION checkIfMonthClosed()
RETURNS TRIGGER AS $$
BEGIN
	IF (TG_OP = 'INSERT') THEN
	    IF EXISTS(
	        SELECT condo_manager_condo.id, account_keeping_invoice.invoice_type, YEAR(account_keeping_invoice.invoice_date), MONTH(account_keeping_invoice.invoice_date)
	        FROM account_keeping_invoice
	        INNER JOIN condo_manager_condo ON condo_manager_condo.id= account_keeping_invoice.condo_id
	       	WHERE invoice_type = 'm'
	      ) IS TRUE THEN 
	      RAISE EXCEPTION 'This is an invalid date, this monthly period is closed';
	    END IF;
	    RETURN NEW;
	ELSIF (TG_OP = 'UPDATE')  THEN 
	    IF EXISTS(
	        SELECT condo_manager_condo.id, account_keeping_invoice.invoice_type, YEAR(account_keeping_invoice.invoice_date), MONTH(account_keeping_invoice.invoice_date)
	        FROM account_keeping_invoice
	        INNER JOIN condo_manager_condo ON condo_manager_condo.id= account_keeping_invoice.condo_id
	       	WHERE invoice_type = 'm'
	      ) IS TRUE THEN 
	      RAISE EXCEPTION 'This is an invalid date, this monthly period is closed';
	    END IF;
	END IF;
	RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS monthTransactionsClosedForUpdate ON account_keeping_transaction;
CREATE TRIGGER monthIsClosedForTransactions 
BEFORE INSERT OR UPDATE ON account_keeping_transaction
FOR EACH ROW EXECUTE PROCEDURE checkIfMonthClosed();



--	DROP A DATABASE PRE STUFF (IF YOU CANT DROP IT)
-- SELECT pg_terminate_backend(pg_stat_activity.pid)
-- FROM pg_stat_activity
-- WHERE pg_stat_activity.datname = 'condominioaldia_db';