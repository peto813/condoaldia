CREATE OR REPLACE FUNCTION dateYear(invoice_date date)
RETURNS integer AS $$
BEGIN
  RETURN YEAR(invoice_date);
END;
$$ LANGUAGE plpgsql
IMMUTABLE;


CREATE OR REPLACE FUNCTION dateMonth(invoice_date date)
RETURNS integer AS $$
BEGIN
  RETURN MONTH(invoice_date);
END;
$$ LANGUAGE plpgsql
IMMUTABLE;


CREATE UNIQUE INDEX IF NOT EXISTS uniqueMonthlyInvoicePerMonth
ON account_keeping_invoice (condo_id, dateYear(account_keeping_invoice.invoice_date), dateMonth(account_keeping_invoice.invoice_date))
WHERE invoice_type = 'm';

ALTER TABLE account_keeping_transaction
ADD CONSTRAINT lessThanOrEqualsToday
CHECK (transaction_date <= date(NOW()) at time zone 'utc');


CREATE OR REPLACE FUNCTION monthIsClosed()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS(
        SELECT * FROM account_keeping_invoice
        WHERE condo=new.condo
        AND invoice.invoice_type='m'
        AND YEAR(invoice.invoice_date) = YEAR(new.invoice_date)
        AND MONTH(invoice.invoice_date)=MONTH(new.invoice_date)
      ) IS TRUE THEN 
      RAISE EXCEPTION 'This Answer is an invalid date';
    END IF;
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS monthIsClosedForInsert ON account_keeping_invoice;
CREATE TRIGGER monthIsClosedForInsert 
BEFORE INSERT ON account_keeping_invoice
FOR EACH ROW EXECUTE PROCEDURE monthIsClosed();