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
        # result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_blue_potions, num_green_potions FROM global_inventory WHERE id=1"))
        result = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE quantity > 0"))
        data = result.fetchall()
        # num_red_potions = data[0]
        # num_blue_potions = data[1]
        # num_green_potions = data[2]

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

        
        # if num_red_potions > 0:
        #     result.append({
        #                 "sku": "RED_POTION",
        #                 "name": "red potion",
        #                 "quantity": num_red_potions,
        #                 "price": 50,
        #                 "potion_type": [100, 0, 0, 0],
        #             })

        # if num_blue_potions > 0:
        #     result.append({
        #         "sku": "BLUE_POTION",
        #         "name": "blue potion",
        #         "quantity": num_blue_potions,
        #         "price": 50,                        
        #         "potion_type": [0, 0, 100, 0],
        #     })
        # if num_green_potions > 0: 
        #     result.append({
        #         "sku": "GREEN_POTION",
        #         "name": "green potion",
        #         "quantity": num_green_potions,
        #         "price": 50,                        
        #         "potion_type": [0, 100, 0, 0],
        #     })
        
        return result
