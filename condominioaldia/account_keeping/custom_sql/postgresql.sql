CREATE OR REPLACE FUNCTION YEAR(DATE) RETURNS INTEGER
AS $$
      SELECT EXTRACT(YEAR FROM $1)::INTEGER;
$$ LANGUAGE SQL IMMUTABLE;

CREATE OR REPLACE FUNCTION MONTH(DATE) RETURNS INTEGER
AS $$
      SELECT EXTRACT(MONTH FROM $1)::INTEGER;
$$ LANGUAGE SQL IMMUTABLE;

CREATE UNIQUE INDEX IF NOT EXISTS uniqueMonthlyInvoicePerMonth
ON account_keeping_invoice (condo_id, YEAR(account_keeping_invoice.invoice_date), MONTH(account_keeping_invoice.invoice_date))
WHERE invoice_type = 'm';

ALTER TABLE account_keeping_transaction DROP CONSTRAINT IF EXISTS lessThanOrEqualsToday;
ALTER TABLE account_keeping_transaction
ADD CONSTRAINT lessThanOrEqualsToday
CHECK (transaction_date <= date(NOW()) at time zone 'utc');