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
        result = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE quantity > 0"))
        data = result.fetchall()

        result = []
        for row in data: 
            print(row.name)
            print(row.sku)
            print(row.quantity)
            print(row.price)
            result.append({
            "sku": row.sku,
                "name": row.name,
                "quantity": row.quantity,
                "price": row.price,
                "potion_type": [row.red, row.green, row.blue, row.dark]
            })
        
        return result
