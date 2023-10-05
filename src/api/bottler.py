import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    with db.engine.begin() as connection: 
        print(potions_delivered)
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_red_ml, num_green_potions, num_green_ml, num_blue_potions, num_blue_ml FROM global_inventory WHERE id=1"))
        data = result.fetchone()
        num_red_potions = data[0]
        num_red_ml = data[1]
        num_green_potions = data[2]
        num_green_ml = data[3]
        num_blue_potions = data[4]
        num_blue_ml = data[5]

        for potion in potions_delivered:
            #if we have a red potion add to num_red_potions
            #also subtract from num red ml when bottling potions 
            if potion.potion_type[0] == 100:
                num_red_potions += potion.quantity
                num_red_ml -= potion.quantity * 100
            elif potion.potion_type[1] == 100:
                num_green_potions += potion.quantity
                num_green_ml -= potion.quantity * 100
            elif potion.potion_type[2] == 100: 
                num_blue_potions += potion.quantity
                num_blue_ml -= potion.quantity * 100
        
        value = {'red_potions':num_red_potions}
        value2 = {'red_ml':num_red_ml}
        value3 = {'green_potions': num_green_potions}
        value4 = {'green_ml':num_green_ml}
        value5 = {'blue_potions': num_blue_potions}
        value6 = {'blue_ml': num_blue_ml}

        sql = sqlalchemy.text("UPDATE global_inventory SET num_red_potions=:red_potions",)
        sql2 = sqlalchemy.text("UPDATE global_inventory SET num_red_ml=:red_ml")
        connection.execute(sql, value)
        connection.execute(sql2, value2)

        sql3 = sqlalchemy.text("UPDATE global_inventory SET num_green_potions=:green_potions",)
        sql4 = sqlalchemy.text("UPDATE global_inventory SET num_green_ml=:green_ml") 
        connection.execute(sql3, value3)
        connection.execute(sql4, value4)

        sql5 = sqlalchemy.text("UPDATE global_inventory SET num_blue_potions=:blue_potions",)
        sql6 = sqlalchemy.text("UPDATE global_inventory SET num_blue_ml=:blue_ml") 
        connection.execute(sql5, value5)
        connection.execute(sql6, value6)


        print(potions_delivered)
        return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory WHERE id=1"))
        data = result.fetchone()
        num_red_ml = data[0]
        num_green_ml = data[1]
        num_blue_ml = data[2]
        
        red_qty = num_red_ml // 100
        green_qty = num_green_ml // 100
        blue_qty = num_blue_ml // 100

        print("red quantity: " + str(red_qty))
        print("green quantity: " + str(green_qty))
        print("blue quantity: " + str(blue_qty))
        result = []

        if red_qty > 0:
            result.append({
                        "potion_type": [100, 0, 0, 0],
                        "quantity": red_qty,
                    })
        if green_qty > 0: 
            result.append({
                        "potion_type": [0, 100, 0, 0],
                        "quantity": green_qty,
                    })
        if blue_qty > 0: 
            result.append({
                        "potion_type": [0, 0, 100, 0],
                        "quantity": blue_qty,
                    })
                    
        return result
