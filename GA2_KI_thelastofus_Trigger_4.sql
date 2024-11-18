CREATE OR REPLACE FUNCTION transfer_to_worker()
RETURNS TRIGGER AS $$
DECLARE
    worker_id UUID;
    amount DECIMAL;
    category_id UUID;
BEGIN
    SELECT workerId, TotalPrice
    INTO worker_id, amount
    FROM TR_SERVICE_ORDER
    WHERE Id = NEW.serviceTrId;

    UPDATE 'user'
    SET MyPayBalance = MyPayBalance + amount
    WHERE Id = worker_id;

    SELECT Id
    INTO category_id
    FROM TR_MYPAY_CATEGORY
    WHERE Name = 'Received Service Transaction Fee';

    INSERT INTO TR_MYPAY userId,
        CURRENT_TIMESTAMP,
        myPayBalance
    VALUES (worker_id, CURRENT_TIMESTAMP, amount, category_id);

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION after_status_update()
RETURNS TRIGGER AS $$
BEGIN
SELECT Status
    INTO order_status
    FROM ORDER_STATUS
    WHERE Id = NEW.statusId;

    IF order_status = 'Order Completed' THEN
        PERFORM transfer_to_worker();
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_status_update
AFTER INSERT ON TR_ORDER_STATUS
FOR EACH ROW
EXECUTE FUNCTION after_status_update();
