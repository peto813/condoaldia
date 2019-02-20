
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
ON account_keeping_invoice (user_id, YEAR(account_keeping_invoice.invoice_date), MONTH(account_keeping_invoice.invoice_date))
WHERE invoice_type = 'm';

CREATE UNIQUE INDEX IF NOT EXISTS uniqueMonthlyOrderPerMonth
ON account_keeping_order (customer_id, YEAR(account_keeping_order.order_date), MONTH(account_keeping_order.order_date))
WHERE order_type = 'm';

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
	        WHERE user_id=new.user_id
	        AND invoice_type='m'
	        AND YEAR(invoice_date) = YEAR(new.invoice_date)
	        AND MONTH(invoice_date)= MONTH(new.invoice_date)
	      ) IS TRUE THEN 
	      RAISE EXCEPTION 'This is an invalid date, this monthly period is closed';
	    END IF;
	  RETURN NEW;
	-- END IF; 
END
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION invocePayed()
RETURNS TRIGGER AS $$
BEGIN
	IF (TG_OP = 'UPDATE')  THEN 
	    IF (
	    	--IF ALREADY PAYED RAISE EXCEPTION
	    	old.is_payed
	      ) IS TRUE THEN
	      RAISE EXCEPTION 'This invoice has been payed, update prohibited';
	    ELSIF (
	    	--IF MODIFYING 
	    	old.user_id <>new.user_id OR
	    	old.invoice_type <>new.invoice_type OR
	    	old.invoice_number <>new.invoice_number OR
	    	old.invoice_date <>new.invoice_date OR
	    	old.order_id <>new.order_id OR
	    	old.created <>new.created

	    ) THEN RAISE EXCEPTION 'This invoice has been payed, update prohibited 2';
	    ELSIF (
	    	--IF MODIFYING 
	    	old.is_payed =new.is_payed AND
	    	old.is_payed IS TRUE

	    ) THEN RAISE EXCEPTION 'This invoice has been payed, update prohibited 3';

	    END IF;
	END IF;
	RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS preventInvoiceUpdateIfPayed ON account_keeping_invoice;
CREATE TRIGGER preventInvoiceUpdateIfPayed 
BEFORE INSERT OR UPDATE ON account_keeping_invoice
FOR EACH ROW EXECUTE PROCEDURE invocePayed();

/* This is the trigger function that is returned by the above function
it prevents an insert if a monthly invoice already exists for the invoice date.
 */
DROP TRIGGER IF EXISTS monthIsClosedForInsert ON account_keeping_invoice;
CREATE TRIGGER monthIsClosedForInvoiceInsert 
BEFORE INSERT OR UPDATE ON account_keeping_invoice
FOR EACH ROW EXECUTE PROCEDURE monthIsClosed();


CREATE OR REPLACE FUNCTION checkOrderInvoiced()
RETURNS TRIGGER AS $$
BEGIN
	IF (TG_OP = 'UPDATE') THEN
		IF OLD.status= 'i' THEN
			RAISE EXCEPTION 'THIS ORDER HAS BEEN INVOICED, UPDATE FORBIDDEN';
		END IF;
	END IF;
	return NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS preventOrderUpdateIfInvoiced ON account_keeping_order;
CREATE TRIGGER preventOrderUpdateIfInvoiced 
BEFORE UPDATE ON account_keeping_order
FOR EACH ROW EXECUTE PROCEDURE checkOrderInvoiced();


CREATE OR REPLACE FUNCTION checkIfMonthClosed()
RETURNS TRIGGER AS $$
BEGIN
	IF (TG_OP = 'INSERT') THEN
	    IF EXISTS(
	        SELECT condo_manager_condo.id, account_keeping_invoice.invoice_type, YEAR(account_keeping_invoice.invoice_date), MONTH(account_keeping_invoice.invoice_date)
	        FROM account_keeping_invoice
	        INNER JOIN condo_manager_condo ON condo_manager_condo.user_id= account_keeping_invoice.user_id
	       	WHERE invoice_type = 'm'
	      ) IS TRUE THEN 
	      RAISE EXCEPTION 'This is an invalid date, this monthly period is closed';
	    END IF;
	    RETURN NEW;
	ELSIF (TG_OP = 'UPDATE')  THEN 
	    IF EXISTS(
	        SELECT condo_manager_condo.id, account_keeping_invoice.invoice_type, YEAR(account_keeping_invoice.invoice_date), MONTH(account_keeping_invoice.invoice_date)
	        FROM account_keeping_invoice
	        INNER JOIN condo_manager_condo ON condo_manager_condo.user_id= account_keeping_invoice.user_id
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