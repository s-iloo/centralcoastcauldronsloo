import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM potions"))
        data = result.fetchall()
        result = []
        for row in data: 
            print(row.name)
            print(row.sku)
            # print(row.quantity)
            print(row.price)
            print(row.id)
            quantity = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM potion_ledger WHERE potion_id=:pot_id"), {'pot_id': row.id})
            quantity = quantity.fetchone()
            quantity = quantity.balance
            print(quantity)
            if(quantity > 0):
                result.append({
                "sku": row.sku,
                    "name": row.name,
                    "quantity": quantity,
                    "price": row.price,
                    "potion_type": [row.red, row.green, row.blue, row.dark],
                })
        
        return result
